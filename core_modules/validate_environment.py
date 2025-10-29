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
ECHOES Hybrid Assistant Environment Validation Script
Tests all AI framework integrations and environment setup
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class EnvironmentValidator:
    """Validates ECHOES hybrid assistant environment setup"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "pending",
            "recommendations": [],
        }

    def validate_openai_integration(self) -> Dict[str, Any]:
        """Test OpenAI API integration"""
        test_result = {"status": "pending", "details": {}, "errors": []}

        try:
            # Check environment variables
            api_key = os.getenv("OPENAI_API_KEY")
            echoes_key = os.getenv("OPENAI_API_KEY_ECHOES")

            if not api_key and not echoes_key:
                test_result["status"] = "failed"
                test_result["errors"].append("No OpenAI API keys found in environment")
                return test_result

            test_result["details"]["primary_key_configured"] = bool(api_key)
            test_result["details"]["echoes_key_configured"] = bool(echoes_key)

            # Test API connectivity if keys are available
            if api_key or echoes_key:
                import openai

                client = openai.OpenAI(api_key=api_key or echoes_key)

                # Simple test call
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                )

                if response.choices:
                    test_result["status"] = "passed"
                    test_result["details"]["api_connectivity"] = True
                    test_result["details"]["model_access"] = True
                else:
                    test_result["status"] = "failed"
                    test_result["errors"].append("OpenAI API returned empty response")

        except ImportError:
            test_result["status"] = "failed"
            test_result["errors"].append("OpenAI package not installed")
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"OpenAI integration failed: {str(e)}")

        return test_result

    def validate_azure_integration(self) -> Dict[str, Any]:
        """Test Azure AI integration"""
        test_result = {"status": "pending", "details": {}, "errors": []}

        try:
            # Check Azure environment variables
            endpoint = os.getenv("AZURE_AI_ENDPOINT")
            api_key = os.getenv("AZURE_AI_API_KEY")
            deployment = os.getenv("AZURE_AI_DEPLOYMENT_NAME", "gpt-4")

            if not endpoint or not api_key:
                test_result["status"] = "warning"
                test_result["details"]["configured"] = False
                test_result["details"]["message"] = "Azure AI not configured (optional for hybrid setup)"
                return test_result

            test_result["details"]["endpoint_configured"] = bool(endpoint)
            test_result["details"]["api_key_configured"] = bool(api_key)
            test_result["details"]["deployment"] = deployment

            # Test Azure AI connectivity
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

            # Simple test call
            response = client.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model=deployment,
                max_tokens=10,
            )

            if response.choices:
                test_result["status"] = "passed"
                test_result["details"]["api_connectivity"] = True
                test_result["details"]["model_access"] = True
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Azure AI API returned empty response")

        except ImportError:
            test_result["status"] = "failed"
            test_result["errors"].append("Azure AI inference package not installed")
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Azure AI integration failed: {str(e)}")

        return test_result

    def validate_github_integration(self) -> Dict[str, Any]:
        """Test GitHub API integration"""
        test_result = {"status": "pending", "details": {}, "errors": []}

        try:
            github_token = os.getenv("GITHUB_TOKEN")

            if not github_token:
                test_result["status"] = "failed"
                test_result["errors"].append("GitHub token not configured")
                return test_result

            test_result["details"]["token_configured"] = True

            # Test GitHub API connectivity
            from github import Github

            g = Github(github_token)

            # Test basic API call
            user = g.get_user()
            test_result["details"]["api_connectivity"] = True
            test_result["details"]["authenticated_user"] = user.login

            # Test repository access if configured
            repo_name = os.getenv("GITHUB_REPOSITORY")
            if repo_name:
                try:
                    repo = g.get_repo(repo_name)
                    test_result["details"]["repository_access"] = True
                    test_result["details"]["repository_name"] = repo.full_name
                except Exception as e:
                    test_result["details"]["repository_access"] = False
                    test_result["errors"].append(f"Repository access failed: {str(e)}")

            test_result["status"] = "passed"

        except ImportError:
            test_result["status"] = "failed"
            test_result["errors"].append("PyGitHub package not installed")
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"GitHub integration failed: {str(e)}")

        return test_result

    def validate_hybrid_configuration(self) -> Dict[str, Any]:
        """Validate hybrid assistant configuration"""
        test_result = {"status": "pending", "details": {}, "errors": []}

        try:
            # Check hybrid assistant settings
            strategy = os.getenv("HYBRID_ASSISTANT_DEFAULT_STRATEGY", "auto")
            threshold = os.getenv("HYBRID_ASSISTANT_COMPLEXITY_THRESHOLD", "0.7")
            cross_validation = os.getenv("HYBRID_ASSISTANT_CROSS_VALIDATION", "true")
            monitoring = os.getenv("HYBRID_ASSISTANT_MONITORING", "true")

            valid_strategies = ["auto", "openai", "azure", "local", "hybrid"]

            if strategy not in valid_strategies:
                test_result["errors"].append(f"Invalid routing strategy: {strategy}")
                test_result["status"] = "failed"
                return test_result

            try:
                threshold_val = float(threshold)
                if not 0.0 <= threshold_val <= 1.0:
                    test_result["errors"].append(f"Invalid complexity threshold: {threshold}")
                    test_result["status"] = "failed"
                    return test_result
            except ValueError:
                test_result["errors"].append(f"Invalid complexity threshold format: {threshold}")
                test_result["status"] = "failed"
                return test_result

            test_result["details"]["routing_strategy"] = strategy
            test_result["details"]["complexity_threshold"] = threshold
            test_result["details"]["cross_validation_enabled"] = cross_validation.lower() == "true"
            test_result["details"]["monitoring_enabled"] = monitoring.lower() == "true"

            test_result["status"] = "passed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Hybrid configuration validation failed: {str(e)}")

        return test_result

    def validate_directory_structure(self) -> Dict[str, Any]:
        """Validate required directory structure"""
        test_result = {"status": "pending", "details": {}, "errors": []}

        try:
            # Check required directories
            required_dirs = [
                "data/assistant",
                "cache/assistant",
                "logs",
                "security/reports",
                "assistants",
            ]

            for dir_path in required_dirs:
                full_path = project_root / dir_path
                if full_path.exists():
                    test_result["details"][dir_path] = "exists"
                else:
                    test_result["details"][dir_path] = "missing"
                    test_result["errors"].append(f"Required directory missing: {dir_path}")

            # Check for configuration files
            config_files = [".env", "pyproject.toml", "requirements.txt"]

            for file_path in config_files:
                full_path = project_root / file_path
                if full_path.exists():
                    test_result["details"][file_path] = "exists"
                else:
                    test_result["details"][file_path] = "missing"
                    test_result["errors"].append(f"Configuration file missing: {file_path}")

            if not test_result["errors"]:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "warning"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Directory validation failed: {str(e)}")

        return test_result

    def run_all_validations(self) -> Dict[str, Any]:
        """Run all environment validations"""

        print("ECHOES Hybrid Assistant Environment Validation")
        print("=" * 60)

        validations = {
            "openai_integration": self.validate_openai_integration,
            "azure_integration": self.validate_azure_integration,
            "github_integration": self.validate_github_integration,
            "hybrid_configuration": self.validate_hybrid_configuration,
            "directory_structure": self.validate_directory_structure,
        }

        for test_name, test_func in validations.items():
            print(f"\nTesting {test_name.replace('_', ' ')}...")
            try:
                result = test_func()
                self.results["tests"][test_name] = result

                status_icon = {
                    "passed": "[PASS]",
                    "failed": "[FAIL]",
                    "warning": "[WARN]",
                    "pending": "[PEND]",
                }.get(result["status"], "[UNK]")

                print(f"   {status_icon} {result['status'].upper()}")

                if result["errors"]:
                    for error in result["errors"]:
                        print(f"     - {error}")

            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                self.results["tests"][test_name] = {
                    "status": "failed",
                    "details": {},
                    "errors": [str(e)],
                }

        # Determine overall status
        test_results = [test["status"] for test in self.results["tests"].values()]
        if "failed" in test_results:
            self.results["overall_status"] = "failed"
        elif "warning" in test_results:
            self.results["overall_status"] = "warning"
        elif all(r == "passed" for r in test_results):
            self.results["overall_status"] = "passed"
        else:
            self.results["overall_status"] = "partial"

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _generate_recommendations(self):
        """Generate setup recommendations based on validation results"""

        recommendations = []

        # Check OpenAI setup
        openai_test = self.results["tests"].get("openai_integration", {})
        if openai_test.get("status") == "failed":
            recommendations.append(
                {
                    "priority": "high",
                    "component": "OpenAI Integration",
                    "action": "Configure valid OpenAI API keys in .env file",
                    "details": "Both OPENAI_API_KEY and OPENAI_API_KEY_ECHOES should be set",
                }
            )

        # Check Azure setup (optional)
        azure_test = self.results["tests"].get("azure_integration", {})
        if azure_test.get("status") == "failed":
            recommendations.append(
                {
                    "priority": "medium",
                    "component": "Azure AI Integration",
                    "action": "Configure Azure AI credentials for hybrid functionality",
                    "details": "Set AZURE_AI_ENDPOINT and AZURE_AI_API_KEY for full hybrid capabilities",
                }
            )

        # Check GitHub setup
        github_test = self.results["tests"].get("github_integration", {})
        if github_test.get("status") == "failed":
            recommendations.append(
                {
                    "priority": "high",
                    "component": "GitHub Integration",
                    "action": "Configure GitHub Personal Access Token",
                    "details": "Set GITHUB_TOKEN with appropriate repository permissions",
                }
            )

        # Check directory structure
        dir_test = self.results["tests"].get("directory_structure", {})
        if dir_test.get("status") in ["failed", "warning"]:
            missing_items = [k for k, v in dir_test.get("details", {}).items() if v == "missing"]
            if missing_items:
                recommendations.append(
                    {
                        "priority": "low",
                        "component": "Directory Structure",
                        "action": "Create missing directories and files",
                        "details": f"Missing: {', '.join(missing_items)}",
                    }
                )

        self.results["recommendations"] = recommendations

    def save_validation_report(self, output_path: str = None):
        """Save validation results to file"""

        if not output_path:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/environment_validation_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\nValidation report saved to: {output_path}")
        return output_path


def main():
    """Main validation function"""

    validator = EnvironmentValidator()
    results = validator.run_all_validations()

    print(f"\nOVERALL STATUS: {results['overall_status'].upper()}")

    if results["recommendations"]:
        print("\nRECOMMENDATIONS:")
        for rec in results["recommendations"]:
            priority_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(rec["priority"], "[UNK]")
            print(f"   {priority_icon} [{rec['priority'].upper()}] {rec['component']}: {rec['action']}")
            if rec.get("details"):
                print(f"      {rec['details']}")

    # Save report
    report_path = validator.save_validation_report()

    return results["overall_status"] == "passed"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
