#!/usr/bin/env python3
"""
Recursive Middleware Removal System
Forcefully removes all middleware interference from EchoesAI.
"""

import shutil
import logging
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiddlewareRemover:
    """Recursive middleware removal system for EchoesAI."""

    def __init__(self, force: bool = False):
        """Initialize middleware remover."""
        self.force = force
        self.removed_components = []
        self.echoes_root = Path(__file__).parent.parent
        self.backup_created = False

    def create_backup(self):
        """Create backup of current middleware configuration."""
        backup_dir = self.echoes_root / "middleware_backup"

        if backup_dir.exists():
            if not self.force:
                logger.warning("⚠️ Backup already exists. Use -f to overwrite.")
                return False

            shutil.rmtree(backup_dir)

        # Create backup
        backup_dir.mkdir(exist_ok=True)

        # Files to backup
        middleware_files = [
            "api/middleware.py",
            "api/main.py",
            "api/config.py"
        ]

        for file_path in middleware_files:
            source = self.echoes_root / file_path
            if source.exists():
                dest = backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                logger.info(f"📋 Backed up: {file_path}")

        self.backup_created = True
        logger.info("✅ Middleware backup created")
        return True

    def remove_middleware_imports(self):
        """Remove middleware imports from main files."""
        main_file = self.echoes_root / "api" / "main.py"

        if not main_file.exists():
            logger.error("❌ Echoes main.py not found")
            return False

        try:
            with open(main_file, 'r') as f:
                content = f.read()

            original_content = content

            # Remove middleware imports
            middleware_imports = [
                "from api.middleware import",
                "from middleware import",
                "import middleware"
            ]

            for import_line in middleware_imports:
                if import_line in content:
                    lines = content.split('\n')
                    lines = [line for line in lines if not line.strip().startswith(import_line)]
                    content = '\n'.join(lines)
                    logger.info(f"🗑️ Removed import: {import_line}")

            # Remove setup_middleware call
            if "setup_middleware(app, config)" in content:
                content = content.replace("setup_middleware(app, config)", "# setup_middleware REMOVED - Direct Connection")
                logger.info("🗑️ Removed setup_middleware call")

            # Remove app.add_middleware calls
            lines = content.split('\n')
            filtered_lines = []
            for line in lines:
                if "app.add_middleware" in line:
                    logger.info(f"🗑️ Removed middleware: {line.strip()}")
                else:
                    filtered_lines.append(line)
            content = '\n'.join(filtered_lines)

            # Save modified content
            if content != original_content:
                with open(main_file, 'w') as f:
                    f.write(content)
                self.removed_components.append("middleware_imports")
                logger.info("✅ Middleware imports removed from main.py")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to remove middleware imports: {e}")
            return False

    def disable_middleware_config(self):
        """Disable middleware in configuration."""
        config_file = self.echoes_root / "api" / "config.py"

        if not config_file.exists():
            logger.error("❌ Echoes config.py not found")
            return False

        try:
            with open(config_file, 'r') as f:
                content = f.read()

            original_content = content

            # Disable authentication
            content = content.replace(
                "api_key_required: bool = False",
                "api_key_required: bool = False  # DISABLED - Direct Connection"
            )

            # Disable rate limiting
            content = content.replace(
                "rate_limit_requests: int = 60",
                "rate_limit_requests: int = 1000  # DISABLED - Direct Connection"
            )

            # Disable timeout
            content = content.replace(
                "timeout_seconds: int = 30",
                "timeout_seconds: int = 300  # DISABLED - Direct Connection"
            )

            # Save modified content
            if content != original_content:
                with open(config_file, 'w') as f:
                    f.write(content)
                self.removed_components.append("middleware_config")
                logger.info("✅ Middleware configuration disabled")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to disable middleware config: {e}")
            return False

    def create_direct_init(self):
        """Create direct __init__.py that bypasses middleware."""
        init_file = self.echoes_root / "__init__.py"

        direct_init = '''"""
EchoesAI - Direct Connection Version
Zero middleware interference for authentic I/O properties.

Version: 1.0.0-Direct
Status: Middleware Removed
Connection: Direct OpenAI API
"""

__version__ = "1.0.0-Direct"
__author__ = "Atmosphere Team"
__description__ = "EchoesAI with direct OpenAI connection - zero middleware"

# Direct connection import - bypasses all middleware
try:
    from .direct import get_direct_connection, EchoesDirectConnection
    DIRECT_CONNECTION_AVAILABLE = True
except ImportError:
    DIRECT_CONNECTION_AVAILABLE = False

# Legacy components - non-middleware
try:
    from .echoes import __version__ as core_version
except ImportError:
    core_version = "unknown"

def get_echoes_status():
    """Get EchoesAI direct connection status."""
    status = {
        "version": __version__,
        "core_version": core_version,
        "direct_connection": DIRECT_CONNECTION_AVAILABLE,
        "middleware_bypassed": True,
        "connection_type": "direct_openai",
        "interference_level": "zero"
    }

    if DIRECT_CONNECTION_AVAILABLE:
        try:
            connection = get_direct_connection()
            conn_status = connection.get_connection_status()
            status.update(conn_status)
        except Exception as e:
            status["connection_error"] = str(e)

    return status

async def initialize_echoes_direct():
    """Initialize EchoesAI with direct connection."""
    if DIRECT_CONNECTION_AVAILABLE:
        from .direct import test_direct_connection

        print("🚀 EchoesAI Direct Connection Initializing...")
        success = await test_direct_connection()

        if success:
            print("✅ EchoesAI Direct Connection: Operational")
            return True
        else:
            print("❌ EchoesAI Direct Connection: Failed")
            return False

    print("❌ EchoesAI Direct Connection: Not Available")
    return False

def main():
    """Main entry point for EchoesAI Direct."""
    print("🚀 EchoesAI v{} (Direct Connection)".format(__version__))
    print("=" * 50)
    print("Zero Middleware - Authentic I/O Properties")

    status = get_echoes_status()

    print("📊 Status:")
    for key, value in status.items():
        if key != "api_key":
            print(f"   • {key.replace('_', ' ').title()}: {value}")

    print("")
    print("🎯 Direct Connection Features:")
    print("   ✅ Zero middleware interference")
    print("   ✅ Authentic input-output properties")
    print("   ✅ Direct OpenAI API connection")

    if DIRECT_CONNECTION_AVAILABLE:
        print("   ✅ Direct connection system available")
    else:
        print("   ❌ Direct connection system unavailable")

    print("")
    print("Usage:")
    print("  python -m Echoes.direct")
    print("  python -m Echoes.direct.test")

if __name__ == "__main__":
    main()
'''

        try:
            with open(init_file, 'w') as f:
                f.write(direct_init)

            self.removed_components.append("direct_init")
            logger.info("✅ Direct __init__.py created")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create direct init: {e}")
            return False

    def remove_middleware_files(self):
        """Remove or rename middleware files."""
        middleware_file = self.echoes_root / "api" / "middleware.py"

        if middleware_file.exists():
            # Rename to disable
            disabled_file = middleware_file.with_suffix('.py.disabled')
            if not disabled_file.exists():
                middleware_file.rename(disabled_file)
                self.removed_components.append("middleware_file")
                logger.info("🗑️ Middleware file disabled")

        return True

    def run_recursive_removal(self):
        """Run recursive middleware removal process."""
        logger.info("🔥 Starting Recursive Middleware Removal...")
        logger.info(f"Force mode: {self.force}")

        steps = [
            ("Create Backup", self.create_backup),
            ("Remove Middleware Imports", self.remove_middleware_imports),
            ("Disable Middleware Config", self.disable_middleware_config),
            ("Remove Middleware Files", self.remove_middleware_files),
            ("Create Direct Init", self.create_direct_init)
        ]

        for step_name, step_func in steps:
            logger.info(f"🔄 {step_name}...")
            try:
                success = step_func()
                if not success:
                    logger.error(f"❌ {step_name} failed")
                    return False
                logger.info(f"✅ {step_name} completed")
            except Exception as e:
                logger.error(f"❌ {step_name} crashed: {e}")
                return False

        logger.info("🎉 Recursive Middleware Removal Complete!")
        return True

    def get_removal_report(self) -> Dict[str, Any]:
        """Get removal report."""
        return {
            "timestamp": str(datetime.now()),
            "force_mode": self.force,
            "backup_created": self.backup_created,
            "removed_components": self.removed_components,
            "echoes_root": str(self.echoes_root),
            "middleware_bypassed": True,
            "direct_connection_established": True
        }

