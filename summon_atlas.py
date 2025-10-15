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
Summon Atlas - Problem/Fix Task Executor

This script manages a registry of problems (notes) and fixes (tasks),
sending structured problem/fix pairs to OpenAI API for execution.

Conceptual Model:
- Problem: Static context input (read-only)
- Fix: Dynamic instruction to execute reasoning or generate output

Each API call separates these vectors for clear context → action pipeline.
"""

import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

client = OpenAI()

# === Problem / Fix Registry ===
# Problems are static notes, fixes are executable tasks
notes_and_tasks = [
    {
        "problem": "Pip installation fails due to missing temporary directory (C:\\temp not writable).",
        "fix": "Assign a task to configure persistent TEMP and TMP environment variables to a valid, writable path (e.g., E:\\Projects\\Development\\.temp) and verify installation success.",
        "priority": "high",
        "tags": ["environment", "pip", "windows"],
    },
    {
        "problem": "Ethical commitments for bias_detection need clear documentation.",
        "fix": "Create a short, clear README section titled 'Ethical Approach' summarizing the commitment to fairness, safety, and collective benefit. Add it to bias_detection/README.md.",
        "priority": "medium",
        "tags": ["ethics", "documentation", "bias_detection"],
    },
    {
        "problem": "Python code execution in PowerShell fails with syntax errors.",
        "fix": "Ensure Python scripts are run via python interpreter, not directly in PowerShell. Provide clear instructions for REPL or script execution.",
        "priority": "high",
        "tags": ["python", "powershell", "execution"],
    },
    {
        "problem": "The machine now runs only Python 1.12.9, and my account cannot write to C:. I need a purely local, directory-to-directory mechanism that lets multiple code-editor instances share data via a common, writable folder while keeping all temporary/lock files out of C:. The solution should also provide a lightweight way to delete stale temporary files without disturbing active sessions.",
        "fix": "Provide detailed and clear tasks, steps and path to a functional system config and setting snapshot for implementing this mechanism.",
        "priority": "high",
        "tags": ["environment", "python", "windows", "shared_data"],
    },
]


def assign_task(
    problem: str, fix: str, priority: str = "medium", tags: list = None
) -> None:
    """Send a structured problem/fix pair to the API and print its reasoning."""
    tags = tags or []
    print(f"\n[Task Assigned :: {datetime.now().isoformat()}]")
    print(f"Priority: {priority}")
    print(f"Tags: {', '.join(tags) if tags else 'None'}")
    print(f"Problem: {problem}")
    print(f"Fix Task: {fix}\n")

    system_prompt = (
        "You are a structured task executor. Address the problem using the fix task logically. "
        "Return a clear, actionable plan or result. Be concise but thorough."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Problem: {problem}\nFix Task: {fix}"},
        ],
        temperature=0.4,
        max_tokens=1000,
    )

    print("---- API Response ----")
    print(response.choices[0].message.content.strip())
    print("[Status] Task processed.\n")


def save_registry(path: Path = Path("notes_and_tasks.json")) -> None:
    """Save the current registry to JSON file for persistence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes_and_tasks, f, indent=2, ensure_ascii=False)
    print(f"Registry saved to {path}")


def load_registry(path: Path = Path("notes_and_tasks.json")) -> None:
    """Load registry from JSON file."""
    global notes_and_tasks
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            notes_and_tasks = json.load(f)
        print(f"Registry loaded from {path}")
    else:
        print(f"No registry file found at {path}, using defaults")


def main():
    """Execute all registered tasks."""
    print("=== Summon Atlas - Task Executor ===")
    print(f"Processing {len(notes_and_tasks)} problem/fix pairs...\n")

    for entry in notes_and_tasks:
        assign_task(
            entry["problem"],
            entry["fix"],
            entry.get("priority", "medium"),
            entry.get("tags", []),
        )

    print("=== All Tasks Complete ===")


if __name__ == "__main__":
    # Optional: Load persistent registry
    # load_registry()

    main()

    # Optional: Save registry after execution
    # save_registry()
