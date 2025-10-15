# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""minicon/pipeline.py

Fully‑typed, robust, and debuggable implementation of the
Download → Transcribe → Write‑report pipeline.

Key features
------------
* TypedDict for Whisper output.
* Custom exception hierarchy.
* Config validation on __init__.
* Detailed debug‑level logging.
* run_batch with progress bar, retries, skip‑already‑done logic,
  statistics return value and optional parallel execution.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from tqdm import tqdm  # pip install tqdm

from .config import Config, ConfigError
from .download_cache import download_cache
from .utils import is_valid_youtube_url, retry, timeout


# --------------------------------------------------------------------- #
# TypedDict for the dict returned by Whisper (and by the wrapper method)
# --------------------------------------------------------------------- #
class WhisperResult(TypedDict, total=False):
    text: str
    segments: List[Dict[str, Any]]
    language: str
    diarization: List[Dict[str, Any]]


# --------------------------------------------------------------------- #
# Custom exception hierarchy – makes error handling explicit
# --------------------------------------------------------------------- #
class MiniConError(RuntimeError):
    """Base class for all MiniCon pipeline errors."""


class DownloadError(MiniConError):
    """Raised when a YouTube download cannot be completed."""


class TranscriptionError(MiniConError):
    """Raised when Whisper fails to produce a transcript."""


class CacheError(MiniConError):
    """Raised for unexpected cache‑related problems."""


# --------------------------------------------------------------------- #
# Main pipeline class
# --------------------------------------------------------------------- #
DEFAULT_DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"


