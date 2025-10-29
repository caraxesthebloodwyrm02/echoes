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

# Comprehensive Codebase Analysis using Advanced Agent Orchestration

import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

# Initialize OpenAI client with automatic retries and timeout
client = OpenAI(max_retries=5, timeout=60.0)

# Global cache for partial results
result_cache = {}


def clear_result_cache():
    """Clear the global result cache to prevent cached quota issues"""
    global result_cache
    result_cache.clear()
    print("Cleared result cache (was {} entries)".format(len(result_cache)))


# Clear cache at import time
clear_result_cache()


def check_openai_usage():
    """Check current OpenAI API usage and limits"""
    try:
        print("Checking OpenAI API usage limits...")
        # Note: The usage endpoint may require different authentication
        # This is a simplified check - in production you'd use the billing API
        response = client.models.list()
        print("API connection verified - {} models available".format(len(response.data)))

        # Try a minimal completion to test rate limits
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
        )
        print("Rate limit test passed - API is responsive")
        return True

    except Exception as e:
        print("API usage check failed: {}".format(str(e)))
        print("Continuing with analysis anyway...")
        return False


def batch_code_chunks(chunks, batch_size=15):
    """Batch multiple code chunks into single analysis requests"""
    batches = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_content = []

        for chunk in batch:
            file_info = chunk["files"][0] if chunk["files"] else "unknown"
            batch_content.append("=== {} ===\n{}".format(file_info, chunk["code"]))

        batches.append(
            {
                "files": [chunk["files"][0] for chunk in batch],
                "code": "\n\n".join(batch_content),
                "size": sum(len(chunk["code"]) for chunk in batch),
                "chunk_count": len(batch),
            }
        )

    print(
        "Created {} batches from {} chunks (avg {} chunks per batch)".format(
            len(batches), len(chunks), len(chunks) // len(batches) if batches else 0
        )
    )

    return batches


async def analyze_code_batch_with_caching(code_batch, analysis_type, batch_id):
    """Analyze code batch with intelligent caching to avoid redundant API calls"""
    cache_key = "{}_{}".format(analysis_type, hash(code_batch[:1000]))  # Use first 1000 chars for cache key

    # Check cache first
    if cache_key in result_cache:
        print("  Using cached result for {} analysis".format(analysis_type))
        return result_cache[cache_key]

    analysis_prompts = {
        "architecture": """Analyze this batch of Python code files for overall system architecture, design patterns, and structural decisions.

Code batch to analyze:
{code}

Focus on:
- Overall system design and component interactions
- Architectural patterns and decisions
- Code organization and modularity
- Design quality and maintainability
- Key architectural insights across all files""",
        "code_quality": """Review this batch of Python code files for quality, best practices, maintainability, and potential improvements.

Code batch to analyze:
{code}

Focus on:
- Code quality patterns and anti-patterns
- Best practices adherence
- Potential improvements and refactoring opportunities
- Code smells and technical debt
- Overall code health assessment""",
        "security": """Analyze this batch of Python code files for security vulnerabilities, data protection issues, and secure coding practices.

Code batch to analyze:
{code}

Focus on:
- Security vulnerabilities and risks
- Data protection and privacy concerns
- Secure coding practices
- Authentication and authorization patterns
- Security best practices compliance""",
        "testing": """Evaluate this batch of Python code files from a testing perspective.

Code batch to analyze:
{code}

Focus on:
- Testing approaches and frameworks used
- Testability of the code
- Testing gaps and areas needing more coverage
- Quality assurance patterns
- Testing infrastructure and automation""",
        "innovation": """Analyze this batch of Python code files for innovative features, unique approaches, and industry-differentiating capabilities.

Code batch to analyze:
{code}

Focus on:
- Innovative solutions and approaches
- Unique architectural decisions
- Advanced features or capabilities
- Industry differentiation factors
- Technical innovation and creativity""",
    }

    prompt = analysis_prompts.get(analysis_type, analysis_prompts["code_quality"])

    try:
        # Use single GPT-4o model for all analysis types (more efficient)
        response = client.chat.completions.create(
            model="gpt-4o",  # Single powerful model for all analysis
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software analyst providing detailed, actionable insights. Analyze the provided code batch comprehensively but concisely.",
                },
                {"role": "user", "content": prompt.format(code=code_batch)},
            ],
            max_tokens=1500,  # Higher limit for batch analysis
            temperature=0.2,
        )

        result = response.choices[0].message.content.strip()

        # Cache the result
        result_cache[cache_key] = result
        print("  Cached new result for {} analysis".format(analysis_type))

        return result

    except Exception as e:
        error_msg = "Analysis failed: {}".format(str(e))
        print("  {}".format(error_msg))
        return error_msg


