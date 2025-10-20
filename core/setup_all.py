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
Master Setup Script for Q4 Automation
Orchestrates all setup tasks for the Q4 roadmap
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class Color:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class SetupOrchestrator:
    """Orchestrates all Q4 automation setup tasks"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.q4_root = Path(__file__).parent.parent
        self.results = []
        self.start_time = datetime.now()
        self.task_order = [
            ("check_prerequisites", "Prerequisites Check"),
            ("check_python_version", "Environment Check"),
            ("install_dependencies", "Dependency Installation"),
            ("setup_database", "Database Setup"),
            ("setup_testing", "Testing Infrastructure"),
            ("setup_code_quality", "Code Quality Tools"),
            ("setup_ci_cd", "CI/CD Pipeline"),
            ("run_security_scan", "Security Testing"),
            ("run_compliance_check", "Compliance Audit"),
            ("setup_metering", "Cost Metering"),
            ("setup_privacy_filters", "Privacy Filters"),
            ("run_load_tests", "Load Testing"),
        ]

    def log(self, message: str, level: str = "INFO"):
        """Colored logging"""
        colors = {
            "INFO": Color.BLUE,
            "SUCCESS": Color.GREEN,
            "WARNING": Color.YELLOW,
            "ERROR": Color.RED,
        }
        color = colors.get(level, "")
        print(f"{color}[{level}]{Color.END} {message}")

    def run_command(self, cmd: List[str], description: str, timeout: int = 300) -> Tuple[bool, str]:
        """Run a command and return success status with timeout"""
        self.log(f"Running: {description}", "INFO")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
                timeout=timeout,
            )
            self.log(f"✓ {description}", "SUCCESS")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"✗ {description}: {e.stderr}", "ERROR")
            return False, e.stderr
        except subprocess.TimeoutExpired:
            self.log(f"✗ {description}: Timeout after {timeout}s", "ERROR")
            return False, f"Timeout after {timeout}s"
        except FileNotFoundError:
            self.log(f"✗ Command not found: {cmd[0]}", "ERROR")
            return False, f"Command not found: {cmd[0]}"

    def check_python_version(self):
        """Verify Python version"""
        self.log("Checking Python version...", "INFO")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"✓ Python {version.major}.{version.minor}.{version.micro}", "SUCCESS")
            return True
        else:
            self.log(
                f"✗ Python 3.8+ required, found {version.major}.{version.minor}",
                "ERROR",
            )
            return False

    def install_dependencies(self):
        """Install all required dependencies"""
        self.log("Installing dependencies...", "INFO")

        # Q4 specific dependencies
        q4_requirements = self.q4_root / "requirements.txt"
        if not q4_requirements.exists():
            self.log("Creating Q4 requirements.txt", "INFO")
            with open(q4_requirements, "w", encoding="utf-8") as f:
                f.write(
                    """pandas>=2.0.0
