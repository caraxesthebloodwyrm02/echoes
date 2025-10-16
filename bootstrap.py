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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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
Echoes Development Environment Bootstrap and Startup System
Automates environment setup, dependency management, and system validation
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnvironmentBootstrapper:
    """Comprehensive environment bootstrapper for Echoes development"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.pyproject_file = self.project_root / "pyproject.toml"

    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 12:
            logger.info(
                f"✓ Python {version.major}.{version.minor}.{version.micro} detected"
            )
            return True
        else:
            logger.error(
                f"✗ Python 3.12+ required, found {version.major}.{version.minor}.{version.micro}"
            )
            return False

    def ensure_virtual_environment(self) -> bool:
        """Ensure virtual environment exists and is functional"""
        if not self.venv_path.exists():
            logger.info("Creating virtual environment...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "venv", str(self.venv_path)],
                    check=True,
                    capture_output=True,
                )
                logger.info("✓ Virtual environment created")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to create virtual environment: {e}")
                return False

        # Activate and verify
        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            logger.error("✗ Virtual environment Python executable not found")
            return False

        try:
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"✓ Virtual environment active: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            logger.error("✗ Virtual environment verification failed")
            return False

    def install_dependencies(self) -> bool:
        """Install project dependencies"""
        python_exe = self.venv_path / "Scripts" / "python.exe"
        pip_exe = self.venv_path / "Scripts" / "pip.exe"

        success = True

        # Upgrade pip first
        try:
            logger.info("Upgrading pip...")
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Pip upgrade failed: {e}")

        # Install from requirements.txt if it exists
        if self.requirements_file.exists():
            try:
                logger.info("Installing from requirements.txt...")
                subprocess.run(
                    [
                        str(python_exe),
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(self.requirements_file),
                    ],
                    check=True,
                )
                logger.info("✓ Dependencies installed from requirements.txt")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to install dependencies: {e}")
                success = False

        # Install from pyproject.toml if it exists
        if self.pyproject_file.exists():
            try:
                logger.info("Installing from pyproject.toml...")
                subprocess.run(
                    [str(python_exe), "-m", "pip", "install", "-e", "."],
                    check=True,
                    capture_output=True,
                )
                logger.info("✓ Package installed in development mode")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to install package: {e}")
                success = False

        return success

    def validate_openai_integration(self) -> bool:
        """Validate OpenAI API integration"""
        python_exe = self.venv_path / "Scripts" / "python.exe"

        try:
            # Test OpenAI import
            result = subprocess.run(
                [
                    str(python_exe),
                    "-c",
                    "import openai; import agents; print('OpenAI SDK available')",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("✓ OpenAI integration validated")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ OpenAI integration failed: {e.stderr}")
            return False

    def run_configuration_validation(self) -> bool:
        """Run configuration validation"""
        try:
            from tools.validate_configuration import validate_workspace_config

            logger.info("Running configuration validation...")
            result = validate_workspace_config()
            if result:
                logger.info("✓ Configuration validation passed")
            else:
                logger.error("✗ Configuration validation failed")
            return result
        except ImportError:
            logger.warning("Configuration validation tool not available")
            return True
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def generate_startup_script(self) -> None:
        """Generate PowerShell startup script for automatic activation"""
        startup_script = self.project_root / "activate_environment.ps1"

        script_content = """# Echoes Environment Activation Script
# Generated automatically - do not edit manually

param(
    [switch]$NoValidation,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor Green
    }
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

try {
    # Check if we're in the right directory
    if (-not (Test-Path ".venv")) {
        Write-Error "Virtual environment not found. Run bootstrap first."
        exit 1
    }

    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    & ".venv/Scripts/Activate.ps1"

    # Set environment variables
    $env:ECHOES_ENV = "development"
    $env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

    # Validate environment (unless disabled)
    if (-not $NoValidation) {
        Write-Info "Validating environment..."
        & python -c "
import sys
try:
    from utils.safe_imports import get_import_status
    import prompting.core.context_manager as cm
    import ai_agents.orchestrator as orch
    print('Environment validation successful')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Environment validation failed"
            exit 1
        }
    }

    Write-Info "Echoes development environment ready!"
    Write-Info "Available commands:"
    Write-Info "  python main.py              - Start main application"
    Write-Info "  python -m pytest           - Run tests"
    Write-Info "  python tools/validate_configuration.py - Validate config"

} catch {
    Write-Error "Environment activation failed: $_"
    exit 1
}
"""

        startup_script.write_text(script_content, encoding="utf-8")
        logger.info(f"✓ Startup script generated: {startup_script}")

    def bootstrap(self, skip_validation: bool = False) -> bool:
        """Complete environment bootstrap"""
        logger.info("=" * 60)
        logger.info("ECHOES DEVELOPMENT ENVIRONMENT BOOTSTRAP")
        logger.info("=" * 60)

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Ensuring virtual environment", self.ensure_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Validating OpenAI integration", self.validate_openai_integration),
        ]

        if not skip_validation:
            steps.append(
                ("Running configuration validation", self.run_configuration_validation)
            )

        success = True
        for step_name, step_func in steps:
            logger.info(f"\n{step_name}...")
            if not step_func():
                success = False
                break

        if success:
            self.generate_startup_script()
            logger.info("\n" + "=" * 60)
            logger.info("BOOTSTRAP COMPLETE - Environment ready!")
            logger.info("=" * 60)
            logger.info("Next steps:")
            logger.info("1. Restart your terminal or run: .\\activate_environment.ps1")
            logger.info("2. Start developing with: python main.py")
        else:
            logger.error("\n" + "=" * 60)
            logger.error("BOOTSTRAP FAILED - Check errors above")
            logger.error("=" * 60)

        return success


def main():
    parser = argparse.ArgumentParser(
        description="Echoes Development Environment Bootstrapper"
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip configuration validation"
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    bootstrapper = EnvironmentBootstrapper()
    success = bootstrapper.bootstrap(skip_validation=args.skip_validation)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
