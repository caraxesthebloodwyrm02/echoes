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

import json
import os
import re
from collections import Counter
from pathlib import Path


def generate_echoes_snapshot():
    """Generate comprehensive snapshot of ECHOES platform for AI analysis"""

    project_root = Path("e:/Projects/Development")
    snapshot = {
        "project_overview": {
            "name": "ECHOES",
            "description": "Modular Python AI orchestration platform",
            "root_path": str(project_root),
            "timestamp": "2025-10-15",
        },
        "codebase_metrics": {},
        "architecture_analysis": {},
        "file_analysis": {},
        "dependency_analysis": {},
        "security_scan": {},
        "innovation_patterns": {},
    }

    # 1. Codebase Metrics
    print("Gathering codebase metrics...")
    python_files = []
    all_files = []

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
            filepath = Path(root) / file
            rel_path = filepath.relative_to(project_root)

            all_files.append(
                {
                    "path": str(rel_path),
                    "extension": filepath.suffix,
                    "size": filepath.stat().st_size if filepath.exists() else 0,
                }
            )

            if filepath.suffix == ".py":
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        python_files.append(
                            {
                                "path": str(rel_path),
                                "content": content,
                                "lines": len(content.splitlines()),
                                "size": len(content),
                                "classes": len(re.findall(r"^class\s+\w+", content, re.MULTILINE)),
                                "functions": len(re.findall(r"^def\s+\w+", content, re.MULTILINE)),
                                "imports": len(
                                    re.findall(
                                        r"^import\s+|^from\s+.*import",
                                        content,
                                        re.MULTILINE,
                                    )
                                ),
                            }
                        )
                except Exception as e:
                    python_files.append(
                        {
                            "path": str(rel_path),
                            "error": str(e),
                            "size": filepath.stat().st_size if filepath.exists() else 0,
                        }
                    )

    snapshot["codebase_metrics"] = {
        "total_files": len(all_files),
        "python_files": len(python_files),
        "total_lines": sum(f.get("lines", 0) for f in python_files),
        "total_classes": sum(f.get("classes", 0) for f in python_files),
        "total_functions": sum(f.get("functions", 0) for f in python_files),
        "language_distribution": Counter(f["extension"] for f in all_files),
    }

    # 2. Architecture Analysis
    print("Analyzing architecture patterns...")
    architecture_patterns = {
        "ai_agents": [],
        "orchestration": [],
        "security": [],
        "analysis": [],
        "utilities": [],
    }

    for file_info in python_files:
        path = file_info["path"].lower()
        content = file_info.get("content", "")

        if "ai_agent" in path or "orchestrator" in path:
            architecture_patterns["ai_agents"].append(file_info["path"])
        elif "security" in path or "guard" in path:
            architecture_patterns["security"].append(file_info["path"])
        elif "analysis" in path or "audit" in path:
            architecture_patterns["analysis"].append(file_info["path"])
        elif "orchestration" in path or "workflow" in path:
            architecture_patterns["orchestration"].append(file_info["path"])
        elif "util" in path or "helper" in path:
            architecture_patterns["utilities"].append(file_info["path"])

        # Check for async patterns
        if "async def" in content or "await" in content:
            file_info["async_patterns"] = True

        # Check for OpenAI usage
        if "openai" in content.lower() or "client.chat.completions" in content:
            file_info["openai_integration"] = True

    snapshot["architecture_analysis"] = architecture_patterns

    # 3. Key File Analysis (top files by size and complexity)
    print("Analyzing key files...")
    sorted_files = sorted(python_files, key=lambda x: x.get("size", 0), reverse=True)
    key_files = []

    for file_info in sorted_files[:10]:  # Top 10 files
        file_data = {
            "path": file_info["path"],
            "size": file_info.get("size", 0),
            "lines": file_info.get("lines", 0),
            "classes": file_info.get("classes", 0),
            "functions": file_info.get("functions", 0),
            "imports": file_info.get("imports", 0),
            "async_patterns": file_info.get("async_patterns", False),
            "openai_integration": file_info.get("openai_integration", False),
        }

        # Extract key patterns
        content = file_info.get("content", "")
        if content:
            # Key imports
            imports = re.findall(r"^(?:import|from)\s+(.+?)(?:\s+import|$)", content, re.MULTILINE)
            file_data["key_imports"] = list(set(imports))[:10]  # Top 10 unique imports

            # Key classes/functions (first few)
            classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
            functions = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)
            file_data["key_classes"] = classes[:5]
            file_data["key_functions"] = functions[:10]

        key_files.append(file_data)

    snapshot["file_analysis"] = {
        "top_files": key_files,
        "file_categories": architecture_patterns,
    }

    # 4. Dependency Analysis
    print("Analyzing dependencies...")
    all_imports = []
    for file_info in python_files:
        content = file_info.get("content", "")
        if content:
            imports = re.findall(r"^(?:import|from)\s+(.+?)(?:\s+import|$)", content, re.MULTILINE)
            all_imports.extend(imports)

    dependency_counts = Counter(all_imports)
    top_dependencies = dependency_counts.most_common(20)

    snapshot["dependency_analysis"] = {
        "total_unique_imports": len(set(all_imports)),
        "top_dependencies": [{"package": pkg, "count": count} for pkg, count in top_dependencies],
        "external_vs_stdlib": {
            "likely_external": [
                pkg
                for pkg, count in top_dependencies
                if not pkg.startswith(
                    (
                        "os",
                        "sys",
                        "json",
                        "re",
                        "pathlib",
                        "collections",
                        "typing",
                        "datetime",
                    )
                )
            ],
            "likely_stdlib": [
                pkg
                for pkg, count in top_dependencies
                if pkg.startswith(
                    (
                        "os",
                        "sys",
                        "json",
                        "re",
                        "pathlib",
                        "collections",
                        "typing",
                        "datetime",
                    )
                )
            ],
        },
    }

    # 5. Security Scan (basic patterns)
    print("Performing security scan...")
    security_findings = {
        "api_keys": [],
        "passwords": [],
        "secrets": [],
        "insecure_patterns": [],
    }

    for file_info in python_files:
        content = file_info.get("content", "")
        if content:
            # Check for potential secrets
            if re.search(r"api[_-]?key|secret|password|token", content, re.IGNORECASE):
                security_findings["secrets"].append(
                    {
                        "file": file_info["path"],
                        "pattern": "Potential secret/credential reference",
                    }
                )

            # Check for insecure patterns
            if "eval(" in content or "exec(" in content:
                security_findings["insecure_patterns"].append(
                    {"file": file_info["path"], "pattern": "Use of eval()/exec()"}
                )

    snapshot["security_scan"] = security_findings

    # 6. Innovation Patterns
    print("Analyzing innovation patterns...")
    innovation_patterns = {
        "trajectory_concepts": [],
        "harmonic_resonance": [],
        "ai_orchestration": [],
        "unique_terminology": [],
    }

    trajectory_keywords = [
        "trajectory",
        "alignment",
        "harmonic",
        "resonance",
        "orchestration",
    ]
    unique_terms = ["echoes", "symphony", "plant", "ecosystem", "minicon"]

    for file_info in python_files:
        content = file_info.get("content", "").lower()

        for keyword in trajectory_keywords:
            if keyword in content:
                if keyword == "trajectory" or keyword == "alignment":
                    innovation_patterns["trajectory_concepts"].append(file_info["path"])
                elif keyword == "harmonic" or keyword == "resonance":
                    innovation_patterns["harmonic_resonance"].append(file_info["path"])
                elif keyword == "orchestration":
                    innovation_patterns["ai_orchestration"].append(file_info["path"])

        for term in unique_terms:
            if term in content:
                innovation_patterns["unique_terminology"].append({"term": term, "file": file_info["path"]})

    snapshot["innovation_patterns"] = innovation_patterns

    # Save snapshot
    os.makedirs("reports", exist_ok=True)
    with open("reports/echoes_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print("ECHOES snapshot generated and saved to reports/echoes_snapshot.json")
    print(f"Analyzed {len(python_files)} Python files with {snapshot['codebase_metrics']['total_lines']} total lines")

    return snapshot


if __name__ == "__main__":
    print("Generating ECHOES Platform Snapshot...")
    snapshot = generate_echoes_snapshot()
    print("Snapshot ready for GPT-4o analysis!")
