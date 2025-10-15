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
Create a sentimental telephone booth communication in PodcastData format
"""

import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from packages.core.schemas import PodcastData, PodcastEvent


def create_telephone_communication() -> PodcastData:
    """Create a sentimental telephone booth conversation."""

    # Nostalgic telephone conversation script with ¿Qué tal? scenario
    conversation_lines = [
        ("Operator", "Number please?", "cognitive_load"),
        ("Caller", "Paddington 8-7-4-2, please.", "handoff"),
        ("Operator", "Connecting you now. Mind the weather, sir.", "rhetorical"),
        ("Recipient", "¿Qué tal?", "cognitive_load"),  # Spanish greeting
        (
            "Caller",
            "He estado bien. Algunos días están bien, otros son difíciles y algunos son absolutamente fantásticos. Espero que estés bien.",
            "rhetorical",
        ),  # Spanish response
        (
            "Recipient",
            "¡Qué maravilla escucharte! Me alegra que las cosas vayan bien en general.",
            "rhetorical",
        ),  # Natural Spanish response
        (
            "Caller",
            "Ah, my dear friend! It's been ages since we spoke from these iconic booths.",
            "rhetorical",
        ),
        (
            "Caller",
            "Remember when we'd queue for hours just to make a call home?",
            "rhetorical",
        ),
        (
            "Recipient",
            "Indeed! These red sentinels have witnessed countless stories - proposals, emergencies, farewells.",
            "rhetorical",
        ),
        (
            "Recipient",
            "Each coin dropped, each dial turned, each voice carried across the wires...",
            "cognitive_load",
        ),
        (
            "Caller",
            "They may be fewer now, but their spirit lives on in London.",
            "rhetorical",
        ),
        ("Caller", "Thank you for preserving this piece of our history.", "handoff"),
        ("Recipient", "And thank you for remembering. Goodbye for now.", "handoff"),
        (
            "Operator",
            "Call completed. Please hang up and retrieve your change.",
            "other",
        ),
    ]

    events = []
    current_time = 0.0

    for speaker, utterance, label in conversation_lines:
        # Simulate realistic telephone conversation timing
        duration = 1.5 + (len(utterance) * 0.08)  # Base time + reading time
        if speaker == "Operator":
            duration += 0.5  # Operators speak more formally

        start_time = current_time
        end_time = current_time + duration

        event = PodcastEvent(
            timestamp_start_s=start_time,
            timestamp_end_s=end_time,
            speaker=speaker,
            utterance=utterance,
            pause_after_s=0.3
            + (0.2 if label == "handoff" else 0.0),  # Longer pauses for handoffs
            label=label,
        )
        events.append(event)
        current_time = end_time + event.pause_after_s

    podcast_data = PodcastData(
        podcast="Telephone Booth Communication",
        episode_title="A Call from the Red Box - London Nostalgia",
        source="Simulated telephone conversation (circa 1960s London)",
        events=events,
    )

    return podcast_data


def generate_telephone_report(podcast_data: PodcastData) -> str:
    """Generate a report styled like old telephone communications."""

    report_lines = []
    report_lines.append("# Telephone Booth Communication Report")
    report_lines.append("")
    report_lines.append("*Dial tone echoes through the streets of London...*")
    report_lines.append("")
    report_lines.append(f"**Exchange:** {podcast_data.podcast}")
    report_lines.append(f"**Connection:** {podcast_data.episode_title}")
    report_lines.append(f"**Operator:** {podcast_data.source}")
    report_lines.append("")
    report_lines.append("## Conversation Transcript")
    report_lines.append("")
    report_lines.append("*Click... Ring... Hello?*")
    report_lines.append("")

    current_speaker = None
    for event in podcast_data.events:
        timestamp = f"[{event.timestamp_start_s:.1f}s]"

        # Add speaker change formatting
        if event.speaker != current_speaker:
            if current_speaker:
                report_lines.append("")  # Space between speakers
            report_lines.append(f"**{event.speaker}:**")
            current_speaker = event.speaker

        # Format like old telephone transcript
        report_lines.append(f"{timestamp} {event.utterance}")

    report_lines.append("")
    report_lines.append("*Click... Line disconnects...*")
    report_lines.append("")
    report_lines.append("## Connection Analysis")
    report_lines.append("")

    # Calculate conversation metrics
    total_duration = podcast_data.events[-1].timestamp_end_s
    speaker_count = len(set(event.speaker for event in podcast_data.events))

    report_lines.append(f"- **Connection Duration:** {total_duration:.1f} seconds")
    report_lines.append(f"- **Participants:** {speaker_count}")
    report_lines.append(f"- **Exchanges:** {len(podcast_data.events)}")

    # Communication pattern analysis
    labels = {}
    for event in podcast_data.events:
        labels[event.label] = labels.get(event.label, 0) + 1

    report_lines.append("")
    report_lines.append("### Communication Patterns:")
    for label, count in labels.items():
        pattern_desc = {
            "cognitive_load": "Information exchange",
            "rhetorical": "Conversational flow",
            "handoff": "Turn transitions",
            "other": "System messages",
        }.get(label, label)
        report_lines.append(f"- **{label}:** {count} exchanges ({pattern_desc})")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append(
        "*Preserved in the red telephone boxes of London - a sentimental connection to our past.*"
    )

    return "\n".join(report_lines)


def main():
    print("Creating sentimental telephone booth communication...")

    # Create the conversation
    telephone_data = create_telephone_communication()

    # Generate report
    report = generate_telephone_report(telephone_data)

    # Save outputs
    report_path = Path("text_reports") / "telephone_booth_communication.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    json_path = Path("text_reports") / "telephone_booth_podcast_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(telephone_data.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {report_path}")
    print(f"Data saved to: {json_path}")

    # Display the report
    print("\n" + "=" * 60)
    print("TELEPHONE BOOTH COMMUNICATION:")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()
