"""
Transcribe Carl Jung interview for Glimpse system analysis.

This script transcribes the 1950s Carl Jung interview to analyze concepts
related to the collective unconscious and their relationship to the Glimpse
preflight system's validation architecture.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent / "c_o_r_e"))

from youtube_transcriber import (
    _download_audio,
    _transcribe,
    _build_youtube_report,
    _slugify,
)

# Configuration
OUTPUT_DIR = Path(__file__).parent / "glimpse"
DEFAULT_MODEL = "base"

# Carl Jung interview URL
JUNG_INTERVIEW_URL = "https://www.youtube.com/watch?v=2AMu-G51yTY&t=1725s"


def save_transcript(report: str, title: str) -> Path:
    """Save the transcript report"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = _slugify(title) if title else "jung_interview"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = OUTPUT_DIR / f"{safe_title}_{timestamp}.txt"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main():
    """Transcribe the Carl Jung interview"""
    print("=" * 80)
    print("Transcribing Carl Jung Interview (1950s)")
    print("=" * 80)
    print(f"URL: {JUNG_INTERVIEW_URL}")
    print(f"Model: whisper-{DEFAULT_MODEL}")
    print()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)

            print("Step 1/3: Downloading audio...")
            audio_path, info = _download_audio(JUNG_INTERVIEW_URL, temp_dir)
            print(f"✓ Downloaded: {info.get('title', 'Unknown')}")
            print(f"  Duration: {info.get('duration', 0) / 60:.1f} minutes")
            print()

            print("Step 2/3: Transcribing audio with Whisper...")
            print("  (This may take several minutes depending on video length)")
            transcript = _transcribe(audio_path, DEFAULT_MODEL)
            print("✓ Transcription complete")
            print()

            print("Step 3/3: Building report...")
            report = _build_youtube_report(
                info, transcript, JUNG_INTERVIEW_URL, DEFAULT_MODEL
            )
            report_path = save_transcript(report, info.get("title"))
            print(f"✓ Report saved to: {report_path}")
            print()

            # Display preview
            print("=" * 80)
            print("TRANSCRIPT PREVIEW (first 500 characters):")
            print("=" * 80)
            text = transcript.get("text", "")
            print(text[:500] + "..." if len(text) > 500 else text)
            print()

            print("=" * 80)
            print("ANALYSIS READY")
            print("=" * 80)
            print(f"Full transcript available at: {report_path}")
            print(f"Total words: {len(text.split())}")
            print()

            return report_path, transcript

    except Exception as err:
        print(f"✗ Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