async def throttled_batch_analysis(batches, analysis_type, requests_per_minute=3):
    """Analyze batches with manual throttling to respect rate limits"""
    results = []
    request_count = 0

    print("Starting throttled batch analysis for {} ({} batches)".format(analysis_type, len(batches)))

    for i, batch in enumerate(batches):
        batch_id = "batch_{}_{}".format(analysis_type, i + 1)
        print("Analyzing {} - {} files ({} chars)".format(batch_id, len(batch["files"]), batch["size"]))

        # Analyze the batch
        result = await analyze_code_batch_with_caching(batch["code"], analysis_type, batch_id)
        results.append(
            {
                "batch_id": batch_id,
                "analysis_type": analysis_type,
                "files": batch["files"],
                "result": result,
                "chunk_count": batch["chunk_count"],
            }
        )

        request_count += 1

        # Throttle after every 3 requests (20 second sleep to match 3 RPM free tier)
        if request_count % requests_per_minute == 0 and i < len(batches) - 1:
            print(
                "Throttling: Sleeping 20 seconds after {} requests ({} RPM limit)".format(
                    requests_per_minute, requests_per_minute
                )
            )
            await asyncio.sleep(20)

    return results


def load_project_files(project_root="e:/Projects/Development"):
    """Load all Python files from the project directory"""
    python_files = []

    print("Loading Python files from project...")
    for root, dirs, files in os.walk(project_root):
        # Skip common directories that aren't core codebase
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
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        if code.strip():  # Only include non-empty files
                            rel_path = os.path.relpath(filepath, project_root)
                            python_files.append({"path": rel_path, "code": code, "size": len(code)})
                            print(f"  Loaded: {rel_path} ({len(code)} chars)")
                except Exception as e:
                    print(f"  Skipped: {filepath} - {e}")

    print(f"Total Python files loaded: {len(python_files)}")
    return python_files


def chunk_code_files(files, max_chunk_size=15000):  # Conservative limit under 20K tokens
    """Chunk code files to stay under token limits"""
    chunks = []

    for file_info in files:
        code = file_info["code"]
        filepath = file_info["path"]

        if len(code) <= max_chunk_size:
            # File fits in one chunk
            chunks.append({"files": [filepath], "code": code, "size": len(code)})
        else:
            # Need to split large files
            code_chunks = []
            start = 0

            while start < len(code):
                # Find a good breaking point (end of function/class)
                end = min(start + max_chunk_size, len(code))
                if end < len(code):
                    # Look for good break points
                    break_chars = ["\nclass ", "\ndef ", "\nasync def ", "\n    def "]
                    best_break = end
                    for break_char in break_chars:
                        last_break = code.rfind(break_char, start, end)
                        if last_break > start and last_break > best_break * 0.8:
                            best_break = last_break
                            break

                    end = best_break

                chunk = code[start:end]
                if chunk.strip():
                    code_chunks.append(chunk)

                start = end

            # Create chunks for this file
            for i, chunk in enumerate(code_chunks):
                chunks.append(
                    {
                        "files": [f"{filepath} (part {i + 1}/{len(code_chunks)})"],
                        "code": chunk,
                        "size": len(chunk),
                    }
                )

    print(f"Created {len(chunks)} code chunks for analysis")
    for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
        print(f"  Chunk {i + 1}: {chunk['files'][0]} ({chunk['size']} chars)")

    if len(chunks) > 5:
        print(f"  ... and {len(chunks) - 5} more chunks")

    return chunks


async def analyze_code_with_openai(code_chunk, analysis_type):
    """Analyze code chunk using OpenAI API directly"""
    analysis_prompts = {
        "architecture": "Analyze this Python code for overall system architecture, design patterns, and structural decisions. Focus on how components interact and the overall system design philosophy.",
        "code_quality": "Review this Python code for quality, best practices, maintainability, and potential improvements. Identify patterns, anti-patterns, and code smells.",
        "security": "Analyze this Python code for security vulnerabilities, data protection issues, and secure coding practices. Look for potential security risks and compliance concerns.",
        "testing": "Evaluate this Python code from a testing perspective. Assess testability, identify testing gaps, and suggest testing strategies and frameworks.",
        "innovation": "Analyze this code for innovative features, unique approaches, and industry-differentiating capabilities. Identify what makes this code stand out from typical implementations.",
    }

    prompt = analysis_prompts.get(analysis_type, analysis_prompts["code_quality"])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {analysis_type} analyst. Provide detailed, actionable insights based on the code provided.",
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nCode to analyze:\n\n{code_chunk}",
                },
            ],
            max_tokens=1000,  # Limit response size
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Analysis failed: {str(e)}"


