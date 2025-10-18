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

# src/batch_processor.py
import argparse
import os

from modules.transformer import transform_text
from utils.budget_guard import (
    check_budget,
    choose_model_for_task,
    estimate_tokens,
    throttle,
    update_budget,
)

# Use relative paths since we run from src/
INPUT_DIR = "data/input_samples"
OUTPUT_DIR = "data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_file(path, task, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Estimate tokens & choose model
    est_tokens = estimate_tokens(text)
    ok, remaining, data = check_budget()
    if not ok:
        print(f"[SKIP] Budget exhausted. Remaining: ${remaining:.2f}")
        return False

    model = choose_model_for_task(est_tokens, remaining)
    print(
        f"[INFO] File: {os.path.basename(path)} | est_tokens: {est_tokens} | model: {model} | remaining: ${remaining:.2f}"
    )

    if dry_run:
        print("[DRY RUN] would call API here.")
        return True

    # Call transformer
    result, usage, used_model = transform_text(task, text, model=model, max_tokens=600)
    # extract real token usage if available
    tokens_used = None
    try:
        tokens_used = int(usage.get("total_tokens", usage.total_tokens))
    except Exception:
        # fallback: use estimate if API didn't return usage
        tokens_used = est_tokens + 50

    # Update budget with real usage
    data, cost = update_budget(tokens_used, model=used_model)
    print(
        f"[DONE] tokens_used: {tokens_used} | cost: ${cost:.5f} | total_spent: ${data['spent']:.3f}"
    )

    # Write output file
    out_name = os.path.splitext(os.path.basename(path))[0] + f"_{task}.txt"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as out_f:
        header = f"# source: {os.path.basename(path)}\n# model: {used_model}\n# tokens_used: {tokens_used}\n\n"
        out_f.write(header + result)

    throttle(1)
    return True


def main(task, dry_run=False):
    files = [
        os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".txt")
    ]
    if not files:
        print("[WARN] No input .txt files found in", INPUT_DIR)
        return

    for path in files:
        ok, remaining, _ = check_budget()
        if not ok:
            print("[STOP] Budget exhausted before processing next file.")
            break
        process_file(path, task, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch process input_samples through transformer"
    )
    parser.add_argument(
        "--task",
        type=str,
        default="summarize",
        choices=["summarize", "rephrase", "extract_actions"],
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't call API; simulate steps"
    )
    args = parser.parse_args()
    main(task=args.task, dry_run=args.dry_run)
