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
    raise EnvironmentError(
        "❌ Missing API key. Add OPENAI_API_KEY or OPENAI_API_KEY_ECHOES to .env"
    )

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
                print(
                    f"[RATE_LIMIT] Rate limit (attempt {attempt}/5). Waiting {delay}s..."
                )
                time.sleep(delay + random.uniform(0, 3))  # jitter
                delay = min(delay * 2, 90)
                continue
            else:
                raise
    raise RuntimeError("Rate limit persisted after multiple retries.")


# ==========================================================
# Load actual codebase files
# ==========================================================
def load_codebase_files(project_root="e:/Projects/Development", max_files=20):
    """Load Python files from the repository for analysis"""
    python_files = []

    print("[LOADING] Loading Python files from repository...")

    for root, dirs, files in os.walk(project_root):
        # Skip common directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in [
                "__pycache__",
                ".git",
                ".venv",
                "node_modules",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                "htmlcov",
            ]
        ]

        for file in files:
            if file.endswith(".py") and len(python_files) < max_files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        if code.strip() and len(code) > 100:  # Skip empty/minimal files
                            rel_path = os.path.relpath(filepath, project_root)
                            python_files.append(
                                {
                                    "path": rel_path,
                                    "code": code[:3000],
                                    "size": len(code),
                                }  # Limit size for API
                            )
                            print(f"  [LOADED] {rel_path} ({len(code)} chars)")
                except Exception as e:
                    print(f"  [SKIPPED] {filepath} - {e}")

    print(f"[STATS] Loaded {len(python_files)} Python files for analysis\n")
    return python_files


# ==========================================================
# Step 1. Verify API Connection
# ==========================================================
def verify_api():
    print("[VERIFY] Verifying OpenAI API connectivity...")
    resp = safe_api_call(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Respond with OK"}],
        max_tokens=5,
    )
    if "OK" in resp.choices[0].message.content:
        print("[SUCCESS] Live connection confirmed.\n")
        return True
    print("[WARNING] Unexpected response; continuing anyway.\n")
    return False


# ==========================================================
# Step 2. Run practical, insight-focused audit on real code
# ==========================================================
def run_codebase_audit():
    # Load actual code files
    codebase_files = load_codebase_files(max_files=15)  # Limit for API constraints

    if not codebase_files:
        print("[ERROR] No code files loaded for analysis!")
        return

    # Create a comprehensive code summary for analysis
    code_summary = "ECHOES CODEBASE ANALYSIS:\n\n"
    total_lines = 0

    for i, file_info in enumerate(codebase_files, 1):
        code_summary += f"FILE {i}: {file_info['path']} ({file_info['size']} chars)\n"
        code_summary += f"```{python}\n{file_info['code'][:2000]}...\n```\n\n"  # Truncate for API limits
        total_lines += file_info["code"].count("\n") + 1

    code_summary += f"\nSUMMARY: {len(codebase_files)} files analyzed, approximately {total_lines} lines of code total."

    audit_prompt = f"""
    You are a senior AI code auditor analyzing the ECHOES platform codebase.

    CODEBASE TO AUDIT:
    {code_summary}

    Based on this actual code analysis, provide a comprehensive audit covering:

    1. **ARCHITECTURE & DESIGN PATTERNS**
       - Overall system architecture quality
       - Design patterns used (good/bad)
       - Code organization and modularity
       - Component separation and coupling

    2. **CODE QUALITY & BEST PRACTICES**
       - Code clarity and readability
       - Python conventions and standards
       - Error handling patterns
       - Documentation quality

    3. **SECURITY & VALIDATION**
       - Security implementations
       - Input validation approaches
       - Data protection patterns
       - Authentication/authorization code

    4. **PERFORMANCE & OPTIMIZATION**
       - Performance considerations
       - API usage efficiency
       - Resource management
       - Scalability patterns

    5. **TESTING & QA SYSTEMS**
       - Testing approaches implemented
       - Quality assurance patterns
       - Validation frameworks used

    6. **REAL-WORLD PRACTICAL USE CASES**
       - Where this architecture excels
       - Industry applications it serves well
       - Competitive advantages over alternatives

    7. **SUBTLE/NOVEL ADVANTAGES**
       - Hidden strengths in the design
       - Innovative approaches not obvious
       - Unique value propositions

    8. **STRATEGIC RECOMMENDATIONS**
       - High-impact improvements
       - Scaling strategies
       - Responsible development practices
       - Market positioning advice

    Be specific, reference actual files when relevant, and provide actionable insights.
    Focus on practical value and real-world applicability.
    """

    print("[AUDIT] Performing comprehensive codebase audit on real code...\n")

    completion = safe_api_call(
        client.chat.completions.create,
        model="gpt-4o",
        temperature=0.3,
        top_p=0.85,
        max_tokens=2500,
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI systems auditor and senior software architect with deep experience in production systems.",
            },
            {"role": "user", "content": audit_prompt},
        ],
    )

    result = completion.choices[0].message.content

    print("=== COMPREHENSIVE CODEBASE AUDIT REPORT ===\n")
    print(result)

    # Save to file
    os.makedirs("reports", exist_ok=True)
    report_filename = (
        f"reports/codebase_audit_{project_name.lower()}_{int(time.time())}.txt"
    )

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("ECHOES CODEBASE AUDIT REPORT\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Files Analyzed: {len(codebase_files)}\n")
        f.write(f"Total Lines: ~{total_lines}\n")
        f.write("=" * 80 + "\n\n")
        f.write(result)

    print(f"\n[SUCCESS] Report saved to {report_filename}")
    print(
        f"[STATS] Analysis covered {len(codebase_files)} files with ~{total_lines} lines of code"
    )


# ==========================================================
# Main
# ==========================================================
if __name__ == "__main__":
    print(
        f"[AUDIT] Starting Rate-Limit-Aware Codebase Audit for Project: {project_name}\n"
    )

    try:
        if verify_api():
            run_codebase_audit()
        else:
            print(
                "[WARNING] Proceeding in best-effort mode due to API verification warning."
            )
            run_codebase_audit()
    except Exception as e:
        print(f"[ERROR] Audit failed: {e}")
        print("[TIP] Check your API key and rate limits")