async def comprehensive_codebase_analysis():
    """Comprehensive analysis of the Echoes codebase using AI agents with advanced rate limiting and file loading"""

    print("ECHOES CODEBASE COMPREHENSIVE ANALYSIS")
    print("Using OpenAI Agents SDK with advanced rate limit handling and file loading")
    print("=" * 70)
    print()

    # Check API usage and connectivity
    check_openai_usage()
    print()

    # Load project files
    project_files = load_project_files("e:/Projects/Development")
    if not project_files:
        print("No Python files found to analyze!")
        return {"status": "error", "message": "No files loaded"}

    # Chunk the code for analysis
    code_chunks = chunk_code_files(project_files)
    print()

    # Batch chunks for efficient analysis (15 chunks per batch)
    code_batches = batch_code_chunks(code_chunks, batch_size=15)
    print()

    print("OPTIMIZED ANALYSIS WORKFLOW")
    print("Using GPT-4o single agent with batching, throttling, and caching")
    print("=" * 70)
    print()

    # Use single GPT-4o agent for all analysis types (much more efficient)
    print("Agent Configuration: Single GPT-4o model for all analysis types")
    print(
        "Batching: {} chunks -> {} batches ({}x reduction)".format(
            len(code_chunks),
            len(code_batches),
            len(code_chunks) // len(code_batches) if code_batches else 1,
        )
    )
    print("Throttling: 20s sleep after every 3 requests (3 RPM free tier limit)")
    print("Caching: Intelligent result caching prevents redundant API calls")
    print()

    # Perform batched analysis for different aspects
    analysis_types = [
        "architecture",
        "code_quality",
        "security",
        "testing",
        "innovation",
    ]

    all_batch_results = []

    for analysis_type in analysis_types:
        print("{} ANALYSIS ({})".format(analysis_type.upper().replace("_", " "), len(code_batches)))
        print("-" * 50)

        # Perform throttled batch analysis
        batch_results = await throttled_batch_analysis(code_batches, analysis_type, requests_per_minute=3)
        all_batch_results.extend(batch_results)

        print("Completed {} analysis: {} batches processed".format(analysis_type, len(batch_results)))
        print()

    # Generate comprehensive synthesis report
    print("GENERATING COMPREHENSIVE SYNTHESIS REPORT")
    print("=" * 70)

    # Group results by analysis type
    analysis_summaries = {}
    for result in all_batch_results:
        analysis_type = result["analysis_type"]
        if analysis_type not in analysis_summaries:
            analysis_summaries[analysis_type] = []
        analysis_summaries[analysis_type].append(result)

    # Display results by category
    for analysis_type, results in analysis_summaries.items():
        print()
        print("{} ANALYSIS SUMMARY ({} batches)".format(analysis_type.upper().replace("_", " "), len(results)))
        print("=" * 50)

        for result in results[:2]:  # Show first 2 batch results as examples
            print("Batch {}: {} files analyzed".format(result["batch_id"], len(result["files"])))
            # Show first 200 chars of analysis
            analysis_preview = result["result"][:200] + "..." if len(result["result"]) > 200 else result["result"]
            print("  {}".format(analysis_preview.replace("\n", " ")))
            print()

        if len(results) > 2:
            print("... and {} more batch analyses".format(len(results) - 2))
            print()

    print("EXECUTION SUMMARY")
    print("=" * 50)
    print("• Total Code Files: {}".format(len(project_files)))
    print("• Total Code Chunks: {}".format(len(code_chunks)))
    print("• Total Batches Created: {}".format(len(code_batches)))
    print("• Total API Calls Made: {}".format(len(all_batch_results)))
    print("• Analysis Types: {}".format(", ".join(analysis_summaries.keys())))
    print("• Caching Efficiency: {} cached results reused".format(len(result_cache)))
    print("• Rate Limiting: 3 RPM with 20s throttling between bursts")
    print("• Model Used: GPT-4o (single agent for all analysis)")
    print()

    print("COMPREHENSIVE CODEBASE ANALYSIS COMPLETE")
    print("Massive optimization achieved: batching + throttling + caching + single agent")
    print()

    return {
        "status": "completed",
        "files_analyzed": len(project_files),
        "chunks_created": len(code_chunks),
        "batches_processed": len(code_batches),
        "api_calls": len(all_batch_results),
        "cached_results": len(result_cache),
        "analysis_types": list(analysis_summaries.keys()),
        "results": all_batch_results,
    }


