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

# ==========================================================
# Load API key from environment (supports both key names)
# ==========================================================
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
project_name = os.getenv("PROJECT", "ECHOES")

if not api_key:
    raise EnvironmentError(
        "❌ No valid API key found. Please set OPENAI_API_KEY or OPENAI_API_KEY_ECHOES in .env"
    )

client = OpenAI(api_key=api_key)

# ==========================================================
# Helper: Verify real API connection with retries
# ==========================================================


def verify_api_live(client, retries=3, wait_time=25):
    """
    Verify API connection with retries and rate limiting.

    Args:
        client: OpenAI client instance
        retries: Number of retry attempts
        wait_time: Wait time between retries in seconds

    Returns:
        bool: True if connection verified, False otherwise
    """
    from core_inference.safeguards import MockManager
    from core_inference.utils import rate_limit_safe_call

    mock_mgr = MockManager()

    def api_check():
        print("🧠 Verifying API connection...")
        test = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply only with the word: LIVE"}],
            max_tokens=5,
        )
        response_text = test.choices[0].message.content.strip()
        if "LIVE" in response_text:
            print("✅ Live OpenAI API connection confirmed.\n")
            return True
        return False

    try:
        return rate_limit_safe_call(api_check, retries=retries)
    except Exception as e:
        print(f"❌ API verification failed: {e}")
        mock_mgr.activate_mock_mode(f"API verification failed: {e}")
        return False


# ==========================================================
# Helper: Perform the codebase audit via API with rate limiting
# ==========================================================
def run_audit(client, project_name, cache_duration=3600):  # Cache for 1 hour by default
    """
    Run a rate-limit-aware system audit with caching support.

    Args:
        client: OpenAI client instance
        project_name: Name of the project to audit
        cache_duration: How long to cache results in seconds (default: 1 hour)
    """
    from datetime import timedelta
    from pathlib import Path

    from core_inference.cache_manager import CacheManager
    from core_inference.safeguards import MockManager
    from core_inference.utils import rate_limit_safe_call

    # Initialize managers
    cache_mgr = CacheManager()
    mock_mgr = MockManager()

    # Setup cache file
    cache_file = Path(f"audit_cache_{project_name}.json")

    # Check for cached results
    if cache_duration:
        cached_result = cache_mgr.get_cached_result(
            cache_file, max_age=timedelta(seconds=cache_duration)
        )
        if cached_result:
            print("📚 Using cached audit results\n")
            return cached_result

    print("🔍 Gathering code samples...")
    # You can replace this with actual code loader logic
    code_summary = "The Echoes codebase uses modular Python architecture, integrated with OpenAI SDK agents for analysis and orchestration."

    print("🚀 Running codebase audit...\n")

    prompt = f"""
    You are a senior AI code auditor.
    Analyze the '{project_name}' codebase based on this summary:
    {code_summary}

    Include:
    1. Architecture & design patterns
    2. Security & validation
    3. Code quality & best practices
    4. Testing & QA systems
    5. Performance & optimization
    6. Real-world practical use cases where this codebase excels
    7. Actionable recommendations for improvement
    """

    def perform_audit():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=1.0,
            top_p=0.9,
            max_tokens=2000,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code auditor and architect.",
                },
                {"role": "user", "content": prompt},
            ],
        )

    try:
        if mock_mgr.is_mock_mode_active():
            print("🔄 Running in mock mode")
            result = {
                "analysis": "Mock audit analysis for testing",
                "timestamp": "2025-10-15T00:00:00Z",
                "mode": "mock",
            }
        else:
            response = rate_limit_safe_call(perform_audit)
            # Handle both live API response and mock response
            if isinstance(response, dict) and response.get("mock"):
                result = {
                    "analysis": "Mock audit analysis - API rate limited",
                    "timestamp": "2025-10-15T00:00:00Z",
                    "mode": "mock",
                }
            else:
                result = {
                    "analysis": response.choices[0].message.content,
                    "timestamp": str(response.created),
                    "mode": "live",
                }

        # Cache successful results
        if cache_duration:
            cache_mgr.cache_result(cache_file, result)

        return result

    except Exception as e:
        print(f"❌ Audit failed: {str(e)}")
        mock_mgr.activate_mock_mode(f"Audit failed: {str(e)}")
        return {"error": str(e), "mode": "mock_fallback"}


# ==========================================================
# Main execution
# ==========================================================
if __name__ == "__main__":
    print(f"🔧 Starting ECHOES Audit for Project: {project_name}\n")

    live = verify_api_live(client)

    if live:
        success = run_audit(client, project_name)
        if not success:
            print("⚠️ Audit failed after retries.")
    else:
        print("⚠️ Falling back to mock mode due to failed API verification.")
        print("🧪 Running offline mock audit...\n")
        mock_report = f"""
        [MOCK MODE] Codebase Audit Report for {project_name}

        ⚠️ This report was generated in mock mode due to API rate limits or invalid API credentials.

        Summary:
        - Modular architecture detected.
        - Security layers minimal, but extendable.
        - Testing framework not integrated yet.
        - Real-world use cases: AI-driven analysis, educational tools, orchestration systems.
        """
        print(mock_report)
        os.makedirs("reports", exist_ok=True)
        with open("reports/code_audit_with_usecases.txt", "w", encoding="utf-8") as f:
            f.write(mock_report)
        print("\n✅ Mock report saved successfully.")
