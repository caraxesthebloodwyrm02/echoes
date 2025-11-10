"""
Edge case Glimpse tests for GlimpseEngine
Tests boundary values, null inputs, invalid types, and performance limits
"""
import asyncio
import time

from glimpse.Glimpse import Draft, GlimpseEngine, LatencyMonitor, PrivacyGuard


def test_boundary_values():
    """Test values at the boundaries of acceptable input ranges"""

    async def run():
        # Create fresh Glimpse for each test
        engine = GlimpseEngine()

        # Test empty string
        r1 = await engine.glimpse(Draft(input_text="", goal="test", constraints=""))
        assert r1.status in ["aligned", "not_aligned"]

        # Create fresh Glimpse for long input test
        engine2 = GlimpseEngine()
        long_text = "x" * 10000
        r2 = await engine2.glimpse(
            Draft(input_text=long_text, goal="test", constraints="")
        )
        assert r2.status in ["aligned", "not_aligned"]

        # Create fresh Glimpse for single character test
        engine3 = GlimpseEngine()
        r3 = await engine3.glimpse(Draft(input_text="a", goal="test", constraints=""))
        assert r3.status in ["aligned", "not_aligned"]

        # Test maximum attempt boundary
        engine4 = GlimpseEngine()
        for i in range(2):
            await engine4.glimpse(Draft(input_text="test", goal="test", constraints=""))
        r4 = await engine4.glimpse(
            Draft(input_text="test", goal="test", constraints="")
        )
        assert r4.status == "redial"

    asyncio.run(run())


def test_null_and_invalid_inputs():
    """Test behavior with null/undefined inputs and invalid types"""

    async def run():
        # Test with None values (should be handled gracefully)
        engine1 = GlimpseEngine()
        try:
            r1 = await engine1.glimpse(
                Draft(input_text=None, goal="test", constraints="")
            )
            # If it doesn't raise an error, ensure reasonable behavior
            assert r1.status in ["not_aligned", "aligned"]
        except (TypeError, AttributeError):
            # Expected behavior for None inputs
            pass

        # Test with numeric input (invalid type)
        engine2 = GlimpseEngine()
        try:
            r2 = await engine2.glimpse(
                Draft(input_text=123, goal="test", constraints="")
            )
            # Should handle type conversion gracefully
            assert r2.status in ["not_aligned", "aligned"]
        except (TypeError, AttributeError):
            # Expected behavior for invalid types
            pass

        # Test with special characters
        engine3 = GlimpseEngine()
        r3 = await engine3.glimpse(
            Draft(input_text="!@#$%^&*()", goal="test", constraints="")
        )
        assert r3.status in ["aligned", "not_aligned"]

        # Test with unicode characters
        engine4 = GlimpseEngine()
        r4 = await engine4.glimpse(
            Draft(input_text="测试中文", goal="test", constraints="")
        )
        assert r4.status in ["aligned", "not_aligned"]

    asyncio.run(run())


def test_performance_limits():
    """Test with large datasets and performance constraints"""

    async def run():
        # Test with very large constraints
        large_constraints = " ".join(["constraint"] * 1000)
        engine = GlimpseEngine()

        start_time = time.time()
        r = await Glimpse.glimpse(
            Draft(
                input_text="test input", goal="test goal", constraints=large_constraints
            )
        )
        elapsed = time.time() - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed < 5.0, f"Too slow: {elapsed}s"
        assert r.status in ["aligned", "not_aligned"]

    asyncio.run(run())