openpyxl>=3.1.0
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
bandit>=1.7.5
sphinx>=7.0.0
locust>=2.15.0
safety>=2.3.0
"""
                )

        success, _ = self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", str(q4_requirements)],
            "Installing Q4 dependencies",
        )
        self.results.append(("Dependencies", success))
        return success

    def execute_pipeline(self) -> bool:
        """Execute the complete automation pipeline with proper flow control"""
        self.log("Starting Q4 Automation Pipeline", "INFO")
        print("=" * 80)

        successful_tasks = 0
        failed_tasks = []

        try:
            for i, (task_name, task_description) in enumerate(self.task_order, 1):
                print(f"\n[{i:2d}/{len(self.task_order):2d}] {task_description}")
                print("-" * 60)

                # Execute task
                task_method = getattr(self, task_name)
                success = task_method()

                if success:
                    successful_tasks += 1
                    print(f"✓ Task {i} completed successfully")
                else:
                    failed_tasks.append(task_description)
                    print(f"⚠ Task {i} completed with warnings")

                # Brief pause between tasks for visibility
                import time

                time.sleep(0.5)

            print("\n" + "=" * 80)
            success_rate = successful_tasks / len(self.task_order) * 100

            if success_rate >= 90:
                self.log(
                    f"Pipeline completed successfully! ({successful_tasks}/{len(self.task_order)} tasks)",
                    "SUCCESS",
                )
                pipeline_success = True
            else:
                self.log(
                    f"Pipeline completed with issues ({successful_tasks}/{len(self.task_order)} tasks)",
                    "WARNING",
                )
                pipeline_success = False

            # Validate pipeline health
            if not self.validate_pipeline_health():
                pipeline_success = False
                self.log("Pipeline validation failed", "ERROR")

            return pipeline_success

        except KeyboardInterrupt:
            self.log("Pipeline interrupted by user", "WARNING")
            return False
        except (OSError, subprocess.SubprocessError) as e:
            self.log(f"Pipeline failed with error: {e}", "ERROR")
            self.cleanup_on_failure()
            return False

    def setup_database(self):
        """Setup database persistence layer"""
        self.log("Setting up database...", "INFO")

        # Check if PostgreSQL is available
        success, _ = self.run_command(["psql", "--version"], "Checking PostgreSQL installation")

        if not success:
            self.log("PostgreSQL not found - skipping database setup", "WARNING")
            self.log("Install PostgreSQL to enable database features", "INFO")
            self.results.append(("Database Setup", False))
            return False

        # Run database setup script
        db_script = self.q4_root / "automation" / "setup_database.py"
        if db_script.exists():
            success, _ = self.run_command([sys.executable, str(db_script)], "Running database setup script")
            self.results.append(("Database Setup", success))
            return success
        else:
            self.log("Database setup script not found", "WARNING")
            self.results.append(("Database Setup", False))
            return False

    def run_security_scan(self):
        """Run security penetration testing"""
        self.log("Running security scan...", "INFO")

        security_script = self.q4_root / "automation" / "security_scan.py"
        if security_script.exists():
            success, _ = self.run_command(
                [sys.executable, str(security_script)],
                "Running security penetration testing",
            )
            self.results.append(("Security Scan", success))
            return success
        else:
            self.log("Security scan script not found", "WARNING")
            self.results.append(("Security Scan", False))
            return False

    def run_compliance_check(self):
        """Run compliance audit framework"""
        self.log("Running compliance check...", "INFO")

        compliance_script = self.q4_root / "automation" / "compliance_check.py"
        if compliance_script.exists():
            success, _ = self.run_command(
                [sys.executable, str(compliance_script)],
                "Running compliance audit framework",
            )
            self.results.append(("Compliance Check", success))
            return success
        else:
            self.log("Compliance check script not found", "WARNING")
            self.results.append(("Compliance Check", False))
            return False

    def setup_metering(self):
        """Setup cost metering and quotas"""
        self.log("Setting up metering...", "INFO")

        metering_script = self.q4_root / "automation" / "setup_metering.py"
        if metering_script.exists():
            success, _ = self.run_command([sys.executable, str(metering_script)], "Running cost metering setup")
            self.results.append(("Metering Setup", success))
            return success
        else:
            self.log("Metering setup script not found", "WARNING")
            self.results.append(("Metering Setup", False))
            return False

    def setup_privacy_filters(self):
        """Setup privacy filters implementation"""
        self.log("Setting up privacy filters...", "INFO")

        privacy_script = self.q4_root / "automation" / "privacy_filters.py"
        if privacy_script.exists():
            success, _ = self.run_command([sys.executable, str(privacy_script)], "Running privacy filters setup")
            self.results.append(("Privacy Filters", success))
            return success
        else:
            self.log("Privacy filters script not found", "WARNING")
            self.results.append(("Privacy Filters", False))
            return False

    def run_load_tests(self):
        """Run load testing suite"""
        self.log("Running load tests...", "INFO")

        load_script = self.q4_root / "automation" / "run_load_tests.py"
        if load_script.exists():
            success, _ = self.run_command([sys.executable, str(load_script)], "Running load testing suite")
            self.results.append(("Load Tests", success))
            return success
        else:
            self.log("Load tests script not found", "WARNING")
            self.results.append(("Load Tests", False))
            return False

    def setup_testing(self):
        """Setup testing infrastructure"""
        self.log("Setting up testing infrastructure...", "INFO")

        # Create test directories
        test_dirs = [
            self.q4_root / "tests",
            self.q4_root / "tests" / "unit",
            self.q4_root / "tests" / "integration",
            self.q4_root / "tests" / "load",
        ]

        for test_dir in test_dirs:
            test_dir.mkdir(parents=True, exist_ok=True)
            (test_dir / "__init__.py").touch()

        # Create pytest.ini if it doesn't exist
        pytest_ini = self.q4_root / "pytest.ini"
        if not pytest_ini.exists():
            with open(pytest_ini, "w", encoding="utf-8") as f:
                f.write(
                    """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=.
    --cov-report=term-missing
    --cov-report=html
