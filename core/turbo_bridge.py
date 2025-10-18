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
TurboBridge: Unified Cross-Platform Integration
Connects E:\ Echoes with D:\ TurboBookshelf and GlimpsePreview research platforms
r"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from .glimpse_connector import GlimpseConnector

logger = logging.getLogger(__name__)


class TurboBridge:
    r"""
    Unified bridge connecting three platforms:
    1. E:\ Echoes - AI orchestration, knowledge graphs, deterministic workflows
    2. D:\ TurboBookshelf - Bias detection, web interface, creative content
    3. D:\ GlimpsePreview - Trajectory analysis, real-time visualization

    Purpose: Streamline communication between research and development
    r"""

    def __init__(
        self,
        turbo_root: str = "D:/",
        glimpse_root: str = "E:/Projects/Development/realtime",
        echoes_root: str = "E:/Projects/Development",
    ):
        r"""
        Initialize cross-platform bridge

        Args:
            turbo_root: Path to TurboBookshelf (default: D:/)
            glimpse_root: Path to GlimpsePreview/Realtime (default: E:/Projects/Development/realtime)
            echoes_root: Path to Echoes (default: E:/Projects/Development)
        r"""
        self.turbo_root = Path(turbo_root)
        self.glimpse_root = Path(glimpse_root)
        self.echoes_root = Path(echoes_root)

        # Initialize connectors
        self.glimpse = GlimpseConnector(str(glimpse_root))

        # Connection status
        self.connections = {
            "turbo": False,
            "glimpse": False,
            "echoes": True,
        }  # Already in Echoes

        logger.info("TurboBridge initialized")

    def connect_all(self) -> Dict[str, bool]:
        r"""
        Establish connections to all platforms

        Returns:
            dict: Connection status for each platform
        r"""
        # Connect to GlimpsePreview
        self.connections["glimpse"] = self.glimpse.connect()

        # Connect to TurboBookshelf
        self.connections["turbo"] = self._connect_turbo()

        logger.info(f"Connection status: {self.connections}")
        return self.connections

    def _connect_turbo(self) -> bool:
        r"""Connect to TurboBookshelf componentsr"""
        try:
            # Add D:\ to path
            sys.path.insert(0, str(self.turbo_root))
            sys.path.insert(0, str(self.turbo_root / "engines"))

            # Try importing TurboBookshelf components
            from engines.insights.bias import BiasPatternDetector

            self.bias_detector = BiasPatternDetector()
            logger.info("✅ Connected to TurboBookshelf")
            return True

        except ImportError as e:
            logger.warning(f"⚠️ TurboBookshelf not available: {e}")
            return False

    def unified_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        r"""
        Perform cross-platform unified analysis

        Combines:
        - Trajectory analysis (GlimpsePreview)
        - Bias detection (TurboBookshelf)
        - Knowledge graph enrichment (Echoes)

        Args:
            data: Input data with 'text', 'query', 'trajectory' fields

        Returns:
            dict: Unified analysis results
        r"""
        results = {}

        # Trajectory analysis from GlimpsePreview
        if self.connections["glimpse"]:
            try:
                results["trajectory"] = self.glimpse.analyze_trajectory(data)
                results["visualization"] = self.glimpse.get_visualization()
                results["metrics"] = self.glimpse.get_comprehension_metrics()
            except Exception as e:
                logger.error(f"Trajectory analysis failed: {e}")
                results["trajectory"] = {"error": str(e)}

        # Bias detection from TurboBookshelf
        if self.connections["turbo"] and "text" in data:
            try:
                results["bias"] = self.bias_detector.detect(data["text"])
            except Exception as e:
                logger.error(f"Bias detection failed: {e}")
                results["bias"] = {"error": str(e)}

        # Knowledge graph from Echoes
        if "query" in data:
            try:
                from knowledge_graph.system import KnowledgeGraphBridge

                kg = KnowledgeGraphBridge()
                results["knowledge"] = kg.semantic_search(data["query"])
            except Exception as e:
                logger.error(f"Knowledge graph failed: {e}")
                results["knowledge"] = {"error": str(e)}

        return results

    def streamline_communication(
        self, source: str, target: str, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        r"""
        Streamline communication between platforms

        Args:
            source: Source platform ('echoes', 'turbo', 'glimpse')
            target: Target platform ('echoes', 'turbo', 'glimpse')
            message: Message data to transmit

        Returns:
            dict: Response from target platform
        r"""
        logger.info(f"Routing message: {source} → {target}")

        if target == "glimpse" and self.connections["glimpse"]:
            # Route to GlimpsePreview for trajectory analysis
            return self.glimpse.analyze_trajectory(message)

        elif target == "turbo" and self.connections["turbo"]:
            # Route to TurboBookshelf for bias detection
            if "text" in message:
                return {"bias": self.bias_detector.detect(message["text"])}

        elif target == "echoes":
            # Route to Echoes for AI orchestration
            return {"status": "routed_to_echoes", "message": message}

        return {"error": f"Target {target} not connected"}

    def get_system_status(self) -> Dict[str, Any]:
        r"""
        Get comprehensive system status across all platforms

        Returns:
            dict: Status of all platforms and components
        r"""
        status = {
            "connections": self.connections,
            "platforms": {
                "echoes": {
                    "root": str(self.echoes_root),
                    "exists": self.echoes_root.exists(),
                },
                "turbo": {
                    "root": str(self.turbo_root),
                    "exists": self.turbo_root.exists(),
                },
                "glimpse": {
                    "root": str(self.glimpse_root),
                    "exists": self.glimpse_root.exists(),
                },
            },
        }

        # Add GlimpsePreview health check
        if self.connections["glimpse"]:
            status["glimpse_health"] = self.glimpse.health_check()

        return status

    def enable_cross_platform_features(self):
        r"""
        Enable advanced cross-platform features

        Features:
        - Trajectory-aware bias detection
        - Knowledge-enhanced visualizations
        - Unified suggestion providers
        r"""
        if self.connections["glimpse"]:
            # Register Echoes knowledge graph as suggestion provider
            def kg_suggestions(context):
                r"""Generate suggestions from Echoes knowledge graphr"""
                try:
                    from knowledge_graph.system import KnowledgeGraphBridge

                    kg = KnowledgeGraphBridge()
                    return kg.semantic_search(context.get("query", ""))
                except Exception:
                    return []

            self.glimpse.register_suggestion_provider(kg_suggestions)
            logger.info("✅ Enabled cross-platform features")


def create_bridge(
    turbo_root: str = "D:/",
    glimpse_root: str = "E:/Projects/Development/realtime",
    echoes_root: str = "E:/Projects/Development",
) -> TurboBridge:
    r"""
    Factory function to create and connect TurboBridge

    Args:
        turbo_root: Path to TurboBookshelf
        glimpse_root: Path to GlimpsePreview
        echoes_root: Path to Echoes

    Returns:
        TurboBridge: Connected instance
    r"""
    bridge = TurboBridge(turbo_root, glimpse_root, echoes_root)
    bridge.connect_all()
    bridge.enable_cross_platform_features()
    return bridge
