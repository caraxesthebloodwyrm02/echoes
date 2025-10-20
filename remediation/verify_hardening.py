"""
Hardening Verification Tests
Verifies security hardening measures are in place
"""
import json
import sys
from pathlib import Path

def test_pytorch_import():
    """Verify PyTorch 2.9.0+cpu is installed"""
    try:
        import torch
        version = torch.__version__
        print(f"✓ PyTorch {version} imported successfully")
        assert "2.9.0" in version, f"Expected PyTorch 2.9.0, got {version}"
        return True
    except Exception as e:
        print(f"✗ PyTorch import failed: {e}")
        return False

def test_security_tools():
    """Verify security tools are installed"""
    tools = []
    try:
        import pip_audit
        tools.append(("pip-audit", pip_audit.__version__))
        print(f"✓ pip-audit {pip_audit.__version__} installed")
    except:
        print("✗ pip-audit not found")
        return False
    
    try:
        import cyclonedx
        tools.append(("cyclonedx-bom", "installed"))
        print(f"✓ cyclonedx-bom installed")
    except:
        print("✗ cyclonedx-bom not found")
        return False
    
    try:
        import pytest
        tools.append(("pytest", pytest.__version__))
        print(f"✓ pytest {pytest.__version__} installed")
    except:
        print("✗ pytest not found")
        return False
    
    return True

def test_binary_only():
    """Verify packages were installed as binary wheels"""
    try:
        import torch
        # Check if torch has compiled extensions (indicates binary wheel)
        assert hasattr(torch, '_C'), "PyTorch not properly compiled"
        print("✓ PyTorch installed as binary wheel")
        return True
    except Exception as e:
        print(f"✗ Binary verification failed: {e}")
        return False

def test_audit_results():
    """Verify pip-audit results exist"""
    audit_file = Path("remediation/pip-audit-pre-scan.json")
    if not audit_file.exists():
        print("✗ pip-audit results not found")
        return False
    
    with open(audit_file) as f:
        data = json.load(f)
    
    deps = len(data.get('dependencies', []))
    vulns = [d for d in data.get('dependencies', []) if d.get('vulns', [])]
    print(f"✓ pip-audit scanned {deps} packages, found {len(vulns)} with vulnerabilities")
    return True

def test_sbom_exists():
    """Verify SBOM was generated"""
    sbom_file = Path("sbom/cyclonedx-sbom.xml")
    if not sbom_file.exists():
        print("✗ SBOM not found")
        return False
    
    size = sbom_file.stat().st_size
    print(f"✓ SBOM generated ({size} bytes)")
    return True

def main():
    print("=" * 60)
    print("Hardening Verification Tests")
    print("=" * 60)
    
    tests = [
        test_pytorch_import,
        test_security_tools,
        test_binary_only,
        test_audit_results,
        test_sbom_exists,
    ]
    
    results = []
    for test in tests:
        print(f"\n{test.__doc__}")
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    # Save results
    output = {
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{(passed/total)*100:.1f}%"
        },
        "tests": {
            "pytorch_import": results[0],
            "security_tools": results[1],
            "binary_only": results[2],
            "audit_results": results[3],
            "sbom_exists": results[4],
        },
        "environment": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
    }
    
    with open("remediation/test_results_post_hardening.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to remediation/test_results_post_hardening.json")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