"""
                )

        self.log("✓ Testing infrastructure ready", "SUCCESS")
        self.results.append(("Testing Setup", True))
        return True

    def setup_code_quality(self):
        """Setup code quality tools"""
        self.log("Setting up code quality tools...", "INFO")

        # Create .flake8 config
        flake8_config = self.q4_root / ".flake8"
        if not flake8_config.exists():
            with open(flake8_config, "w", encoding="utf-8") as f:
                f.write(
                    """[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,build,dist
ignore = E203,W503
"""
                )

        # Create mypy.ini config
        mypy_config = self.q4_root / "mypy.ini"
        if not mypy_config.exists():
            with open(mypy_config, "w", encoding="utf-8") as f:
                f.write(
                    """[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
"""
                )

        self.log("✓ Code quality tools configured", "SUCCESS")
        self.results.append(("Code Quality Setup", True))
        return True

    def setup_ci_cd(self):
        """Setup CI/CD pipeline"""
        self.log("Setting up CI/CD pipeline...", "INFO")

        github_dir = self.project_root / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = github_dir / "q4_automation.yml"
        with open(workflow_file, "w", encoding="utf-8") as f:
            f.write(
                """name: Q4 Automation Pipeline

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'Q4/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'Q4/**'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        cd Q4
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd Q4
        python automation/run_tests.py

    - name: Security scan
      run: |
        cd Q4
        python automation/security_scan.py

    - name: Compliance check
      run: |
        cd Q4
        python automation/compliance_check.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Deploy
      run: |
        cd Q4
        python automation/deploy.py --env production
"""
            )

        self.log("✓ CI/CD pipeline configured", "SUCCESS")
        self.results.append(("CI/CD Setup", True))
        return True

    def generate_report(self):
        """Generate setup report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("\n" + "=" * 60)
        print(f"{Color.BOLD}Q4 AUTOMATION SETUP REPORT{Color.END}")
        print("=" * 60)

        total = len(self.results)
        successful = sum(1 for _, success in self.results if success)

        for task, success in self.results:
            status = f"{Color.GREEN}✓{Color.END}" if success else f"{Color.RED}✗{Color.END}"
            print(f"{status} {task}")

        print("=" * 60)
        print(f"Total: {successful}/{total} tasks completed")
        print(f"Duration: {duration:.2f} seconds")
        print("=" * 60)

        # Save report to JSON
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "total_tasks": total,
            "successful_tasks": successful,
            "tasks": [{"name": task, "success": success} for task, success in self.results],
        }

        report_file = self.q4_root / "automation" / "setup_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        self.log(f"Report saved to: {report_file}", "INFO")

        return successful == total

    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all required tools are available"""
        self.log("Checking prerequisites...", "INFO")

        prerequisites = {
            "python": sys.executable,
            "pip": [sys.executable, "-m", "pip", "--version"],
            "pytest": [sys.executable, "-m", "pytest", "--version"],
            "git": ["git", "--version"],
            "node": ["node", "--version"],  # For some tools
        }

        available_tools = {}

        for tool, command in prerequisites.items():
            try:
                if isinstance(command, list):
                    subprocess.run(command, capture_output=True, check=True, timeout=10)
                else:
                    Path(command).exists()  # Just check if file exists
                available_tools[tool] = True
                self.log(f"✓ {tool} available", "SUCCESS")
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                available_tools[tool] = False
                self.log(f"⚠ {tool} not found", "WARNING")

        return available_tools

    def cleanup_on_failure(self):
        """Clean up resources if pipeline fails"""
        self.log("Performing cleanup due to pipeline failure...", "WARNING")

        # Remove any temporary files or partial setups
        cleanup_dirs = [
            self.q4_root / "build",
            self.q4_root / "dist",
            self.q4_root / ".pytest_cache",
        ]

        for cleanup_dir in cleanup_dirs:
            if cleanup_dir.exists():
                import shutil

                shutil.rmtree(cleanup_dir, ignore_errors=True)
                self.log(f"Cleaned up: {cleanup_dir}", "INFO")

    def validate_pipeline_health(self) -> bool:
        """Validate that the pipeline completed successfully"""
        self.log("Validating pipeline health...", "INFO")

        # Check that key files were created
        key_files = [
            self.q4_root / "requirements.txt",
            self.q4_root / "pytest.ini",
            self.q4_root / ".flake8",
            self.q4_root / "mypy.ini",
            self.q4_root / "automation" / "setup_report.json",
        ]

        missing_files = []
        for key_file in key_files:
            if not key_file.exists():
                missing_files.append(key_file.name)

        if missing_files:
            self.log(f"Missing expected files: {', '.join(missing_files)}", "ERROR")
            return False

        self.log("✓ Pipeline validation passed", "SUCCESS")
        return True


def main():
    """Main setup orchestration"""
    orchestrator = SetupOrchestrator()

    print(f"\n{Color.BOLD}Q4 Automation Setup{Color.END}")
    print("=" * 60)

    # Execute streamlined pipeline
    success = orchestrator.execute_pipeline()

    # Generate detailed report
    orchestrator.generate_report()

    if success:
        print(f"\n{Color.GREEN}{Color.BOLD}✓ Pipeline completed successfully!{Color.END}")
        return 0
    else:
        print(f"\n{Color.YELLOW}{Color.BOLD}⚠ Pipeline completed with warnings{Color.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
