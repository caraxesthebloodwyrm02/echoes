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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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
Unified Import Safety System
Provides safe imports with graceful degradation for optional dependencies
Prevents cascade failures from missing packages
"""

import importlib
import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Track import status for diagnostics
_import_status: Dict[str, Dict[str, Any]] = {}


def safe_import(module_name: str, fallback: Any = None, required: bool = False) -> Tuple[bool, Any]:
    """
    Safely import a module with fallback handling.

    Args:
        module_name: The module name to import
        fallback: Fallback object if import fails
        required: If True, raise ImportError on failure instead of falling back

    Returns:
        Tuple of (success: bool, module_or_fallback)
    """
    try:
        module = importlib.import_module(module_name)
        _import_status[module_name] = {
            "status": "success",
            "module": module,
            "error": None,
        }
        return True, module
    except ImportError as e:
        if required:
            logger.error(f"Required module '{module_name}' not available: {e}")
            raise

        logger.warning(f"Optional module '{module_name}' not available, using fallback: {e}")
        _import_status[module_name] = {
            "status": "fallback",
            "module": fallback,
            "error": str(e),
        }
        return False, fallback
    except Exception as e:
        if required:
            logger.error(f"Critical error importing '{module_name}': {e}")
            raise

        logger.error(f"Unexpected error importing '{module_name}': {e}")
        _import_status[module_name] = {
            "status": "error",
            "module": fallback,
            "error": str(e),
        }
        return False, fallback


def get_import_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all tracked imports."""
    return _import_status.copy()


class SafeKnowledgeGraphBridge:
    """Knowledge Graph Bridge with safe imports"""

    def __init__(self, enable_kg: bool = True, cache_size: int = 100):
        self.enabled = False
        self.kg_bridge = None
        self.cache_size = cache_size

        if enable_kg:
            # Try to import KG system safely
            kg_success, kg_module = safe_import("knowledge_graph.system")
            bridge_success, _ = safe_import("prompting.core.kg_bridge", required=False)

            if kg_success and bridge_success:
                try:
                    from prompting.core.kg_bridge import KnowledgeGraphBridge

                    self.kg_bridge = KnowledgeGraphBridge(enable_kg=True, cache_size=cache_size)
                    self.enabled = True
                    logger.info("Knowledge Graph Bridge initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize KG Bridge: {e}")
                    self.enabled = False
            else:
                logger.info("Knowledge Graph dependencies not available - operating in fallback mode")

    def sync_insights_to_kg(self, insights):
        """Safe sync with fallback"""
        if self.enabled and self.kg_bridge:
            try:
                return self.kg_bridge.sync_insights_to_kg(insights)
            except Exception as e:
                logger.error(f"KG sync failed: {e}")
        return 0

    def semantic_search(self, query, **kwargs):
        """Safe semantic search with fallback"""
        if self.enabled and self.kg_bridge:
            try:
                return self.kg_bridge.semantic_search(query, **kwargs)
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")
        return []

    def get_stats(self):
        """Safe stats retrieval"""
        if self.enabled and self.kg_bridge:
            try:
                return self.kg_bridge.get_stats()
            except Exception as e:
                logger.error(f"Stats retrieval failed: {e}")
        return {"kg_enabled": False, "cache_size": self.cache_size}


class SafeAgentKnowledgeLayer:
    """Agent Knowledge Layer with safe imports"""

    def __init__(self, enable_kg: bool = True):
        self.enabled = False
        self.agents = {}
        self.discoveries = []
        self.contexts = []

        # Try to import agent knowledge layer safely
        akl_success, akl_module = safe_import("ai_agents.agent_knowledge_layer", required=False)

        if akl_success and enable_kg:
            try:
                from ai_agents.agent_knowledge_layer import AgentKnowledgeLayer

                self.akl = AgentKnowledgeLayer(enable_kg=True)
                self.enabled = True
                logger.info("Agent Knowledge Layer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Agent Knowledge Layer: {e}")
                self.enabled = False
        else:
            logger.info("Agent Knowledge Layer dependencies not available - operating in fallback mode")

    def register_agent(self, agent_name, **kwargs):
        """Safe agent registration"""
        if self.enabled:
            try:
                return self.akl.register_agent(agent_name, **kwargs)
            except Exception as e:
                logger.error(f"Agent registration failed: {e}")

        # Fallback: store locally
        self.agents[agent_name] = kwargs
        return True

    def add_discovery(self, discovery):
        """Safe discovery addition"""
        if self.enabled:
            try:
                return self.akl.add_discovery(discovery)
            except Exception as e:
                logger.error(f"Discovery addition failed: {e}")

        # Fallback: store locally
        self.discoveries.append(discovery)
        return True

    def get_stats(self):
        """Safe stats retrieval"""
        if self.enabled:
            try:
                return self.akl.get_stats()
            except Exception as e:
                logger.error(f"Stats retrieval failed: {e}")
        return {
            "enabled": False,
            "agents": len(self.agents),
            "discoveries": len(self.discoveries),
        }


# Global instances for reuse
_kg_bridge_instance: Optional[SafeKnowledgeGraphBridge] = None
_akl_instance: Optional[SafeAgentKnowledgeLayer] = None


def get_safe_kg_bridge(enable_kg: bool = True) -> SafeKnowledgeGraphBridge:
    """Get singleton KG bridge instance"""
    global _kg_bridge_instance
    if _kg_bridge_instance is None:
        _kg_bridge_instance = SafeKnowledgeGraphBridge(enable_kg=enable_kg)
    return _kg_bridge_instance


def get_safe_agent_knowledge_layer(enable_kg: bool = True) -> SafeAgentKnowledgeLayer:
    """Get singleton agent knowledge layer instance"""
    global _akl_instance
    if _akl_instance is None:
        _akl_instance = SafeAgentKnowledgeLayer(enable_kg=enable_kg)
    return _akl_instance


# Initialize critical imports on module load
def _initialize_safe_imports():
    """Initialize all safe imports on module load"""
    logger.info("Initializing unified import safety system...")

    # Test core dependencies
    safe_import("networkx")
    safe_import("rdflib")
    safe_import("openai")
    safe_import("agents")

    logger.info(f"Import safety system initialized. Status: {len(_import_status)} modules checked")


# Auto-initialize on import
_initialize_safe_imports()
