#!/usr/bin/env python3
"""
Environment Validation Script for Echoes Project
Ensures Python environment is properly configured and all dependencies are installed.
"""

import sys
import os
import subprocess
import importlib.util


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(
            f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.12+"
        )
        return False


def check_virtual_env():
    """Check if running in virtual environment"""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print(f"✅ Virtual environment active: {sys.prefix}")
        return True
    else:
        print("❌ Not running in virtual environment")
        return False


def check_dependencies():
    """Check critical dependencies"""
    critical_deps = [
        "openai",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "pytest",
        "httpx",
        "requests",
        "numpy",
        "pandas",
    ]

    missing = []
    for dep in critical_deps:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            missing.append(dep)

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All critical dependencies installed")
        return True


def check_env_file():
    """Check .env file exists"""
    if os.path.exists(".env"):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found - create from .env.example")
        return False


def check_imports():
    """Test project imports"""
    test_imports = ["app.main", "core.config", "ai_agents.orchestrator"]

    failed = []
    for module in test_imports:
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                raise ImportError(f"No module named '{module}'")
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            failed.append(module)

    if failed:
        print(f"\n❌ Failed imports: {', '.join(failed)}")
        return False
    else:
        print("\n✅ All project imports working")
        return True


def main():
    """Main validation function"""
    print("🔍 Echoes Environment Validation")
    print("=" * 40)

    checks = [
        check_python_version,
        check_virtual_env,
        check_dependencies,
        check_env_file,
        check_imports,
    ]

    results = []
    for check in checks:
        print()
        results.append(check())

    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All checks passed ({passed}/{total})")
        print("Environment is ready for development!")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("Please resolve the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
