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
Simple AutoML Test - Verify the implementation works
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all AutoML components can be imported."""
    print("Testing AutoML imports...")

    try:
        from packages.automl import AutoMLConfig, SimpleAutoML

        print("✅ SimpleAutoML and AutoMLConfig imported")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    return True


def test_basic_functionality():
    """Test basic AutoML functionality."""
    print("\nTesting basic AutoML functionality...")

    try:
        from sklearn.datasets import make_classification

        from packages.automl import AutoMLConfig, SimpleAutoML

        # Create sample data
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)

        # Test configuration
        config = AutoMLConfig(task_type="classification", max_models=2)
        print("✅ AutoMLConfig created")

        # Test AutoML
        automl = SimpleAutoML(config)
        results = automl.fit(X, y)

        # Verify results
        assert "best_model" in results
        assert "best_score" in results
        assert results["models_evaluated"] > 0
        assert results["task_type"] == "classification"

        print("✅ SimpleAutoML executed successfully")
        print(f"🎯 Best Score: {results['best_score']:.4f}")
        print(f"🏆 Best Model: {results['best_model_name']}")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


if __name__ == "__main__":
    print("🤖 AutoML Implementation Test")
    print("=" * 40)

    success = True

    success &= test_imports()
    success &= test_basic_functionality()

    if success:
        print("\n🎉 All AutoML tests passed!")
        print("🚀 AutoML pipeline is ready for use!")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
        sys.exit(1)