def test_concurrent_access():
    """Test concurrent glimpse requests"""

    async def run():
        # Create multiple engines for concurrent testing
        engines = [GlimpseEngine() for _ in range(10)]

        async def make_glimpse(Glimpse, text):
            return await engine.glimpse(
                Draft(input_text=text, goal="test", constraints="")
            )

        # Create multiple concurrent requests with different engines
        tasks = [make_glimpse(engines[i], f"test message {i}") for i in range(10)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete without errors
        for result in results:
            if isinstance(result, Exception):
                assert False, f"Concurrent request failed: {result}"
            else:
                assert result.status in ["aligned", "not_aligned"]

    asyncio.run(run())


def test_latency_monitor_edge_cases():
    """Test latency monitor with various timing scenarios"""
    monitor = LatencyMonitor()

    # Test immediate start/stop
    monitor.start()
    elapsed = monitor.elapsed_ms()
    assert elapsed >= 0

    # Test multiple starts without stops
    monitor.start()
    monitor.start()
    elapsed2 = monitor.elapsed_ms()
    assert elapsed2 >= 0

    # Test status generation for edge time values
    status_0ms = monitor.statuses_for_elapsed(1)
    assert isinstance(status_0ms, list)

    status_very_long = monitor.statuses_for_elapsed(1)
    # Simulate long elapsed time by directly checking the logic
    monitor.t1 = 0  # Force status generation
    status_very_long = monitor.statuses_for_elapsed(1)
    assert isinstance(status_very_long, list)


def test_privacy_guard_edge_cases():
    """Test privacy guard with various commit scenarios"""

    async def run():
        commit_called = []

        def test_commit(draft):
            commit_called.append(draft)

        guard = PrivacyGuard(on_commit=test_commit)

        # Test with empty draft
        empty_draft = Draft(input_text="", goal="", constraints="")
        guard.commit(empty_draft)
        assert len(commit_called) == 1

        # Test with very large draft
        large_draft = Draft(
            input_text="x" * 10000, goal="y" * 1000, constraints="z" * 1000
        )
        guard.commit(large_draft)
        assert len(commit_called) == 2

        # Test commit with None (should handle gracefully)
        try:
            guard.commit(None)
        except (AttributeError, TypeError):
            # Expected for None input
            pass

    asyncio.run(run())


def test_essence_only_mode_edge_cases():
    """Test essence-only mode with various scenarios"""

    async def run():
        # Test toggling essence-only multiple times
        engine1 = GlimpseEngine()
        engine1.set_essence_only(True)
        assert engine1._essence_only == True

        engine1.set_essence_only(False)
        assert engine1._essence_only == False

        engine1.set_essence_only(True)
        assert engine1._essence_only == True

        # Test glimpse with essence-only on
        engine2 = GlimpseEngine()
        engine2.set_essence_only(True)
        r1 = await engine2.glimpse(
            Draft(input_text="test", goal="test", constraints="")
        )
        assert r1.sample == ""
        assert r1.essence != ""

        # Test glimpse with essence-only off
        engine3 = GlimpseEngine()
        r2 = await engine3.glimpse(
            Draft(input_text="test", goal="test", constraints="")
        )
        assert r2.sample != ""
        assert r2.essence != ""

    asyncio.run(run())


def test_cancel_behavior_edge_cases():
    """Test cancel behavior in various scenarios"""

    async def run():
        engine = GlimpseEngine()

        # Test cancel without active glimpse
        Glimpse.cancel()

        # Test cancel multiple times
        Glimpse.cancel()
        Glimpse.cancel()

        # Test cancel during slow operation
        async def slow_sampler(draft):
            await asyncio.sleep(0.1)
            return ("sample", "essence", None, True)

        slow_engine = GlimpseEngine(sampler=slow_sampler)

        task = asyncio.create_task(
            slow_engine.glimpse(Draft(input_text="test", goal="test", constraints=""))
        )

        # Cancel quickly
        await asyncio.sleep(0.01)
        slow_engine.cancel()

        result = await task
        assert result.status == "not_aligned"

    asyncio.run(run())


def test_status_history_edge_cases():
    """Test status history generation and management"""

    async def run():
        engine = GlimpseEngine()

        # Test normal operation
        r1 = await engine.glimpse(Draft(input_text="test", goal="test", constraints=""))
        assert isinstance(r1.status_history, list)
        assert len(r1.status_history) > 0

        # Test with stale result
        async def very_slow_sampler(draft):
            await asyncio.sleep(3)
            return ("sample", "essence", None, True)

        slow_engine = GlimpseEngine(sampler=very_slow_sampler)
        r2 = await slow_engine.glimpse(
            Draft(input_text="test", goal="test", constraints="")
        )

        assert isinstance(r2.status_history, list)
        assert any("trying" in s.lower() for s in r2.status_history)
        assert r2.stale == True

    asyncio.run(run())


if __name__ == "__main__":
    # Run all edge case tests
    test_boundary_values()
    test_null_and_invalid_inputs()
    test_performance_limits()
    test_concurrent_access()
    test_latency_monitor_edge_cases()
    test_privacy_guard_edge_cases()
    test_essence_only_mode_edge_cases()
    test_cancel_behavior_edge_cases()
    test_status_history_edge_cases()
    print("✓ All edge case tests passed")
