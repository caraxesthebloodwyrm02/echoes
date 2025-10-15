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
Process Spanish response text into PodcastData format (reverse of transcription)
"""

import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from packages.core.schemas import PodcastData, PodcastEvent


def create_podcast_data_from_text(text: str) -> PodcastData:
    """Convert text into PodcastData format with simulated events."""

    # Split text into sentences/logical segments
    sentences = [
        "He estado bien.",
        "Algunos días están bien, otros son difíciles y algunos son absolutamente fantásticos.",
        "Espero que estés bien.",
    ]

    events = []
    current_time = 0.0

    for i, sentence in enumerate(sentences):
        # Simulate timestamps (each sentence ~2-3 seconds)
        duration = 2.5 + (len(sentence) * 0.05)  # Rough estimation
        start_time = current_time
        end_time = current_time + duration

        event = PodcastEvent(
            timestamp_start_s=start_time,
            timestamp_end_s=end_time,
            speaker="Responder",  # The person responding
            utterance=sentence.strip(),
            pause_after_s=0.8 if i < len(sentences) - 1 else 0.0,
            label="rhetorical",  # Since it's a response to "¿Qué tal?"
        )
        events.append(event)
        current_time = end_time + 0.5  # Small pause between sentences

    podcast_data = PodcastData(
        podcast="Text Response Simulation",
        episode_title="Response to ¿Qué tal?",
        source="Spanish text input",
        events=events,
    )

    return podcast_data


def generate_report_from_text(podcast_data: PodcastData) -> str:
    """Generate a report from the text-based PodcastData."""

    report_lines = []
    report_lines.append("# Text Response Analysis Report")
    report_lines.append("")
    report_lines.append(f"**Podcast:** {podcast_data.podcast}")
    report_lines.append(f"**Episode:** {podcast_data.episode_title}")
    report_lines.append(f"**Source:** {podcast_data.source}")
    report_lines.append("")
    report_lines.append("## Response Summary")
    report_lines.append(f"- Total segments: {len(podcast_data.events)}")
    report_lines.append(
        f"- Duration: {podcast_data.events[-1].timestamp_end_s:.1f} seconds"
        if podcast_data.events
        else "- Duration: Unknown"
    )
    report_lines.append("")
    report_lines.append("## Full Response")
    report_lines.append("")

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
        report_lines.append(f"- **{label}:** {count} segments")

    return "\n".join(report_lines)


def main():
    text = "He estado bien. Algunos días están bien, otros son difíciles y algunos son absolutamente fantásticos. Espero que estés bien."

    print("Processing text response into PodcastData format...")

    # Create PodcastData
    podcast_data = create_podcast_data_from_text(text)

    # Generate report
    report = generate_report_from_text(podcast_data)

    # Save outputs
    report_path = Path("text_reports") / "spanish_response_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    json_path = Path("text_reports") / "spanish_response_podcast_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(podcast_data.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {report_path}")
    print(f"PodcastData saved to: {json_path}")

    # Display the report
    print("\n" + "=" * 50)
    print("GENERATED REPORT:")
    print("=" * 50)
    print(report)


if __name__ == "__main__":
    main()
