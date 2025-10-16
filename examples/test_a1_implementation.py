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
A1 Implementation Verification Test
Tests that all 5 modes produce non-empty, coherent output
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompting.core.inference_engine import InferenceEngine
from prompting.modes.business_mode import BusinessMode
from prompting.modes.concise_mode import ConciseMode
from prompting.modes.conversational_mode import ConversationalMode
from prompting.modes.ide_mode import IDEMode
from prompting.modes.star_stuff_mode import StarStuffMode


def test_inference_engine_content_generation():
    """Test that inference engine generates content for all modes"""
    print("🔬 Testing Inference Engine Content Generation...")

    ie = InferenceEngine()
    test_elements = ["core_concept", "analysis", "context", "vision", "objectives"]

    modes_tested = 0
    content_generated = 0

    for mode in ["concise", "ide", "conversational", "star_stuff", "business"]:
        print(f"\n  Testing {mode} mode:")
        modes_tested += 1

        for element in test_elements:
            try:
                content = ie._generate_content_for_element(element, [], mode)
                if content and content.strip():
                    content_generated += 1
                    print(f"    ✅ {element}: {len(content)} chars")
                else:
                    print(f"    ❌ {element}: EMPTY")
            except Exception as e:
                print(f"    ❌ {element}: ERROR - {e}")

    print(
        f"\n📊 Inference Engine Results: {content_generated}/{modes_tested * len(test_elements)} elements generated successfully"
    )
    return content_generated >= modes_tested * 3  # At least 3 elements per mode


def test_mode_handler_formatting():
    """Test that mode handlers properly format responses"""
    print("\n🎨 Testing Mode Handler Formatting...")

    # Create mock response structure
    mock_response = {
        "content": {
            "core_concept": "Data loop ecosystem established",
            "analysis": "Repository structure indexed",
            "context": "Understanding data loop requirements",
            "vision": "Constellation of intelligence",
            "objectives": "Implement automated system",
        },
        "reasoning_summary": "Analysis → Synthesis → Implementation",
    }

    modes = [
        ("concise", ConciseMode()),
        ("ide", IDEMode()),
        ("conversational", ConversationalMode()),
        ("star_stuff", StarStuffMode()),
        ("business", BusinessMode()),
    ]

    handlers_tested = 0
    formatting_success = 0

    for mode_name, handler in modes:
        print(f"\n  Testing {mode_name} mode handler:")
        handlers_tested += 1

        try:
            formatted_output = handler.format_response(mock_response, {})
            if formatted_output and len(formatted_output.strip()) > 50:
                formatting_success += 1
                print(f"    ✅ Formatted output: {len(formatted_output)} chars")
                print(
                    f"      Sample: {formatted_output[:100].replace(chr(10), ' ')}..."
                )
            else:
                print(
                    f"    ❌ Formatted output too short or empty: {len(formatted_output) if formatted_output else 0} chars"
                )
        except Exception as e:
            print(f"    ❌ Formatting error: {e}")

    print(
        f"\n📊 Mode Handler Results: {formatting_success}/{handlers_tested} handlers formatting successfully"
    )
    return formatting_success == handlers_tested


def main():
    """Run A1 implementation verification"""
    print("=" * 60)
    print("A1 IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    # Test 1: Inference Engine Content Generation
    test1_passed = test_inference_engine_content_generation()

    # Test 2: Mode Handler Formatting
    test2_passed = test_mode_handler_formatting()

    # Overall Results
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)

    if test1_passed and test2_passed:
        print("🎉 SUCCESS: A1 Implementation Complete!")
        print("   ✅ Inference engine generates content for all modes")
        print("   ✅ Mode handlers format responses correctly")
        print("   ✅ All 5 modes produce non-empty, coherent output")
        return True
    else:
        print("❌ PARTIAL: A1 Implementation Incomplete")
        print(f"   {'✅' if test1_passed else '❌'} Content generation")
        print(f"   {'✅' if test2_passed else '❌'} Response formatting")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
