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
AI-Enhanced Security Scanning System
Advanced vulnerability detection using multiple tools with AI-powered analysis
"""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""

    tool: str
    severity: str
    title: str
    description: str
    file: str
    line: Optional[int]
    cwe: Optional[str]
    confidence: float
    ai_analysis: Optional[str] = None
    o1_validation: Optional[Dict[str, Any]] = None


@dataclass
class SecurityReport:
    """Complete security assessment report"""

    timestamp: datetime
    vulnerabilities: List[Vulnerability]
    summary: Dict[str, int]
    ai_insights: List[str]


class AISecurityAnalyzer:
    """AI-powered security analysis and insights"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def analyze_vulnerability(self, vuln: Vulnerability) -> str:
        """Use AI to analyze and provide insights on vulnerabilities"""
        if not self.api_key:
            return "AI analysis unavailable - no API key configured"

        try:
            import openai

            prompt = f"""
            Analyze this security vulnerability and provide actionable insights:

            Tool: {vuln.tool}
            Severity: {vuln.severity}
            Title: {vuln.title}
            Description: {vuln.description}
            File: {vuln.file}
            Line: {vuln.line or "N/A"}
            CWE: {vuln.cwe or "N/A"}

            Please provide:
            1. Risk assessment
            2. Potential impact
            3. Recommended fix
            4. Prevention measures
            """

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"AI analysis failed: {str(e)}"


class O1PreviewSecurityAnalyzer:
    """Advanced security analysis using o1-preview for complex vulnerability reasoning"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def validate_vulnerability_complexity(self, vuln: Vulnerability) -> Dict[str, Any]:
        """Use o1-preview to validate and analyze complex security vulnerabilities"""
        if not self.api_key:
            return {
                "is_valid": True,
                "issue": "AI analysis unavailable - no API key configured",
            }

        try:
            import openai

            # Determine if this vulnerability needs complex reasoning
            if not self._requires_complex_analysis(vuln):
                return {"is_valid": True, "issue": None}

            prompt = f"""
You are a cybersecurity expert analyzing a potential security vulnerability. Your task is to determine whether this represents a genuine security issue and assess its validity.

SECURITY VULNERABILITY DATA:
- Tool: {vuln.tool}
- Severity: {vuln.severity}
- Title: {vuln.title}
- Description: {vuln.description}
- File: {vuln.file}
- Line: {vuln.line or "N/A"}
- CWE: {vuln.cwe or "N/A"}
- Confidence: {vuln.confidence}

ANALYSIS REQUIREMENTS:
- Carefully evaluate if this represents a real security vulnerability
- Consider the tool's detection accuracy and potential false positives
- Analyze the context, code patterns, and security implications
- Assess whether the issue is exploitable or just a code quality concern
- Evaluate the severity assessment accuracy

Return only a JSON object with the following properties:
- "is_valid": boolean indicating if this is a genuine security vulnerability
- "issue": if "is_valid" is false, provide the specific reason why this is not a valid vulnerability; if "is_valid" is true, set to null

Consider these factors:
- False positives from automated tools
- Code quality issues misidentified as security problems
- Context-dependent security implications
- Tool-specific detection patterns and accuracy
- Actual exploitability vs theoretical vulnerabilities