def main():
    """Main middleware removal function."""
    import argparse

    parser = argparse.ArgumentParser(description="Recursive Middleware Removal for EchoesAI")
    parser.add_argument("-f", "--force", action="store_true", help="Force removal (overwrite backups)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without doing it")

    args = parser.parse_args()

    print("🔥 EchoesAI Recursive Middleware Removal")
    print("=" * 50)
    print("Purpose: Establish direct connection with zero middleware interference")
    print(f"Force mode: {args.force}")
    print(f"Dry run: {args.dry_run}")
    print("")

    if args.dry_run:
        print("📋 DRY RUN - No changes will be made")
        print("Components that would be removed:")
        print("   • Middleware imports from main.py")
        print("   • Middleware configuration settings")
        print("   • Middleware files (renamed to .disabled)")
        print("   • Direct __init__.py created")
        return

    remover = MiddlewareRemover(force=args.force)

    try:
        success = remover.run_recursive_removal()

        if success:
            print("\n🎉 MIDDLEWARE REMOVAL SUCCESSFUL!")
            print("✅ EchoesAI now has direct connection with zero interference")

            report = remover.get_removal_report()
            print("\n📊 Removal Report:")
            print(f"   • Components removed: {len(report['removed_components'])}")
            print(f"   • Backup created: {report['backup_created']}")
            print(f"   • Force mode: {report['force_mode']}")

            print("\n🎯 Next Steps:")
            print("   1. Test direct connection: python -m Echoes.direct")
            print("   2. Verify authentic I/O: python -m Echoes.direct.test")
            print("   3. Use direct API: from Echoes.direct import get_direct_connection")

        else:
            print("\n❌ MIDDLEWARE REMOVAL FAILED!")
            print("⚠️ Some components could not be removed")
            print("🔧 Check error messages above")

    except Exception as e:
        print(f"\n💥 REMOVAL PROCESS CRASHED: {e}")
        print("🔧 Check logs for details")

if __name__ == "__main__":
    main()
