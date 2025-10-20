"""
Glimpse Orchestrator - Main Engine
Integrates trajectory tracking, input adaptation, visual rendering, and security
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import time
import json
import logging

from .core_trajectory import TrajectoryEngine
from .input_adapter import InputAdapter
from .visual_renderer import VisualRenderer, VisualizationMode, PreviewFrame
from .security_integration import SecurityManager, SecurityContext

# Setup logging
LOG = logging.getLogger("glimpse")
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
LOG.handlers = [handler]


@dataclass
class GlimpseConfiguration:
    """Configuration for Glimpse orchestration"""

    visualization_mode: VisualizationMode = VisualizationMode.TIMELINE
    enable_security: bool = True
    enable_guardrails: bool = True
    enable_predictions: bool = True
    enable_suggestions: bool = True
    trajectory_window_size: int = 100
    input_buffer_size: int = 50
    auto_save_interval: float = 60.0  # seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visualization_mode": self.visualization_mode.value,
            "enable_security": self.enable_security,
            "enable_guardrails": self.enable_guardrails,
            "enable_predictions": self.enable_predictions,
            "enable_suggestions": self.enable_suggestions,
            "trajectory_window_size": self.trajectory_window_size,
            "input_buffer_size": self.input_buffer_size,
            "auto_save_interval": self.auto_save_interval,
        }


@dataclass
class GlimpseState:
    """Current state of the Glimpse system"""

    is_active: bool = False
    start_time: float = 0.0
    total_events: int = 0
    current_frame: Optional[PreviewFrame] = None
    security_context: Optional[SecurityContext] = None

    def uptime(self) -> float:
        if not self.is_active:
            return 0.0
        return time.time() - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_active": self.is_active,
            "uptime": self.uptime(),
            "total_events": self.total_events,
            "has_current_frame": self.current_frame is not None,
            "security_context": self.security_context.to_dict() if self.security_context else None,
        }


class GlimpseOrchestrator:
    """
    Main orchestrator for Glimpse.

    This system provides:
    - Real-time trajectory tracking and visualization
    - Dynamic input adaptation with suggestions
    - Cause-effect chain mapping
    - Integrated security and safety
    - Multiple visualization modes
    """

    def __init__(self, config: Optional[GlimpseConfiguration] = None, base_path: Optional[Path] = None):
        self.config = config or GlimpseConfiguration()
        self.base_path = Path(base_path) if base_path else Path(__file__).parent

        # Initialize core components
        self.trajectory = TrajectoryEngine(window_size=self.config.trajectory_window_size)
        self.input_adapter = InputAdapter(buffer_size=self.config.input_buffer_size)
        self.renderer = VisualRenderer(mode=self.config.visualization_mode)
        self.security = SecurityManager(base_path=self.base_path) if self.config.enable_security else None

        # State
        self.state = GlimpseState()
        self.last_save_time = 0.0
        self.event_callbacks: List[Callable] = []

        LOG.info("GlimpseOrchestrator initialized")
        if self.security:
            LOG.info("Security module active")

    def start(self) -> bool:
        """Start the Glimpse system"""
        if self.state.is_active:
            LOG.warning("System already active")
            return False

        # Security check
        if self.security:
            if not self.security.run_security_check():
                LOG.error("Security check failed - cannot start")
                return False

            self.state.security_context = self.security.assess_security_context()

        self.state.is_active = True
        self.state.start_time = time.time()

        LOG.info("✓ Glimpse system started")
        return True

    def stop(self):
        """Stop the Glimpse system"""
        if not self.state.is_active:
            return

        self.state.is_active = False
        LOG.info(f"✓ System stopped after {self.state.uptime():.2f}s")

    def process_input(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Process input action and generate a Glimpse preview.

        Actions: insert, delete, replace, undo, redo
        """
        if not self.state.is_active:
            LOG.warning("System not active - call start() first")
            return {"error": "system_not_active"}

        # Validate security if enabled
        if self.security and not self.security.validate_operation("track"):
            return {"error": "operation_not_allowed", "operation": "track"}

        # Process input event
        event = None

        if action == "insert":
            position = kwargs.get("position", 0)
            text = kwargs.get("text", "")
            event = self.input_adapter.process_insert(position, text)

        elif action == "delete":
            start = kwargs.get("start", 0)
            end = kwargs.get("end", 0)
            event = self.input_adapter.process_delete(start, end)

        elif action == "replace":
            start = kwargs.get("start", 0)
            end = kwargs.get("end", 0)
            text = kwargs.get("text", "")
            event = self.input_adapter.process_replace(start, end, text)

        elif action == "undo":
            event = self.input_adapter.undo()

        elif action == "redo":
            event = self.input_adapter.redo()

        if not event:
            return {"error": "invalid_action", "action": action}

        # Update trajectory
        trajectory_point = self.trajectory.add_point(
            content=self.input_adapter.current_content,
            metadata={
                "event_type": event.event_type.value,
                "delta": event.delta,
                "typing_velocity": self.input_adapter.get_typing_velocity(),
                "edit_intensity": self.input_adapter.get_edit_intensity(),
            },
        )

        # Generate preview
        preview = self._generate_preview()

        # Get adaptation context (suggestions)
        adaptation = None
        if self.config.enable_suggestions:
            adaptation = self.input_adapter.get_adaptation_context()

        # Get predictions
        predictions = None
        if self.config.enable_predictions:
            predictions = self.trajectory.predict_next_states()

        # Update state
        self.state.total_events += 1

        # Trigger callbacks
        self._trigger_callbacks(
            {"event": event.to_dict(), "trajectory_point": trajectory_point.to_dict(), "preview": preview}
        )

        # Auto-save check
        self._check_auto_save()

        result = {
            "success": True,
            "event": event.to_dict(),
            "trajectory": {
                "current_direction": trajectory_point.direction.value,
                "confidence": trajectory_point.confidence,
                "cause_effect_chain": trajectory_point.cause_effect_chain,
            },
            "preview": {
                "frame_id": preview.frame_id if preview else None,
                "element_count": len(preview.elements) if preview else 0,
            },
        }

        if adaptation:
            result["suggestions"] = adaptation.suggestions

        if predictions:
            result["predictions"] = predictions

        return result

    def _generate_preview(self) -> Optional[PreviewFrame]:
        """Generate visual preview frame"""
        try:
            trajectory_state = self.trajectory.get_current_state()
            input_context = {
                "recent_activity": self.input_adapter.get_recent_activity(),
                "typing_velocity": self.input_adapter.get_typing_velocity(),
                "edit_intensity": self.input_adapter.get_edit_intensity(),
            }

            frame = self.renderer.render(trajectory_state, input_context)
            self.state.current_frame = frame

            return frame

        except Exception as e:
            LOG.error(f"Error generating preview: {e}")
            return None

    def get_current_preview(self) -> Optional[str]:
        """Get ASCII representation of current preview"""
        if not self.state.current_frame:
            return None

        return self.renderer.generate_ascii_preview(self.state.current_frame)

    def get_full_state(self) -> Dict[str, Any]:
        """Get comprehensive system state"""
        state = {
            "system": self.state.to_dict(),
            "config": self.config.to_dict(),
            "trajectory": self.trajectory.get_trajectory_summary(),
            "input": {
                "content_length": len(self.input_adapter.current_content),
                "cursor_position": self.input_adapter.cursor_position,
                "typing_velocity": self.input_adapter.get_typing_velocity(),
                "edit_intensity": self.input_adapter.get_edit_intensity(),
            },
            "visualization": {"mode": self.renderer.mode.value, "total_frames": len(self.renderer.frames)},
        }

        if self.security:
            state["security"] = self.security.get_security_metrics()

        return state

    def set_visualization_mode(self, mode: str) -> bool:
        """Change visualization mode"""
        try:
            viz_mode = VisualizationMode(mode)
            self.renderer.set_mode(viz_mode)
            LOG.info(f"Visualization mode changed to: {mode}")
            return True
        except ValueError:
            LOG.error(f"Invalid visualization mode: {mode}")
            return False

    def register_event_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback for events"""
        self.event_callbacks.append(callback)

    def _trigger_callbacks(self, event_data: Dict[str, Any]):
        """Trigger all registered callbacks"""
        for callback in self.event_callbacks:
            try:
                callback(event_data)
            except Exception as e:
                LOG.error(f"Error in callback: {e}")

    def _check_auto_save(self):
        """Check if auto-save should trigger"""
        if self.config.auto_save_interval <= 0:
            return

        current_time = time.time()
        if current_time - self.last_save_time >= self.config.auto_save_interval:
            self.auto_save()
            self.last_save_time = current_time

    def auto_save(self):
        """Auto-save current state"""
        try:
            timestamp = int(time.time())
            save_dir = self.base_path / "autosave"
            save_dir.mkdir(exist_ok=True)

            # Save trajectory
            trajectory_file = save_dir / f"trajectory_{timestamp}.json"
            self.trajectory.export_trajectory(str(trajectory_file))

            # Save preview animation
            animation_file = save_dir / f"animation_{timestamp}.json"
            self.renderer.export_animation(str(animation_file), frame_limit=50)

            LOG.info(f"Auto-saved to {save_dir}")

        except Exception as e:
            LOG.error(f"Auto-save failed: {e}")

    def export_session(self, output_dir: str):
        """Export complete session data"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Full state
        state_file = output_path / "session_state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.get_full_state(), f, indent=2)

        # Trajectory
        trajectory_file = output_path / "trajectory.json"
        self.trajectory.export_trajectory(str(trajectory_file))

        # Animation
        animation_file = output_path / "animation.json"
        self.renderer.export_animation(str(animation_file))

        # Security report if available
        if self.security:
            security_file = output_path / "security_report.json"
            self.security.export_security_report(str(security_file))

        LOG.info(f"✓ Session exported to {output_path}")

    def clear_all(self):
        """Clear all state and history"""
        self.trajectory.clear()
        self.input_adapter.clear()
        self.renderer.clear_frames()
        self.state = GlimpseState()
        LOG.info("All state cleared")


# Convenience function for quick setup
def create_glimpse(
    mode: str = "timeline",
    enable_security: bool = True,
    enable_guardrails: bool = True,
    base_path: Optional[Path] = None,
) -> GlimpseOrchestrator:
    """Create and configure a Glimpse system"""

    config = GlimpseConfiguration(
        visualization_mode=VisualizationMode(mode), enable_security=enable_security, enable_guardrails=enable_guardrails
    )

    system = GlimpseOrchestrator(config=config, base_path=base_path)
    return system


# Backward compatibility aliases
PreviewConfiguration = GlimpseConfiguration
RealtimeState = GlimpseState
RealtimePreview = GlimpseOrchestrator


def create_preview_system(
    mode: str = "timeline", enable_security: bool = True, base_path: Optional[Path] = None
) -> GlimpseOrchestrator:
    """Compatibility wrapper for `create_glimpse`."""
    return create_glimpse(mode=mode, enable_security=enable_security, base_path=base_path)
