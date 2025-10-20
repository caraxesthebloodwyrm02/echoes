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
A5 Regression Test Suite
Establishes automated assurance that Phase 1 fixes remain invariant
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.core.context import Context
from prompting.core.loop_controller import LoopController
from prompting.system import PromptingSystem


class TestLoopController:
    """Test loop controller stability"""

    def test_metrics_calculation_no_division_error(self):
        """Verify metrics calculation doesn't cause division by zero"""
        lc = LoopController()

        # Simulate empty loop history (potential division by zero scenario)
        assert lc.loop_history == []

        # This should not raise ZeroDivisionError
        metrics = lc.get_loop_metrics()
        assert "average_iterations" in metrics
        assert isinstance(metrics["average_iterations"], (int, float))

    def test_metrics_with_data(self):
        """Test metrics calculation with actual loop data"""
        lc = LoopController()

        # Add mock loop data
        mock_loop = {
            "loop_id": "test_loop",
            "iterations": [{"quality_score": 0.8}, {"quality_score": 0.9}],
            "converged": True,
        }
        lc.loop_history.append(mock_loop)

        metrics = lc.get_loop_metrics()
        assert metrics["total_loops"] == 1
        assert metrics["successful_loops"] == 1
        assert metrics["average_iterations"] > 0


class TestSystemTiming:
    """Test system timing precision"""

    @pytest.mark.asyncio
    async def test_timing_precision(self):
        """Verify timing uses high-precision counter"""
        system = PromptingSystem()

        result = await system.process_prompt("test", mode="concise", enable_data_loop=False)

        # Check that timing is recorded
        assert "metadata" in result
        assert "processing_time" in result["metadata"]
        assert result["metadata"]["processing_time"] > 0

        # Verify timing is reasonable (should be much less than 1 second for simple prompt)
        assert result["metadata"]["processing_time"] < 1.0

    @pytest.mark.asyncio
    async def test_timing_realistic(self):
        """Ensure timing reflects actual processing, not mock values"""
        system = PromptingSystem()

        result = await system.process_prompt("test timing", mode="concise", enable_data_loop=False)

        # Should not be exactly 0.00 (which would indicate mock timing)
        processing_time = result["metadata"]["processing_time"]
        assert processing_time != 0.00
        assert processing_time != 0


class TestModeHandlers:
    """Test mode handler output integrity"""

    @pytest.mark.asyncio
    async def test_all_modes_produce_output(self):
        """Verify all 5 modes return non-empty responses"""
        system = PromptingSystem()
        modes = ["concise", "ide", "conversational", "star_stuff", "business"]

        for mode in modes:
            result = await system.process_prompt("test mode output", mode=mode, enable_data_loop=False)

            # Check response exists and is non-empty
            assert "response" in result
            assert result["response"] is not None
            assert result["response"].strip() != ""

            # Check mode is correctly identified
            assert result["mode"] == mode

            # Check metadata contains required fields
            assert "metadata" in result
            assert "processing_time" in result["metadata"]

    @pytest.mark.asyncio
    async def test_mode_output_lengths(self):
        """Verify mode outputs have reasonable lengths"""
        system = PromptingSystem()

        # Test concise mode (should be shorter)
        concise_result = await system.process_prompt("test", mode="concise", enable_data_loop=False)
        concise_length = len(concise_result["response"])

        # Test IDE mode (should be longer with structure)
        ide_result = await system.process_prompt("test", mode="ide", enable_data_loop=False)
        ide_length = len(ide_result["response"])

        # Concise should be reasonably short, IDE should have structure
        assert concise_length > 10  # At least some content
        assert ide_length > concise_length  # IDE should be more verbose

    @pytest.mark.asyncio
    async def test_mode_specific_content(self):
        """Verify modes produce mode-specific content markers"""
        system = PromptingSystem()

        # Test concise mode has compression markers
        concise_result = await system.process_prompt("test", mode="concise", enable_data_loop=False)
        assert "compressed" in concise_result["response"].lower() or "synthesis" in concise_result["response"].lower()

        # Test IDE mode has structure markers
        ide_result = await system.process_prompt("test", mode="ide", enable_data_loop=False)
        ide_content = ide_result["response"].lower()
        assert "##" in ide_content or "step" in ide_content


class TestErrorHandling:
    """Test error handling and fallback systems"""

    @pytest.mark.asyncio
    async def test_fallback_activation(self):
        """Verify fallback systems activate safely"""
        system = PromptingSystem()

        # Test with invalid mode (should fallback gracefully)
        result = await system.process_prompt("test", mode="invalid_mode", enable_data_loop=False)

        # Should still produce a response
        assert "response" in result
        assert result["response"].strip() != ""
        # Should fallback to default mode
        assert result["mode"] in [
            "concise",
            "ide",
            "conversational",
            "star_stuff",
            "business",
        ]

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """Test handling of empty or invalid prompts"""
        system = PromptingSystem()

        # Test with empty prompt
        result = await system.process_prompt("", mode="concise", enable_data_loop=False)

        # Should handle gracefully
        assert "response" in result
        assert isinstance(result["response"], str)


class TestAutomationIntegration:
    """Test automation framework integration"""

    @pytest.mark.asyncio
    async def test_context_integration(self):
        """Test Context object integration"""
        system = PromptingSystem()

        context = Context(dry_run=True)
        context.extra_data = {
            "prompt": "automation test",
            "mode": "concise",
            "enable_data_loop": False,
        }

        # Should not raise exceptions
        await system.process_prompt_task(context)

        # Context should remain intact
        assert context.dry_run is True
        assert "prompt" in context.extra_data

    def test_task_creation(self):
        """Test automation task creation"""
        system = PromptingSystem()

        task_config = system.create_automation_task(task_name="test_task", prompt="test prompt", mode="concise")

        assert task_config["name"] == "test_task"
        assert task_config["module"] == "prompting.system"
        assert task_config["function"] == "process_prompt_task"
        assert task_config["params"]["prompt"] == "test prompt"
        assert task_config["params"]["mode"] == "concise"


if __name__ == "__main__":
    # Run basic smoke test if executed directly
    import asyncio

    async def smoke_test():
        print("🧪 Running A5 Regression Test Suite smoke test...")

        # Test basic functionality
        system = PromptingSystem()
        result = await system.process_prompt("smoke test", mode="concise", enable_data_loop=False)

        assert result["response"].strip() != ""
        assert result["mode"] == "concise"
        assert result["metadata"]["processing_time"] > 0

        print("✅ Smoke test passed - basic functionality working")

        # Test loop controller
        lc = LoopController()
        metrics = lc.get_loop_metrics()
        assert isinstance(metrics["average_iterations"], (int, float))
        print("✅ Loop controller test passed")

        print("🎉 A5 Regression Test Suite ready for pytest execution")

    asyncio.run(smoke_test())
