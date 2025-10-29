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
# copies or substantial portions of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions.
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
Echoes Profile Setup and Environment Manager
Automates profile alignment and environment configuration
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ProfileManager:
    """Manages IDE profiles and environment alignment"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.vscode_settings = self.project_root / ".vscode" / "settings.json"
        self.vscode_extensions = self.project_root / ".vscode" / "extensions.json"

        # User profile paths
        self.user_appdata = Path(os.environ.get("APPDATA", ""))
        self.vscode_user_settings = self.user_appdata / "Code" / "User" / "settings.json"
        self.windsurf_user_settings = self.user_appdata / "Windsurf" / "User" / "settings.json"

    def backup_existing_settings(self) -> bool:
        """Backup existing user settings before modification"""
        logger.info("Creating backups of existing settings...")

        backups_created = []

        # Backup VS Code settings
        if self.vscode_user_settings.exists():
            backup_path = self.vscode_user_settings.with_suffix(".backup.json")
            shutil.copy2(self.vscode_user_settings, backup_path)
            backups_created.append(f"VS Code settings -> {backup_path}")

        # Backup Windsurf settings
        if self.windsurf_user_settings.exists():
            backup_path = self.windsurf_user_settings.with_suffix(".backup.json")
            shutil.copy2(self.windsurf_user_settings, backup_path)
            backups_created.append(f"Windsurf settings -> {backup_path}")

        if backups_created:
            logger.info("Backups created:")
            for backup in backups_created:
                logger.info(f"  ✓ {backup}")
            return True
        else:
            logger.info("No existing settings to backup")
            return True

    def align_user_profiles(self) -> bool:
        """Align user profiles with project requirements"""
        logger.info("Aligning user profiles...")

        # Load project settings as template
        if not self.vscode_settings.exists():
            logger.error("Project settings not found")
            return False

        try:
            with open(self.vscode_settings, "r", encoding="utf-8") as f:
                project_settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project settings: {e}")
            return False

        # Extract user-level settings (exclude workspace-specific ones)
        user_level_settings = self._extract_user_settings(project_settings)

        # Update VS Code user settings
        success_vscode = self._update_user_settings(self.vscode_user_settings, user_level_settings, "VS Code")

        # Update Windsurf user settings
        success_windsurf = self._update_user_settings(self.windsurf_user_settings, user_level_settings, "Windsurf")

        return success_vscode and success_windsurf

    def _extract_user_settings(self, project_settings: Dict) -> Dict:
        """Extract user-level settings from project settings"""
        # These are typically global user preferences, not workspace-specific
        user_keys = {
            # Appearance
            "workbench.colorTheme",
            "workbench.iconTheme",
            "editor.fontFamily",
            "editor.fontSize",
            "editor.lineHeight",
            "editor.fontLigatures",
            "editor.cursorStyle",
            "editor.cursorBlinking",
            # Editor behavior
            "editor.wordWrap",
            "editor.minimap.enabled",
            "editor.scrollBeyondLastLine",
            "editor.smoothScrolling",
            "editor.mouseWheelZoom",
            # File handling
            "files.trimTrailingWhitespace",
            "files.insertFinalNewline",
            "files.autoSave",
            "files.autoSaveDelay",
            "files.hotExit",
            # Search
            "search.smartCase",
            "search.useGlobalIgnoreFiles",
            "search.useIgnoreFiles",
            # Git
            "git.autofetch",
            "git.confirmSync",
            "git.enableSmartCommit",
            "git.showPushSuccessNotification",
            # Extensions
            "extensions.autoUpdate",
            "extensions.autoCheckUpdates",
            # Security & Privacy
            "security.workspace.trust.enabled",
            "telemetry.telemetryLevel",
            # Breadcrumbs
            "breadcrumbs.enabled",
            # Status/Activity bars
            "workbench.statusBar.visible",
            "workbench.activityBar.visible",
            # Zen mode
            "zenMode.centerLayout",
            # Accessibility
            "accessibility.signals.terminalBell",
            "accessibility.signals.terminalQuickFix",
            # Experimental
            "workbench.enableExperiments",
        }

        user_settings = {}
        for key in user_keys:
            if key in project_settings:
                user_settings[key] = project_settings[key]

        return user_settings

    def _update_user_settings(self, settings_path: Path, new_settings: Dict, name: str) -> bool:
        """Update user settings file"""
        try:
            # Load existing settings
            existing_settings = {}
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    existing_settings = json.load(f)

            # Merge with new settings (new settings take precedence)
            merged_settings = {**existing_settings, **new_settings}

            # Write back
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(merged_settings, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Updated {name} user settings")
            return True

        except Exception as e:
            logger.error(f"Failed to update {name} settings: {e}")
            return False

    def setup_auto_startup(self) -> bool:
        """Setup automatic environment startup"""
        logger.info("Setting up automatic startup...")

        # Create startup scripts
        startup_script = self.project_root / "startup.py"
        startup_content = '''#!/usr/bin/env python3
"""
Echoes Automatic Startup Script
Validates and prepares the development environment
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    try:
        # Quick validation
        from utils.safe_imports import get_safe_kg_bridge, get_safe_agent_knowledge_layer
        from utils.openai_integration import get_openai_integration

        # Test core imports
        kg_bridge = get_safe_kg_bridge(enable_kg=False)
        akl = get_safe_agent_knowledge_layer(enable_kg=False)
        openai = get_openai_integration()

        print("Echoes development environment ready!")
        print(f"Knowledge Graph: {'Available' if kg_bridge.enabled else 'Fallback mode'}")
        print(f"Agent Layer: {'Available' if akl.enabled else 'Fallback mode'}")
        print(f"OpenAI: {'Configured' if openai.is_configured else 'Not configured'}")

        return True

    except Exception as e:
        print(f"Startup validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''

        try:
            startup_script.write_text(startup_content, encoding="utf-8")
            startup_script.chmod(0o755)  # Make executable on Unix-like systems
            logger.info("✓ Created startup validation script")
        except Exception as e:
            logger.error(f"Failed to create startup script: {e}")
            return False

        # Create .env template if it doesn't exist
        env_template = self.project_root / ".env.template"
        if not env_template.exists():
            env_content = """# Echoes Environment Configuration
# Copy this file to .env and fill in your values

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30

# Application Settings
APP_ENV=development
DEBUG=true

# Optional: Database (if needed)
# DATABASE_URL=sqlite:///./echoes.db

# Optional: Redis (if needed)
# REDIS_URL=redis://localhost:6379

# Optional: External Services
# GITHUB_TOKEN=your_github_token_here
"""
            try:
                env_template.write_text(env_content, encoding="utf-8")
                logger.info("✓ Created .env template")
            except Exception as e:
                logger.error(f"Failed to create .env template: {e}")

        return True

    def validate_environment(self) -> bool:
        """Validate the complete environment setup"""
        logger.info("Validating environment setup...")

        issues = []

        # Check Python version
        if sys.version_info < (3, 12):
            issues.append(f"Python {sys.version_info.major}.{sys.version_info.minor} detected, 3.12+ required")

        # Check virtual environment
        venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            issues.append("Virtual environment not found - run bootstrap.py first")

        # Check core imports
        try:
            from ai_agents.orchestrator import AIAgentOrchestrator
            from prompting.core.context_manager import ContextManager
            from utils.openai_integration import get_openai_integration
            from utils.safe_imports import get_safe_kg_bridge
        except ImportError as e:
            issues.append(f"Import error: {e}")

        # Check configuration
        try:
            from tools.validate_configuration import validate_workspace_config

            if not validate_workspace_config():
                issues.append("Configuration validation failed")
        except ImportError:
            logger.warning("Configuration validation tool not available")

        if issues:
            logger.error("Environment validation failed:")
            for issue in issues:
                logger.error(f"  ✗ {issue}")
            return False
        else:
            logger.info("✓ Environment validation passed")
            return True


def main():
    parser = argparse.ArgumentParser(description="Echoes Profile and Environment Manager")
    parser.add_argument("--backup", action="store_true", help="Create backups before making changes")
    parser.add_argument(
        "--align-profiles",
        action="store_true",
        help="Align user profiles with project settings",
    )
    parser.add_argument("--setup-startup", action="store_true", help="Setup automatic startup scripts")
    parser.add_argument("--validate", action="store_true", help="Validate environment setup")
    parser.add_argument("--all", action="store_true", help="Run all setup steps")

    args = parser.parse_args()

    if not any([args.backup, args.align_profiles, args.setup_startup, args.validate, args.all]):
        args.all = True

    manager = ProfileManager()
    success = True

    try:
        if args.all or args.backup:
            if not manager.backup_existing_settings():
                success = False

        if args.all or args.align_profiles:
            if not manager.align_user_profiles():
                success = False

        if args.all or args.setup_startup:
            if not manager.setup_auto_startup():
                success = False

        if args.all or args.validate:
            if not manager.validate_environment():
                success = False

        if success:
            logger.info("\n" + "=" * 60)
            logger.info("PROFILE SETUP COMPLETE")
            logger.info("=" * 60)
            logger.info("Your Echoes development environment is configured!")
            logger.info("")
            logger.info("Quick start:")
            logger.info("1. Copy .env.template to .env and add your OPENAI_API_KEY")
            logger.info("2. Run: python bootstrap.py")
            logger.info("3. Run: python startup.py")
            logger.info("4. Start developing!")
        else:
            logger.error("\n" + "=" * 60)
            logger.error("PROFILE SETUP FAILED")
            logger.error("=" * 60)

    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
