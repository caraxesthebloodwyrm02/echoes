#!/usr/bin/env python3
"""
Unified Dependency Management Script for Echoes Platform
This script manages dependencies across different package managers (pip, poetry)
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

class DependencyManager:
    """Manages dependencies across the entire project"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.backend_path = self.root_path / "backend"
        self.requirements_path = self.root_path / "requirements.txt"
        
    def check_environment(self) -> Dict[str, Any]:
        """Check the current environment status"""
        status = {
            "python_version": sys.version,
            "pip_version": self._get_pip_version(),
            "poetry_available": self._check_poetry(),
            "virtual_env": sys.prefix != sys.base_prefix,
            "issues": []
        }
        
        if not status["virtual_env"]:
            status["issues"].append("Not in a virtual environment")
            
        if not status["poetry_available"] and self.backend_path.exists():
            status["issues"].append("Poetry not available but backend/ exists")
            
        return status
    
    def _get_pip_version(self) -> str:
        """Get pip version"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True, text=True
            )
            return result.stdout.split()[1] if result.returncode == 0 else "Unknown"
        except Exception:
            return "Not installed"
    
    def _check_poetry(self) -> bool:
        """Check if poetry is available"""
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def update_root_dependencies(self) -> bool:
        """Update root requirements.txt dependencies"""
        print("📦 Updating root dependencies...")
        
        if not self.requirements_path.exists():
            print("❌ requirements.txt not found")
            return False
            
        try:
            # Upgrade pip first
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True
            )
            
            # Install/upgrade requirements
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_path), "--upgrade"],
                check=True
            )
            
            print("✅ Root dependencies updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update root dependencies: {e}")
            return False
    
    def update_backend_dependencies(self) -> bool:
        """Update backend Poetry dependencies"""
        print("📦 Updating backend dependencies...")
        
        if not self.backend_path.exists():
            print("⚠️  backend/ directory not found, skipping")
            return True
            
        if not self._check_poetry():
            print("⚠️  Poetry not available, attempting to install...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "poetry"],
                    check=True
                )
            except subprocess.CalledProcessError:
                print("❌ Failed to install Poetry")
                return False
        
        try:
            # Try to update Poetry dependencies
            subprocess.run(
                ["poetry", "update"],
                cwd=self.backend_path,
                check=True
            )
            print("✅ Backend dependencies updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Poetry update failed, trying to fix environment...")
            
            # Try to fix Poetry environment
            try:
                # Use current Python for Poetry
                subprocess.run(
                    ["poetry", "env", "use", sys.executable],
                    cwd=self.backend_path,
                    check=True
                )
                
                # Retry update
                subprocess.run(
                    ["poetry", "update"],
                    cwd=self.backend_path,
                    check=True
                )
                print("✅ Backend dependencies updated after environment fix")
                return True
                
            except subprocess.CalledProcessError:
                print("❌ Failed to update backend dependencies")
                return False
    
    def generate_lock_file(self) -> bool:
        """Generate requirements-lock.txt with exact versions"""
        print("🔒 Generating lock file...")
        
        lock_path = self.root_path / "requirements-lock.txt"
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True, text=True, check=True
            )
            
            with open(lock_path, "w") as f:
                f.write(f"# Generated lock file - {Path(__file__).name}\n")
                f.write(f"# Python {sys.version}\n\n")
                f.write(result.stdout)
            
            print(f"✅ Lock file generated: {lock_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate lock file: {e}")
            return False
    
    def audit_security(self) -> bool:
        """Run security audit on dependencies"""
        print("🔍 Running security audit...")
        
        try:
            # Ensure pip-audit is installed
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pip-audit"],
                capture_output=True, check=True
            )
            
            # Run audit
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "-r", str(self.requirements_path)],
                capture_output=True, text=True
            )
            
            print(result.stdout)
            
            if "No known vulnerabilities" in result.stdout:
                print("✅ No security vulnerabilities found")
                return True
            else:
                print("⚠️  Security vulnerabilities detected - review above")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Security audit failed: {e}")
            return False
    
    def add_missing_dependencies(self) -> bool:
        """Add commonly missing dependencies to requirements.txt"""
        print("➕ Adding missing dependencies...")
        
        missing_deps = [
            "pre-commit>=4.3.0",
            "pip-audit>=2.9.0",
            "pipdeptree>=2.29.0",
        ]
        
        if not self.requirements_path.exists():
            print("❌ requirements.txt not found")
            return False
        
        with open(self.requirements_path, "r") as f:
            current_deps = f.read()
        
        deps_to_add = []
        for dep in missing_deps:
            dep_name = dep.split(">=")[0].split("==")[0]
            if dep_name not in current_deps:
                deps_to_add.append(dep)
        
        if deps_to_add:
            with open(self.requirements_path, "a") as f:
                f.write("\n# Additional dependencies\n")
                for dep in deps_to_add:
                    f.write(f"{dep}\n")
                    print(f"  Added: {dep}")
            print("✅ Missing dependencies added")
        else:
            print("✅ No missing dependencies to add")
        
        return True
    
    def run_all(self):
        """Run all dependency management tasks"""
        print("=" * 60)
        print("🚀 Echoes Platform Dependency Manager")
        print("=" * 60)
        
        # Check environment
        print("\n📊 Environment Status:")
        status = self.check_environment()
        print(f"  Python: {status['python_version'].split()[0]}")
        print(f"  Pip: {status['pip_version']}")
        print(f"  Poetry: {'Available' if status['poetry_available'] else 'Not available'}")
        print(f"  Virtual Env: {'Active' if status['virtual_env'] else 'Not active'}")
        
        if status["issues"]:
            print("\n⚠️  Issues detected:")
            for issue in status["issues"]:
                print(f"  - {issue}")
        
        print("\n" + "=" * 60)
        
        # Run updates
        tasks = [
            ("Add missing dependencies", self.add_missing_dependencies),
            ("Update root dependencies", self.update_root_dependencies),
            ("Update backend dependencies", self.update_backend_dependencies),
            ("Generate lock file", self.generate_lock_file),
            ("Security audit", self.audit_security),
        ]
        
        results = []
        for task_name, task_func in tasks:
            print(f"\n▶️  {task_name}")
            success = task_func()
            results.append((task_name, success))
            print()
        
        # Summary
        print("=" * 60)
        print("📋 Summary:")
        for task_name, success in results:
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {task_name}")
        
        all_success = all(success for _, success in results)
        if all_success:
            print("\n🎉 All tasks completed successfully!")
        else:
            print("\n⚠️  Some tasks failed. Please review the output above.")
        
        return all_success


if __name__ == "__main__":
    manager = DependencyManager()
    success = manager.run_all()
    sys.exit(0 if success else 1)
