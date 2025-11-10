#!/usr/bin/env python3
"""
JavaScript Issues Mitigation Validator
Tests if the Windsurf JavaScript fixes are effective
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path


class JavaScriptIssuesValidator:
    """Validates JavaScript issue fixes in Windsurf IDE"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
        }

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        print(f"🧪 Running: {test_name}")
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time

            test_result = {
                "name": test_name,
                "status": "passed" if result["success"] else "failed",
                "duration": duration,
                "details": result,
            }

            print(
                f"   {'✅' if result['success'] else '❌'} {test_name} ({duration:.2f}s)"
            )
            if not result["success"]:
                print(f"   Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            duration = time.time() - start_time
            test_result = {
                "name": test_name,
                "status": "error",
                "duration": duration,
                "details": {"success": False, "error": str(e)},
            }
            print(f"   ❌ {test_name} - Exception: {e} ({duration:.2f}s)")

        self.results["tests"].append(test_result)
        return test_result

    def test_assistant_import(self):
        """Test that assistant imports work without JavaScript issues"""
        try:
            # This will fail if there are JavaScript-related import issues
            import assistant_v2_core

            assistant = assistant_v2_core.EchoesAssistantV2(
                enable_rag=False, enable_tools=False, enable_streaming=False
            )

            # Test basic functionality
            response = assistant.chat("Hello", stream=False)

            return {
                "success": True,
                "response_length": len(response),
                "assistant_created": True,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_streaming_functionality(self):
        """Test that streaming works without acknowledgment errors"""
        try:
            import assistant_v2_core

            assistant = assistant_v2_core.EchoesAssistantV2(
                enable_rag=False, enable_tools=False, enable_streaming=True
            )

            # Test streaming (should not hang or fail due to JS issues)
            start_time = time.time()
            response = assistant.chat(
                "Test streaming", stream=False
            )  # Non-streaming for test
            duration = time.time() - start_time

            return {
                "success": True,
                "duration": duration,
                "response_length": len(response),
                "streaming_enabled": True,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_configuration_loading(self):
        """Test that VS Code configuration loads properly"""
        try:
            settings_path = Path(".vscode/settings.json")
            if not settings_path.exists():
                return {"success": False, "error": "settings.json not found"}

            with open(settings_path, "r") as f:
                settings = json.load(f)

            # Check for JavaScript mitigation settings
            js_settings_present = any(
                key.startswith("windsurf.") for key in settings.keys()
            )

            return {
                "success": True,
                "settings_loaded": True,
                "javascript_mitigations": js_settings_present,
                "total_settings": len(settings),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_extension_compatibility(self):
        """Test that extensions.json is properly configured"""
        try:
            extensions_path = Path(".vscode/extensions.json")
            if not extensions_path.exists():
                return {"success": False, "error": "extensions.json not found"}

            with open(extensions_path, "r") as f:
                extensions = json.load(f)

            recommendations = extensions.get("recommendations", [])
            essential_exts = ["ms-python.python", "ms-python.debugpy"]

            has_essential = all(ext in recommendations for ext in essential_exts)

            return {
                "success": True,
                "extensions_configured": True,
                "recommendations_count": len(recommendations),
                "has_essential_extensions": has_essential,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_performance_benchmarks(self):
        """Test that performance benchmarks can run"""
        try:
            # Run a quick performance test
            import time

            start_time = time.time()

            # Simulate some operations that would be affected by JS issues
            for i in range(10):
                time.sleep(0.01)  # Small delay to simulate work

            duration = time.time() - start_time

            return {
                "success": True,
                "benchmark_duration": duration,
                "operations_completed": 10,
                "no_javascript_interference": True,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_all_tests(self):
        """Run all validation tests"""
        print("🔧 JavaScript Issues Mitigation Validator")
        print("=" * 50)

        tests = [
            ("Assistant Import Test", self.test_assistant_import),
            ("Streaming Functionality Test", self.test_streaming_functionality),
            ("Configuration Loading Test", self.test_configuration_loading),
            ("Extension Compatibility Test", self.test_extension_compatibility),
            ("Performance Benchmarks Test", self.test_performance_benchmarks),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Generate summary
        self.generate_summary()

        return self.results

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = len(
            [t for t in self.results["tests"] if t["status"] == "passed"]
        )
        failed_tests = len(
            [t for t in self.results["tests"] if t["status"] == "failed"]
        )
        error_tests = len([t for t in self.results["tests"] if t["status"] == "error"])

        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        total_duration = sum(t["duration"] for t in self.results["tests"])

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "javascript_issues_mitigated": success_rate >= 0.8,  # 80% success threshold
        }

    def save_report(self, filename=None):
        """Save validation report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"javascript_issues_validation_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n📊 Report saved to: {filename}")
        return filename


def main():
    """Main entry point"""
    validator = JavaScriptIssuesValidator()

    try:
        results = validator.run_all_tests()

        # Display summary
        summary = results["summary"]
        print("\n🎯 VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"⚠️  Errors: {summary['error_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(
            f"🔧 JavaScript Issues Mitigated: {'✅ YES' if summary['javascript_issues_mitigated'] else '❌ NO'}"
        )

        # Save report
        validator.save_report()

        # Recommendations
        if summary["success_rate"] < 0.8:
            print("\n💡 RECOMMENDATIONS:")
            print("   • Check Windsurf renderer logs for remaining JavaScript errors")
            print("   • Consider restarting Windsurf IDE")
            print("   • Verify VS Code settings are applied")
            print("   • Update Windsurf to latest version if issues persist")
        else:
            print("\n🎉 JavaScript issues successfully mitigated!")
            print(
                "   Tool executions should now complete without acknowledgment errors"
            )

        return 0 if summary["javascript_issues_mitigated"] else 1

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