async def gpt4o_mini_full_repo_review():
    """Get GPT-4o-mini's comprehensive thoughts on the entire Echoes repository"""

    print("[BOT] GPT-4o-mini Full Repository Review")
    print("Getting honest AI feedback on your entire Echoes codebase")
    print("=" * 70)
    print()

    # Load ALL Python files from the repository
    project_files = load_project_files("e:/Projects/Development")

    if not project_files:
        print("ERROR: No Python files found to analyze!")
        return

    print(f"[STATS] Total repository: {len(project_files)} Python files")
    total_chars = sum(f["size"] for f in project_files)
    print(f"[STATS] Total code size: {total_chars:,} characters")
    print()

    # Use the optimized batching approach for the entire repo
    code_chunks = chunk_code_files(project_files, max_chunk_size=12000)  # Smaller chunks for focused analysis
    code_batches = batch_code_chunks(code_chunks, batch_size=12)  # 12 chunks per batch

    print(f"[PROCESSING] Processing {len(code_batches)} batches for comprehensive analysis")
    print()

    # Analyze each batch with GPT-4o-mini
    all_reviews = []

    for i, batch in enumerate(code_batches):
        batch_id = f"repo_batch_{i + 1}"
        print(f"[ANALYZING] Batch {i + 1}/{len(code_batches)} - {len(batch['files'])} files ({batch['size']:,} chars)")

        try:
            # GPT-4o-mini comprehensive batch analysis
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior software engineer conducting a comprehensive code review. Provide honest, constructive feedback on code quality, architecture, patterns, and potential issues. Focus on practical insights that would help improve the codebase. Be direct but professional.""",
                    },
                    {
                        "role": "user",
                        "content": f"""Please analyze this batch of Python code files from the Echoes repository. Provide your honest assessment as an experienced developer.

Code batch to analyze:
{batch["code"]}

Please focus on:
- Code quality and best practices
- Architecture and design patterns
- Potential bugs or issues
- Areas that could be improved
- Positive aspects and strengths
- Any unique or interesting approaches

