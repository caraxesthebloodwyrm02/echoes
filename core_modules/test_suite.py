"""
Comprehensive Test Suite for Glimpse
"""

import unittest
import time
from pathlib import Path
from core_trajectory import TrajectoryEngine
from input_adapter import InputAdapter, InputEventType
from visual_renderer import VisualRenderer, VisualizationMode, PIL_AVAILABLE
from security_integration import SecurityManager
from realtime_preview import GlimpseOrchestrator, GlimpseConfiguration
import urllib.request
import json
import socket


class TestTrajectoryEngine(unittest.TestCase):
    """Test trajectory tracking functionality"""

    def setUp(self):
        self.engine = TrajectoryEngine(window_size=50)

    def test_add_point(self):
        """Test adding trajectory points"""
        point = self.engine.add_point("Hello world")
        self.assertIsNotNone(point)
        self.assertEqual(len(self.engine.points), 1)
        self.assertEqual(point.content, "Hello world")

    def test_direction_analysis(self):
        """Test direction analysis"""
        # Add expanding content
        for i in range(10):
            self.engine.add_point("x" * (i * 10))

        # Should detect expanding
        current = self.engine.current_direction
        self.assertIsNotNone(current)

    def test_confidence_computation(self):
        """Test confidence scoring"""
        # Not enough data
        point = self.engine.add_point("test")
        self.assertLess(point.confidence, 0.5)

        # Add consistent data
        for _ in range(10):
            point = self.engine.add_point("consistent content")

        # Confidence should increase
        self.assertGreater(point.confidence, 0.5)

    def test_cause_effect_chain(self):
        """Test cause-effect chain tracking"""
        self.engine.add_point("First")
        self.engine.add_point("Second")
        point = self.engine.add_point("Third")

        self.assertGreater(len(point.cause_effect_chain), 0)

    def test_predictions(self):
        """Test trajectory predictions"""
        for i in range(10):
            self.engine.add_point(f"Content {i}")

        predictions = self.engine.predict_next_states(lookahead=3)
        self.assertGreater(len(predictions), 0)

    def test_export(self):
        """Test trajectory export"""
        for i in range(5):
            self.engine.add_point(f"Point {i}")

        export_path = Path(__file__).parent / "test_export.json"
        self.engine.export_trajectory(str(export_path))

        self.assertTrue(export_path.exists())
        export_path.unlink()  # Cleanup


class TestInputAdapter(unittest.TestCase):
    """Test input adaptation functionality"""

    def setUp(self):
        self.adapter = InputAdapter(buffer_size=20)

    def test_insert(self):
        """Test text insertion"""
        event = self.adapter.process_insert(0, "Hello")
        self.assertEqual(event.event_type, InputEventType.INSERT)
        self.assertEqual(self.adapter.current_content, "Hello")
        self.assertEqual(event.delta, "Hello")

    def test_delete(self):
        """Test text deletion"""
        self.adapter.process_insert(0, "Hello World")
        event = self.adapter.process_delete(5, 11)  # Delete " World"

        self.assertEqual(event.event_type, InputEventType.DELETE)
        self.assertEqual(self.adapter.current_content, "Hello")
        self.assertEqual(event.delta, " World")

    def test_replace(self):
        """Test text replacement"""
        self.adapter.process_insert(0, "Hello World")
        event = self.adapter.process_replace(6, 11, "Python")

        self.assertEqual(event.event_type, InputEventType.REPLACE)
        self.assertEqual(self.adapter.current_content, "Hello Python")

    def test_undo_redo(self):
        """Test undo/redo functionality"""
        self.adapter.process_insert(0, "First")
        self.adapter.process_insert(5, " Second")

        # Undo
        event = self.adapter.undo()
        self.assertEqual(self.adapter.current_content, "First")

        # Redo
        event = self.adapter.redo()
        self.assertEqual(self.adapter.current_content, "First Second")

    def test_typing_velocity(self):
        """Test typing velocity calculation"""
        self.adapter.process_insert(0, "a")
        time.sleep(0.1)
        self.adapter.process_insert(1, "b")

        velocity = self.adapter.get_typing_velocity()
        self.assertGreater(velocity, 0)

    def test_suggestions(self):
        """Test suggestion generation"""
        self.adapter.process_insert(0, "the ")
        context = self.adapter.get_adaptation_context()

        self.assertIsNotNone(context)
        self.assertIsInstance(context.suggestions, list)