JSON RESPONSE FORMAT:
{{"is_valid": true/false, "issue": "explanation or null"}}
"""

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="o1-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1,  # Low temperature for consistent analysis
            )

            response_content = response.choices[0].message.content.strip()
            response_content = response_content.replace("```json", "").replace(
                "```", ""
            )

            try:
                result = json.loads(response_content)
                return result
            except json.JSONDecodeError as e:
                print(f"O1-preview JSON decode error: {e}")
                return {"is_valid": True, "issue": f"Analysis parsing failed: {str(e)}"}

        except Exception as e:
            return {"is_valid": True, "issue": f"O1-preview analysis failed: {str(e)}"}

    def _requires_complex_analysis(self, vuln: Vulnerability) -> bool:
        """Determine if vulnerability needs complex o1-preview analysis"""
        # Criteria for complex analysis:
        # - High severity issues (need careful validation)
        # - Low confidence detections (may be false positives)
        # - Specific tools known for false positives
        # - Complex CWE categories requiring deep reasoning

        complex_indicators = [
            vuln.severity == "high",
            vuln.confidence < 0.7,
            vuln.tool
            in ["semgrep", "checkov"],  # Tools with higher false positive rates
            vuln.cwe
            in [
                "CWE-79",
                "CWE-89",
                "CWE-352",
                "CWE-400",
            ],  # Complex injection/DoS issues
            "injection" in vuln.title.lower(),
            "xss" in vuln.title.lower(),
            "csrf" in vuln.title.lower(),
            "deserialization" in vuln.title.lower(),
        ]

        return any(complex_indicators)

    def batch_validate_vulnerabilities(
        self, vulnerabilities: List[Vulnerability], max_workers: int = 3
    ) -> Dict[str, Dict]:
        """Batch validate multiple vulnerabilities with o1-preview for efficiency"""
        results = {}

        # Filter vulnerabilities that need complex analysis
        complex_vulns = [
            (i, vuln)
            for i, vuln in enumerate(vulnerabilities)
            if self._requires_complex_analysis(vuln)
        ]

        if not complex_vulns:
            return results

        print(
            f"Running o1-preview validation on {len(complex_vulns)} complex vulnerabilities..."
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.validate_vulnerability_complexity, vuln): i
                for i, vuln in complex_vulns
            }

            for future in as_completed(future_to_index):
                vuln_index = future_to_index[future]
                try:
                    validation_result = future.result()
                    vuln_id = f"{vulnerabilities[vuln_index].tool}_{vuln_index}"
                    results[vuln_id] = {
                        "vulnerability_index": vuln_index,
                        "validation": validation_result,
                        "original_vuln": {
                            "tool": vulnerabilities[vuln_index].tool,
                            "severity": vulnerabilities[vuln_index].severity,
                            "title": vulnerabilities[vuln_index].title,
                            "confidence": vulnerabilities[vuln_index].confidence,
                        },
                    }
                except Exception as e:
                    vuln_id = f"{vulnerabilities[vuln_index].tool}_{vuln_index}"
                    results[vuln_id] = {
                        "vulnerability_index": vuln_index,
                        "validation": {
                            "is_valid": True,
                            "issue": f"Validation failed: {str(e)}",
                        },
                        "original_vuln": {
                            "tool": vulnerabilities[vuln_index].tool,
                            "severity": vulnerabilities[vuln_index].severity,
                            "title": vulnerabilities[vuln_index].title,
                            "confidence": vulnerabilities[vuln_index].confidence,
                        },
                    }

        return results


class SecurityScanner:
    def __init__(self):
        self.ai_analyzer = AISecurityAnalyzer()
        self.o1_analyzer = O1PreviewSecurityAnalyzer()
        self.tools = {
            "bandit": self._run_bandit,
            "semgrep": self._run_semgrep,
            "snyk": self._run_snyk,
            "checkov": self._run_checkov,
        }

    def scan_project(self, path: str = ".") -> SecurityReport:
        """Run comprehensive security scan"""
        print("Starting comprehensive security scan...")

        all_vulnerabilities = []

        for tool_name, scanner_func in self.tools.items():
            print(f"Running {tool_name}...")
            try:
                vulns = scanner_func(path)
                all_vulnerabilities.extend(vulns)
                print(f"  ✓ {tool_name}: {len(vulns)} issues found")
            except Exception as e:
                print(f"  ✗ {tool_name}: Failed - {str(e)}")

        # AI-enhanced analysis
        print("Running AI-powered analysis...")
        for vuln in all_vulnerabilities:
            vuln.ai_analysis = self.ai_analyzer.analyze_vulnerability(vuln)

        # O1-preview complex vulnerability validation
        print("Running o1-preview complex vulnerability validation...")
        o1_validation_results = self.o1_analyzer.batch_validate_vulnerabilities(
            all_vulnerabilities
        )

        # Apply o1-preview validation results
        for vuln_id, validation_data in o1_validation_results.items():
            vuln_index = validation_data["vulnerability_index"]
            validation_result = validation_data["validation"]

            # Store o1 validation result
            all_vulnerabilities[vuln_index].o1_validation = validation_result

            if not validation_result["is_valid"]:
                all_vulnerabilities[vuln_index].severity = "info"  # Downgrade severity
                all_vulnerabilities[
                    vuln_index
                ].ai_analysis += (
                    f"\n\nWARNING: O1-Preview Validation: {validation_result['issue']}"
                )

        # Generate summary
        summary = self._generate_summary(all_vulnerabilities)

        # Generate AI insights with o1 validation context
        ai_insights = self._generate_ai_insights(
            all_vulnerabilities, o1_validation_results
        )

        report = SecurityReport(
            timestamp=datetime.now(),
            vulnerabilities=all_vulnerabilities,
            summary=summary,
            ai_insights=ai_insights,
        )

        return report

    def _run_bandit(self, path: str) -> List[Vulnerability]:
        """Run Bandit security scanner"""
        try:
            result = subprocess.run(
                ["bandit", "-f", "json", "-r", path],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode in [0, 1]:  # Bandit returns 1 when issues found
                data = json.loads(result.stdout)
                vulnerabilities = []

                for issue in data.get("results", []):
                    vuln = Vulnerability(
                        tool="bandit",
                        severity=self._map_bandit_severity(
                            issue.get("issue_severity", "medium")
                        ),
                        title=issue.get("issue_text", ""),
                        description=issue.get("issue_text", ""),
                        file=issue.get("filename", ""),
                        line=issue.get("line_number"),
                        cwe=issue.get("issue_cwe", {}).get("id"),
                        confidence=self._map_bandit_confidence(
                            issue.get("issue_confidence", "medium")
                        ),
                    )
                    vulnerabilities.append(vuln)

                return vulnerabilities
        except Exception as e:
            print(f"Bandit scan failed: {e}")

        return []

    def _run_semgrep(self, path: str) -> List[Vulnerability]:
        """Run Semgrep security scanner"""
        try:
            result = subprocess.run(
                ["semgrep", "--json", "--config", "auto", path],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                vulnerabilities = []

                for result_item in data.get("results", []):
                    vuln = Vulnerability(
                        tool="semgrep",
                        severity=result_item.get("extra", {}).get("severity", "medium"),
                        title=result_item.get("check_id", ""),
                        description=result_item.get("extra", {}).get("message", ""),
                        file=result_item.get("path", ""),
                        line=result_item.get("start", {}).get("line"),
                        cwe=None,
                        confidence=0.8,
                    )
                    vulnerabilities.append(vuln)

                return vulnerabilities
        except Exception as e:
            print(f"Semgrep scan failed: {e}")

        return []

    def _run_snyk(self, path: str) -> List[Vulnerability]:
        """Run Snyk security scanner"""
        try:
            result = subprocess.run(
                ["snyk", "code", "test", path, "--json"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            vulnerabilities = []

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    for vuln in (
                        data.get("runs", [{}])[0]
                        .get("results", {})
                        .get("vulnerabilities", [])
                    ):
                        vulnerability = Vulnerability(
                            tool="snyk",
                            severity=vuln.get("level", "medium"),
                            title=vuln.get("ruleId", ""),
                            description=vuln.get("message", {}).get("text", ""),
                            file=vuln.get("locations", [{}])[0]
                            .get("physicalLocation", {})
                            .get("artifactLocation", {})
                            .get("uri", ""),
                            line=vuln.get("locations", [{}])[0]
                            .get("physicalLocation", {})
                            .get("region", {})
                            .get("startLine"),
                            cwe=None,
                            confidence=0.7,
                        )
                        vulnerabilities.append(vulnerability)
                except json.JSONDecodeError:
                    pass

            return vulnerabilities
        except Exception as e:
            print(f"Snyk scan failed: {e}")

        return []

    def _run_checkov(self, path: str) -> List[Vulnerability]:
        """Run Checkov infrastructure scanner"""
        try:
            result = subprocess.run(
                [
                    "checkov",
                    "-f",
                    path,
                    "--framework",
                    "terraform,cloudformation,kubernetes,dockerfile,secrets",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            vulnerabilities = []

            if result.returncode in [0, 1]:
                try:
                    data = json.loads(result.stdout)
                    for result_item in data.get("results", {}).get("failed_checks", []):
                        vuln = Vulnerability(
                            tool="checkov",
                            severity=result_item.get("check_result", "medium"),
                            title=result_item.get("check_name", ""),
                            description=result_item.get("check_name", ""),
                            file=result_item.get("file_path", ""),
                            line=result_item.get("file_line_range", [0])[0],
                            cwe=None,
                            confidence=0.6,
                        )
                        vulnerabilities.append(vuln)
                except json.JSONDecodeError:
                    pass

            return vulnerabilities
        except Exception as e:
            print(f"Checkov scan failed: {e}")

        return []

    def _map_bandit_severity(self, severity: str) -> str:
        """Map Bandit severity levels"""
        mapping = {"low": "low", "medium": "medium", "high": "high"}
        return mapping.get(severity.lower(), "medium")

    def _map_bandit_confidence(self, confidence: str) -> float:
        """Map Bandit confidence levels to float"""
        mapping = {"low": 0.3, "medium": 0.6, "high": 0.9}
        return mapping.get(confidence.lower(), 0.6)

    def _generate_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """Generate summary statistics"""
        summary = {
            "total": len(vulnerabilities),
            "high": len([v for v in vulnerabilities if v.severity == "high"]),
            "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
            "low": len([v for v in vulnerabilities if v.severity == "low"]),
        }
        return summary

    def _generate_ai_insights(
        self, vulnerabilities: List[Vulnerability], o1_validation_results: Dict = None
    ) -> List[str]:
        """Generate AI-powered insights with o1-preview validation context"""
        insights = []
        o1_validation_results = o1_validation_results or {}

        if not vulnerabilities:
            insights.append("No security vulnerabilities detected!")
            return insights

        # Severity analysis
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        if high_count > 0:
            insights.append(
                f"ALERT: {high_count} high-severity vulnerabilities require immediate attention"
            )

        # O1-preview validation insights
        if o1_validation_results:
            invalid_count = len(
                [
                    r
                    for r in o1_validation_results.values()
                    if not r["validation"]["is_valid"]
                ]
            )
            if invalid_count > 0:
                insights.append(
                    f"O1-preview validation identified {invalid_count} false positive(s) from automated tools"
                )

            # Calculate validation accuracy
            total_validated = len(o1_validation_results)
            if total_validated > 0:
                validation_rate = (
                    (total_validated - invalid_count) / total_validated * 100
                )
                insights.append(
                    f"O1-preview validated {total_validated} complex vulnerabilities with {validation_rate:.1f}% confirmed as genuine"
                )

        # Tool effectiveness
        tool_counts = {}
        for vuln in vulnerabilities:
            tool_counts[vuln.tool] = tool_counts.get(vuln.tool, 0) + 1

        top_tool = max(tool_counts.items(), key=lambda x: x[1])
        insights.append(
            f"Tool analysis: {top_tool[0]} detected the most issues ({top_tool[1]} total)"
        )

        # Common patterns
        file_counts = {}
        for vuln in vulnerabilities:
            file_counts[vuln.file] = file_counts.get(vuln.file, 0) + 1

        if file_counts:
            riskiest_file = max(file_counts.items(), key=lambda x: x[1])
            insights.append(
                f"File analysis: {riskiest_file[0]} has the most security issues ({riskiest_file[1]})"
            )

        return insights


def run_security_audit(path: str = ".") -> SecurityReport:
    """Run complete security audit"""
    scanner = SecurityScanner()
    report = scanner.scan_project(path)

    # Save report
    os.makedirs("security/reports", exist_ok=True)
    report_file = f"security/reports/security_audit_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_file, "w") as f:
        json.dump(
            {
                "timestamp": report.timestamp.isoformat(),
                "summary": report.summary,
                "ai_insights": report.ai_insights,
                "vulnerabilities": [
                    {
                        "tool": v.tool,
                        "severity": v.severity,
                        "title": v.title,
                        "description": v.description,
                        "file": v.file,
                        "line": v.line,
                        "cwe": v.cwe,
                        "confidence": v.confidence,
                        "ai_analysis": v.ai_analysis,
                        "o1_validation": v.o1_validation,
                    }
                    for v in report.vulnerabilities
                ],
            },
            f,
            indent=2,
        )

    print(f"🔒 Security report saved to {report_file}")
    return report


if __name__ == "__main__":
    report = run_security_audit()
    print(f"Security audit completed: {report.summary}")
