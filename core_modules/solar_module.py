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

"""Solar research utilities

Provides small helpers to parse the `solar_energy_research_plan.md` and produce
compact summaries and a simple "inspiration vector" score that compares gaps
against breakthroughs. This is intentionally lightweight and deterministic so
it can be used in CI and tests.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

# from sentence_transformers import SentenceTransformer, util  # Moved to function

DEFAULT_PLAN = Path(__file__).parent / "solar_energy_research_plan.md"

# Load the model globally to avoid reloading it multiple times
# MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # Moved


def load_plan(path: Path | str = DEFAULT_PLAN) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Research plan not found: {path}")
    return path.read_text(encoding="utf-8")


def parse_sections(markdown: str) -> Dict[str, List[str]]:
    """Parse top-level sections (## headings) into a mapping heading -> bullets/text.

    Returns a dict where each key is the section title and the value is a list
    of the bullet lines or paragraph lines under that section.
    """
    sections: Dict[str, List[str]] = {}
    current = None
    for line in markdown.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is None:
            continue
        # collect bullets or text lines
        stripped = line.strip()
        if not stripped:
            continue
        # remove leading hyphens or numbering
        stripped = re.sub(r"^[-*\d\.\)\s]+", "", stripped)
        sections[current].append(stripped)
    return sections


def extract_bullets_for_section(sections: Dict[str, List[str]], name: str) -> List[str]:
    # Do a case-insensitive match for convenience
    for k in sections:
        if k.lower().startswith(name.lower()):
            return sections[k]
    return []


def compute_inspiration_vector(gaps: List[str], breakthroughs: List[str]) -> Dict[str, float]:
    """Compute an inspiration-vector using semantic embeddings for better matching.

    Scoring heuristic:
      - Compute semantic similarity between each gap and all breakthroughs.
      - Score = 1 - max(similarity) (higher = more under-served).

    Returns a mapping gap -> score.
    """
    from sentence_transformers import SentenceTransformer, util

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vector: Dict[str, float] = {}
    breakthrough_embeddings = model.encode(breakthroughs, convert_to_tensor=True)

    for gap in gaps:
        gap_embedding = model.encode(gap, convert_to_tensor=True)
        similarities = util.cos_sim(gap_embedding, breakthrough_embeddings)[0]
        max_similarity = similarities.max().item()  # Get the highest similarity score
        score = round(1 - max_similarity, 3)  # Higher score = more under-served
        vector[gap] = score

    return vector


def summarize_plan(path: Path | str = DEFAULT_PLAN) -> Dict[str, object]:
    md = load_plan(path)
    sections = parse_sections(md)
    gaps = extract_bullets_for_section(sections, "Current Gaps and Challenges")
    breakthroughs = extract_bullets_for_section(sections, "Recent Breakthroughs")
    # fallback: try alternate heading names
    if not breakthroughs:
        breakthroughs = extract_bullets_for_section(sections, "Recent Breakthroughs and Innovations")
    vector = compute_inspiration_vector(gaps, breakthroughs)
    return {
        "gaps": gaps,
        "breakthroughs": breakthroughs,
        "inspiration_vector": vector,
    }


def export_solar_summary_as_json(parsed_data, inspiration_vectors, semantic_scores, output_file=None):
    """
    Export solar summary as a JSON object.

    Args:
        parsed_data (dict): Parsed solar data (e.g., irradiance, location).
        inspiration_vectors (list): List of inspiration vectors (e.g., storage focus).
        semantic_scores (dict): Semantic scores (e.g., relevance scores).
        output_file (str, optional): File path to save JSON. If None, returns JSON string.

    Returns:
        str: JSON string if no output_file, else saves to file and returns success message.
    """
    summary = {
        "parsed_data": parsed_data,
        "inspiration_vectors": inspiration_vectors,
        "semantic_scores": semantic_scores,
    }

    json_str = json.dumps(summary, indent=4)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json_str)
        return f"JSON exported to {output_file}"
    else:
        return json_str


def cli_print(path: Path | str = DEFAULT_PLAN) -> None:
    summary = summarize_plan(path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Solar module CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand for print
    subparsers.add_parser("print", help="Print solar summary")

    # Subcommand for export
    export_parser = subparsers.add_parser("export", help="Export solar summary as JSON")
    export_parser.add_argument(
        "--parsed_data",
        type=str,
        default='{"location": "Staten Island", "irradiance": 145}',
        help="Parsed data as JSON string",
    )
    export_parser.add_argument(
        "--inspiration_vectors",
        type=str,
        default='["storage integration", "efficiency boost"]',
        help="Inspiration vectors as JSON string",
    )
    export_parser.add_argument(
        "--semantic_scores",
        type=str,
        default='{"relevance": 0.9, "impact": 0.8}',
        help="Semantic scores as JSON string",
    )
    export_parser.add_argument("--output_file", type=str, help="Output file path")
    export_parser.add_argument("--add_field", type=str, help="Additional field as key:value")

    args = parser.parse_args()

    if args.command == "print":
        cli_print()
    elif args.command == "export":
        parsed_data = json.loads(args.parsed_data)
        inspiration_vectors = json.loads(args.inspiration_vectors)
        semantic_scores = json.loads(args.semantic_scores)

        # Add custom field if provided
        if args.add_field:
            key, value = args.add_field.split(":", 1)
            parsed_data[key] = json.loads(value) if value.startswith("[") or value.startswith("{") else value

        result = export_solar_summary_as_json(parsed_data, inspiration_vectors, semantic_scores, args.output_file)
        print(result)
    else:
        cli_print()