class TestVisualRenderer(unittest.TestCase):
    """Test visual rendering functionality"""

    def setUp(self):
        self.renderer = VisualRenderer(mode=VisualizationMode.TIMELINE)

    def test_render_timeline(self):
        """Test timeline rendering"""
        trajectory_data = {
            "current_direction": "expanding",
            "recent_points": [
                {
                    "content": "test1",
                    "direction": "expanding",
                    "confidence": 0.8,
                    "cause_effect_chain": [],
                    "timestamp": time.time(),
                },
                {
                    "content": "test2",
                    "direction": "expanding",
                    "confidence": 0.9,
                    "cause_effect_chain": [],
                    "timestamp": time.time(),
                },
            ],
        }

        frame = self.renderer.render_timeline(trajectory_data)
        self.assertIsNotNone(frame)
        self.assertGreater(len(frame.elements), 0)

    def test_render_flow(self):
        """Test flow rendering"""
        trajectory_data = {"current_direction": "stable", "confidence": 0.7}

        frame = self.renderer.render_flow(trajectory_data)
        self.assertIsNotNone(frame)
        self.assertGreater(len(frame.elements), 0)

    def test_mode_switching(self):
        """Test visualization mode switching"""
        self.renderer.set_mode(VisualizationMode.TREE)
        self.assertEqual(self.renderer.mode, VisualizationMode.TREE)

    def test_ascii_preview(self):
        """Test ASCII preview generation"""
        trajectory_data = {
            "current_direction": "expanding",
            "recent_points": [
                {
                    "content": "test",
                    "direction": "expanding",
                    "confidence": 0.8,
                    "cause_effect_chain": [],
                    "timestamp": time.time(),
                }
            ],
        }

        frame = self.renderer.render_timeline(trajectory_data)
        ascii_preview = self.renderer.generate_ascii_preview(frame)

        self.assertIsNotNone(ascii_preview)
        self.assertIsInstance(ascii_preview, str)
        self.assertNotIn("\033[", ascii_preview)

    def test_ansi_preview(self):
        """ANSI-colored preview should include escape codes when enabled"""
        trajectory_data = {
            "current_direction": "expanding",
            "recent_points": [
                {
                    "content": "test",
                    "direction": "expanding",
                    "confidence": 0.9,
                    "cause_effect_chain": [],
                    "timestamp": time.time(),
                }
            ],
        }
        frame = self.renderer.render_timeline(trajectory_data)
        ansi_preview = self.renderer.generate_ascii_preview(frame, use_ansi=True, blur=0.0)
        if self.renderer.ansi_enabled:
            self.assertIn("\033[38;2", ansi_preview)
        else:
            self.assertNotIn("\033[", ansi_preview)

    def test_image_preview_optional(self):
        """Image preview returns PIL Image only when Pillow is available"""
        trajectory_data = {
            "current_direction": "expanding",
            "recent_points": [
                {
                    "content": "img",
                    "direction": "expanding",
                    "confidence": 0.8,
                    "cause_effect_chain": [],
                    "timestamp": time.time(),
                }
            ],
        }
        frame = self.renderer.render_timeline(trajectory_data)
        image = self.renderer.generate_image_preview(frame, width=200, height=120)
        if PIL_AVAILABLE:
            from PIL import Image  # type: ignore  # pragma: no cover

            self.assertIsInstance(image, Image.Image)
        else:
            self.assertIsNone(image)

    def test_export_animation(self):
        """Test animation export"""
        # Generate some frames
        for i in range(3):
            data = {
                "current_direction": "stable",
                "recent_points": [
                    {
                        "content": f"test{i}",
                        "direction": "stable",
                        "confidence": 0.5,
                        "cause_effect_chain": [],
                        "timestamp": time.time(),
                    }
                ],
            }
            self.renderer.render_timeline(data)

        export_path = Path(__file__).parent / "test_animation.json"
        self.renderer.export_animation(str(export_path))

        self.assertTrue(export_path.exists())
        export_path.unlink()  # Cleanup


class TestSecurityIntegration(unittest.TestCase):
    """Test security integration"""

    def setUp(self):
        self.security = SecurityManager(base_path=Path(__file__).parent, enable_thon_integration=True)

    def test_security_assessment(self):
        """Test security context assessment"""
        context = self.security.assess_security_context()

        self.assertIsNotNone(context)
        self.assertGreaterEqual(context.shield_factor, 0.0)
        self.assertLessEqual(context.shield_factor, 1.0)
        self.assertIn(context.risk_level, ["low", "medium", "high"])

    def test_operation_validation(self):
        """Test operation validation"""
        self.security.assess_security_context()

        # Read should always be allowed
        self.assertTrue(self.security.validate_operation("read"))

    def test_command_validation(self):
        """Test command validation"""
        # Safe command
        result = self.security.validate_command("echo test")
        self.assertIsNotNone(result)
        self.assertIn("allowed", result)

        # Unsafe command
        result = self.security.validate_command("rm -rf /")
        self.assertFalse(result.get("allowed", True))

    def test_security_metrics(self):
        """Test security metrics retrieval"""
        metrics = self.security.get_security_metrics()

        self.assertIsNotNone(metrics)
        self.assertIn("context", metrics)
        self.assertIn("thon_integrated", metrics)


