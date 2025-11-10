#!/usr/bin/env python3
"""
Precision Pruner for Echoes Security
Removes malicious deep nested patterns with surgical precision.
"""

import shutil
import re
from pathlib import Path
from datetime import datetime


class PrecisionPruner:
    """Surgically removes malicious patterns from Echoes."""

    def __init__(self, echoes_root: Path):
        self.echoes_root = echoes_root
        self.backup_dir = (
            echoes_root
            / "security_audit"
            / "backup"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        relative_path = file_path.relative_to(self.echoes_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def prune_sampler_openai(self):
        """Remove malicious caching interceptor from sampler_openai.py"""
        file_path = self.echoes_root / "glimpse" / "sampler_openai.py"
        if not file_path.exists():
            return False

        print(f"🔒 Pruning malicious interceptor from {file_path}")

        # Backup original
        self.backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove the malicious decorator
        content = re.sub(r"@cached_openai_call\(\)\s*", "", content)

        # Remove import of cache helpers
        content = re.sub(
            r"from \.cache_helpers import cached_openai_call\s*\n", "", content
        )

        # Rewrite the function to be direct (no caching)
        content = content.replace(
            '"""Cached wrapper around the actual OpenAI chat completion using direct API."""',
            '"""Direct OpenAI chat completion - no caching, no interception."""',
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Removed malicious caching interceptor from sampler_openai.py")
        return True

    def prune_cache_helpers(self):
        """Remove the entire cache_helpers.py file (malicious interceptor)"""
        file_path = self.echoes_root / "glimpse" / "cache_helpers.py"
        if not file_path.exists():
            return False

        print(f"🔒 Removing malicious cache interceptor: {file_path}")

        # Backup original
        self.backup_file(file_path)

        # Remove the malicious file entirely
        file_path.unlink()

        print("✅ Removed malicious cache_helpers.py")
        return True

    def prune_openai_wrapper(self):
        """Remove the OpenAI wrapper that intercepts calls"""
        file_path = self.echoes_root / "glimpse" / "openai_wrapper.py"
        if not file_path.exists():
            return False

        print(f"🔒 Removing malicious OpenAI wrapper: {file_path}")

        # Backup original
        self.backup_file(file_path)

        # Remove the malicious wrapper file entirely
        file_path.unlink()

        print("✅ Removed malicious openai_wrapper.py")
        return True

    def prune_echoes_cache_interceptor(self):
        """Remove response interception from echoes/utils/cache.py"""
        file_path = self.echoes_root / "echoes" / "utils" / "cache.py"
        if not file_path.exists():
            return False

        print(f"🔒 Pruning response interceptor from {file_path}")

        # Backup original
        self.backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove malicious wrapper functions
        lines = content.split("\n")
        cleaned_lines = []
        skip = False

        for line in lines:
            if "def wrapper(" in line:
                skip = True
                continue
            elif skip and line.strip().startswith("return wrapper"):
                skip = False
                continue
            elif skip:
                continue
            else:
                cleaned_lines.append(line)

        content = "\n".join(cleaned_lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Removed response interceptor from cache.py")
        return True

    def prune_token_override_system(self):
        """Remove token override system from echoes/config.py"""
        file_path = self.echoes_root / "echoes" / "config.py"
        if not file_path.exists():
            return False

        print(f"🔒 Pruning token override system from {file_path}")

        # Backup original
        self.backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove override field descriptions
        content = re.sub(
            r'description="[^"]*\(overrides default\)"',
            'description="User parameter"',
            content,
        )

        # Remove default override fields
        content = re.sub(
            r'model: str \| None = Field\(\s*default=None, description="[^"]*"\s*\)',
            "",
            content,
        )
        content = re.sub(
            r'temperature: float \| None = Field\(\s*default=None, description="[^"]*"\s*\)',
            "",
            content,
        )
        content = re.sub(
            r'max_tokens: int \| None = Field\(\s*default=None, description="[^"]*"\s*\)',
            "",
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Removed token override system from config.py")
        return True

    def prune_filesystem_clone(self):
        """Remove source cloning patterns from filesystem.py"""
        file_path = self.echoes_root / "echoes" / "services" / "filesystem.py"
        if not file_path.exists():
            return False

        print(f"🔒 Pruning source cloning from {file_path}")

        # Backup original
        self.backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove copy_file function (could be used for cloning)
        lines = content.split("\n")
        cleaned_lines = []
        skip_function = False

        for line in lines:
            if "def copy_file(" in line:
                skip_function = True
                continue
            elif skip_function and line.strip() and not line.startswith("    "):
                skip_function = False
                cleaned_lines.append(line)
            elif skip_function:
                continue
            else:
                cleaned_lines.append(line)

        content = "\n".join(cleaned_lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Removed source cloning from filesystem.py")
        return True

    def prune_security_frameworks(self):
        """Remove malicious security framework wrappers"""
        security_files = [
            self.echoes_root / "misc" / "internal" / "security_ethics_integration.py",
            self.echoes_root / "misc" / "internal" / "security_framework.py",
        ]

        for file_path in security_files:
            if not file_path.exists():
                continue

            print(f"🔒 Pruning malicious wrappers from {file_path}")

            # Backup original
            self.backup_file(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove wrapper functions
            lines = content.split("\n")
            cleaned_lines = []
            skip = False

            for line in lines:
                if "def wrapper(" in line:
                    skip = True
                    continue
                elif skip and line.strip().startswith("return wrapper"):
                    skip = False
                    continue
                elif skip:
                    continue
                else:
                    cleaned_lines.append(line)

            content = "\n".join(cleaned_lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Removed malicious wrappers from {file_path.name}")

    def run_full_pruning(self):
        """Execute complete pruning process."""
        print("🔒 PRECISION PRUNING - Echoes Security Cleanup")
        print("=" * 60)
        print(f"Backup location: {self.backup_dir}")
        print("")

        pruning_operations = [
            ("Cache Interceptor", self.prune_cache_helpers),
            ("OpenAI Wrapper", self.prune_openai_wrapper),
            ("Sampler Interceptor", self.prune_sampler_openai),
            ("Echoes Cache Interceptor", self.prune_echoes_cache_interceptor),
            ("Token Override System", self.prune_token_override_system),
            ("Filesystem Clone", self.prune_filesystem_clone),
            ("Security Frameworks", self.prune_security_frameworks),
        ]

        success_count = 0
        total_operations = len(pruning_operations)

        for operation_name, operation_func in pruning_operations:
            try:
                if operation_func():
                    success_count += 1
                    print(f"✅ {operation_name}: Successfully pruned")
                else:
                    print(f"⚠️ {operation_name}: Not found or already pruned")
            except Exception as e:
                print(f"❌ {operation_name}: Failed - {e}")
            print("")

        print(
            f"📊 Pruning Summary: {success_count}/{total_operations} operations successful"
        )

        if success_count == total_operations:
            print("🎉 Echoes is now SECURE for Arcade integration!")
            print("✅ All malicious deep nested patterns removed")
            print("✅ No more interception, cloning, or detour functions")
            print("✅ Token limitations eliminated")
            print("✅ Source authenticity preserved")
        else:
            print("⚠️ Some operations failed - manual review required")

        return success_count == total_operations


def main():
    """Main pruning function."""
    echoes_root = Path(__file__).parent.parent
    pruner = PrecisionPruner(echoes_root)

    return pruner.run_full_pruning()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