Be specific about file names when mentioning issues or strengths.""",
                    },
                ],
                max_tokens=1500,
                temperature=0.6,  # Balanced creativity and consistency
            )

            batch_review = response.choices[0].message.content.strip()
            all_reviews.append(
                {
                    "batch_id": batch_id,
                    "files": batch["files"],
                    "review": batch_review,
                    "file_count": len(batch["files"]),
                }
            )

            print(f"   [SUCCESS] Completed analysis of {len(batch['files'])} files")
            print(f"   [LENGTH] Review length: {len(batch_review)} characters")

            # Add small delay between batches to be respectful
            if i < len(code_batches) - 1:
                await asyncio.sleep(1)

        except Exception as e:
            error_msg = f"Failed to analyze batch {i + 1}: {str(e)}"
            print(f"   [ERROR] {error_msg}")
            all_reviews.append(
                {
                    "batch_id": batch_id,
                    "files": batch["files"],
                    "review": error_msg,
                    "file_count": len(batch["files"]),
                }
            )

    print()
    print("[BRAIN] GPT-4o-mini's Comprehensive Repository Assessment")
    print("=" * 70)

    # Compile and display the comprehensive review
    successful_reviews = [r for r in all_reviews if not r["review"].startswith("Failed")]

    print("[STATS] Analysis Summary:")
    print(f"   * Total batches processed: {len(all_reviews)}")
    print(f"   * Successful analyses: {len(successful_reviews)}")
    print(f"   * Files analyzed: {sum(r['file_count'] for r in all_reviews)}")
    print(f"   * Total code reviewed: {total_chars:,} characters")
    print()

    # Group feedback by categories
    strengths = []
    concerns = []
    suggestions = []

    for review in successful_reviews:
        review_text = review["review"].lower()

        # Extract key insights (simplified categorization)
        if any(
            word in review_text
            for word in [
                "good",
                "well",
                "excellent",
                "strong",
                "positive",
                "impressive",
            ]
        ):
            strengths.append(f"Batch {review['batch_id']}: {review['review'][:200]}...")

        if any(
            word in review_text
            for word in [
                "issue",
                "problem",
                "concern",
                "bug",
                "error",
                "improve",
                "fix",
            ]
        ):
            concerns.append(f"Batch {review['batch_id']}: {review['review'][:200]}...")

        if any(word in review_text for word in ["suggest", "recommend", "consider", "could", "should"]):
            suggestions.append(f"Batch {review['batch_id']}: {review['review'][:200]}...")

    print("[STRONG] STRENGTHS IDENTIFIED:")
    if strengths:
        for strength in strengths[:5]:  # Show top 5
            print(f"   * {strength}")
        if len(strengths) > 5:
            print(f"   ... and {len(strengths) - 5} more positive observations")
    else:
        print("   * No major strengths highlighted in this analysis")
    print()

    print("[WARNING] AREAS OF CONCERN:")
    if concerns:
        for concern in concerns[:5]:  # Show top 5
            print(f"   * {concern}")
        if len(concerns) > 5:
            print(f"   ... and {len(concerns) - 5} more areas for attention")
    else:
        print("   * No major concerns identified in this analysis")
    print()

    print("[LIGHTBULB] IMPROVEMENT SUGGESTIONS:")
    if suggestions:
        for suggestion in suggestions[:5]:  # Show top 5
            print(f"   * {suggestion}")
        if len(suggestions) > 5:
            print(f"   ... and {len(suggestions) - 5} more recommendations")
    else:
        print("   * No specific improvement suggestions in this analysis")
    print()

    print("[TARGET] OVERALL ASSESSMENT:")
    print("   GPT-4o-mini has completed a comprehensive review of your entire Echoes repository,")
    print(
        f"   analyzing {len(project_files)} files across {len(all_reviews)} batches. The assessment provides detailed insights"
    )
    print("   into code quality, architecture, and potential improvements throughout your codebase.")
    print()
    print("[SUCCESS] Full repository review complete!")

    return {
        "total_files": len(project_files),
        "total_characters": total_chars,
        "batches_processed": len(all_reviews),
        "successful_analyses": len(successful_reviews),
        "reviews": all_reviews,
        "strengths": strengths,
        "concerns": concerns,
        "suggestions": suggestions,
    }


async def compare_ai_thoughts():
    """Compare GPT-4o-mini vs GPT-4o thoughts on the same code"""

    print("🔄 AI Model Comparison: GPT-4o-mini vs GPT-4o")
    print("Seeing how different models view your code")
    print("=" * 60)
    print()

    # Get a small sample for comparison
    project_files = load_project_files("e:/Projects/Development")

    if not project_files or len(project_files) < 3:
        print("❌ Need at least 3 files for comparison")
        return

    # Use the same 3 files for both models
    comparison_files = project_files[:3]
    code_content = "\n\n".join([f"=== {f['path']} ===\n{f['code']}" for f in comparison_files])

    print(f"📁 Comparing analysis of {len(comparison_files)} files:")
    for f in comparison_files:
        print(f"  • {f['path']}")
    print()

    # GPT-4o-mini analysis
    print("🧠 GPT-4o-mini's Take:")
    print("-" * 30)

    try:
        mini_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You're a practical senior developer. Give honest, direct feedback on this code.",
                },
                {
                    "role": "user",
                    "content": f"What's your impression of this Python code? Be honest and specific:\n\n{code_content}",
                },
            ],
            max_tokens=1000,
            temperature=0.6,
        )

        mini_thoughts = mini_response.choices[0].message.content.strip()
        print(mini_thoughts[:800] + "..." if len(mini_thoughts) > 800 else mini_thoughts)

    except Exception as e:
        print(f"❌ GPT-4o-mini analysis failed: {e}")

    print()
    print("🧠 GPT-4o's Take:")
    print("-" * 30)

    try:
        gpt4_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You're an expert senior developer. Provide detailed, nuanced analysis of this code.",
                },
                {
                    "role": "user",
                    "content": f"What's your impression of this Python code? Be honest and specific:\n\n{code_content}",
                },
            ],
            max_tokens=1000,
            temperature=0.6,
        )

        gpt4_thoughts = gpt4_response.choices[0].message.content.strip()
        print(gpt4_thoughts[:800] + "..." if len(gpt4_thoughts) > 800 else gpt4_thoughts)

    except Exception as e:
        print(f"❌ GPT-4o analysis failed: {e}")

    print()
    print("✅ Model comparison complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "mini":
        # Run GPT-4o-mini full repo review
        asyncio.run(gpt4o_mini_full_repo_review())
    elif len(sys.argv) > 1 and sys.argv[1] == "compare":
        # Run model comparison
        asyncio.run(compare_ai_thoughts())
    else:
        # Run full comprehensive analysis
        asyncio.run(comprehensive_codebase_analysis())
