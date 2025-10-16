#!/usr/bin/env python3
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

"""
AI Refactor Agent - Advanced Context-Aware Codebase Refactoring
Uses GPT-4o for iterative, intelligent codebase restructuring
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.openai_integration import get_openai_integration


class AIRefactorAgent:
    """Advanced AI-powered refactor agent with iterative capabilities"""

    def __init__(self, config_path: Optional[Path] = None):
        self.openai_integration = get_openai_integration()
        self.project_root = PROJECT_ROOT
        self.config_path = config_path or self.project_root / "refactor_config.json"
        self.migration_log = self.project_root / "refactor_migrations.log"

        if not self.openai_integration.is_configured:
            raise RuntimeError("OpenAI integration not configured. Set OPENAI_API_KEY.")

        self.load_config()

    def load_config(self) -> None:
        """Load refactor agent configuration"""
        default_config = {
            "model": "gpt-4o",
            "temperature": 0.9,
            "max_tokens": 12000,
            "iterations": 3,
            "auto_commit": True,
            "test_after_refactor": True,
            "backup_before_refactor": True,
            "excluded_patterns": ["__pycache__", "*.pyc", ".git", "node_modules"],
            "target_structure": {
                "core": ["context_manager", "logger", "utils", "exceptions"],
                "integrations": ["openai_client", "api_router"],
                "services": ["chat_service", "orchestration"],
                "cli": ["main_cli"],
                "tests": ["test_*"],
            },
        }

        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                user_config = json.load(f)
            default_config.update(user_config)

        self.config = default_config

    def analyze_codebase_changes(self) -> str:
        """Analyze what has changed since last refactor"""
        # Check git status for changes
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            git_status = result.stdout.strip()
        except:
            git_status = "Git status unavailable"

        # Check recent commits
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            recent_commits = result.stdout.strip()
        except:
            recent_commits = "Recent commits unavailable"

        return f"""
RECENT CHANGES ANALYSIS:
Git Status: {git_status}
Recent Commits: {recent_commits}

This analysis helps the AI understand what has changed and focus refactoring efforts accordingly.
"""

    def generate_iterative_refactor_prompt(
        self, iteration: int, total_iterations: int
    ) -> str:
        """Generate prompt for iterative refactoring"""

        codebase_content = self.analyze_codebase()
        changes_analysis = self.analyze_codebase_changes()

        iterative_prompt = f"""
        You are an expert AI architect performing ITERATIVE CODEBASE REFACTORING.
        This is iteration {iteration} of {total_iterations}.

        CONTEXT:
        - This is an ongoing refactor process, not a one-time restructure
        - Previous iterations may have already created new files/structure
        - Focus on incremental improvements rather than complete rewrites
        - Preserve working functionality while improving architecture

        CURRENT STATE ANALYSIS:
        {changes_analysis}

        REQUIREMENTS FOR THIS ITERATION:
        1. Analyze the current state and recent changes
        2. Identify specific improvement opportunities
        3. Create incremental changes that build upon previous work
        4. Ensure all changes are backward compatible
        5. Focus on high-impact, low-risk improvements

        SPECIFIC GOALS:
        - Improve separation of concerns
        - Enhance error handling and logging
        - Add type hints where beneficial
        - Create reusable utility functions
        - Improve configuration management
        - Add comprehensive docstrings

        OUTPUT FORMAT:
        Return JSON with incremental changes:
        {{
          "iteration": {iteration},
          "focus_areas": ["list", "of", "specific", "areas", "to", "improve"],
          "changes": [
            {{
              "type": "create_file|modify_file|delete_file",
              "path": "relative/path/to/file.py",
              "content": "new or modified content",
              "reason": "why this change improves the architecture"
            }}
          ],
          "tests_to_add": [
            {{
              "file": "test_something.py",
              "function": "test_specific_functionality",
              "description": "what this test validates"
            }}
          ],
          "next_iteration_focus": "what to focus on in the next iteration"
        }}

        CODEBASE CONTENT:
        {codebase_content}
        """

        return iterative_prompt

    def run_iterative_refactor(self, iterations: int = 3) -> None:
        """Run iterative refactoring process"""
        print("🚀 AI REFACTOR AGENT - ITERATIVE MODE")
        print("=" * 60)
        print(f"Running {iterations} iterations of AI-powered refactoring")
        print("=" * 60)

        for iteration in range(1, iterations + 1):
            print(f"\n🔄 ITERATION {iteration}/{iterations}")
            print("-" * 40)

            try:
                # Generate refactor prompt for this iteration
                prompt = self.generate_iterative_refactor_prompt(iteration, iterations)

                print("🤖 Consulting GPT-4o for refactoring suggestions...")

                # Get AI suggestions
                response = self.openai_integration.create_completion(
                    prompt=prompt,
                    model=self.config["model"],
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"],
                )

                if not response:
                    print("❌ No response from AI - skipping iteration")
                    continue

                # Parse AI response - handle markdown formatting
                try:
                    clean_response = response.strip()

                    # Remove markdown code blocks if present
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    if clean_response.startswith("```"):
                        clean_response = clean_response[3:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]

                    # Clean up any remaining whitespace
                    clean_response = clean_response.strip()

                    changes_data = json.loads(clean_response)
                    self.apply_changes(changes_data, iteration)

                    if self.config["test_after_refactor"]:
                        self.run_tests()

                    if self.config["auto_commit"]:
                        self.commit_changes(iteration, changes_data)

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse AI response: {e}")
                    print("Raw response preview:")
                    print(response[:500] + "...")

            except Exception as e:
                print(f"❌ Iteration {iteration} failed: {e}")
                continue

        print("\n🎉 ITERATIVE REFACTORING COMPLETE!")
        print("=" * 60)

    def apply_changes(self, changes_data: Dict[str, Any], iteration: int) -> None:
        """Apply the changes suggested by AI"""

        changes = changes_data.get("changes", [])
        print(f"📝 Applying {len(changes)} changes from iteration {iteration}")

        applied_changes = 0

        for change in changes:
            change_type = change["type"]
            file_path = change["path"]
            content = change.get("content", "")
            reason = change.get("reason", "")

            full_path = self.project_root / file_path

            try:
                if change_type == "create_file":
                    if not full_path.exists():
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"✅ Created: {file_path}")
                        applied_changes += 1
                    else:
                        print(f"⚠️  Skipped (exists): {file_path}")

                elif change_type == "modify_file":
                    if full_path.exists():
                        # For modifications, we'd need more sophisticated diff logic
                        # For now, just log the suggestion
                        print(f"📝 Modification suggested: {file_path}")
                        print(f"   Reason: {reason}")
                    else:
                        print(f"⚠️  File not found for modification: {file_path}")

                elif change_type == "delete_file":
                    if full_path.exists():
                        # Be careful with deletions - require explicit confirmation
                        print(
                            f"⚠️  Deletion suggested: {file_path} (manual review required)"
                        )
                    else:
                        print(f"⚠️  File not found for deletion: {file_path}")

            except Exception as e:
                print(f"❌ Failed to apply change to {file_path}: {e}")

        print(f"✅ Applied {applied_changes} changes successfully")

        # Log the changes
        self.log_changes(iteration, changes_data)

    def log_changes(self, iteration: int, changes_data: Dict[str, Any]) -> None:
        """Log applied changes to migration log"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"""
