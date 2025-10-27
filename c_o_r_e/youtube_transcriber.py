# Consent-Based License
#
# Version 1.0
# Effective Date: October 27, 2025
#
# This module is part of the Echoes AI Assistant project and requires explicit consent for use.
# Please read the main LICENSE file and contact the author for usage terms.
#
# Author Contact Information
# Erfan Kabir
# irfankabir02@gmail.com
# GitHub: caraxesthebloodwyrm02

"""YouTube transcription and website content extraction tool for Echoes AI Assistant.

Supports two modes:
- YouTube transcription: downloads audio, transcribes via OpenAI Whisper, and writes a
  formatted report to the configured output directory.
- Website extraction: fetches a web page, extracts the main article text, and writes a
  textual report to the configured output directory.

Dependencies (install what you need):
    pip install yt-dlp openai-whisper torch \
        --extra-index-url https://download.pytorch.org/whl/cu121
    pip install requests beautifulsoup4 readability-lxml

Note: FFmpeg must be installed and available on PATH for yt_dlp post-processing
and Whisper audio decoding.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import requests

OUTPUT_DIR = Path(r"D:\reprots")
DEFAULT_MODEL = "base"

try:
    import yt_dlp  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yt_dlp = None  # type: ignore

try:
    import whisper  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    whisper = None  # type: ignore

try:  # Optional imports for web content extraction
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    BeautifulSoup = None  # type: ignore

try:
    from readability import Document  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Document = None  # type: ignore


def _slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    value = value.strip("_")
    return value or "youtube_transcript"


def _format_duration(seconds: Any) -> str:
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return "--:--"
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _format_timestamp(seconds: Any) -> str:
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return "--:--"
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _download_audio(url: str, temp_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    if yt_dlp is None:
        raise ImportError("yt-dlp is required for YouTube transcription. Install with 'pip install yt-dlp'.")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(temp_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = Path(ydl.prepare_filename(info))
    audio_path = filename.with_suffix(".mp3")
    if not audio_path.exists():
        audio_path = filename
    if not audio_path.exists():
        raise FileNotFoundError("Failed to locate downloaded audio file.")
    return audio_path, info


def _transcribe(audio_path: Path, model_name: str) -> Dict[str, Any]:
    if whisper is None:
        raise ImportError("openai-whisper is required for transcription. Install with 'pip install openai-whisper'.")
    model = whisper.load_model(model_name)
    return model.transcribe(str(audio_path), fp16=False)


def _build_youtube_report(info: Dict[str, Any], transcript: Dict[str, Any], url: str, model_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    upload_date = info.get("upload_date")
    if upload_date and len(str(upload_date)) == 8:
        upload_date = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    segments = transcript.get("segments", [])
    segments_text = "\n".join(
        f"[{_format_timestamp(seg.get('start'))} - {_format_timestamp(seg.get('end'))}] {seg.get('text', '').strip()}"
        for seg in segments
    )
    if not segments_text:
        segments_text = "No timestamped segments available."
    return (
        "YouTube Transcription Report\n"
        f"Generated: {timestamp}\n"
        f"Video Title: {info.get('title', 'Unknown')}\n"
        f"Channel: {info.get('uploader', 'Unknown')}\n"
        f"Video URL: {url}\n"
        f"Duration: {_format_duration(info.get('duration'))}\n"
        f"Published: {upload_date or 'unknown'}\n"
        f"Model: whisper-{model_name}\n\n"
        "Full Transcript:\n"
        f"{transcript.get('text', '').strip() or 'No transcript available.'}\n\n"
        "Timestamped Segments:\n"
        f"{segments_text}\n"
    )


def _save_report(report: str, title: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = _slugify(title) if title else "content_report"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = OUTPUT_DIR / f"{safe_title}_{timestamp}.txt"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def _fetch_website(url: str) -> Dict[str, Any]:
    if BeautifulSoup is None or Document is None:
        raise ImportError("Website extraction requires beautifulsoup4 and readability-lxml. Install with 'pip install beautifulsoup4 readability-lxml'.")

    headers = {"User-Agent": "Mozilla/5.0 (Cascade Content Reporter)"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    doc = Document(response.text)
    article_html = doc.summary() or response.text
    soup = BeautifulSoup(article_html, "html.parser")
    text = _clean_text(soup.get_text("\n"))

    if not text:
        fallback = BeautifulSoup(response.text, "html.parser").get_text("\n")
        text = _clean_text(fallback)

    title = doc.short_title() or soup.title.string if soup.title else None
    return {
        "title": title or "website_content",
        "text": text,
        "content_length": len(text.split()) if text else 0,
    }


def _clean_text(raw: str) -> str:
    lines = [line.strip() for line in (raw or "").splitlines()]
    cleaned = [line for line in lines if line]
    return "\n".join(cleaned)


def _build_website_report(metadata: Dict[str, Any], url: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = metadata.get("text", "")
    lines = text.splitlines()
    preview = "\n".join(lines[:10]) if lines else "No text extracted."
    return (
        "Website Content Report\n"
        f"Generated: {timestamp}\n"
        f"Page Title: {metadata.get('title', 'Unknown')}\n"
        f"URL: {url}\n"
        f"Word Count: {metadata.get('content_length', 0)}\n\n"
        "Full Text:\n"
        f"{text or 'No text extracted.'}\n\n"
        "Preview (first 10 lines):\n"
        f"{preview}\n"
    )


def main() -> None:
    print("Content Reporting Tool")
    mode = (
        input("Select source type: [1] YouTube video (transcribe audio), " "[2] Website (extract text) [1]: ").strip()
        or "1"
    )

    url = input("Enter the URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    if mode == "2":
        try:
            metadata = _fetch_website(url)
        except requests.exceptions.RequestException as err:
            print(f"Failed to retrieve website: {err}")
            sys.exit(1)
        report = _build_website_report(metadata, url)
        report_path = _save_report(report, metadata.get("title"))
        print(f"Website report written to: {report_path}")
        return

    if yt_dlp is None or whisper is None:
        print(
            "YouTube transcription requires yt-dlp and openai-whisper. " "Install the missing packages before retrying."
        )
        sys.exit(1)

    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required but not found on PATH. Install ffmpeg and try again.")
        sys.exit(1)

    model_name = input("Choose Whisper model (tiny, base, small, medium, large) [base]: ").strip() or DEFAULT_MODEL

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            print("Downloading audio...")
            audio_path, info = _download_audio(url, temp_dir)
            print("Transcribing audio... this can take a few minutes depending on the model.")
            transcript = _transcribe(audio_path, model_name)
    except Exception as err:  # noqa: BLE001
        # Provide more specific guidance when possible
        if yt_dlp is not None and isinstance(err, yt_dlp.utils.DownloadError):
            print(f"Failed to download video: {err}")
        else:
            print(f"Transcription error: {err}")
        sys.exit(1)

    report = _build_youtube_report(info, transcript, url, model_name)
    report_path = _save_report(report, info.get("title"))
    print(f"Transcription report written to: {report_path}")


if __name__ == "__main__":
    main()