class MiniConPipeline:
    """
    End‑to‑end pipeline that downloads a YouTube video, transcribes it
    with Whisper and writes a plain‑text report.

    Required configuration parameters
    --------------------------------
    * ``temp_dir`` – where raw audio files are stored.
    * ``report_dir_primary`` – directory for the final transcript.
    * ``model_name`` – Whisper model identifier (e.g. ``"base"``).
    * ``language`` – default transcription language (e.g. ``"en"``).
    * ``fp16`` – ``True`` to use half‑precision, ``False`` otherwise.
    * ``audio_suffix`` – file‑extension for downloaded audio (default ``".mp3"``).
    * ``transcript_suffix`` – extension for cached transcript files
      (default ``".txt"``).
    * ``report_suffix`` – extension for final reports
      (default ``".txt"``).

    Example URLs file (one URL per line, comments with ‘#’ are ignored)::

        # My favourite talks
        https://youtu.be/abc123
        https://www.youtube.com/watch?v=def456

    """

    # ----------------------------------------------------------------- #
    # Construction & config validation
    # ----------------------------------------------------------------- #
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.log = logger or logging.getLogger("minicon.pipeline")
        self._debug = logging.getLogger("minicon.pipeline.debug")
        self._whisper_model: Optional[Any] = None
        self._diarization_enabled: bool = False
        self._diarization_pipeline: Optional[Any] = None
        self._diarization_failed: bool = False
        self._diarization_import_error: Optional[Exception] = None

        try:
            import pyannote.audio  # noqa: F401
        except Exception as exc:  # pragma: no cover - environment specific
            self._diarization_import_error = exc
            self.log.warning(
                "pyannote.audio not available – diarisation will stay disabled. "
                "Install 'minicon[diarisation]' to enable it."
            )

        try:
            self._validate_config()
        except ConfigError as exc:
            self.log.error("Invalid configuration: %s", exc)
            raise
        self._debug.info("Pipeline configuration validated")

        if getattr(self.config, "diarization_enabled", False):
            self.enable_diarization(True)

    def _validate_config(self) -> None:
        """Make sure the supplied Config contains all mandatory attributes."""
        required = [
            "temp_dir",
            "report_dir_primary",
            "model_name",
            "language",
            "fp16",
            "audio_suffix",
            "transcript_suffix",
            "report_suffix",
        ]
        missing = []
        for attr in required:
            if not hasattr(self.config, attr):
                missing.append(attr)
                continue
            value = getattr(self.config, attr)
            if value is None:
                missing.append(attr)
                continue
            if isinstance(value, str) and value.strip() == "":
                missing.append(attr)
                continue
        if missing:
            raise ValueError(f"Missing required Config attributes: {missing}")

    # ----------------------------------------------------------------- #
    # URL validation helpers
    # ----------------------------------------------------------------- #
    def _ensure_valid_url(self, url: str) -> None:
        """Raise a ValueError if *url* is not a recognised YouTube link."""
        if not is_valid_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url!r}")

    # ----------------------------------------------------------------- #
    # Whisper model lazy loader
    # ----------------------------------------------------------------- #
    def _ensure_whisper(self) -> None:
        """Import Whisper and load the model only once."""
        if self._whisper_model is None:
            try:
                import whisper  # type: ignore
            except Exception as exc:  # pragma: no cover
                self.log.error("Unable to import whisper: %s", exc)
                raise MiniConError("Whisper not installed") from exc

            self._debug.info("Loading Whisper model %s", self.config.model_name)
            self._whisper_model = whisper.load_model(self.config.model_name)

    # ----------------------------------------------------------------- #
    # Transcription (public)
    # ----------------------------------------------------------------- #
    def transcribe(self, audio_path: Path, url: Optional[str] = None) -> WhisperResult:
        """
        Transcribe *audio_path* using Whisper.

        If *url* is provided we first attempt to fetch a cached transcript.
        The full Whisper result (including optional diarisation) is returned
        as a :class:`WhisperResult` TypedDict.
        """
        # ---- Cache hit -------------------------------------------------
        if url and download_cache.is_transcribed(url):
            cached = download_cache.get_transcribed_videos()
            entry = next(
                (e for e in cached if e.get("url") == url and "transcript_path" in e),
                None,
            )
            if entry and Path(entry["transcript_path"]).exists():
                self.log.info("Using cached transcript for %s", url)
                with open(entry["transcript_path"], "r", encoding="utf-8") as fh:
                    return WhisperResult(text=fh.read(), segments=[], language="en")

        # ---- Actual transcription ---------------------------------------
        self._ensure_whisper()
        assert self._whisper_model is not None

        self.log.info("Transcribing %s", audio_path.name)
        self._debug.debug(
            "Whisper options: language=%s fp16=%s",
            self.config.language,
            self.config.fp16,
        )

        opts: Dict[str, Any] = {
            "language": self.config.language,
            "task": "transcribe",
            "fp16": self.config.fp16,
        }
        if self._diarization_enabled:
            opts["word_timestamps"] = True
            self._debug.debug("Word‑timestamp option enabled for diarisation")

        try:
            with timeout(self.config.transcribe_timeout_seconds):
                result: WhisperResult = self._whisper_model.transcribe(
                    str(audio_path), **opts
                )  # type: ignore[arg-type]
        except TimeoutError as exc:
            raise TranscriptionError(
                f"Transcription timed out for {audio_path}"
            ) from exc
        except Exception as exc:  # pragma: no cover
            raise TranscriptionError(f"Whisper failed for {audio_path}") from exc

        # ---- Optional diarisation --------------------------------------
        if self._diarization_enabled and result.get("segments"):
            self._debug.info(
                "Running diarisation on %d segments",
                len(result["segments"]),
            )
            result["segments"] = self._perform_diarization(
                audio_path, result["segments"]
            )
            result["diarization"] = result["segments"]

        # ---- Cache the plain‑text transcript ---------------------------
        if url:
            transcript_path = audio_path.with_suffix(self.config.transcript_suffix)
            with open(transcript_path, "w", encoding="utf-8") as fh:
                fh.write(result.get("text", ""))
            download_cache.mark_transcribed(url, str(transcript_path))
            self._debug.debug("Cached transcript to %s", transcript_path)

        return result

    def _ensure_diarizer(self) -> bool:
        """Lazy-load the diarization pipeline if available."""
        if self._diarization_pipeline is not None:
            return True
        if self._diarization_failed or self._diarization_import_error:
            return False

        model_id = self.config.diarization_model or DEFAULT_DIARIZATION_MODEL

        try:
            from pyannote.audio import Pipeline as PyannotePipeline  # type: ignore
        except ImportError:
            self.log.warning(
                "pyannote.audio is not installed. Speaker diarisation will "
                "fallback to a single-speaker transcript."
            )
            self._diarization_failed = True
            return False

        pipeline_kwargs: Dict[str, Any] = {}
        if self.config.diarization_auth_token:
            pipeline_kwargs["use_auth_token"] = self.config.diarization_auth_token

        try:
            self._diarization_pipeline = PyannotePipeline.from_pretrained(
                model_id, **pipeline_kwargs
            )
        except Exception as exc:  # pragma: no cover - library/runtime specific
            self.log.error("Failed to load diarization model %s: %s", model_id, exc)
            self._diarization_failed = True
            return False

        self.log.info("Loaded diarization model: %s", model_id)
        return True

    @staticmethod
    def _assign_default_speakers(
        segments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Fallback speaker assignment when diarisation is unavailable."""
        fallback: List[Dict[str, Any]] = []
        for segment in segments:
            entry = dict(segment)
            entry.setdefault("speaker", "SPEAKER_00")
            fallback.append(entry)
        return fallback

    @staticmethod
    def _select_speaker(
        start: float,
        end: float,
        diarization_tracks: List[Tuple[float, float, str]],
    ) -> str:
        """Select the speaker label with the greatest overlap."""

        def _overlap(
            a_start: float, a_end: float, b_start: float, b_end: float
        ) -> float:
            return max(0.0, min(a_end, b_end) - max(a_start, b_start))

        best_label = "SPEAKER_00"
        best_score = 0.0
        for d_start, d_end, label in diarization_tracks:
            score = _overlap(start, end, d_start, d_end)
            if score > best_score:
                best_label = label
                best_score = score
        return best_label

    def _perform_diarization(
        self, audio_path: Path, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run diarisation via pyannote.audio with graceful fallback."""
        if not segments:
            return []

        if not self._ensure_diarizer():
            return self._assign_default_speakers(segments)

        diarizer = self._diarization_pipeline
        if diarizer is None:
            return self._assign_default_speakers(segments)

        diarization_kwargs: Dict[str, Any] = {}
        if self.config.diarization_min_speakers is not None:
            diarization_kwargs["min_speakers"] = self.config.diarization_min_speakers
        if self.config.diarization_max_speakers is not None:
            diarization_kwargs["max_speakers"] = self.config.diarization_max_speakers

        try:
            diarization = diarizer(str(audio_path), **diarization_kwargs)
        except Exception as exc:  # pragma: no cover - runtime specific
            self.log.error("Diarization failed for %s: %s", audio_path, exc)
            self._diarization_failed = True
            return self._assign_default_speakers(segments)

        diarization_tracks: List[Tuple[float, float, str]] = [
            (turn.start, turn.end, speaker)
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]

        if not diarization_tracks:
            self._debug.warning("Diarization produced no speaker segments.")
            return self._assign_default_speakers(segments)

        enriched: List[Dict[str, Any]] = []
        for segment in segments:
            start = float(segment.get("start", 0.0))
            end = float(segment.get("end", start))
            if end <= start:
                end = start + 1e-6
            label = self._select_speaker(start, end, diarization_tracks)
            enriched_segment = dict(segment)
            enriched_segment["speaker"] = label
            enriched.append(enriched_segment)

        return enriched

    def enable_diarization(self, enable: bool = True) -> None:
        """Toggle speaker diarisation."""
        if not enable:
            self._diarization_enabled = False
            self.log.info("Speaker diarisation disabled")
            return

        if self._diarization_import_error:
            self._diarization_enabled = False
            self.log.error(
                "Cannot enable diarisation: %s",
                self._diarization_import_error,
            )
            return

        if not self.config.diarization_auth_token:
            self._diarization_enabled = False
            self.log.info(
                "Diarisation disabled – missing authentication token."
                " Set HUGGINGFACE_TOKEN or DIARIZATION_AUTH_TOKEN to proceed."
            )
            return

        self._diarization_failed = False
        self._diarization_enabled = True
        if not self.config.diarization_model:
            self.log.warning(
                "Diarization enabled but no model configured. Using default %s.",
                DEFAULT_DIARIZATION_MODEL,
            )
        if not self._ensure_diarizer():
            self.log.warning("Diarisation pipeline unavailable; using fallback labels.")

        self.log.info("Speaker diarisation enabled")

    # ----------------------------------------------------------------- #
    # Download helper
    # ----------------------------------------------------------------- #
    def download(self, url: str, force: bool = False) -> Path:
        """Download a YouTube audio stream and return the file path."""
        self._ensure_valid_url(url)
        return self._download_with_retry(url, force=force)

    @retry(
        max_attempts=3,
        delay_seconds=1.0,
        backoff_factor=2.0,
        jitter_seconds=0.5,
        retry_exceptions=(DownloadError,),
    )
    def _download_with_retry(self, url: str, force: bool = False) -> Path:
        return self._download_once(url, force)

    def _download_once(self, url: str, force: bool = False) -> Path:
        from pytube import YouTube  # Lazy import

        self.config.temp_dir.mkdir(parents=True, exist_ok=True)

        # ---- Cache hit -------------------------------------------------
        if not force and download_cache.is_downloaded(url):
            cached = download_cache.get_file_path(url)
            if cached and Path(cached).exists():
                self.log.info("Using cached download: %s", cached)
                return Path(cached)
            self._debug.warning("Cache entry exists but file missing – re‑downloading")

        # ---- Fresh download --------------------------------------------
        try:
            self.log.info("Downloading %s", url)
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            if stream is None:
                raise DownloadError(f"No audio stream found for {url}")

            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "_" for c in yt.title
            )
            output_path = (
                self.config.temp_dir / f"{safe_title}{self.config.audio_suffix}"
            )
            self._debug.debug(
                "Downloading audio to %s (mime=%s)", output_path, stream.mime_type
            )
            stream.download(
                output_path=str(self.config.temp_dir),
                filename=f"{safe_title}{self.config.audio_suffix}",
            )
            download_cache.mark_downloaded(url, str(output_path))
            self.log.info("Download complete: %s", output_path)
            return output_path
        except DownloadError:
            raise
        except Exception as exc:  # pragma: no cover
            raise DownloadError(f"Failed to download {url}") from exc

    # ----------------------------------------------------------------- #
    # Report writer
    # ----------------------------------------------------------------- #
    def write_report(self, text: str, source: Path) -> Tuple[Path, Optional[Path]]:
        """
        Write the transcript to the primary directory and optionally mirror it
        to a secondary directory.

        Returns ``(primary_path, secondary_path_or_None)``.
        """
        self.config.report_dir_primary.mkdir(parents=True, exist_ok=True)
        stem = source.stem
        primary_path = (
            self.config.report_dir_primary / f"{stem}{self.config.report_suffix}"
        )

        with open(primary_path, "w", encoding="utf-8") as fh:
            fh.write(text)

        secondary_path: Optional[Path] = None
        if self.config.report_dir_secondary:
            self.config.report_dir_secondary.mkdir(parents=True, exist_ok=True)
            secondary_path = (
                self.config.report_dir_secondary / f"{stem}{self.config.report_suffix}"
            )
            with open(secondary_path, "w", encoding="utf-8") as fh:
                fh.write(text)

        self._debug.debug(
            "Report written to %s%s",
            primary_path,
            f" and {secondary_path}" if secondary_path else "",
        )
        return primary_path, secondary_path

    # ----------------------------------------------------------------- #
    # Single‑URL workflow
    # ----------------------------------------------------------------- #
    def run_single(
        self,
        url: str,
        dry_run: bool = False,
        force_redownload: bool = False,
        force_retranscribe: bool = False,
    ) -> Optional[Path]:
        """
        Execute the complete pipeline for a single URL.

        Returns the path to the generated report, or ``None`` if the
        processing failed / was skipped.
        """
        self._ensure_valid_url(url)
        self.log.info("Processing %s", url)

        # ---- Download -------------------------------------------------
        audio_path = self.download(url, force=force_redownload)
        if not audio_path or not audio_path.exists():
            self.log.error("Download failed for %s", url)
            return None
        self.log.info("Audio ready: %s", audio_path.name)

        # ---- Cached transcript ? --------------------------------------
        if not force_retranscribe and download_cache.is_transcribed(url):
            cached = download_cache.get_transcribed_videos()
            entry = next(
                (e for e in cached if e.get("url") == url and "transcript_path" in e),
                None,
            )
            if entry and Path(entry["transcript_path"]).exists():
                self.log.info("Using cached transcript for %s", url)
                if dry_run:
                    self.log.info("[DRY‑RUN] Would use cached transcript")
                    return Path(entry["transcript_path"])
                return Path(entry["transcript_path"])

        # ---- Transcribe ------------------------------------------------
        result = self.transcribe(audio_path, url=url)
        transcript = result.get("text", "")
        if not transcript.strip():
            self.log.error("Empty transcription for %s", audio_path.name)
            return None
        self.log.info("Transcription finished (%.1f KB)", len(transcript) / 1024)

        # ---- Write report ---------------------------------------------
        if dry_run:
            self.log.info("[DRY‑RUN] Would write report")
            return None

        primary_path, _ = self.write_report(transcript, audio_path)
        if primary_path and primary_path.exists():
            self.log.info("Report saved at %s", primary_path)
            download_cache.mark_transcribed(url, str(primary_path))
            return primary_path

        self.log.error("Failed to persist report for %s", url)
        return None

    # ----------------------------------------------------------------- #
    # Batch processing – the star of this rewrite
    # ----------------------------------------------------------------- #
    def run_batch(
        self,
        urls_file: Path,
        dry_run: bool = False,
        force_redownload: bool = False,
        force_retranscribe: bool = False,
        max_retries: int = 3,
        skip_processed: bool = True,
        parallel: bool = False,
        max_workers: int = 4,
        rate_limit_seconds: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Process many URLs from a file with progress tracking, retries,
        optional parallelism and a final statistics summary.

        Parameters
        ----------
        urls_file:
            Path to a UTF‑8 text file – one URL per line.  Empty lines and
            lines starting with ``#`` are ignored.
        dry_run:
            When ``True`` nothing is written to disk – actions are only logged.
        force_redownload / force_retranscribe:
            Bypass the cache when set to ``True``.
        max_retries:
            How many times a failed download should be retried.
        skip_processed:
            If ``True`` URLs that already have a cached transcript are
            counted as *skipped* and not re‑processed.
        parallel:
            Run each URL in its own thread (useful for I/O bound steps).
            Set ``max_workers`` to control the pool size.
        rate_limit_seconds:
            Minimum pause between two consecutive download attempts
            (helps staying under YouTube‑API rate limits).

        Returns
        -------
        dict
            Statistics about the run::

                {
                    "total":   int,
                    "success": int,
                    "failed":  int,
                    "skipped": int,
                    "errors":  list[str]   # human‑readable messages
                }
        """
        if not urls_file.is_file():
            raise FileNotFoundError(f"URL list not found: {urls_file}")

        # -----------------------------------------------------------------
        # Load URLs -------------------------------------------------------
        # -----------------------------------------------------------------
        with open(urls_file, "r", encoding="utf-8") as fh:
            raw_urls = [ln.strip() for ln in fh.readlines()]

        urls = [u for u in raw_urls if u and not u.startswith("#")]  # simple filter
        total = len(urls)

        self.log.info("Starting batch: %d URLs loaded from %s", total, urls_file)
        if skip_processed:
            self._debug.debug("skip_processed is enabled – checking cache first")

        # -----------------------------------------------------------------
        # Helper that processes a single URL with retry logic
        # -----------------------------------------------------------------
        def _process_one(u: str) -> Tuple[str, Union[Path, None, Exception]]:
            attempts = 0
            while attempts <= max_retries:
                try:
                    # Optional early‑skip
                    if skip_processed and download_cache.is_transcribed(u):
                        cached = download_cache.get_transcribed_videos()
                        entry = next(
                            (
                                e
                                for e in cached
                                if e.get("url") == u and "transcript_path" in e
                            ),
                            None,
                        )
                        if entry and Path(entry["transcript_path"]).exists():
                            self.log.info("[SKIP] Cached transcript exists for %s", u)
                            return u, Path(entry["transcript_path"])

                    # Actual processing
                    path = self.run_single(
                        u,
                        dry_run=dry_run,
                        force_redownload=force_redownload,
                        force_retranscribe=force_retranscribe,
                    )
                    return u, path
                except Exception as exc:  # pragma: no cover
                    attempts += 1
                    self.log.warning(
                        "Attempt %d/%d failed for %s: %s",
                        attempts,
                        max_retries,
                        u,
                        exc,
                    )
                    if attempts > max_retries:
                        return u, exc
                finally:
                    if rate_limit_seconds:
                        time.sleep(rate_limit_seconds)

        # -----------------------------------------------------------------
        # Execution (serial or parallel)
        # -----------------------------------------------------------------
        stats = {
            "total": total,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

        start = time.time()
        if parallel:
            self.log.info("Running batch in parallel (workers=%d)", max_workers)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(_process_one, u): u for u in urls}
                for future in tqdm(
                    as_completed(future_to_url),
                    total=total,
                    desc="Batch",
                    unit="url",
                ):
                    url = future_to_url[future]
                    try:
                        _, outcome = future.result()
                    except Exception as exc:  # pragma: no cover
                        outcome = exc

                    # -----------------------------------------------------------------
                    # Update statistics
                    # -----------------------------------------------------------------
                    if isinstance(outcome, Path):
                        stats["success"] += 1
                    elif isinstance(outcome, Exception):
                        stats["failed"] += 1
                        stats["errors"].append(f"{url}: {outcome}")
                    else:  # ``None`` means the URL was skipped (dry‑run or skip flag)
                        stats["skipped"] += 1
        else:
            self.log.info("Running batch sequentially")
            for url in tqdm(urls, desc="Batch", unit="url"):
                _, outcome = _process_one(url)
                if isinstance(outcome, Path):
                    stats["success"] += 1
                elif isinstance(outcome, Exception):
                    stats["failed"] += 1
                    stats["errors"].append(f"{url}: {outcome}")
                else:
                    stats["skipped"] += 1

        elapsed = time.time() - start
        self.log.info(
            "Batch finished in %.1f s – %d success, %d failed, %d skipped",
            elapsed,
            stats["success"],
            stats["failed"],
            stats["skipped"],
        )
        if stats["errors"]:
            self.log.error("Errors encountered:\n%s", "\n".join(stats["errors"]))

        return stats

    # ----------------------------------------------------------------- #
    # Helper – simple rate limiter (if you prefer the explicit version)
    # ----------------------------------------------------------------- #
    @staticmethod
    def _rate_limit(seconds: float) -> None:
        """Sleep ``seconds`` if > 0 – convenience wrapper."""
        if seconds > 0:
            time.sleep(seconds)


# --------------------------------------------------------------------- #
# Unit‑test stubs (real tests should live in ``tests/``)
# --------------------------------------------------------------------- #
# Example pytest style unit test for the batch method
def test_run_batch_statistics(tmp_path, monkeypatch):
    cfg = Config(
        temp_dir=tmp_path / "tmp",
        report_dir_primary=tmp_path / "reports",
        model_name="base",
        language="en",
        fp16=False,
        audio_suffix=".mp3",
        transcript_suffix=".txt",
        report_suffix=".txt",
    )
    pipe = MiniConPipeline(cfg)

    # mock out heavy work
    monkeypatch.setattr(pipe, "run_single", lambda *a, **kw: Path("dummy.txt"))
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://youtu.be/abc123\\nhttps://youtu.be/def456\\n")
    stats = pipe.run_batch(urls_file, dry_run=True, parallel=False)

    assert stats["total"] == 2
    assert stats["success"] == 2
    assert stats["failed"] == 0
    assert stats["skipped"] == 0
