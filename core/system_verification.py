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
import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("verification")


class SystemVerification:
    def __init__(self):
        self.user_dir = Path(os.path.expanduser("~"))
        self.codeium_dir = self.user_dir / ".codeium"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "issues": [],
            "recommendations": [],
        }

    def check_directory_structure(self):
        """Verify the directory structure is correct"""
        required_dirs = [
            "brain",
            "cascade",
            "chat_state",
            "code_tracker",
            "context_state",
            "database",
            "implicit",
            "memories",
        ]

        for dir_name in required_dirs:
            dir_path = self.codeium_dir / dir_name
            if not dir_path.exists():
                self.results["issues"].append(f"Missing directory: {dir_name}")
            else:
                self.results["checks"].append(f"Directory present: {dir_name}")

    def verify_configuration_files(self):
        """Verify configuration files exist and are valid"""
        config_files = ["user_settings.pb", "installation_id"]

        for file_name in config_files:
            file_path = self.codeium_dir / file_name
            if not file_path.exists():
                self.results["issues"].append(
                    f"Missing configuration file: {file_name}"
                )
            else:
                self.results["checks"].append(
                    f"Configuration file present: {file_name}"
                )

    def check_permissions(self):
        """Verify directory permissions"""
        try:
            test_file = self.codeium_dir / "test_permissions.tmp"
            test_file.touch()
            test_file.unlink()
            self.results["checks"].append("Directory permissions verified")
        except Exception as e:
            self.results["issues"].append(f"Permission issue: {str(e)}")

    def verify_integration(self):
        """Verify integration with VS Code"""
        vscode_dir = self.user_dir / ".vscode"
        if not vscode_dir.exists():
            self.results["issues"].append("VS Code directory not found")
            return

        # Check extensions
        extensions_dir = vscode_dir / "extensions"
        if extensions_dir.exists():
            codeium_ext = list(extensions_dir.glob("*codeium*"))
            if not codeium_ext:
                self.results["issues"].append("Codeium extension not found")
            else:
                self.results["checks"].append("Codeium extension found")

    def generate_recommendations(self):
        """Generate recommendations based on issues found"""
        if self.results["issues"]:
            for issue in self.results["issues"]:
                if "Missing directory" in issue:
                    self.results["recommendations"].append(
                        f"Create missing directory: {issue.split(': ')[1]}"
                    )
                elif "Permission issue" in issue:
                    self.results["recommendations"].append(
                        "Check and fix directory permissions"
                    )
                elif "Missing configuration" in issue:
                    self.results["recommendations"].append(
                        f"Restore configuration file: {issue.split(': ')[1]}"
                    )

    def run_verification(self):
        """Run all verification checks"""
        logger.info("Starting system verification...")

        self.check_directory_structure()
        self.verify_configuration_files()
        self.check_permissions()
        self.verify_integration()
        self.generate_recommendations()

        # Save results
        output_file = Path("verification_results.json")
        with output_file.open("w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Verification complete. Results saved to {output_file}")

        return self.results


if __name__ == "__main__":
    verifier = SystemVerification()
    results = verifier.run_verification()

    # Print summary
    print("\nVerification Summary:")
    print("=" * 50)
    print(f"Checks passed: {len(results['checks'])}")
    print(f"Issues found: {len(results['issues'])}")
    print(f"Recommendations: {len(results['recommendations'])}")

    if results["issues"]:
        print("\nIssues Found:")
        for issue in results["issues"]:
            print(f"- {issue}")

    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"- {rec}")
