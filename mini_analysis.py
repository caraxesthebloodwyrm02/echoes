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

from openai import OpenAI

# Load API key from environment
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
if not api_key:
    print(
        "[ERROR] No API key found. Set OPENAI_API_KEY or OPENAI_API_KEY_ECHOES in .env"
    )
    exit(1)

client = OpenAI(api_key=api_key)


def get_gpt4o_mini_analysis():
    """Get GPT-4o's focused analysis of the ECHOES platform"""

    analysis_prompt = """
    You are a senior AI architect analyzing the ECHOES platform. Provide your assessment as an experienced developer.

    ECHOES Platform Overview:
    - Modular Python platform for AI orchestration and multi-agent systems
    - Features trajectory-aligned development, harmonic resonance patterns
    - Includes comprehensive security, rate limiting, and error handling
    - Uses OpenAI SDK for agent orchestration and analysis
    - Research-focused with educational and ethical AI applications

    Key Components:
    - ai_agents/orchestrator.py: Advanced agent coordination with rate limiting
    - comprehensive_analysis.py: Automated codebase analysis with batching
    - packages/security/: Multi-vector security validation
    - packages/prompting/: AI prompt engineering and response handling
    - Plant-based ecosystem monitoring metaphors

    Provide your honest assessment focusing on:
    1. Architectural strengths and innovation level
    2. Technical implementation quality
    3. Market differentiation and competitive advantages
    4. Recommendations for improvement and scaling

    Be direct, specific, and focus on practical value.
    """

    print("[GPT-4o-mini] Analyzing ECHOES platform architecture...\n")

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "You are a senior AI systems architect."},
                {"role": "user", "content": analysis_prompt},
            ],
            temperature=0.4,
            max_output_tokens=1500,
        )

        analysis_segments = []
        for item in response.output or []:
            if item.type == "message":
                for content in item.content:
                    if getattr(content, "type", None) == "text" and getattr(
                        content, "text", None
                    ):
                        analysis_segments.append(content.text)

        analysis = "\n".join(analysis_segments).strip()

        if not analysis:
            print("[WARNING] No textual content returned by GPT-4o-mini response.")
            return None

        print("=== GPT-4o-mini's ECHOES Platform Analysis ===\n")
        print(analysis)

        # Save to file
        os.makedirs("reports", exist_ok=True)
        with open("reports/gpt4o_mini_echoes_analysis.txt", "w", encoding="utf-8") as f:
            f.write("GPT-4o-mini ECHOES Platform Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write(analysis)

        print("\n[SUCCESS] Analysis saved to reports/gpt4o_mini_echoes_analysis.txt")
        return analysis

    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        return None


if __name__ == "__main__":
    print("[START] Getting GPT-4o-mini's thoughts on ECHOES platform\n")
    result = get_gpt4o_mini_analysis()
    if result:
        print("\n[COMPLETE] GPT-4o-mini analysis finished!")
    else:
        print("\n[FAILED] Could not complete analysis")
