"""
AI-Enhanced Security Scanning System
Advanced vulnerability detection using multiple tools with AI-powered analysis
"""

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


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
            Line: {vuln.line or 'N/A'}
            CWE: {vuln.cwe or 'N/A'}

            Please provide:
            1. Risk assessment
            2. Potential impact
            3. Recommended fix
            4. Prevention measures
            """

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4", messages=[{"role": "user", "content": prompt}], max_tokens=300, temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"AI analysis failed: {str(e)}"


class SecurityScanner:
    """Unified security scanning with multiple tools"""

    def __init__(self):
        self.ai_analyzer = AISecurityAnalyzer()
        self.tools = {
            "bandit": self._run_bandit,
            "semgrep": self._run_semgrep,
            "snyk": self._run_snyk,
            "checkov": self._run_checkov,
        }

    def scan_project(self, path: str = ".") -> SecurityReport:
        """Run comprehensive security scan"""
        print("🔒 Starting comprehensive security scan...")

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
        print("🤖 Running AI-powered analysis...")
        for vuln in all_vulnerabilities:
            vuln.ai_analysis = self.ai_analyzer.analyze_vulnerability(vuln)

        # Generate summary
        summary = self._generate_summary(all_vulnerabilities)

        # Generate AI insights
        ai_insights = self._generate_ai_insights(all_vulnerabilities)

        report = SecurityReport(
            timestamp=datetime.now(), vulnerabilities=all_vulnerabilities, summary=summary, ai_insights=ai_insights
        )

        return report

    def _run_bandit(self, path: str) -> List[Vulnerability]:
        """Run Bandit security scanner"""
        try:
            result = subprocess.run(["bandit", "-f", "json", "-r", path], capture_output=True, text=True, timeout=300)

            if result.returncode in [0, 1]:  # Bandit returns 1 when issues found
                data = json.loads(result.stdout)
                vulnerabilities = []

                for issue in data.get("results", []):
                    vuln = Vulnerability(
                        tool="bandit",
                        severity=self._map_bandit_severity(issue.get("issue_severity", "medium")),
                        title=issue.get("issue_text", ""),
                        description=issue.get("issue_text", ""),
                        file=issue.get("filename", ""),
                        line=issue.get("line_number"),
                        cwe=issue.get("issue_cwe", {}).get("id"),
                        confidence=self._map_bandit_confidence(issue.get("issue_confidence", "medium")),
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
                ["semgrep", "--json", "--config", "auto", path], capture_output=True, text=True, timeout=300
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
                ["snyk", "code", "test", path, "--json"], capture_output=True, text=True, timeout=300
            )

            vulnerabilities = []

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    for vuln in data.get("runs", [{}])[0].get("results", {}).get("vulnerabilities", []):
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

    def _generate_ai_insights(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate AI-powered insights"""
        insights = []

        if not vulnerabilities:
            insights.append("🎉 No security vulnerabilities detected!")
            return insights

        # Severity analysis
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        if high_count > 0:
            insights.append(f"🚨 {high_count} high-severity vulnerabilities require immediate attention")

        # Tool effectiveness
        tool_counts = {}
        for vuln in vulnerabilities:
            tool_counts[vuln.tool] = tool_counts.get(vuln.tool, 0) + 1

        top_tool = max(tool_counts.items(), key=lambda x: x[1])
        insights.append(f"📊 {top_tool[0]} detected the most issues ({top_tool[1]} total)")

        # Common patterns
        file_counts = {}
        for vuln in vulnerabilities:
            file_counts[vuln.file] = file_counts.get(vuln.file, 0) + 1

        if file_counts:
            riskiest_file = max(file_counts.items(), key=lambda x: x[1])
            insights.append(f"🎯 {riskiest_file[0]} has the most security issues ({riskiest_file[1]})")

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
