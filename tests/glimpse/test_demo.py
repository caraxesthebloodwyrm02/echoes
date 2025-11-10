"""
Tests for glimpse demo module
"""

from unittest.mock import MagicMock, patch

import pytest

from glimpse.demo_glimpse_engine import main


class TestDemoGlimpseEngine:
    """Test the demo glimpse Glimpse functions"""

    @patch("builtins.print")
    async def test_main_function(self, mock_print):
        """Test main function"""
        # Should run without error
        await main()

        # Check that print was called with expected values
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Attempt:" in call for call in print_calls)
        assert any("Status:" in call for call in print_calls)
        assert any("History:" in call for call in print_calls)
        assert any("Sample:" in call for call in print_calls)
        assert any("Essence:" in call for call in print_calls)

    @patch("glimpse.demo_glimpse_engine.GlimpseEngine")
    @patch("builtins.print")
    async def test_main_with_mock_engine(self, mock_print, mock_glimpse_class):
        """Test main with mocked Glimpse"""
        # Setup mock Glimpse
        mock_engine = MagicMock()
        mock_glimpse_class.return_value = mock_engine

        # Setup mock glimpse result
        mock_result = MagicMock()
        mock_result.attempt = 1
        mock_result.status = "aligned"
        mock_result.status_history = ["Trying..."]
        mock_result.sample = "Sample output"
        mock_result.essence = "Essence of request"
        mock_result.delta = None

        # Make glimpse async
        async def async_glimpse(*args, **kwargs):
            return mock_result

        mock_engine.glimpse = async_glimpse

        # Run main
        await main()

        # Verify commit was called
        mock_engine.commit.assert_called()

    @patch("glimpse.demo_glimpse_engine.GlimpseEngine")
    @patch("builtins.print")
    async def test_main_with_not_aligned_result(self, mock_print, mock_glimpse_class):
        """Test main when first result is not aligned"""
        # Setup mock Glimpse
        mock_engine = MagicMock()
        mock_glimpse_class.return_value = mock_engine

        # Setup mock glimpse results
        mock_result1 = MagicMock()
        mock_result1.attempt = 1
        mock_result1.status = "not_aligned"
        mock_result1.status_history = ["Trying..."]
        mock_result1.sample = "Sample 1"
        mock_result1.essence = "Essence 1"
        mock_result1.delta = "Needs adjustment"

        mock_result2 = MagicMock()
        mock_result2.attempt = 2
        mock_result2.status = "aligned"
        mock_result2.status_history = ["Trying...", "Aligned"]
        mock_result2.sample = "Sample 2"
        mock_result2.essence = "Essence 2"
        mock_result2.delta = None

        # Make glimpse async with side effect
        call_count = 0

        async def async_glimpse(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_result1 if call_count == 1 else mock_result2

        mock_engine.glimpse = async_glimpse

        # Run main
        await main()

        # Verify commit was called
        mock_engine.commit.assert_called()
        # Verify we had two attempts (call_count tracked in closure)
        assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
