#!/usr/bin/env python
"""Verify Echoes environment setup and configuration."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], capture: bool = True) -> tuple[bool, str, str]:
    """Run a command (list of args, no shell) and return success, stdout, stderr."""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=False, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout or "", result.stderr or ""
        result = subprocess.run(cmd, shell=False, timeout=30)
        return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def check_venv():
    """Check virtual environment state."""
    print("🔍 Checking virtual environment...")

    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ .venv directory not found")
        return False

    print(f"✅ .venv exists at {venv_path.absolute()}")

    # Check pyvenv.cfg
    cfg_path = venv_path / "pyvenv.cfg"
    if cfg_path.exists():
        with open(cfg_path) as f:
            cfg = f.read()
            print("📄 pyvenv.cfg contents:")
            for line in cfg.strip().split("\n"):
                print(f"   {line}")

    # Check Scripts directory
    scripts_path = venv_path / "Scripts"
    if scripts_path.exists():
        print("✅ Scripts directory exists")

        # Check key executables
        for exe in ["python.exe", "pip.exe", "Activate.ps1"]:
            exe_path = scripts_path / exe
            if exe_path.exists():
                print(f"✅ {exe} exists")
            else:
                print(f"❌ {exe} missing")

    return True


def check_python_version():
    """Check Python version compatibility."""
    print("\n🐍 Checking Python version...")

    success, output, _ = run_command([sys.executable, "--version"])
    if success:
        version = output.strip()
        print(f"System Python: {version}")

        # Parse version
        major, minor = version.split()[-1].split(".")[:2]
        major, minor = int(major), int(minor)

        if major >= 3 and minor >= 12:
            print("✅ Python version meets requirements (>=3.12)")
            return True
        else:
            print("❌ Python version too old (<3.12)")
            return False
    else:
        print("❌ Failed to get Python version")
        return False


def _venv_python() -> Path | None:
    """Return path to venv Python (Windows or Unix)."""
    for subpath in [Path("Scripts", "python.exe"), Path("bin", "python")]:
        p = Path(".venv") / subpath
        if p.exists():
            return p
    return None


def check_venv_python():
    """Check venv Python version."""
    print("\n🐍 Checking venv Python version...")

    venv_py = _venv_python()
    if venv_py is None:
        print("❌ venv Python not found")
        return False

    success, output, _ = run_command([str(venv_py.resolve()), "--version"])
    if success:
        print(f"Venv Python: {output.strip()}")
        return True
    else:
        print("❌ Failed to get venv Python version")
        return False


def check_dependencies():
    """Check key dependencies."""
    print("\n📦 Checking dependencies...")

    venv_py = _venv_python()
    if venv_py is None:
        print("❌ venv Python not found, skipping dependency check")
        return False

    deps = ["pydantic", "pydantic-settings", "fastapi", "openai", "uvicorn"]
    all_ok = True

    for dep in deps:
        mod = dep.replace("-", "_")
        success, _, _ = run_command([str(venv_py.resolve()), "-c", f"import {mod}"])
        if success:
            print(f"✅ {dep}")
        else:
            print(f"❌ {dep} missing")
            all_ok = False

    return all_ok


def check_config():
    """Check configuration loading."""
    print("\n⚙️ Checking configuration...")

    venv_py = _venv_python()
    if venv_py is None:
        print("❌ venv Python not found, skipping config check")
        return False

    success, output, error = run_command(
        [str(venv_py.resolve()), "test_config_import.py"]
    )
    if success:
        print("✅ Configuration loads successfully")
        print(f"Output: {output.strip()}")
        return True
    else:
        print("❌ Configuration failed to load")
        print(f"Error: {error}")
        return False


def main():
    """Run all checks."""
    print("🔧 Echoes Environment Verification")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_venv),
        ("Venv Python", check_venv_python),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("📊 Summary:")

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Environment is ready.")
        return 0
    else:
        print("⚠️ Some checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
