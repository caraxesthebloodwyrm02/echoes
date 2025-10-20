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
Transcribe alt-J 3WW video and generate PodcastData report
"""

import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

import whisper
import yt_dlp

from packages.core.schemas import PodcastData, PodcastEvent


def download_audio(url: str, output_path: Path) -> tuple[Path, str]:
    """Download audio from YouTube URL using yt-dlp."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "unknown")
        filename = ydl.prepare_filename(info)
        audio_path = Path(filename)

    if not audio_path.exists():
        raise FileNotFoundError(f"Downloaded file not found: {audio_path}")

    print(f"Downloaded: {title}")
    return audio_path, title


def transcribe_audio(audio_path: Path) -> dict:
    """Transcribe audio using Whisper."""
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Transcribing...")
    result = model.transcribe(str(audio_path))

    return result


def create_podcast_data(transcript_result: dict, video_title: str, url: str) -> PodcastData:
    """Convert transcript to PodcastData format."""
    segments = transcript_result.get("segments", [])

    events = []
    for i, segment in enumerate(segments):
        # Create events from segments
        event = PodcastEvent(
            timestamp_start_s=segment["start"],
            timestamp_end_s=segment["end"],
            speaker=None,  # No speaker diarization
            utterance=segment["text"].strip(),
            pause_after_s=0.5 if i < len(segments) - 1 else 0.0,
            label="cognitive_load",  # Default label
        )
        events.append(event)

    podcast_data = PodcastData(
        podcast="YouTube Music Video",
        episode_title=video_title,
        source=url,
        events=events,
    )

    return podcast_data


def generate_report(podcast_data: PodcastData) -> str:
    """Generate a comprehensive report from PodcastData."""
    report_lines = []
    report_lines.append("# Podcast Transcription Report")
    report_lines.append("")
    report_lines.append(f"**Podcast:** {podcast_data.podcast}")
    report_lines.append(f"**Episode:** {podcast_data.episode_title}")
    report_lines.append(f"**Source:** {podcast_data.source}")
    report_lines.append("")
    report_lines.append("## Transcript Summary")
    report_lines.append(f"- Total events: {len(podcast_data.events)}")
    report_lines.append(
        f"- Duration: {podcast_data.events[-1].timestamp_end_s:.1f} seconds"
        if podcast_data.events
        else "- Duration: Unknown"
    )
    report_lines.append("")
    report_lines.append("## Full Transcript")
    report_lines.append("")

    current_speaker = None
    for event in podcast_data.events:
        timestamp = f"[{event.timestamp_start_s:.1f}s - {event.timestamp_end_s:.1f}s]"
        speaker = f" {event.speaker}:" if event.speaker else ""
        report_lines.append(f"{timestamp}{speaker} {event.utterance}")

    report_lines.append("")
    report_lines.append("## Event Analysis")
    report_lines.append("")

    # Count labels
    labels = {}
    for event in podcast_data.events:
        labels[event.label] = labels.get(event.label, 0) + 1

    for label, count in labels.items():
        report_lines.append(f"- **{label}:** {count} events")

    return "\n".join(report_lines)


def main():
    url = "https://www.youtube.com/watch?v=ZwBkXgWNs_M"

    # Create temp directory
    temp_dir = Path("yt_temp_altj")
    temp_dir.mkdir(exist_ok=True)

    try:
        # Download audio
        audio_path, video_title = download_audio(url, temp_dir)

        # Transcribe
        transcript = transcribe_audio(audio_path)

        # Create PodcastData
        podcast_data = create_podcast_data(transcript, video_title, url)

        # Generate report
        report = generate_report(podcast_data)

        # Save report
        report_path = Path("text_reports") / "altj_3ww_report.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

        # Save PodcastData as JSON
        json_path = Path("text_reports") / "altj_3ww_podcast_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(podcast_data.model_dump(), f, indent=2, ensure_ascii=False)

        print(f"Report saved to: {report_path}")
        print(f"PodcastData saved to: {json_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        import shutil

        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