class TestGlimpseOrchestrator(unittest.TestCase):
    """Test main Glimpse orchestrator"""

    def setUp(self):
        config = GlimpseConfiguration(enable_security=False)  # Disable for faster tests
        self.system = GlimpseOrchestrator(config=config, base_path=Path(__file__).parent)

    def test_start_stop(self):
        """Test system start/stop"""
        self.assertFalse(self.system.state.is_active)

        self.system.start()
        self.assertTrue(self.system.state.is_active)

        self.system.stop()
        self.assertFalse(self.system.state.is_active)

    def test_process_input(self):
        """Test input processing"""
        self.system.start()

        result = self.system.process_input(action="insert", position=0, text="Hello")

        self.assertTrue(result.get("success"))
        self.assertIn("trajectory", result)
        self.assertIn("preview", result)

    def test_multiple_operations(self):
        """Test multiple operations"""
        self.system.start()

        # Insert
        self.system.process_input(action="insert", position=0, text="Hello")

        # Insert more
        self.system.process_input(action="insert", position=5, text=" World")

        # Delete
        result = self.system.process_input(action="delete", start=5, end=11)

        self.assertTrue(result.get("success"))
        self.assertEqual(self.system.state.total_events, 3)

    def test_visualization_mode_change(self):
        """Test changing visualization modes"""
        self.system.start()

        self.assertTrue(self.system.set_visualization_mode("flow"))
        self.assertEqual(self.system.renderer.mode, VisualizationMode.FLOW)

        self.assertTrue(self.system.set_visualization_mode("tree"))
        self.assertEqual(self.system.renderer.mode, VisualizationMode.TREE)

    def test_export_session(self):
        """Test session export"""
        self.system.start()

        # Generate some activity
        self.system.process_input(action="insert", position=0, text="Test export")

        export_dir = Path(__file__).parent / "test_export_session"
        self.system.export_session(str(export_dir))

        # Verify files exist
        self.assertTrue((export_dir / "session_state.json").exists())
        self.assertTrue((export_dir / "trajectory.json").exists())
        self.assertTrue((export_dir / "animation.json").exists())

        # Cleanup
        import shutil

        shutil.rmtree(export_dir)

    def test_event_callbacks(self):
        """Test event callback system"""
        callback_data = []

        def test_callback(data):
            callback_data.append(data)

        self.system.register_event_callback(test_callback)
        self.system.start()

        self.system.process_input(action="insert", position=0, text="Test")

        self.assertGreater(len(callback_data), 0)

    def test_clear_all(self):
        """Test clearing all state"""
        self.system.start()

        self.system.process_input(action="insert", position=0, text="Test")
        self.system.clear_all()

        self.assertEqual(len(self.system.trajectory.points), 0)
        self.assertEqual(self.system.input_adapter.current_content, "")
        self.assertEqual(len(self.system.renderer.frames), 0)


class TestSSEIntegration(unittest.TestCase):
    """Smoke tests for SSE server and Tk UI pipeline endpoints"""

    def setUp(self):
        # Start server on ephemeral port
        from server_sse import start_server

        self.server = start_server(host="127.0.0.1", port=0, base_path=Path(__file__).parent)
        self.port = self.server.server_address[1]

    def tearDown(self):
        try:
            self.server.shutdown()
        except Exception:
            pass

    def _url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def test_health_and_input(self):
        # health
        with urllib.request.urlopen(self._url("/health"), timeout=1) as resp:
            self.assertEqual(resp.status, 200)

        # input
        data = json.dumps({"prompt": "forest with green trees", "stage": "draft"}).encode("utf-8")
        req = urllib.request.Request(self._url("/input"), data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            self.assertEqual(resp.status, 200)
            body = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(body.get("ok"))

    def test_events_stream_receives_preview(self):
        # Open events first
        req = urllib.request.Request(self._url("/events"), headers={"Accept": "text/event-stream"})
        resp = urllib.request.urlopen(req, timeout=3)

        # Trigger input to generate a frame
        data = json.dumps({"prompt": "colorful forest", "stage": "draft"}).encode("utf-8")
        post = urllib.request.Request(self._url("/input"), data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(post, timeout=2)

        got_preview = False
        started = time.time()
        buf = []
        try:
            while time.time() - started < 2.0:
                line = resp.readline()
                if not line:
                    break
                s = line.decode("utf-8", errors="replace").rstrip("\r\n")
                if s.startswith("data:"):
                    buf.append(s[5:].strip())
                elif s == "":
                    if buf:
                        try:
                            payload = json.loads("\n".join(buf))
                            if payload.get("type") == "preview" and "ascii" in payload:
                                got_preview = True
                                break
                        except Exception:
                            pass
                        buf = []
        except socket.timeout:
            pass
        finally:
            try:
                resp.close()
            except Exception:
                pass

        self.assertTrue(got_preview)


def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("GLIMPSE - TEST SUITE")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTrajectoryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestInputAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualRenderer))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGlimpseOrchestrator))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
