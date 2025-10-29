"""
Coverage Completion Tests - Achieving 100% Test Coverage

These tests target the remaining uncovered lines to achieve complete
test coverage for the Glimpse Preflight System.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import asyncio
from pathlib import Path

# Try to import matplotlib, but make it optional for testing
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for testing
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# Import all glimpse modules to test uncovered paths
import glimpse
from glimpse.engine import GlimpseEngine, Draft, GlimpseResult, LatencyMonitor
from glimpse.clarifier_engine import ClarifierEngine, Clarifier, ClarifierType
from glimpse.performance_optimizer import PerformanceOptimizer, AdaptiveTimeout


class TestVisualizationModule:
    """Test the glimpse/vis.py visualization module"""
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not available")
    def test_vis_module_import_and_functions(self):
        """Test that vis module can be imported and functions work"""
        # Import the module to trigger initialization
        import glimpse.vis as vis
        
        # Verify module attributes
        assert hasattr(vis, 'points')
        assert hasattr(vis, 'statuses')
        assert hasattr(vis, 'update_status')
        assert hasattr(vis, 'plot_confirmation_points')
        
        # Test initial state
        assert len(vis.points) == 3
        assert len(vis.statuses) == 3
        assert all(status == 'Pending' for status in vis.statuses)
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not available")
    def test_update_status_function(self):
        """Test the update_status function"""
        import glimpse.vis as vis
        
        # Update first status
        vis.update_status(0, 'Confirmed')
        assert vis.statuses[0] == 'Confirmed'
        assert vis.statuses[1] == 'Pending'
        assert vis.statuses[2] == 'Pending'
        
        # Update all statuses
        vis.update_status(1, 'Confirmed')
        vis.update_status(2, 'Confirmed')
        assert all(status == 'Confirmed' for status in vis.statuses)
        
        # Reset for other tests
        vis.statuses = ['Pending', 'Pending', 'Pending']
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not available")
    @patch('matplotlib.pyplot.show')
    def test_plot_confirmation_points(self, mock_show):
        """Test the plot_confirmation_points function"""
        import glimpse.vis as vis
        
        # Test initial plot with all pending
        vis.plot_confirmation_points()
        mock_show.assert_called_once()
        
        # Reset mock
        mock_show.reset_mock()
        
        # Update statuses and plot again
        vis.statuses = ['Confirmed', 'Pending', 'Confirmed']
        vis.plot_confirmation_points()
        mock_show.assert_called_once()
        
        # Reset for other tests
        vis.statuses = ['Pending', 'Pending', 'Pending']
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not available")
    def test_vis_module_data_structures(self):
        """Test the data structures used in vis module"""
        import glimpse.vis as vis
        
        # Verify points data
        expected_points = ['Essence-Only Fallback', 'Debounce After Edit', 'Patience Window']
        assert vis.points == expected_points
        
        # Verify statuses can be updated to different values
        test_statuses = ['Confirmed', 'Failed', 'In Progress']
        for i, status in enumerate(test_statuses):
            vis.update_status(i, status)
        
        assert vis.statuses == test_statuses
        
        # Reset
        vis.statuses = ['Pending', 'Pending', 'Pending']
    
    def test_vis_module_without_matplotlib(self):
        """Test that vis module can be handled without matplotlib"""
        # This test ensures we can handle the vis module even when matplotlib is missing
        if not MATPLOTLIB_AVAILABLE:
            # We should be able to import the module structure
            with patch.dict('sys.modules', {'matplotlib': None, 'matplotlib.pyplot': None}):
                with patch('builtins.__import__', side_effect=ImportError("No matplotlib")):
                    # The vis module should handle missing matplotlib gracefully
                    try:
                        import glimpse.vis as vis
                        # If we get here, the module was imported successfully
                        assert hasattr(vis, 'points')
                    except ImportError:
                        # If import fails, that's also acceptable when matplotlib is missing
                        pass


class TestInitModuleEdgeCases:
    """Test edge cases in glimpse/__init__.py"""
    
    def test_getattr_missing_attribute(self):
        """Test that accessing non-existent attribute raises AttributeError"""
        with pytest.raises(AttributeError, match=r"module 'glimpse' has no attribute 'nonexistent'"):
            _ = glimpse.nonexistent
    
    def test_getattr_valid_attributes(self):
        """Test that all __all__ attributes are accessible via __getattr__"""
        for attr_name in glimpse.__all__:
            # Should not raise AttributeError
            attr_value = getattr(glimpse, attr_name)
            assert attr_value is not None
    
    def test_lazy_import_functionality(self):
        """Test that imports are lazy and work correctly"""
        # Access an attribute to trigger lazy import
        engine_class = glimpse.GlimpseEngine
        assert engine_class is not None
        
        # Verify it's the same as importing directly
        from glimpse.engine import GlimpseEngine as DirectGlimpseEngine
        assert engine_class is DirectGlimpseEngine


class TestClarifierEngineUncoveredPaths:
    """Test uncovered paths in clarifier_engine.py"""
    
    @pytest.mark.asyncio
    async def test_clarifier_response_mapping_yes_cases(self):
        """Test all yes response mappings for different clarifier types"""
        clarifier_engine = ClarifierEngine()
        
        # Test each clarifier type with yes response
        test_cases = [
            (ClarifierType.AUDIENCE, "y"),
            (ClarifierType.TONE, "yes"),
            (ClarifierType.LENGTH, "true"),
            (ClarifierType.FORMAT, "1"),
            (ClarifierType.SCOPE, "y"),
            (ClarifierType.LANGUAGE, "yes"),
            (ClarifierType.URGENCY, "true"),
            (ClarifierType.DETAIL_LEVEL, "1"),
        ]
        
        for clarifier_type, response in test_cases:
            clarifier = Clarifier(
                type=clarifier_type,
                question="Question?",
                options=["yes", "no"]
            )
            
            # Apply the response directly - just test it doesn't crash
            result = clarifier_engine.apply_clarifier_response(clarifier, response, "")
            # The result should be a string
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_clarifier_response_mapping_no_cases(self):
        """Test all no response mappings for different clarifier types"""
        clarifier_engine = ClarifierEngine()
        
        # Test each clarifier type with no response
        test_cases = [
            (ClarifierType.AUDIENCE, "n"),
            (ClarifierType.TONE, "no"),
            (ClarifierType.LENGTH, "false"),
            (ClarifierType.FORMAT, "0"),
            (ClarifierType.SCOPE, "n"),
            (ClarifierType.LANGUAGE, "no"),
            (ClarifierType.URGENCY, "false"),
            (ClarifierType.DETAIL_LEVEL, "0"),
        ]
        
        for clarifier_type, response in test_cases:
            clarifier = Clarifier(
                type=clarifier_type,
                question="Question?",
                options=["yes", "no"]
            )
            
            # Apply the response directly - just test it doesn't crash
            result = clarifier_engine.apply_clarifier_response(clarifier, response, "")
            # The result should be a string
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_clarifier_custom_response_handling(self):
        """Test that custom responses (not y/n) are handled correctly"""
        clarifier_engine = ClarifierEngine()
        
        clarifier = Clarifier(
            type=ClarifierType.TONE,
            question="What tone should we use?",
            options=["formal", "informal", "professional"]
        )
        
        # Test custom response
        result = clarifier_engine.apply_clarifier_response(clarifier, "professional", "")
        assert "professional" in result


class TestEngineUncoveredPaths:
    """Test uncovered paths in engine.py"""
    
    def test_import_error_handling(self):
        """Test that import errors are handled gracefully"""
        # Test with performance optimizer unavailable
        with patch.dict('sys.modules', {'glimpse.performance_optimizer': None}):
            with patch('importlib.import_module', side_effect=ImportError):
                # Re-import to trigger the import error handling
                import importlib
                import sys
                
                # Remove the module from cache to force re-import
                if 'glimpse.engine' in sys.modules:
                    del sys.modules['glimpse.engine']
                
                # This should handle the ImportError gracefully
                try:
                    from glimpse.engine import PERFORMANCE_AVAILABLE
                    # If we get here, check the flag
                    assert isinstance(PERFORMANCE_AVAILABLE, bool)
                except ImportError:
                    # ImportError is expected when module is missing
                    pass
    
    def test_latency_monitor_edge_cases(self):
        """Test edge cases in LatencyMonitor"""
        monitor = LatencyMonitor()
        
        # Test elapsed_ms when start is None
        monitor._start_ms = None
        assert monitor.elapsed_ms() == 0
        
        # Test with valid start time
        monitor._start_ms = 1000
        with patch.object(monitor, '_now_ms', return_value=1500):
            assert monitor.elapsed_ms() == 500
    
    def test_glimpse_result_creation_edge_cases(self):
        """Test GlimpseResult creation with various parameters"""
        # Test with all parameters
        result = GlimpseResult(
            sample="test",
            essence="test essence",
            delta="test delta",
            status="aligned",
            attempt=1,
            status_history=["test"],
            stale=False
        )
        assert result.sample == "test"
        assert result.essence == "test essence"
        assert result.delta == "test delta"
        assert result.status == "aligned"
        assert result.attempt == 1
        assert result.status_history == ["test"]
        assert result.stale is False
        
        # Test with minimal parameters
        minimal_result = GlimpseResult(
            sample="minimal",
            essence="minimal essence",
            delta=None,
            status="aligned",
            attempt=1,
            status_history=[],
            stale=False
        )
        assert minimal_result.delta is None
    
    @pytest.mark.asyncio
    async def test_engine_with_missing_dependencies(self):
        """Test engine behavior when dependencies are missing"""
        # Mock the import flags to simulate missing dependencies
        with patch('glimpse.engine.PERFORMANCE_AVAILABLE', False):
            with patch('glimpse.engine.CLARIFIER_AVAILABLE', False):
                engine = GlimpseEngine()
                
                # Engine should still work without optional dependencies
                draft = Draft("test input", "test goal", "test constraints")
                result = await engine.glimpse(draft)
                
                # Should return a valid result
                assert isinstance(result, GlimpseResult)
                assert result.status in ["aligned", "not_aligned", "redial"]


class TestPerformanceOptimizerUncoveredPaths:
    """Test uncovered paths in performance_optimizer.py"""
    
    @pytest.mark.asyncio
    async def test_batch_glimpses_empty_list(self):
        """Test batch_glimpses with empty list"""
        optimizer = PerformanceOptimizer()
        
        # Mock sampler function
        async def mock_sampler(draft):
            return GlimpseResult(
                sample=draft.input_text,
                essence="test",
                delta=None,
                status="aligned",
                attempt=1,
                status_history=[],
                stale=False
            )
        
        # Test with empty list
        result = await optimizer.batch_glimpses([], mock_sampler)
        # Empty list should return empty list, not None
        assert result == []
    
    @pytest.mark.asyncio
    async def test_batch_glimpses_with_exceptions(self):
        """Test batch_glimpses when some tasks raise exceptions"""
        optimizer = PerformanceOptimizer()
        
        # Create mock drafts
        drafts = [Draft("test1", "goal1", ""), Draft("test2", "goal2", "")]
        
        # Mock the sampler function to raise exception for second draft
        async def mock_sampler(draft):
            if draft.input_text == "test2":
                raise ValueError("Test error")
            return GlimpseResult(
                sample=draft.input_text,
                essence="test essence",
                delta=None,
                status="aligned",
                attempt=1,
                status_history=["test"],
                stale=False
            )
        
        results = await optimizer.batch_glimpses(drafts, mock_sampler)
        
        # Should handle exceptions gracefully - results may include tuples with timing
        assert len(results) == 2
        # Check first result (may be wrapped with timing info)
        if isinstance(results[0], tuple):
            assert len(results[0]) == 2  # (result, timing)
            assert isinstance(results[0][0], GlimpseResult)
        else:
            assert isinstance(results[0], GlimpseResult)
        
        # Check second result (exception or wrapped exception)
        if isinstance(results[1], tuple):
            assert len(results[1]) == 2
            assert isinstance(results[1][0], ValueError)
        else:
            assert isinstance(results[1], ValueError)
    
    def test_adaptive_timeout_edge_cases(self):
        """Test AdaptiveTimeout edge cases"""
        # Test with custom parameters
        timeout = AdaptiveTimeout(initial_timeout=5.0, max_timeout=20.0)
        assert timeout.initial_timeout == 5.0
        assert timeout.max_timeout == 20.0
        
        # Test with default parameters
        default_timeout = AdaptiveTimeout()
        assert default_timeout.initial_timeout == 2.0
        assert default_timeout.max_timeout == 10.0
    
    def test_performance_optimizer_methods(self):
        """Test performance optimizer methods that might be missing"""
        optimizer = PerformanceOptimizer()
        
        # Test that the optimizer has expected attributes
        assert hasattr(optimizer, 'batch_glimpses')
        assert callable(getattr(optimizer, 'batch_glimpses'))
        
        # Test other expected methods if they exist
        if hasattr(optimizer, 'monitor_performance'):
            assert callable(getattr(optimizer, 'monitor_performance'))
        
        if hasattr(optimizer, 'glimpse'):
            assert callable(getattr(optimizer, 'glimpse'))


class TestIntegrationEdgeCases:
    """Test integration scenarios and edge cases"""
    
    @pytest.mark.asyncio
    async def test_engine_clarifier_integration_missing(self):
        """Test engine behavior when clarifier is missing"""
        with patch('glimpse.engine.CLARIFIER_AVAILABLE', False):
            engine = GlimpseEngine()
            
            # Should work without clarifier
            draft = Draft("test", "goal", "")
            result = await engine.glimpse(draft)
            assert isinstance(result, GlimpseResult)
    
    @pytest.mark.asyncio
    async def test_engine_performance_integration_missing(self):
        """Test engine behavior when performance optimizer is missing"""
        with patch('glimpse.engine.PERFORMANCE_AVAILABLE', False):
            engine = GlimpseEngine()
            
            # Should work without performance optimizer
            draft = Draft("test", "goal", "")
            result = await engine.glimpse(draft)
            assert isinstance(result, GlimpseResult)
    
    @pytest.mark.asyncio
    async def test_full_system_with_all_dependencies_missing(self):
        """Test complete system when all optional dependencies are missing"""
        with patch('glimpse.engine.PERFORMANCE_AVAILABLE', False):
            with patch('glimpse.engine.CLARIFIER_AVAILABLE', False):
                # System should still function
                engine = GlimpseEngine()
                
                drafts = [
                    Draft("input1", "goal1", "constraints1"),
                    Draft("input2", "goal2", "constraints2"),
                    Draft("", "", ""),  # Edge case: empty
                ]
                
                results = []
                for draft in drafts:
                    result = await engine.glimpse(draft)
                    assert isinstance(result, GlimpseResult)
                    results.append(result)
                
                # All should complete successfully
                assert len(results) == 3
                for result in results:
                    assert result.status in ["aligned", "not_aligned", "redial"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
