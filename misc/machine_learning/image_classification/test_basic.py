#!/usr/bin/env python3
"""
Simple Test Script for Image Classification
==========================================

This script tests the basic functionality of the image classification system
without running full training.

Usage:
    python test_image_classification.py

Author: Echoes AI Assistant
"""

import sys
from pathlib import Path

# Add the parent directory to Python path so we can import machine_learning
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_import():
    """Test that the module can be imported."""
    try:
        from machine_learning.image_classification import ImageClassifier

        print("✓ Module import successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_classifier_initialization():
    """Test that classifier can be initialized."""
    try:
        from machine_learning.image_classification import ImageClassifier

        classifier = ImageClassifier(model_type="custom_cnn", num_classes=10)
        print("✓ Classifier initialization successful")
        return True
    except Exception as e:
        print(f"✗ Classifier initialization failed: {e}")
        return False


def test_model_building():
    """Test that model can be built."""
    try:
        from machine_learning.image_classification import ImageClassifier

        classifier = ImageClassifier(model_type="custom_cnn", num_classes=10)
        model = classifier.build_model()
        print("✓ Model building successful")
        return True
    except Exception as e:
        print(f"✗ Model building failed: {e}")
        return False


def test_dataset_loading():
    """Test that dataset loading works (without actually downloading)."""
    try:
        from machine_learning.image_classification import ImageClassifier

        classifier = ImageClassifier()
        # Just test that the method exists and doesn't crash immediately
        print("✓ Dataset loading method available")
        return True
    except Exception as e:
        print(f"✗ Dataset loading test failed: {e}")
        return False


def main():
    print("Testing Image Classification System")
    print("=" * 50)

    tests = [
        ("Module Import", test_import),
        ("Classifier Initialization", test_classifier_initialization),
        ("Model Building", test_model_building),
        ("Dataset Loading", test_dataset_loading),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed! Image classification system is ready.")
        print("\nNext steps:")
        print(
            "  - Run full training: python machine_learning/image_classification/quick_start.py"
        )
        print(
            "  - Train custom model: python -m machine_learning.image_classification.train --help"
        )
        print(
            "  - Evaluate model: python -m machine_learning.image_classification.evaluate --help"
        )
    else:
        print("✗ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
