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

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import minicon.pipeline as pipeline_module
import minicon.utils as utils_module
import pytest
from minicon.config import Config
from minicon.pipeline import DownloadError, MiniConPipeline, TranscriptionError


@pytest.fixture()
def pipeline_config(tmp_path: Path) -> Config:
    cfg = Config(
        report_dir_primary=tmp_path / "reports",
        report_dir_secondary=None,
        temp_dir=tmp_path / "temp",
        model_name="tiny",
        openai_api_key_primary="test-key",
        openai_api_key_secondary=None,
        active_openai_key="PRIMARY",
        diarization_model=None,
        diarization_auth_token=None,
        diarization_min_speakers=None,
        diarization_max_speakers=None,
        diarization_enabled=False,
        language="en",
        fp16=False,
        audio_suffix=".mp3",
        transcript_suffix=".txt",
        report_suffix=".txt",
        transcribe_timeout_seconds=1,
        log_level=logging.INFO,
    )
    cfg.ensure_dirs()
    return cfg


@pytest.fixture(autouse=True)
def stub_download_cache(monkeypatch: pytest.MonkeyPatch):
    class _StubCache:
        def __init__(self):
            self.downloads: dict[str, str] = {}
            self.transcripts: dict[str, str] = {}

        def is_downloaded(self, url: str) -> bool:
            return url in self.downloads

        def get_file_path(self, url: str) -> str | None:
            return self.downloads.get(url)

        def mark_downloaded(self, url: str, file_path: str) -> None:
            self.downloads[url] = file_path

        def is_transcribed(self, url: str) -> bool:
            return url in self.transcripts

        def get_transcribed_videos(self) -> list[dict[str, str]]:
            return [
                {"url": url, "transcript_path": path}
                for url, path in self.transcripts.items()
            ]

        def mark_transcribed(self, url: str, transcript_path: str) -> None:
            self.transcripts[url] = transcript_path

    monkeypatch.setattr(pipeline_module, "download_cache", _StubCache())


@pytest.mark.unit
def test_ensure_valid_url_rejects_invalid(pipeline_config: Config) -> None:
    pipe = MiniConPipeline(pipeline_config)
    with pytest.raises(ValueError):
        pipe._ensure_valid_url("ftp://example.com/video")
    with pytest.raises(ValueError):
        pipe._ensure_valid_url("https://notyoutube.com/watch?v=123")


@pytest.mark.unit
def test_download_retries_then_succeeds(
    pipeline_config: Config, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipe = MiniConPipeline(pipeline_config)
    target = tmp_path / "downloaded.mp3"
    target.write_text("dummy")

    attempts: list[int] = []

    def fake_download_once(
        self: MiniConPipeline, url: str, force: bool = False
    ) -> Path:
        attempts.append(1)
        if len(attempts) < 3:
            raise DownloadError("temporary failure")
        return target

    monkeypatch.setattr(
        MiniConPipeline, "_download_once", fake_download_once, raising=False
    )
    monkeypatch.setattr(utils_module.time, "sleep", lambda *_: None)
    monkeypatch.setattr(utils_module.random, "uniform", lambda *_: 0.0)

    result = pipe.download("https://youtu.be/abc123")

    assert result == target
    assert len(attempts) == 3


@pytest.mark.unit
def test_download_retries_and_raises(
    pipeline_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipe = MiniConPipeline(pipeline_config)

    def always_fail(self: MiniConPipeline, url: str, force: bool = False) -> Path:
        raise DownloadError("boom")

    monkeypatch.setattr(MiniConPipeline, "_download_once", always_fail, raising=False)
    monkeypatch.setattr(utils_module.time, "sleep", lambda *_: None)
    monkeypatch.setattr(utils_module.random, "uniform", lambda *_: 0.0)

    with pytest.raises(DownloadError):
        pipe.download("https://www.youtube.com/watch?v=def456")


@pytest.mark.unit
def test_transcribe_timeout_raises_transcription_error(
    pipeline_config: Config, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipe = MiniConPipeline(pipeline_config)
    pipe._whisper_model = SimpleNamespace(transcribe=lambda *a, **kw: {"text": "hi"})

    audio_path = tmp_path / "sample.mp3"
    audio_path.write_text("audio")

    @contextmanager
    def immediate_timeout(_seconds: float | None):
        raise TimeoutError("forced timeout")
        yield

    monkeypatch.setattr(pipeline_module, "timeout", immediate_timeout)

    with pytest.raises(TranscriptionError) as exc:
        pipe.transcribe(audio_path)

    assert "timeout" in str(exc.value).lower()


@pytest.mark.unit
def test_run_batch_parallel_returns_success(
    pipeline_config: Config, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipe = MiniConPipeline(pipeline_config)

    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://youtu.be/abc123\nhttps://youtu.be/def456\n")

    calls: list[str] = []

    def fake_run_single(self: MiniConPipeline, url: str, **kwargs: Any) -> Path:
        calls.append(url)
        report = tmp_path / f"{url.split('/')[-1]}.txt"
        report.write_text("report")
        return report

    monkeypatch.setattr(MiniConPipeline, "run_single", fake_run_single, raising=False)

    stats = pipe.run_batch(
        urls_file,
        dry_run=False,
        skip_processed=False,
        parallel=True,
        max_workers=2,
    )

    assert stats == {"total": 2, "success": 2, "failed": 0, "skipped": 0, "errors": []}
    assert sorted(calls) == ["https://youtu.be/abc123", "https://youtu.be/def456"]
