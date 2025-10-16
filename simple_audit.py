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

# Load API key
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
if not api_key:
    raise EnvironmentError(
        "Missing API key. Set OPENAI_API_KEY or OPENAI_API_KEY_ECHOES"
    )

client = OpenAI(api_key=api_key)


def safe_api_call(func, *args, **kwargs):
    """Rate-limit aware API call with exponential backoff"""
    delay = 10
    for attempt in range(1, 6):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg:
                print(
                    f"[RATE_LIMIT] Rate limit hit (attempt {attempt}/5). Waiting {delay}s..."
                )
                time.sleep(delay + random.uniform(0, 3))
                delay = min(delay * 2, 90)
                continue
            else:
                raise
    raise RuntimeError("Rate limit persisted after multiple retries.")


def verify_connection():
    """Test API connection"""
    print("[TEST] Testing OpenAI API connection...")
    try:
        resp = safe_api_call(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say OK if you can read this."}],
            max_tokens=10,
        )
        if "OK" in resp.choices[0].message.content.upper():
            print("[SUCCESS] API connection verified!\n")
            return True
        else:
            print("[WARNING] Unexpected response, but continuing...\n")
            return True
    except Exception as e:
        print(f"[ERROR] API test failed: {e}")
        return False


def run_simple_audit():
    """Run a focused audit on the Echoes codebase architecture"""

    # High-level description of the codebase for analysis
    codebase_description = """
    ECHOES is a modular multi-agent Python platform for AI orchestration featuring:

    CORE COMPONENTS:
    - ai_agents/orchestrator.py: Advanced agent orchestration with OpenAI SDK, rate limiting, and task management
    - comprehensive_analysis.py: Automated codebase analysis with batching and GPT-4o-mini integration
    - packages/security/: Security validation, encryption, and monitoring modules
    - packages/prompting/: AI prompt engineering and response handling systems
    - packages/orchestration/: Workflow management and task coordination

    ARCHITECTURAL PATTERNS:
    - Modular design with separate packages for different concerns
    - Async/await patterns throughout for non-blocking operations
    - OpenAI SDK integration for agent-based workflows
    - Rate limiting and retry logic for API resilience
    - Comprehensive error handling and logging

    UNIQUE FEATURES:
    - Trajectory-aligned development methodology
    - Harmonic resonance design patterns for AI systems
    - Multi-vector security analysis
    - Plant-based ecosystem monitoring metaphors
    - Research-grade workflow automation

    DEVELOPMENT APPROACH:
    - Poetry-based dependency management
    - Extensive analysis and testing frameworks
    - Focus on AI ethics and responsible development
    - Educational and research-oriented use cases
    """

    audit_prompt = f"""
    You are a senior AI systems architect conducting a comprehensive audit of the ECHOES platform.

    CODEBASE OVERVIEW:
    {codebase_description}

    Provide a detailed technical audit covering these key areas:

    1. **ARCHITECTURAL STRENGTHS & WEAKNESSES**
       - How well does the modular architecture scale?
       - Are the separation of concerns effective?
       - How does the agent orchestration pattern compare to alternatives?

    2. **TECHNICAL IMPLEMENTATION QUALITY**
       - Effectiveness of the async/await patterns
       - Quality of error handling and resilience
       - API integration patterns and rate limiting strategies

    3. **INNOVATION ASSESSMENT**
       - How novel are the "trajectory alignment" and "harmonic resonance" concepts?
       - Practical value of the plant-based ecosystem metaphors?
       - Differentiation from standard AI orchestration platforms?

    4. **PRODUCTION READINESS**
       - Security implementation adequacy
       - Scalability considerations
       - Operational monitoring and maintenance

    5. **COMPETITIVE ANALYSIS**
       - How does this compare to CrewAI, LangChain, or AutoGen?
       - Market positioning and unique value propositions
       - Target use cases where this excels

    6. **RECOMMENDATIONS FOR IMPROVEMENT**
       - High-priority technical improvements
       - Architecture refinements
       - Development process enhancements

    Be specific, technical, and provide actionable insights. Focus on practical value and market potential.
    """

    print("[AUDIT] Running comprehensive ECHOES platform audit...\n")

    completion = safe_api_call(
        client.chat.completions.create,
        model="gpt-4o",
        temperature=0.3,
        top_p=0.85,
        max_tokens=2500,
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI systems architect with extensive experience in production AI platforms, agent orchestration, and enterprise software development.",
            },
            {"role": "user", "content": audit_prompt},
        ],
    )

    audit_report = completion.choices[0].message.content

    print("=== ECHOES PLATFORM TECHNICAL AUDIT ===\n")
    print(audit_report)

    # Save report
    os.makedirs("reports", exist_ok=True)
    timestamp = int(time.time())
    filename = f"reports/echoes_technical_audit_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ECHOES PLATFORM TECHNICAL AUDIT\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(audit_report)

    print(f"\n[SUCCESS] Audit report saved to: {filename}")
    return audit_report


if __name__ == "__main__":
    print("[START] ECHOES Technical Audit with GPT-4o\n")

    if verify_connection():
        try:
            audit_result = run_simple_audit()
            print("\n[COMPLETE] Technical audit finished successfully!")
        except Exception as e:
            print(f"[FAILED] Audit failed: {e}")
    else:
        print("[ABORT] Cannot proceed without API connection.")
