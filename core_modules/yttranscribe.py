#!/usr/bin/env python3
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

"""
yt_transcriber.py
=================
A simple command‑line tool that:
  1. Asks for a YouTube link.
  2. Downloads the video/audio.
  3. Transcribes the audio with Whisper.
  4. Saves the transcription to D:\reports.

Author : ChatGPT
Date   : 2025‑10‑09
"""

import os
import sys
from pathlib import Path
from typing import Optional

import whisper
from pytube import YouTube

# --------------------------------------------------------------------------- #
# CONFIGURATION
# --------------------------------------------------------------------------- #

# Where the reports will be written. Change this if you want a different folder.
REPORT_DIR = Path(os.getenv("REPORT_DIR", r"D:\reports"))

# --------------------------------------------------------------------------- #
# HELPER FUNCTIONS
# --------------------------------------------------------------------------- #


def _ensure_report_dir() -> Path:
    """Create the report directory if it does not exist."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    return REPORT_DIR


def _download_video(url: str, target_dir: Path) -> Optional[Path]:
    """
    Download the best quality audio stream from the provided YouTube URL.

    Returns the path to the downloaded file, or None on failure.
    """
    try:
        yt = YouTube(url)
    except Exception as e:
        print(f"[ERROR] Could not load YouTube URL: {e}")
        return None

    # Choose the highest quality audio-only stream
    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

    if audio_stream is None:
        print("[ERROR] No audio stream found for this video.")
        return None

    print(f"\nDownloading: {yt.title}")
    print(f"Duration   : {yt.length // 60} min {yt.length % 60} sec")
    print(f"Audio Quality : {audio_stream.abr}\n")

    # Use tqdm to show download progress
    def progress_bar(chunk: bytes, file_handle, bytes_remaining: int):
        downloaded = audio_stream.filesize - bytes_remaining
        percent = downloaded / audio_stream.filesize
        bar_length = 50
        filled = int(bar_length * percent)
        bar = "=" * filled + " " * (bar_length - filled)
        percent_str = f"{percent * 100:5.1f}%"
        print(f"\r[{bar}] {percent_str}", end="")

    audio_stream.download(
        output_path=str(target_dir),
        filename_prefix="",  # No prefix
        on_progress=progress_bar,
    )
    print()  # newline after progress bar

    # The downloaded file will be something like <title>.mp4 or .webm depending on source
    # Get the full path to the file
    downloaded_file = next(target_dir.glob(f"{audio_stream.default_filename}"))
    return downloaded_file


def _transcribe_file(audio_path: Path, model: whisper.Whisper) -> str:
    """
    Transcribe the audio file using the provided Whisper model.
    Returns the transcription text.
    """
    print("\nTranscribing audio... This may take a while for long videos.")
    # Whisper's `transcribe` function returns a dict with `text`, among other keys
    result = model.transcribe(str(audio_path))
    return result["text"]


def _save_report(text: str, source_video_path: Path) -> Path:
    """
    Save the transcription text to a file in REPORT_DIR.
    The filename is derived from the source video's name.
    Returns the path to the saved report.
    """
    _ensure_report_dir()
    base_name = source_video_path.stem  # e.g. "video_title"
    report_path = REPORT_DIR / f"{base_name}_transcript.txt"

    with report_path.open("w", encoding="utf-8") as f:
        f.write(text)

    return report_path


# --------------------------------------------------------------------------- #
# MAIN LOGIC
# --------------------------------------------------------------------------- #


def main() -> None:
    print("=== YouTube Video Transcriber ===")
    url = input("Enter the YouTube link: ").strip()
    if not url:
        print("[ERROR] No URL provided. Exiting.")
        sys.exit(1)

    # Temporary folder to store the downloaded file
    temp_dir = Path.cwd() / "yt_temp"
    temp_dir.mkdir(exist_ok=True)

    # 1️⃣ Download the video/audio
    downloaded_file = _download_video(url, temp_dir)
    if downloaded_file is None:
        print("[ERROR] Download failed. Exiting.")
        sys.exit(1)

    # 2️⃣ Load Whisper model (small is fast, large is best quality)
    # You can choose 'tiny', 'base', 'small', 'medium', 'large'
    # For best quality and longer videos, 'medium' or 'large' are recommended.
    # Note: Larger models require more RAM and take longer to load.
    print("\nLoading Whisper model... (this happens once per run)")
    model = whisper.load_model("medium")  # change to "large" if you have the GPU

    # 3️⃣ Transcribe
    transcription = _transcribe_file(downloaded_file, model)

    # 4️⃣ Save report
    report_path = _save_report(transcription, downloaded_file)

    print("\n✅ Transcription complete!")
    print(f"Report saved to: {report_path}")

    # Clean up temporary files
    try:
        for p in temp_dir.iterdir():
            p.unlink()
        temp_dir.rmdir()
    except Exception:
        pass


# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