[{timestamp}] ITERATION {iteration}
Focus Areas: {", ".join(changes_data.get("focus_areas", []))}
Changes Applied: {len(changes_data.get("changes", []))}
Next Focus: {changes_data.get("next_iteration_focus", "N/A")}

"""

        with open(self.migration_log, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def run_tests(self) -> bool:
        """Run tests after refactoring"""
        try:
            print("🧪 Running tests...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print("✅ Tests passed")
                return True
            else:
                print("⚠️  Tests failed - review changes")
                print("Test output:")
                print(result.stdout)
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  Tests timed out")
            return False
        except Exception as e:
            print(f"⚠️  Test execution failed: {e}")
            return False

    def commit_changes(self, iteration: int, changes_data: Dict[str, Any]) -> None:
        """Commit changes to git"""
        try:
            focus_areas = ", ".join(changes_data.get("focus_areas", [])[:3])

            commit_message = f"AI Refactor Iteration {iteration}: {focus_areas}"

            # Stage changes
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)

            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                check=True,
            )

            print(f"✅ Changes committed: {commit_message}")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git commit failed: {e}")
        except Exception as e:
            print(f"⚠️  Git operation failed: {e}")

    def analyze_codebase(self) -> str:
        """Analyze current codebase for refactoring"""
        # Reuse the existing analysis method but make it more focused for iterations
        key_files = [
            "main.py",
            "cli/main.py",
            "core/repl/echoes_repl.py",
            "core/openai/integration.py",
            "core/utils/safe_imports.py",
            "config/settings.py",
        ]

        codebase_analysis = []

        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Focus on recent changes and architectural patterns
                    lines = content.split("\n")
                    analysis = f"""
=== FILE: {file_path} ===
Lines: {len(lines)}
Classes: {content.count("class ")}
Functions: {content.count("def ")}
Imports: {content.count("import ") + content.count("from ")}

Recent changes and architectural notes:
- File structure and imports
- Function/class organization
- Error handling patterns
- Integration points

CONTENT PREVIEW:
{content[:1000]}...
"""
                    codebase_analysis.append(analysis)

                except Exception as e:
                    codebase_analysis.append(f"=== FILE: {file_path} ===\nERROR: {e}")

        return "\n".join(codebase_analysis)


def main():
    """Main entry point with CLI interface"""
    parser = argparse.ArgumentParser(
        description="AI Refactor Agent - Automated Codebase Refactoring"
    )

    parser.add_argument(
        "command", choices=["run", "analyze", "config"], help="Command to execute"
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of refactoring iterations (default: 3)",
    )

    parser.add_argument(
        "--no-commit", action="store_true", help="Don't auto-commit changes"
    )

    parser.add_argument(
        "--no-test", action="store_true", help="Don't run tests after refactoring"
    )

    args = parser.parse_args()

    try:
        agent = AIRefactorAgent()

        if args.command == "run":
            # Update config based on args
            agent.config["iterations"] = args.iterations
            agent.config["auto_commit"] = not args.no_commit
            agent.config["test_after_refactor"] = not args.no_test

            agent.run_iterative_refactor(args.iterations)

        elif args.command == "analyze":
            print("📊 CODEBASE ANALYSIS")
            print("=" * 40)
            analysis = agent.analyze_codebase()
            print(analysis[:2000] + "..." if len(analysis) > 2000 else analysis)

        elif args.command == "config":
            print("⚙️  CURRENT CONFIGURATION")
            print("=" * 40)
            print(json.dumps(agent.config, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
