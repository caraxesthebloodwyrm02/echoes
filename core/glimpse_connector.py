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

r"""
GlimpsePreview Integration Connector
Bridges D:\ GlimpsePreview trajectory analysis with E:\ Echoes platform
r"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GlimpseConnector:
    r"""
    Connect GlimpsePreview/Realtime trajectory analysis with Echoes platform

    Purpose: Enable cross-platform communication between research and development
    - Realtime/HITL: E:\Projects\Development\realtime (trajectory analysis, HITL workflows, real-time visualization)
    - Echoes Core: E:\Projects\Development (AI orchestration, knowledge graphs, deterministic workflows)
    - Research (Optional): D:\ GlimpsePreview (additional research platform if available)
    r"""

    def __init__(self, glimpse_root: str = "E:/Projects/Development/realtime"):
        r"""
        Initialize connector to GlimpsePreview/Realtime system

        Args:
            glimpse_root: Path to GlimpsePreview/Realtime installation (default: E:/Projects/Development/realtime)
        r"""
        self.glimpse_root = Path(glimpse_root)
        self.connected = False
        self._add_glimpse_to_path()

    def _add_glimpse_to_path(self):
        r"""Add GlimpsePreview to Python path for importsr"""
        if self.glimpse_root.exists():
            sys.path.insert(0, str(self.glimpse_root))
            logger.info(f"Added GlimpsePreview path: {self.glimpse_root}")
        else:
            logger.warning(f"GlimpsePreview path not found: {self.glimpse_root}")

    def connect(self) -> bool:
        r"""
        Establish connection to GlimpsePreview components

        Returns:
            bool: True if connection successful
        r"""
        try:
            # Import GlimpsePreview core components
            from core_trajectory import TrajectoryEngine
            from input_adapter import InputAdapter
            from visual_renderer import VisualRenderer

            self.trajectory_engine = TrajectoryEngine()
            self.input_adapter = InputAdapter()
            self.visual_renderer = VisualRenderer()

            self.connected = True
            logger.info("✅ Connected to GlimpsePreview system")
            return True

        except ImportError as e:
            logger.error(f"❌ Failed to connect to GlimpsePreview: {e}")
            self.connected = False
            return False

    def analyze_trajectory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        r"""
        Analyze trajectory using GlimpsePreview engine

        Args:
            data: Input data for trajectory analysis

        Returns:
            dict: Trajectory analysis results with direction, confidence, health
        r"""
        if not self.connected:
            raise RuntimeError("Not connected to GlimpsePreview. Call connect() first.")

        try:
            # Process input through adapter
            # Note: context available if needed for future enhancements
            # context = self.input_adapter.get_adaptation_context()

            # Analyze trajectory
            trajectory_data = self.trajectory_engine.analyze()

            return {
                "direction": trajectory_data.get("current_direction", "unknown"),
                "confidence": trajectory_data.get("confidence", 0.0),
                "health": trajectory_data.get("trajectory_health", 0.0),
                "predictions": trajectory_data.get("predictions", []),
                "segments": trajectory_data.get("segments", []),
            }

        except Exception as e:
            logger.error(f"Trajectory analysis failed: {e}")
            return {"error": str(e)}

    def get_visualization(self, mode: str = "timeline") -> Optional[str]:
        r"""
        Generate visualization using GlimpsePreview renderer

        Args:
            mode: Visualization mode (timeline/tree/flow/heatmap)

        Returns:
            str: Visualization output or None if failed
        r"""
        if not self.connected:
            raise RuntimeError("Not connected to GlimpsePreview. Call connect() first.")

        try:
            return self.visual_renderer.render(mode=mode)
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            return None

    def register_suggestion_provider(self, provider_func):
        r"""
        Register custom suggestion provider with GlimpsePreview

        Args:
            provider_func: Function that generates suggestions
        r"""
        if not self.connected:
            raise RuntimeError("Not connected to GlimpsePreview. Call connect() first.")

        self.input_adapter.register_suggestion_provider(provider_func)
        logger.info("Registered custom suggestion provider")

    def get_comprehension_metrics(self) -> Dict[str, Any]:
        r"""
        Get comprehension metrics from GlimpsePreview

        Returns:
            dict: Metrics including comprehension_speed, trajectory_health, confidence
        r"""
        if not self.connected:
            return {"error": "Not connected"}

        try:
            trajectory_data = self.trajectory_engine.analyze()

            return {
                "comprehension_speed": trajectory_data.get("comprehension_speed", 0.0),
                "trajectory_health": trajectory_data.get("trajectory_health", 0.0),
                "confidence": trajectory_data.get("confidence", 0.0),
                "edit_intensity": trajectory_data.get("edit_intensity", 0.0),
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        r"""
        Check health of GlimpsePreview connection

        Returns:
            dict: Health status and component availability
        r"""
        return {
            "connected": self.connected,
            "glimpse_root_exists": self.glimpse_root.exists(),
            "components": {
                "trajectory_engine": hasattr(self, "trajectory_engine"),
                "input_adapter": hasattr(self, "input_adapter"),
                "visual_renderer": hasattr(self, "visual_renderer"),
            },
        }


def create_glimpse_connector(
    glimpse_root: str = "E:/Projects/Development/realtime",
) -> GlimpseConnector:
    r"""
    Factory function to create and connect GlimpseConnector

    Args:
        glimpse_root: Path to GlimpsePreview/Realtime installation (default: E:/Projects/Development/realtime)

    Returns:
        GlimpseConnector: Connected instance
    r"""
    connector = GlimpseConnector(glimpse_root)
    connector.connect()
    return connector
