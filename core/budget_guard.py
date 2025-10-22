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

# src/utils/budget_guard.py
import json
import os
import sys
import time

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Fix path to be relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)  # src/
PROJECT_ROOT = os.path.dirname(SRC_DIR)  # project root
LOG_FILE = os.path.join(SRC_DIR, "logs", "budget.json")
DEFAULT_BUDGET = 5.00  # USD - change if needed

# Configure model prices (USD per 1,000 tokens). **UPDATED with current OpenAI pricing as of Oct 2024**
MODEL_COST_PER_1K = {
    "gpt-4o": 2.50,  # $2.50 per 1k input tokens, $10.00 per 1k output tokens
    "gpt-4o-mini": 0.15,  # $0.15 per 1k input tokens, $0.60 per 1k output tokens
    "gpt-3.5-turbo": 0.50,  # $0.50 per 1k input tokens, $1.50 per 1k output tokens
    "gpt-4": 30.00,  # $30.00 per 1k input tokens, $60.00 per 1k output tokens
    "gpt-4-turbo": 10.00,  # $10.00 per 1k input tokens, $30.00 per 1k output tokens
}

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# initialize budget log
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump({"spent": 0.0, "calls": 0}, f, indent=2)


def load_budget():
    with open(LOG_FILE, "r") as f:
        return json.load(f)


def update_budget(tokens_used, model="gpt-4.1"):
    """
    Add actual token usage to spent and return (data, cost)
    tokens_used: integer number of tokens used
    model: which model was used to calculate cost
    """
    data = load_budget()
    cost_per_1k = MODEL_COST_PER_1K.get(model, MODEL_COST_PER_1K["gpt-4.1"])
    cost = (tokens_used / 1000.0) * cost_per_1k
    data["spent"] += cost
    data["calls"] += 1
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return data, cost


def check_budget():
    data = load_budget()
    remaining = DEFAULT_BUDGET - data["spent"]
    return remaining > 0, remaining, data


def throttle(seconds=1):
    """prevent rapid accidental re-calls"""
    time.sleep(seconds)


def estimate_tokens(text):
    """
    VERY simple heuristic token estimate (for model selection).
    Approximate: 1 token ≈ 4 characters (depends on content/language).
    """
    chars = len(text)
    est = max(10, int(chars / 4))
    return est


def choose_model_for_task(estimated_tokens, remaining_budget):
    """
    Choose cheapest model that is likely to fit the current budget.
    This is a simple rule-based optimizer:
      - if budget is low, pick the cheapest model
      - if estimated tokens are large and budget allows, pick a larger model
    """
    # Sort models by cost ascending
    sorted_models = sorted(MODEL_COST_PER_1K.items(), key=lambda kv: kv[1])
    # If remaining budget is tiny, pick cheapest
    if remaining_budget < 0.5:
        return sorted_models[0][0]

    # Otherwise attempt to pick a model whose estimated cost is <= remaining_budget/2
    for model, cost_per_1k in sorted_models:
        est_cost = (estimated_tokens / 1000.0) * cost_per_1k
        if est_cost <= remaining_budget * 0.5:
            return model

    # fallback to cheapest
    return sorted_models[0][0]
