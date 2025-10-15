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
Codebase Auto-Audit Script

Uses static AST + regex scanning to answer intelligence probe questions.
Safe, read-only analysis for CI integration and codebase insights.

Usage: python audit_codebase.py [--format json|markdown] [--output file]
"""

import ast
import json
import re
from pathlib import Path
from typing import Optional


class CodebaseAuditor:
    """Comprehensive static analysis of Python codebase."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.findings = {
            "architecture": {},
            "configuration": {},
            "code_quality": {},
            "testing": {},
            "logic_functionality": {},
            "safety": {},
            "integration_readiness": {},
        }

        # File extensions to analyze
        self.python_files = []
        self._collect_python_files()

    def _collect_python_files(self):
        """Collect all Python files for analysis."""
        for py_file in self.root_path.rglob("*.py"):
            # Skip common exclusions
            if any(
                skip in str(py_file)
                for skip in [
                    "__pycache__",
                    ".venv",
                    ".git",
                    "node_modules",
                    "domains/",
                    "examples/",
                    ".pytest_cache",
                ]
            ):
                continue
            self.python_files.append(py_file)

    def audit_architecture(self):
        """Answer architecture-related questions."""
        findings = {}

        # 1. Which module explicitly initializes the REPL?
        repl_init_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if "EchoesREPL" in content and 'if __name__ == "__main__"' in content:
                    repl_init_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["repl_initializer"] = {
            "files": repl_init_files,
            "can_be_invoked_programmatically": len(repl_init_files) > 0,
        }

        # 2. Where are config objects first instantiated?
        config_patterns = [
            r"class.*Config",
            r"def.*config",
            r"Config\s*\(",
            r"load.*config",
            r"parse.*config",
        ]

        config_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in config_patterns
                ):
                    config_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["config_instantiation"] = {
            "files": config_files,
            "single_entry_point": len(config_files) <= 3,  # Heuristic
        }

        self.findings["architecture"] = findings

    def audit_configuration(self):
        """Answer configuration-related questions."""
        findings = {}

        # 1. Which .env keys are referenced but never validated?
        env_keys_in_code = set()
        validation_patterns = []

        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Find .env key references
                env_matches = re.findall(
                    r'os\.environ\.get\(["\']([^"\']+)["\']', content
                )
                env_keys_in_code.update(env_matches)

                getenv_matches = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
                env_keys_in_code.update(getenv_matches)

                # Find validation patterns
                if "if not os.environ.get" in content or "if not os.getenv" in content:
                    validation_patterns.append(str(py_file.relative_to(self.root_path)))

            except:
                continue

        # Check .env files for keys
        env_files = list(self.root_path.glob(".env*"))
        env_keys_in_files = set()

        for env_file in env_files:
            try:
                content = env_file.read_text(encoding="utf-8")
                # Extract keys from .env format
                for line in content.split("\n"):
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key = line.split("=")[0].strip()
                        env_keys_in_files.add(key)
            except:
                continue

        findings["env_keys"] = {
            "referenced_but_unvalidated": list(
                env_keys_in_code - set(["PATH", "HOME"])
            ),  # Common exclusions
            "validation_patterns": validation_patterns,
            "total_env_keys_found": len(env_keys_in_files),
        }

        # 2. Do any modules hardcode API URLs or default keys?
        hardcoded_patterns = [
            r'https?://[^\s\'"]+',  # URLs
            r"api\.openai\.com",  # OpenAI API
            r"sk-[a-zA-Z0-9]{32,}",  # API keys pattern
            r"Bearer [a-zA-Z0-9._-]",  # Bearer tokens
        ]

        hardcoded_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in hardcoded_patterns:
                    if re.search(pattern, content):
                        hardcoded_files.append(
                            {
                                "file": str(py_file.relative_to(self.root_path)),
                                "pattern": pattern,
                                "matches": len(re.findall(pattern, content)),
                            }
                        )
                        break
            except:
                continue

        findings["hardcoded_api_info"] = hardcoded_files

        # 3. Are all configs overridable via environment variables?
        static_fallbacks = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Look for hardcoded defaults
                default_patterns = [
                    r'DEFAULT_.*=.*["\'][^"\']+["\']',
                    r'fallback.*=.*["\'][^"\']+["\']',
                    r'default.*=.*["\'][^"\']+["\']',
                ]

                if any(re.search(pattern, content) for pattern in default_patterns):
                    static_fallbacks.append(str(py_file.relative_to(self.root_path)))

            except:
                continue

        findings["static_fallbacks"] = {
            "files_with_hardcoded_defaults": static_fallbacks,
            "all_overridable": len(static_fallbacks) == 0,
        }

        self.findings["configuration"] = findings

    def audit_code_quality(self):
        """Answer code quality questions."""
        findings = {}

        # 1. Where is budget logic duplicated?
        budget_patterns = [
            r"budget",
            r"Budget",
            r"check_budget",
            r"load_budget",
            r"update_budget",
        ]

        budget_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in budget_patterns
                ):
                    budget_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["budget_logic_duplication"] = {
            "files_with_budget_logic": budget_files,
            "primary_location": "src/utils/budget_guard.py",
            "duplicated": len(budget_files) > 1,
        }

        # 2. Which functions lack type hints or docstrings?
        functions_without_hints = []
        functions_without_docs = []

        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for type hints
                        has_hints = any(
                            arg.arg != "self" and arg.annotation
                            for arg in node.args.args
                        ) or (node.returns and str(node.returns) != "None")

                        if not has_hints:
                            functions_without_hints.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "function": node.name,
                                    "line": node.lineno,
                                }
                            )

                        # Check for docstrings
                        has_docstring = ast.get_docstring(node) is not None
                        if not has_docstring:
                            functions_without_docs.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "function": node.name,
                                    "line": node.lineno,
                                }
                            )

            except:
                continue

        findings["missing_hints_docs"] = {
            "functions_without_type_hints": functions_without_hints[:10],  # Top 10
            "functions_without_docstrings": functions_without_docs[:10],  # Top 10
            "total_without_hints": len(functions_without_hints),
            "total_without_docs": len(functions_without_docs),
        }

        # 3. Are any try/except blocks swallowing exceptions without logging?
        silent_exceptions = []
        logged_exceptions = []

        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Look for exception handlers
                exception_blocks = re.findall(
                    r"except\s*\w*\s*:\s*\n(.*?)(?=\n\s*\n|\n\s*except|\n\s*else|\n\s*finally|\Z)",
                    content,
                    re.DOTALL,
                )

                for i, block in enumerate(exception_blocks):
                    block_content = block.strip()

                    # Check if block only contains pass or return None
                    if re.match(r"^\s*(pass|return\s+None)\s*$", block_content):
                        silent_exceptions.append(
                            {
                                "file": str(py_file.relative_to(self.root_path)),
                                "line": "around "
                                + str(content[: content.find(block)].count("\n") + 1),
                            }
                        )

                    # Check for logging in exception block
                    if "log." in block_content or "print(" in block_content:
                        logged_exceptions.append(
                            {
                                "file": str(py_file.relative_to(self.root_path)),
                                "line": "around "
                                + str(content[: content.find(block)].count("\n") + 1),
                            }
                        )

            except:
                continue

        findings["exception_handling"] = {
            "silent_exception_blocks": silent_exceptions[:10],  # Top 10
            "logged_exception_blocks": logged_exceptions[:10],  # Top 10
            "total_silent": len(silent_exceptions),
            "total_logged": len(logged_exceptions),
        }

        self.findings["code_quality"] = findings

    def audit_testing(self):
        """Answer testing-related questions."""
        findings = {}

        # 1. Which functions in bias/ have no corresponding test files?
        bias_dir = self.root_path / "ai_modules" / "bias_detection"
        if bias_dir.exists():
            bias_functions = []

            # Get all functions in bias_detection
            for py_file in bias_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(
                            node, ast.FunctionDef
                        ) and not node.name.startswith("_"):
                            bias_functions.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "function": node.name,
                                }
                            )
                except:
                    continue

            # Look for test files
            test_files = []
            for test_file in self.root_path.rglob("*test*.py"):
                if "bias" in str(test_file).lower():
                    test_files.append(str(test_file.relative_to(self.root_path)))

            findings["bias_test_coverage"] = {
                "bias_functions": bias_functions,
                "test_files": test_files,
                "coverage_ratio": len(test_files) / len(bias_functions)
                if bias_functions
                else 0,
            }

        # 2. Are integration tests using mocks or real API calls?
        mock_usage = []
        api_call_usage = []

        for py_file in self.python_files:
            if "test" in py_file.name.lower():
                try:
                    content = py_file.read_text(encoding="utf-8")

                    # Check for mock usage
                    if (
                        "mock" in content.lower()
                        or "Mock" in content
                        or "patch" in content.lower()
                    ):
                        mock_usage.append(str(py_file.relative_to(self.root_path)))

                    # Check for API calls
                    api_patterns = ["openai", "requests", "httpx", "aiohttp"]
                    if any(api in content.lower() for api in api_patterns):
                        api_call_usage.append(str(py_file.relative_to(self.root_path)))

                except:
                    continue

        findings["test_patterns"] = {
            "uses_mocks": mock_usage,
            "makes_api_calls": api_call_usage,
            "real_api_calls": len(api_call_usage) > len(mock_usage),
        }

        # 3. Coverage comparison between ai_modules vs src
        ai_modules_files = []
        src_files = []

        for py_file in self.python_files:
            rel_path = str(py_file.relative_to(self.root_path))
            if rel_path.startswith("ai_modules/"):
                ai_modules_files.append(rel_path)
            elif rel_path.startswith("src/"):
                src_files.append(rel_path)

        # This is a rough heuristic - real coverage would need pytest-cov
        findings["coverage_heuristic"] = {
            "ai_modules_files": len(ai_modules_files),
            "src_files": len(src_files),
            "ai_modules_test_ratio": (
                len([f for f in ai_modules_files if "test" in f.lower()])
                / len(ai_modules_files)
                if ai_modules_files
                else 0
            ),
            "src_test_ratio": len([f for f in src_files if "test" in f.lower()])
            / len(src_files)
            if src_files
            else 0,
        }

        self.findings["testing"] = findings

    def audit_logic_functionality(self):
        """Answer logic and functionality questions."""
        findings = {}

        # 1. Is schema validation centralized or repeated?
        validation_patterns = [
            r"validate.*schema",
            r"schema.*validation",
            r"pydantic",
            r"jsonschema",
            r"validate.*json",
            r"check.*format",
        ]

        validation_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in validation_patterns
                ):
                    validation_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["schema_validation"] = {
            "validation_files": validation_files,
            "centralized": len(validation_files) <= 3,  # Heuristic
            "uses_pydantic": any("pydantic" in f for f in validation_files),
        }

        # 2. Are bias scoring functions consistent?
        bias_scoring_patterns = [
            r"score.*bias",
            r"bias.*score",
            r"evaluate.*bias",
            r"grade.*response",
            r"rate.*response",
        ]

        scoring_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in bias_scoring_patterns
                ):
                    scoring_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["bias_scoring_consistency"] = {
            "scoring_files": scoring_files,
            "consistent": len(scoring_files) <= 2,  # Heuristic
            "files_count": len(scoring_files),
        }

        # 3. Are batch-processing outputs deterministic?
        deterministic_indicators = [
            r"hashlib",
            r"sha256",
            r"md5",
            r"checksum",
            r"deterministic",
            r"reproducible",
            r"seed",
        ]

        batch_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if "batch" in content.lower() and "process" in content.lower():
                    batch_files.append(str(py_file.relative_to(self.root_path)))

                    # Check for deterministic patterns
                    has_deterministic = any(
                        re.search(pattern, content, re.IGNORECASE)
                        for pattern in deterministic_indicators
                    )

                    if not hasattr(findings["batch_determinism"], "details"):
                        findings["batch_determinism"] = {"details": []}

                    findings["batch_determinism"]["details"].append(
                        {
                            "file": str(py_file.relative_to(self.root_path)),
                            "deterministic": has_deterministic,
                        }
                    )

            except:
                continue

        findings["batch_determinism"] = findings.get("batch_determinism", {})
        findings["batch_determinism"]["overall_deterministic"] = all(
            d["deterministic"] for d in findings["batch_determinism"].get("details", [])
        )

        self.findings["logic_functionality"] = findings

    def audit_safety(self):
        """Answer safety-related questions."""
        findings = {}

        # 1. Are dry-run safeguards checked at both CLI and internal API layers?
        dry_run_patterns = [r"dry.?run", r"dry_run", r"DRY.?RUN"]

        dry_run_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in dry_run_patterns
                ):
                    dry_run_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["dry_run_safeguards"] = {
            "files_with_dry_run": dry_run_files,
            "comprehensive_coverage": len(dry_run_files) >= 3,  # CLI + API + Internal
        }

        # 2. Can budget_guard thresholds be modified dynamically?
        budget_modification_patterns = [
            r"DEFAULT_BUDGET.*=",
            r"budget.*=.*[0-9]",
            r"MODEL_COST_PER_1K.*=",
            r"update.*budget",
            r"modify.*budget",
        ]

        budget_mod_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in budget_modification_patterns
                ):
                    budget_mod_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["budget_modification"] = {
            "files_modifying_budget": budget_mod_files,
            "runtime_modification_possible": len(budget_mod_files) > 1,
        }

        # 3. Are log handlers using rotation across all modules?
        log_rotation_patterns = [
            r"RotatingFileHandler",
            r"rotation",
            r"maxBytes",
            r"backupCount",
            r"log.*rotate",
            r"rotate.*log",
        ]

        log_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if "log" in content.lower() and "handler" in content.lower():
                    log_files.append(str(py_file.relative_to(self.root_path)))

                    # Check for rotation patterns
                    has_rotation = any(
                        re.search(pattern, content, re.IGNORECASE)
                        for pattern in log_rotation_patterns
                    )

                    if not hasattr(findings["log_rotation"], "details"):
                        findings["log_rotation"] = {"details": []}

                    findings["log_rotation"]["details"].append(
                        {
                            "file": str(py_file.relative_to(self.root_path)),
                            "has_rotation": has_rotation,
                        }
                    )

            except:
                continue

        findings["log_rotation"] = findings.get("log_rotation", {})
        findings["log_rotation"]["overall_rotation"] = all(
            d["has_rotation"] for d in findings["log_rotation"].get("details", [])
        )

        self.findings["safety"] = findings

    def audit_integration_readiness(self):
        """Answer integration readiness questions."""
        findings = {}

        # 1. Which functions are pure (side-effect-free)?
        pure_functions = []
        impure_functions = []

        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith(
                        "_"
                    ):
                        # Check for side effects
                        has_side_effects = False

                        # Look for file operations, API calls, global modifications
                        side_effect_patterns = [
                            "open(",
                            "write(",
                            "read(",
                            "json.dump",
                            "json.load",
                            "requests",
                            "httpx",
                            "openai",
                            "client.",
                            "global ",
                            "nonlocal ",
                            "sys.path",
                            "os.environ",
                        ]

                        for pattern in side_effect_patterns:
                            if pattern in content[node.lineno - 1 :]:
                                has_side_effects = True
                                break

                        if not has_side_effects:
                            pure_functions.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "function": node.name,
                                    "line": node.lineno,
                                }
                            )
                        else:
                            impure_functions.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "function": node.name,
                                    "line": node.lineno,
                                }
                            )

            except:
                continue

        findings["pure_functions"] = {
            "pure_functions": pure_functions[:20],  # Top 20
            "impure_functions": impure_functions[:20],  # Top 20
            "total_pure": len(pure_functions),
            "total_impure": len(impure_functions),
        }

        # 2. How is configuration precedence resolved?
        config_precedence_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Look for precedence logic
                precedence_patterns = [
                    r"precedence",
                    r"priority",
                    r"override",
                    r"fallback",
                    r"os\.environ.*get.*or",
                    r"getenv.*or",
                ]

                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in precedence_patterns
                ):
                    config_precedence_files.append(
                        str(py_file.relative_to(self.root_path))
                    )

            except:
                continue

        findings["config_precedence"] = {
            "files_with_precedence_logic": config_precedence_files,
            "has_explicit_precedence": len(config_precedence_files) > 0,
        }

        # 3. Are there any stateful singletons?
        singleton_patterns = [
            r"class.*Singleton",
            r"@singleton",
            r"instance.*=.*None",
            r"__new__.*cls\._instance",
            r"_instance.*=.*self",
        ]

        singleton_files = []
        for py_file in self.python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                if any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in singleton_patterns
                ):
                    singleton_files.append(str(py_file.relative_to(self.root_path)))
            except:
                continue

        findings["stateful_singletons"] = {
            "singleton_files": singleton_files,
            "has_singletons": len(singleton_files) > 0,
        }

        self.findings["integration_readiness"] = findings

    def run_full_audit(self):
        """Run all audit categories."""
        print("[AUDIT] Running comprehensive codebase audit...")

        self.audit_architecture()
        print("[AUDIT] Architecture audit complete")

        self.audit_configuration()
        print("[AUDIT] Configuration audit complete")

        self.audit_code_quality()
        print("[AUDIT] Code quality audit complete")

        self.audit_testing()
        print("[AUDIT] Testing audit complete")

        self.audit_logic_functionality()
        print("[AUDIT] Logic & functionality audit complete")

        self.audit_safety()
        print("[AUDIT] Safety audit complete")

        self.audit_integration_readiness()
        print("[AUDIT] Integration readiness audit complete")

        print(
            f"\n[STATS] Audit complete! Analyzed {len(self.python_files)} Python files"
        )

        return self.findings

    def export_report(self, format: str = "json", output_file: Optional[str] = None):
        """Export audit findings to file."""
        if format.lower() == "markdown":
            report = self._generate_markdown_report()
        else:
            report = json.dumps(self.findings, indent=2, ensure_ascii=False)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"[EXPORT] Report exported to {output_file}")
        else:
            print(report)

    def _generate_markdown_report(self):
        """Generate a comprehensive Markdown report."""
        report = ["# Codebase Audit Report\n", "Generated by auto-audit script\n\n"]

        for category, findings in self.findings.items():
            report.append(f"## {category.replace('_', ' ').title()}\n")

            if isinstance(findings, dict):
                for key, value in findings.items():
                    report.append(f"### {key.replace('_', ' ').title()}\n")

                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, list) and len(subvalue) > 0:
                                if isinstance(subvalue[0], dict):
                                    report.append(
                                        f"- **{subkey}**: {len(subvalue)} items\n"
                                    )
                                    for item in subvalue[:5]:  # Show first 5
                                        if isinstance(item, dict):
                                            report.append(f"  - {item}\n")
                                    if len(subvalue) > 5:
                                        report.append(
                                            f"  - ... and {len(subvalue) - 5} more\n"
                                        )
                                else:
                                    report.append(f"- **{subkey}**: {subvalue}\n")
                            elif isinstance(subvalue, bool):
                                report.append(
                                    f"- **{subkey}**: {'YES' if subvalue else 'NO'}\n"
                                )
                            else:
                                report.append(f"- **{subkey}**: {subvalue}\n")
                    else:
                        report.append(f"- {value}\n")
            report.append("\n")

        return "\n".join(report)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit Python codebase for intelligence gathering"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--path", default=".", help="Path to codebase root")

    args = parser.parse_args()

    auditor = CodebaseAuditor(args.path)
    findings = auditor.run_full_audit()
    auditor.export_report(args.format, args.output)


if __name__ == "__main__":
    main()
