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

import os
import random
import time

from openai import OpenAI

# ==========================================================
# Load API key (supports both names)
# ==========================================================
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
project_name = os.getenv("PROJECT", "ECHOES")

if not api_key:
    raise EnvironmentError("❌ Missing API key. Add OPENAI_API_KEY or OPENAI_API_KEY_ECHOES to .env")

client = OpenAI(api_key=api_key)


# ==========================================================
# Helper: Rate-limit aware API call with exponential backoff
# ==========================================================
def safe_api_call(func, *args, **kwargs):
    delay = 10
    for attempt in range(1, 6):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg:
                print(f"⚠️ Rate limit (attempt {attempt}/5). Waiting {delay}s...")
                time.sleep(delay + random.uniform(0, 3))  # jitter
                delay = min(delay * 2, 90)
                continue
            else:
                raise
    raise RuntimeError("Rate limit persisted after multiple retries.")


# ==========================================================
# Step 1. Verify API Connection
# ==========================================================
def verify_api():
    print("🧠 Verifying OpenAI API connectivity...")
    resp = safe_api_call(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Respond with OK"}],
        max_tokens=5,
    )
    if "OK" in resp.choices[0].message.content:
        print("✅ Live connection confirmed.\n")
        return True
    print("❌ Unexpected response; continuing anyway.\n")
    return False


# ==========================================================
# Step 2. Run practical, insight-focused audit
# ==========================================================
def run_audit():
    summary_context = """
    You are a senior AI auditor analyzing a modular multi-agent Python platform (ECHOES).
    It includes:
    - Modular AI orchestration system with task-specific agents (Architect, Reviewer, Tester)
    - Security validation layers and trajectory testing
    - Rich analytical logic with deterministic workflows
    - Real-world deployment aims for education, AI ethics, and orchestration tooling

    Based on this description, identify:
    1. Practical real-world use cases where this architecture is exceptional.
    2. How its orchestration and modularity could outperform industry norms.
    3. Subtle or nuanced advantages hidden in the design philosophy.
    4. Strategic recommendations for scaling this system responsibly.
    Provide your analysis in detailed sections, concise yet insightful.
    """

    print("🚀 Performing nuanced, rate-limit-aware audit...\n")

    completion = safe_api_call(
        client.chat.completions.create,
        model="gpt-4o-mini",
        temperature=0.3,
        top_p=0.85,
        max_tokens=1800,
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI systems auditor and architect.",
            },
            {"role": "user", "content": summary_context},
        ],
    )

    result = completion.choices[0].message.content
    print("=== AI AUDIT REPORT ===\n")
    print(result)

    os.makedirs("reports", exist_ok=True)
    with open("reports/code_audit_rate_limit_aware.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("\n✅ Report saved to reports/code_audit_rate_limit_aware.txt")


# ==========================================================
# Main
# ==========================================================
if __name__ == "__main__":
    print(f"🔧 Starting Rate-Limit-Aware Audit for Project: {project_name}\n")
    if verify_api():
        run_audit()
    else:
        print("⚠️ Proceeding in best-effort mode due to API verification warning.")
        run_audit()
