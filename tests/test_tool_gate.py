"""Unit tests for the tool gate: allowlist, payload validation, and audit."""
import logging
import unittest

from tools import (
    get_registry,
    register_tool,
    execute_tool,
    safe_dispatch_tool,
)


def _dummy_tool(payload: dict):
    return {"ok": True, "payload": payload}


class TestToolGate(unittest.TestCase):
    """Test tool gate: unknown tool rejected, invalid payload rejected, valid tool runs."""

    def setUp(self):
        self.registry = get_registry()
        # Ensure echo exists for tests that need a registered tool
        try:
            self.registry.get_tool("echo")
        except Exception:
            pass
        if not self.registry.has_tool("_gate_test_tool"):
            register_tool("_gate_test_tool", "Test tool for gate", _dummy_tool)

    def test_unknown_tool_raises_key_error(self):
        with self.assertRaises(KeyError) as ctx:
            execute_tool("_nonexistent_tool_xyz", {})
        self.assertIn("not found", str(ctx.exception))

    def test_unknown_tool_logged(self):
        with self.assertLogs("echoes.tools.gate", level=logging.WARNING) as cm:
            with self.assertRaises(KeyError):
                execute_tool("_nonexistent_tool_xyz", {})
        self.assertTrue(any("tool_gate_rejected" in m for m in cm.output))
        self.assertTrue(any("unknown_tool" in m for m in cm.output))

    def test_allowlisted_tool_runs(self):
        result = execute_tool("_gate_test_tool", {"a": 1})
        self.assertEqual(result, {"ok": True, "payload": {"a": 1}})

    def test_allowlisted_tool_audit_logged(self):
        with self.assertLogs("echoes.tools.gate", level=logging.INFO) as cm:
            execute_tool("_gate_test_tool", {"b": 2})
        self.assertTrue(any("tool_gate_dispatch" in m for m in cm.output))
        self.assertTrue(any("tool_gate_outcome" in m and "success" in m for m in cm.output))

    def test_invalid_payload_non_dict_raises(self):
        with self.assertRaises(ValueError) as ctx:
            execute_tool("_gate_test_tool", "not a dict")
        self.assertIn("Payload must be a dict", str(ctx.exception))

    def test_invalid_payload_dangerous_key_raises(self):
        with self.assertRaises(ValueError) as ctx:
            execute_tool("_gate_test_tool", {"__import__": "os"})
        self.assertIn("not allowed", str(ctx.exception))

    def test_safe_dispatch_tool_with_actor(self):
        with self.assertLogs("echoes.tools.gate", level=logging.INFO) as cm:
            out = safe_dispatch_tool(
                self.registry, "_gate_test_tool", {"x": 1}, actor="test-actor"
            )
        self.assertEqual(out, {"ok": True, "payload": {"x": 1}})
        self.assertTrue(any("actor=test-actor" in m for m in cm.output))


class TestToolGateImplementationStatus(unittest.TestCase):
    """Implementation status: assert tool gate is active and enforced."""

    def setUp(self):
        self.registry = get_registry()
        if not self.registry.has_tool("_gate_test_tool"):
            register_tool("_gate_test_tool", "Test tool for gate", lambda p: {"ok": True, "payload": p})

    def test_implementation_status_unknown_tool_rejected_active(self):
        """Tool gate is ACTIVE: unknown tool names are rejected."""
        with self.assertRaises(KeyError) as ctx:
            execute_tool("_nonexistent_xyz", {})
        self.assertIn("not found", str(ctx.exception))

    def test_implementation_status_dangerous_payload_rejected_active(self):
        """Tool gate is ACTIVE: dangerous payload keys are rejected."""
        with self.assertRaises(ValueError) as ctx:
            execute_tool("_gate_test_tool", {"eval": "code"})
        self.assertIn("not allowed", str(ctx.exception))

    def test_implementation_status_allowlisted_tool_dispatched_and_audited_active(self):
        """Tool gate is ACTIVE: allowlisted tools are dispatched and audit-logged."""
        with self.assertLogs("echoes.tools.gate", level=logging.INFO) as cm:
            result = execute_tool("_gate_test_tool", {"a": 1})
        self.assertEqual(result, {"ok": True, "payload": {"a": 1}})
        self.assertTrue(any("tool_gate_dispatch" in m for m in cm.output))
        self.assertTrue(any("tool_gate_outcome" in m and "success" in m for m in cm.output))
