#!/usr/bin/env python3
"""
Model Evaluation Runner

This script evaluates different language models by running them through a series of
technical questions and saving their responses for comparison.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# Configuration
MODELS = ["mistral:7b-instruct"]
QUESTIONS_DIR = Path(__file__).parent / "questions"
OUTPUT_DIR = Path(__file__).parent / "evaluations"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def get_question_files() -> List[Path]:
    """Get sorted list of question files."""
    return sorted(QUESTIONS_DIR.glob("*.txt"))

def run_model_inference(model: str, prompt: str) -> str:
    """Run inference using the specified model with proper encoding handling."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid characters instead of failing
            timeout=300  # 5 minutes per question
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Inference timed out after 5 minutes"
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    """Main evaluation function."""
    ensure_dir(OUTPUT_DIR)
    questions = get_question_files()

    print(f"Starting evaluation of {len(questions)} questions across {len(MODELS)} models")

    for model in MODELS:
        print(f"\nEvaluating model: {model}")
        model_dir = OUTPUT_DIR / model.replace(":", "_")
        ensure_dir(model_dir)

        for question_file in questions:
            question_id = question_file.stem
            output_file = model_dir / f"{question_id}.md"

            if output_file.exists():
                print(f"  ✓ {question_id} (cached)")
                continue

            print(f"  • {question_id}")

            # Read question
            with open(question_file, 'r', encoding='utf-8') as f:
                prompt = f.read()

            # Get model response
            response = run_model_inference(model, prompt)

            # Save response
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {question_id.replace('_', ' ').title()}\n\n")
                f.write(f"## Model: {model}\n\n")
                f.write(f"## Prompt\n\n```\n{prompt}\n```\n\n")
                f.write(f"## Response\n\n{response}")

    print("\nEvaluation complete!")
    print(f"Results saved to: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    main()
