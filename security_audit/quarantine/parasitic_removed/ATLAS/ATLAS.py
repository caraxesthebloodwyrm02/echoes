#!/usr/bin/env python3
"""
Echoes AI Assistant V2 - Core Implementation (Phase 1)

Integrates:
- Tool Framework (registry-based)
- RAG V2 (semantic knowledge retrieval)
- Context Management (conversation history)
- Streaming (real-time responses)
- Status Indicators (progress tracking)
- Memory Persistence (conversation storage)
"""

import asyncio
import json
import logging
# ============================================================================
# Standard library imports
# ============================================================================
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

# Fix Windows console encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Import numpy for calculations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Warning: numpy not available, using fallback calculations")
    NUMPY_AVAILABLE = False
    def mean(data):
        return sum(data) / len(data) if data else 0
    np = type("obj", (object,), {"mean": mean})()

# ============================================================================
# FALLBACK CLASSES - DEFINED BEFORE USAGE
# ============================================================================
class SimpleIntent:
    def __init__(self, intent_type: str, confidence: float, parameters: Optional[Dict] = None):
        self.type = intent_type
        self.confidence = confidence
        self.parameters = parameters or {}

class SimpleIntentEngine:
    def detect_intent(self, text: str) -> SimpleIntent:
        """Simple intent detection - question if ends with ?, statement otherwise"""
        intent_type = IntentType.QUESTION if text.strip().endswith("?") else IntentType.STATEMENT
        return SimpleIntent(intent_type, 0.9)
    
    def extract_entities(self, text: str) -> List[Any]:
        """Simple entity extraction - empty list in fallback"""
        return []

class SimpleCrossReferenceSystem:
    def analyze_context(self, message: str) -> Dict[str, Any]:
        """Analyze context - empty dict in fallback"""
        return {}
    
    def cross_reference(self, query: str, content_types: List[str] = None, max_results: int = 3, min_relevance: float = 0.3) -> List[Any]:
        """Cross-reference search - empty list in fallback"""
        return []

class SimpleThoughtTracker:
    def __init__(self):
        self.thought_metadata = {}
        self.thought_id_counter = 0
    
    def add_thought(self, thought_id: str, content: str, thought_type: str, entities: List[str] = None, parent_thoughts: List[str] = None) -> str:
        """Add thought to tracker - return thought_id"""
        self.thought_metadata[thought_id] = {
            "content": content,
            "type": thought_type,
            "entities": entities or [],
            "parent_thoughts": parent_thoughts or [],
        }
        return thought_id
    
    def track_thought(self, thought: str, thought_type: str) -> None:
        """Track thought - no-op in fallback"""
        pass
    
    def get_thought_chain(self) -> List[Dict[str, Any]]:
        """Get thought chain - return stored thoughts"""
        return list(self.thought_metadata.values())

class SimplePersonalityEngine:
    def __init__(self):
        pass
    
    def update_from_interaction(self, message: str) -> None:
        """Update personality from user interaction - no-op in fallback"""
        pass
    
    def generate_response_prefix(self, level: str = "response") -> str:
        """Generate response prefix - empty in fallback"""
        return ""
    
    def adapt_response_style(self, text: str) -> str:
        """Adapt response style - return unchanged in fallback"""
        return text

class PrivacyGuard:
    def __init__(self, on_commit=None):
        self.on_commit = on_commit
    
    def commit(self, result) -> None:
        if self.on_commit:
            try:
                self.on_commit(result)
            except Exception:
                pass  # best-effort

class SimpleModelMetrics:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "model_usage": defaultdict(int),
            "response_times": defaultdict(list),
            "errors": defaultdict(int),
            "cache_hits": defaultdict(int),
            "cache_misses": defaultdict(int)
        }
        self.lock = asyncio.Lock()
    
    async def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()
    
    def record_usage_sync(self, model: str, response_time: float, success: bool) -> None:
        self.metrics["total_requests"] += 1
        self.metrics["model_usage"][model] += 1
        self.metrics["response_times"][model].append(response_time)
        if not success:
            self.metrics["errors"][model] += 1
    
    async def reset_metrics(self) -> None:
        self.metrics = {
            "total_requests": 0,
            "model_usage": defaultdict(int),
            "response_times": defaultdict(list),
            "errors": defaultdict(int),
            "cache_hits": defaultdict(int),
            "cache_misses": defaultdict(int)
        }

class SimpleModelRouter:
    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
    
    def select_model(self, message: str, tools: List[Dict] = None) -> str:
        """Select the best model for this request"""
        return "gpt-4o-mini"  # Default to mini model

class SimpleModelResponseCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = asyncio.Lock()

class SimpleQuantumStateManager:
    def __init__(self):
        self.quantum_state = type("QuantumState", (), {
            "_state": {},
            "_entangled": {},
            "_history": {}
        })()
        self.state_machine = None
        self.metrics = type("QuantumMetrics", (), {
            "total_updates": 0,
            "total_measurements": 0,
            "average_transition_time": 0.0,
            "entangled_states_count": 0,
            "last_updated": None
        })()
        self.interference_patterns = {}
    
    def initialize_quantum_states(self):
        pass
    
    def update_state(self, key: str, value: Any, entangle_with: List[str] = None):
        pass
    
    def get_entangled_states(self, key: str):
        return {}
    
    def measure_state(self, key: str):
        return None
    
    def get_superposition(self, keys: List[str]):
        return {}
    
    def transition_state(self):
        return {}
    
    def get_state_history(self, key: str):
        return []
    
    def get_metrics(self):
        return self.metrics

class SimpleKnowledgeManager:
    def add_knowledge(self, content: str, source: str, category: str = "general", tags: List[str] = None) -> str:
        return ""
    
    def search_knowledge(self, query: str = None, category: str = None, limit: int = 10) -> List[Any]:
        return []
    
    def store_roi_analysis(self, roi_results: Dict[str, Any], analysis_id: str = None) -> str:
        return ""
    
    def search_roi_analyses(self, institution: str = None, business_type: str = None, limit: int = 10) -> List[Any]:
        return []
    
    def get_roi_summary(self) -> Dict[str, Any]:
        return {}
    
    def get_stats(self) -> Dict[str, Any]:
        return {}

class SimpleActionExecutor:
    def __init__(self):
        self.action_history = []
    
    def execute_tool_action(self, *args, **kwargs):
        return None
    
    def get_action_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.action_history[-limit:]
    
    def get_action_summary(self) -> Dict[str, Any]:
        total = len(self.action_history)
        successful = sum(1 for action in self.action_history if action.get("success", False))
        failed = total - successful
        avg_duration = sum(action.get("duration_ms", 0) for action in self.action_history) / total if total > 0 else 0
        
        return {
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "avg_duration_ms": avg_duration
        }

class SimpleFilesystemTools:
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
    
    def list_directory(self, dirpath: str, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        try:
            path = Path(dirpath)
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {dirpath}"}
            
            files = list(path.glob(pattern))
            if recursive:
                files = list(path.rglob(pattern))
            
            return {
                "success": True,
                "files": [{"name": f.name, "path": str(f), "size": f.stat().st_size} for f in files if f.is_file()]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "message": f"File written to {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, query: str, search_path: str = None) -> Dict[str, Any]:
        try:
            path = Path(search_path or self.root_dir)
            matches = list(path.rglob(f"*{query}*"))
            return {"success": True, "matches": [str(m) for m in matches]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def organize_roi_files(self, roi_results: Dict[str, Any], base_dir: str = "roi_analysis") -> Dict[str, Any]:
        return {"success": True, "message": "ROI files organized"}

class SimpleAgentWorkflow:
    def __init__(self, assistant):
        self.assistant = assistant
    
    def run_triage_workflow(self, user_input: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"success": True, "result": "Triage workflow completed"}
    
    def run_comparison_workflow(self, file1: str = None, file2: str = None) -> Dict[str, Any]:
        return {"success": True, "result": "Comparison workflow completed"}
    
    def run_data_enrichment_workflow(self, topic: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"success": True, "result": "Data enrichment workflow completed"}

# ============================================================================
# ATLAS Architecture Integration
# ============================================================================
def utc_now_iso():
    return datetime.now(UTC).isoformat()

@dataclass
class InventoryItem:
    sku: str
    name: str
    category: str
    quantity: int
    location: str
    min_stock: int = 0
    max_stock: int = 0
    created_at: str = ""
    updated_at: str = ""
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "location": self.location,
            "min_stock": self.min_stock,
            "max_stock": self.max_stock,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "attributes": self.attributes,
        }

class InventoryService:
    def __init__(self):
        self._items = {}

    def add_item(self, sku: str, name: str, category: str, quantity: int, location: str, **kwargs):
        now = utc_now_iso()
        item = InventoryItem(
            sku=sku,
            name=name,
            category=category,
            quantity=quantity,
            location=location,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self._items[sku] = item.to_dict()
        return item

    def get_item(self, sku: str):
        data = self._items.get(sku)
        return InventoryItem(**data) if data else None

# ============================================================================
# CACHING AND CORE SYSTEMS
# ============================================================================
class CacheLevel:
    SESSION = "session"
    SHORT = "short"
    LONG = "long"
    PERMANENT = "permanent"
    ALL = "all"

class ContentType:
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    MEMORY = "memory"
    CONVERSATION = "conversation"
    ENTITY = "entity"
    CONTEXT = "context"

def catch_release(content, content_type=ContentType.TEXT, cache_level=CacheLevel.SESSION, **kwargs):
    """Simple catch & release fallback"""
    return content

class IntentType:
    QUESTION = "question"
    STATEMENT = "statement"
    REQUEST = "request"
    COMMAND = "command"
    ANALYSIS = "analysis"
    EXPLORATION = "exploration"
    CREATION = "creation"
    COMPARISON = "comparison"
    OBSERVATION = "observation"

# ---------------------------------------------------------------------------
# Thought‑type definitions
# ---------------------------------------------------------------------------
class ThoughtType:
    """Enum‑like container for the possible kinds of thoughts."""

    ANALYSIS    = "analysis"
    PLANNING   = "planning"
    EXECUTION  = "execution"
    REFLECTION = "reflection"

    # Added for the ATLAS chat flow
    OBSERVATION = "observation"
    QUESTION    = "question"

class SimulationType:
    SCENARIO_EXPLORATION = "scenario_exploration"
    OUTCOME_PREDICTION = "outcome_prediction"
    ALTERNATIVE_PATHS = "alternative_paths"
    POSSIBILITY_SPACE = "possibility_space"
    CONTEXT_EXPANSION = "context_expansion"

class parallel_simulation:
    @staticmethod
    def run_parallel_simulations(configs: List[Dict[str, Any]]) -> List[Any]:
        """Simple parallel simulation fallback"""
        results = []
        for config in configs:
            result = type("SimulationResult", (), {
                "simulation_type": config.get("type", SimulationType.SCENARIO_EXPLORATION),
                "confidence": 0.7,
                "reasoning": "Fallback simulation result",
                "outcome": {"result": "completed"},
                "possibilities": [],
                "insights": []
            })()
            results.append(result)
        return results

    @staticmethod
    def get_simulation_statistics() -> Dict[str, Any]:
        """Simple simulation statistics fallback"""
        return {
            "total_simulations": 0,
            "active_simulations": 0,
            "queue_size": 0,
            "status_breakdown": {},
            "type_breakdown": {},
            "performance": {
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "average_confidence": 0.0,
                "average_relevance": 0.0
            },
            "max_workers": 1,
            "max_concurrent": 1
        }

    @staticmethod
    def create_simulation(simulation_type: str, input_data: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Simple simulation creation fallback"""
        return f"sim_{hash(str(input_data))}"

    @staticmethod
    def wait_for_simulation(sim_id: str, timeout: float = 30.0) -> Any:
        """Simple simulation wait fallback"""
        return type("SimulationResult", (), {
            "simulation_type": SimulationType.SCENARIO_EXPLORATION,
            "confidence": 0.7,
            "reasoning": "Fallback simulation completed",
            "outcome": {"result": "completed"}
        })()

    @staticmethod
    def get_simulation_result(sim_id: str) -> Any:
        """Simple simulation result fallback"""
        return type("SimulationResult", (), {
            "instance_id": sim_id,
            "simulation_type": SimulationType.SCENARIO_EXPLORATION,
            "confidence": 0.7,
            "execution_time": 1.0,
            "reasoning": "Fallback simulation result",
            "outcome": {"result": "completed"}
        })()

    @staticmethod
    def clear_completed_simulations() -> None:
        """Simple clear simulations fallback"""
        pass

def cached_method(func=None, **kwargs):
    """Simple cache decorator fallback that accepts any parameters"""
    if func is None:
        return lambda f: f  # Return decorator factory
    return func  # Return function unchanged

# ============================================================================
# EXTERNAL DEPENDENCIES
# ============================================================================
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("⚠️  Missing: pyyaml. Install with: pip install pyyaml")
    yaml = None
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

try:
    from openai import APIError, AuthenticationError, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Tool Framework
try:
    from tools.examples import *  # Load all built-in tools
    from tools.registry import get_registry
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Tools module not available: {e}")
    TOOLS_AVAILABLE = False

    class DummyRegistry:
        def has_tool(self, name):
            return False

        def list_tools(self):
            return []

        def get(self, name):
            return None

        def get_openai_schemas(self):
            return []  # Empty list for no tools

    def get_registry():
        return DummyRegistry()

# Glimpse Suite - Streamlined imports with fallback
try:
    from glimpse import (ClarifierEngine, Draft, GlimpseEngine, GlimpseResult,
                         PrivacyGuard)
    GLIMPSE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Glimpse system unavailable: {e}")
    GLIMPSE_AVAILABLE = False

    class Draft:
        def __init__(self, input_text: str, goal: str, constraints: str = ""):
            self.input_text = input_text
            self.goal = goal
            self.constraints = constraints

    class GlimpseResult:
        def __init__(self, sample: str, essence: str, **kwargs):
            self.sample = sample
            self.essence = essence
            self.status = "aligned"
            self.attempt = 1
            self.delta = None
            self.status_history = ["aligned"]
            self.stale = False

    class GlimpseEngine:
        def __init__(self, **kwargs):
            self.privacy_guard = kwargs.get('privacy_guard', PrivacyGuard())

        async def glimpse(self, draft: Draft) -> GlimpseResult:
            return GlimpseResult(
                sample=(
                    draft.input_text[:100] + "..."
                    if len(draft.input_text) > 100
                    else draft.input_text
                ),
                essence=f"Intent: {draft.goal}; constraints: {draft.constraints or 'none'}",
            )
        
        def commit(self, draft: Draft) -> None:
            pass
        
        def set_essence_only(self, enabled: bool) -> None:
            pass

    class ClarifierEngine:
        def __init__(self, use_enhanced_mode: bool = False):
            pass

# Action Execution
try:
    from app.actions import ActionExecutor
    ACTIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Action executor not available: {e}")
    ACTIONS_AVAILABLE = False

# Knowledge Management
try:
    from app.knowledge import KnowledgeManager
    KNOWLEDGE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Knowledge manager not available: {e}")
    KNOWLEDGE_AVAILABLE = False

# Filesystem Tools
try:
    from app.filesystem import FilesystemTools
    FILESYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Filesystem tools not available: {e}")
    FILESYSTEM_AVAILABLE = False

# Agent Workflow System
try:
    from app.agents import AgentWorkflow
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent workflow not available: {e}")
    AGENTS_AVAILABLE = False

# Dynamic Model Router
try:
    from app.model_router import ModelMetrics, ModelResponseCache, ModelRouter
    MODEL_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Model router not available: {e}")
    MODEL_ROUTER_AVAILABLE = False

# RAG System V2
try:
    from echoes.core.rag_v2 import OPENAI_RAG_AVAILABLE, create_rag_system
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAG V2 not available")

# API Integration for External Contact
try:
    import aiohttp
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("Warning: aiohttp not available. External API contact disabled.")

# ============================================================================
# PROMPT MANAGEMENT
# ============================================================================
def list_available_prompts() -> List[str]:
    prompts_dir = Path("prompts")
    if not prompts_dir.exists():
        print(f"No prompts directory found at {prompts_dir}")
        return []
    return [f.stem for f in prompts_dir.glob("*.yaml")]

def show_prompt_content(prompt_name: str) -> None:
    prompt_path = Path("prompts") / f"{prompt_name}.yaml"
    try:
        with open(prompt_path, encoding="utf-8") as f:
            content = f.read()
            print(f"\n=== {prompt_name} ===\n{content}\n" + "=" * 40)
    except Exception as e:
        print(f"Error loading prompt {prompt_name}: {e}")

def load_prompt(prompt_name: str) -> str:
    if not YAML_AVAILABLE:
        print(f"Warning: YAML not available, cannot load prompt {prompt_name}")
        return ""

    prompt_path = Path("prompts") / f"{prompt_name}.yaml"
    try:
        with open(prompt_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Handle both direct string prompts and structured YAML
            if isinstance(data, str):
                return data
            elif isinstance(data, dict) and "prompt" in data:
                return data["prompt"]
            elif isinstance(data, dict) and "directive" in data:
                return data["directive"]
            return str(data)  # Fallback to string representation
    except Exception as e:
        print(f"Warning: Could not load prompt {prompt_name}: {e}")
        return ""

# ============================================================================
# CORE CLASSES
# ============================================================================
class EnhancedStatusIndicator:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.current_phase = None
        self.current_step = 0
        self.total_steps = 0
        self.spinner_index = 0
        self.phase_start_time = None

    def start_phase(self, phase_name: str, total_steps: int = 0):
        if not self.enabled:
            return
        self.current_phase = phase_name
        self.total_steps = total_steps
        self.current_step = 0
        self.phase_start_time = time.time()
        if total_steps > 0:
            print(f"\n⚙️ {phase_name}")
        else:
            print(f"\n⚙️ {phase_name}...", end="", flush=True)

    def update_step(self, message: str, completed: bool = False):
        if not self.enabled:
            return

        if completed:
            self.current_step += 1
            icon = "✅"
            elapsed = (
                f"({(time.time() - self.phase_start_time)*1000:.0f}ms)"
                if self.phase_start_time
                else ""
            )
            if self.total_steps > 0:
                progress = f"[{self.current_step}/{self.total_steps}]"
                print(f"\r{icon} {progress} {message} {elapsed}")
            else:
                print(f"\r{icon} {message} {elapsed}")
        else:
            spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            icon = spinner[self.spinner_index % len(spinner)]
            self.spinner_index += 1
            if self.total_steps > 0:
                progress = f"[{self.current_step}/{self.total_steps}]"
                print(f"\r{icon} {progress} {message}", end="", flush=True)
            else:
                print(f"\r{icon} {message}...", end="", flush=True)

    def complete_phase(self, message: str = "Done"):
        if not self.enabled:
            return
        elapsed = (
            f"({(time.time() - self.phase_start_time)*1000:.0f}ms)"
            if self.phase_start_time
            else ""
        )
        print(f"\r✅ {message} {elapsed}")

    def error(self, message: str):
        if not self.enabled:
            return
        print(f"\r❌ Error: {message}")

class ContextManager:
    def __init__(self, max_history: int = 10, max_tokens: int = 8000):
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.conversations = {}  # session_id → messages

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        self.conversations[session_id].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # Keep only recent messages
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_history * 2 :
            ]

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if session_id not in self.conversations:
            return []

        messages = self.conversations[session_id]
        if limit:
            return messages[-limit * 2 :]  # * 2 for user + assistant pairs
        return messages[-self.max_history * 2 :]

    def clear_session(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]

class MemoryStore:
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_conversation(self, session_id: str, messages: List[Dict[str, Any]]):
        file_path = self.storage_path / f"{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "session_id": session_id,
                    "messages": messages,
                    "saved_at": datetime.now(UTC).isoformat(),
                },
                f,
                indent=2,
            )

    def load_conversation(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        file_path = self.storage_path / f"{session_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])

    def list_conversations(self) -> List[str]:
        return [f.stem for f in self.storage_path.glob("*.json")]

# ============================================================================
# MAIN ASSISTANT CLASS
# ============================================================================
class EchoesAssistantV2:
    """
    Enhanced AI Assistant with Tool Framework, RAG, Context Management, and ATLAS Integration.
    """

    def __init__(
        self,
        enable_rag: bool = True,
        enable_tools: bool = True,
        enable_streaming: bool = True,
        enable_status: bool = True,
        enable_glimpse: bool = True,
        enable_external_contact: bool = True,
        enable_value_system: bool = True,
        enable_atlas_integration: bool = True,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Initialize the enhanced assistant with ATLAS architecture patterns."""
        # Phase 1: Core Configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.model = model or "gpt-4o-mini"
        self.temperature = temperature or 0.7
        self.max_tokens = max_tokens
        self.use_responses_api = os.getenv("USE_RESPONSES_API", "true").lower() in ("1", "true", "yes")

        # OpenAI client
        self.client = OpenAI(api_key=self.api_key) if OPENAI_AVAILABLE else None

        # Dynamic Model Router and Metrics
        self.model_router = SimpleModelRouter() if not MODEL_ROUTER_AVAILABLE else None
        self.response_cache = SimpleModelResponseCache()
        self.model_metrics = SimpleModelMetrics() if not MODEL_ROUTER_AVAILABLE else None

        # Phase 2: Session Management
        self.session_id = session_id or f"session_{int(time.time())}"

        # Context management
        self.context_manager = ContextManager()
        self.memory_store = MemoryStore()

        # Load existing conversation if available
        saved_messages = self.memory_store.load_conversation(self.session_id)
        if saved_messages:
            self.context_manager.conversations[self.session_id] = saved_messages

        # Phase 3: Component Initialization
        # Initialize fallback engines
        self.personality_engine = SimplePersonalityEngine()
        self.cross_reference_system = SimpleCrossReferenceSystem()
        self.intent_engine = SimpleIntentEngine()
        self.thought_tracker = SimpleThoughtTracker()

        # Tool framework
        self.enable_tools = enable_tools
        self.tool_registry = get_registry() if enable_tools else None

        # Action execution
        self.action_executor = SimpleActionExecutor()

        # Knowledge management
        self.knowledge_manager = SimpleKnowledgeManager()

        # Filesystem tools
        self.fs_tools = SimpleFilesystemTools(root_dir=os.getcwd())

        # Agent workflow system
        self.agent_workflow = SimpleAgentWorkflow(self)

        # Quantum state management
        self.quantum_state_manager = SimpleQuantumStateManager()
        self.quantum_state_manager.initialize_quantum_states()

        # Phase 4: Advanced Features
        # RAG system
        self.enable_rag = enable_rag
        self.rag = None
        if self.enable_rag and RAG_AVAILABLE:
            try:
                rag_preset = "balanced"
                self.rag = create_rag_system(rag_preset)
                print(f"✓ RAG system initialized ({rag_preset} preset)")
            except Exception as e:
                print(f"⚠ RAG initialization failed: {e}")
                self.enable_rag = False

        # Configuration
        self.enable_streaming = enable_streaming
        self.enable_status = enable_status
        self.enable_value_system = enable_value_system
        self.value_system = None

        # Knowledge Graph Integration
        self.enable_knowledge_graph = False
        self.knowledge_graph = None

        # Multimodal Resonance Glimpse
        self.enable_multimodal_resonance = False
        self.multimodal_engine = None

        # Legal Safeguards & Enhanced Accounting
        self.enable_legal_safeguards = False
        self.legal_system = None
        self.accounting_system = None

        # Human-in-the-loop / policy configuration
        self.hitl_enabled = os.getenv("HITL_ENABLED", "false").lower() in ("1", "true", "yes")
        self.policy_model = "gpt-4o"

        # Glimpse Preflight System Integration
        self.enable_glimpse = enable_glimpse and GLIMPSE_AVAILABLE
        self.glimpse_engine = None
        self.glimpse_goal = ""
        self.glimpse_constraints = ""
        self.glimpse_enabled = False

        if self.enable_glimpse:
            try:
                self.glimpse_engine = GlimpseEngine()
                print("✓ Glimpse preflight system initialized")
            except Exception as e:
                print(f"⚠ Glimpse initialization failed: {e}")
                self.enable_glimpse = False

        # External API Contact System
        self.enable_external_contact = enable_external_contact and API_AVAILABLE
        self.api_endpoints = {
            "echoes_api": os.getenv("ECHOES_API_URL", "http://localhost:8000"),
            "patterns_endpoint": "/api/patterns/detect",
            "truth_endpoint": "/api/truth/verify",
            "websocket_endpoint": "/ws/stream",
        }

        # Default model
        self.default_model = "gpt-4o-mini"

        print(
            f"✓ Echoes Assistant V2 ready (session: {self.session_id}, responses_api: {self.use_responses_api}, glimpse: {self.enable_glimpse}, external_contact: {self.enable_external_contact})"
        )

    def add_knowledge(self, documents: List[Union[str, Dict[str, Any]]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add documents to the knowledge base."""
        if not self.enable_rag or not self.rag:
            return {"error": "RAG not enabled"}

        try:
            result = self.rag.add_documents(documents)
            return {
                "success": True,
                "documents_added": len(documents),
                "total_documents": result.get("total_chunks", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        stream: Optional[bool] = None,
        show_status: Optional[bool] = None,
        context_limit: int = 5,
        prompt_file: Optional[str] = None,
        require_approval: Optional[bool] = None,
    ) -> Union[str, Iterator[str]]:
        """Chat with the assistant."""
        import time
        chat_start_time = time.time()
        print(f"[DEBUG] chat() method called at {time.strftime('%H:%M:%S')}.{int(time.time() * 1000) % 1000:03d}")
        print(f"[DEBUG] message: '{message[:50]}...'")
        print(f"[DEBUG] stream: {stream}, show_status: {show_status}")

        try:
            # Update personality from user message
            self.personality_engine.update_from_interaction(message)

            # Analyze context for cross-references
            context = self.cross_reference_system.analyze_context(message)

            # Detect user intent and extract entities
            user_intent = self.intent_engine.detect_intent(message)
            user_entities = self.intent_engine.extract_entities(message)

            print(f"[DEBUG] Intent detected: {user_intent.type}, entities: {len(user_entities)}")

# ---------------------------------------------------------------------------
# Register the user's thought (single, correctly‑parenthesised ternary)
# ---------------------------------------------------------------------------
user_thought = self.thought_tracker.add_thought(
    thought_id=f"user_{len(self.thought_tracker.thought_metadata) + 1}_{int(time.time())}",
    content=message,
    thought_type=(
        ThoughtType.QUESTION
        if user_intent.type == IntentType.QUESTION
        else ThoughtType.OBSERVATION
    ),
    entities=[getattr(e, "text", str(e)) for e in user_entities],
    parent_thoughts=(
        list(self.thought_tracker.thought_metadata.keys())[-3:]
        if self.thought_tracker.thought_metadata
        else None
    ),
)

            # Catch conversation context for quick cross-referencing
            conversation_context = {
                "message": message,
                "intent": user_intent.type,
                "entities": [getattr(e, 'text', str(e)) for e in user_entities],
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
            }

            # Cache the conversation context
            conv_cache_key = catch_release(
                content=conversation_context,
                content_type=ContentType.CONVERSATION,
                cache_level=CacheLevel.SESSION,
            )

            # Quick cross-reference lookup for relevant context
            if user_entities:
                entity_names = [getattr(e, 'text', str(e)) for e in user_entities[:3]]  # Top 3 entities
                cross_refs = self.cross_reference_system.cross_reference(
                    query=" ".join(entity_names),
                    content_types=[ContentType.CONVERSATION, ContentType.CONTEXT],
                    max_results=3,
                    min_relevance=0.3
                )

                if cross_refs:
                    # Add cross-reference context to response generation
                    context["cached_references"] = [getattr(ref, 'content', str(ref)) for ref in cross_refs]

            # Start parallel simulations for possibility exploration
            simulation_configs = []

            # Scenario exploration simulation
            if user_intent.type in [
                IntentType.QUESTION,
                IntentType.ANALYSIS,
                IntentType.EXPLORATION,
            ]:
                simulation_configs.append(
                    {
                        "type": SimulationType.SCENARIO_EXPLORATION,
                        "input_data": {
                            "scenario": message,
                            "context": {"entities": [getattr(e, 'text', str(e)) for e in user_entities]},
                        },
                        "parameters": {"priority": 0.7, "timeout": 15},
                    }
                )

            # Outcome prediction simulation
            if user_intent.type in [IntentType.REQUEST, IntentType.CREATION]:
                simulation_configs.append(
                    {
                        "type": SimulationType.OUTCOME_PREDICTION,
                        "input_data": {
                            "action": message,
                            "context": {"intent": user_intent.type},
                        },
                        "parameters": {"priority": 0.8, "timeout": 20},
                    }
                )

            # Alternative paths simulation
            if user_intent.type in [IntentType.ANALYSIS, IntentType.COMPARISON]:
                simulation_configs.append(
                    {
                        "type": SimulationType.ALTERNATIVE_PATHS,
                        "input_data": {
                            "problem": message,
                            "current_approach": context.get("previous_context", ""),
                        },
                        "parameters": {"priority": 0.6, "timeout": 25},
                    }
                )

            # Context expansion simulation
            if len(user_entities) > 0:
                simulation_configs.append(
                    {
                        "type": SimulationType.CONTEXT_EXPANSION,
                        "input_data": {
                            "topic": " ".join([getattr(e, 'text', str(e)) for e in user_entities[:2]]),
                            "context": {"conversation": message},
                        },
                        "parameters": {"priority": 0.5, "timeout": 10},
                    }
                )

            # Start simulations in parallel
            simulation_ids = []
            for config in simulation_configs:
                sim_id = parallel_simulation.create_simulation(
                    simulation_type=config["type"],
                    input_data=config["input_data"],
                    parameters=config.get("parameters", {}),
                )
                simulation_ids.append(sim_id)

            # Add simulation IDs to context for later retrieval
            context["active_simulations"] = simulation_ids

            # Cache entities for quick lookup
            for entity in user_entities:
                catch_release(
                    content={
                        "text": getattr(entity, 'text', str(entity)),
                        "type": getattr(getattr(entity, 'type', None), 'value', 'UNKNOWN'),
                        "context": getattr(entity, 'context', ''),
                        "confidence": getattr(entity, 'confidence', 0.5),
                    },
                    content_type=ContentType.ENTITY,
                    cache_level=CacheLevel.SHORT,
                )

            # Phase 1: Setup and Validation
            stream = stream if stream is not None else self.enable_streaming
            show_status = show_status if show_status is not None else self.enable_status
            require_approval = (
                require_approval if require_approval is not None else self.hitl_enabled
            )

            print(f"[DEBUG] Stream mode: {stream}, Status: {show_status}")

            # If streaming, delegate to streaming method
            if stream:
                print(f"[DEBUG] Delegating to _chat_streaming at {time.strftime('%H:%M:%S')}.{int(time.time() * 1000) % 1000:03d}")
                result = self._chat_streaming(
                    message,
                    system_prompt,
                    show_status,
                    context_limit,
                    prompt_file,
                    require_approval,
                    user_intent,
                    user_entities,
                )
                print(f"[DEBUG] _chat_streaming returned in {time.time() - chat_start_time:.2f}s")
                return result
            else:
                print(f"[DEBUG] Delegating to _chat_nonstreaming at {time.strftime('%H:%M:%S')}.{int(time.time() * 1000) % 1000:03d}")
                result = self._chat_nonstreaming(
                    message,
                    system_prompt,
                    show_status,
                    context_limit,
                    prompt_file,
                    require_approval,
                    user_intent,
                    user_entities,
                )
                print(f"[DEBUG] _chat_nonstreaming returned in {time.time() - chat_start_time:.2f}s")
                return result

        except Exception as e:
            error_msg = f"Error in chat method: {str(e)}"
            print(f"[DEBUG] Chat method exception after {time.time() - chat_start_time:.2f}s: {e}")
            if show_status:
                status = EnhancedStatusIndicator(enabled=show_status)
                status.error(error_msg)
            return error_msg

    def _chat_streaming(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        show_status: Optional[bool] = None,
        context_limit: int = 5,
        prompt_file: Optional[str] = None,
        require_approval: Optional[bool] = None,
        user_intent=None,
        user_entities=None,
    ) -> Iterator[str]:
        """Streaming chat implementation."""
        status = EnhancedStatusIndicator(
            enabled=show_status if show_status is not None else self.enable_status
        )

        try:
            # Build messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            history = self.context_manager.get_messages(
                self.session_id, limit=context_limit
            )
            messages.extend(
                [{"role": msg["role"], "content": msg["content"]} for msg in history]
            )

            # Add user message
            messages.append({"role": "user", "content": message})

            # Select the best model for this request
            selected_model = self.model_router.select_model(message, [])
            start_time = time.time()

            # Apply personality enhancements to the final response
            personality_prefix = self.personality_engine.generate_response_prefix("response")
            
            # Generate simple response for fallback
            if not self.client:
                simple_response = f"Hello! I received your message: '{message}'. This is a fallback response since OpenAI client is not available."
                if personality_prefix:
                    simple_response = personality_prefix + " " + simple_response
                enhanced_response = self.personality_engine.adapt_response_style(simple_response)
                
                # Add context information
                if user_intent and user_intent.confidence > 0.7:
                    intent_context = f"\n\n🧠 **Intent detected:** {user_intent.type.replace('_', ' ').title()}"
                    if user_intent.parameters:
                        intent_context += f" (Parameters: {', '.join(f'{k}: {v}' for k, v in user_intent.parameters.items())})"
                    enhanced_response += intent_context

                # Add entity insights
                if user_entities:
                    unique_entities = list(set(getattr(e, 'text', str(e)) for e in user_entities))
                    if len(unique_entities) > 1:
                        enhanced_response += f"\n\n📊 **Entities identified:** {', '.join(unique_entities[:5])}"

                # Save response to context
                self.context_manager.add_message(
                    self.session_id, "assistant", enhanced_response
                )

                # Stream the response
                for char in enhanced_response:
                    yield char
                return

            # If we have a client, make actual API call
            try:
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True,
                )

                # Stream response chunks
                full_response = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content

                # Apply personality enhancements to the final response
                personality_prefix = self.personality_engine.generate_response_prefix("response")
                enhanced_response = personality_prefix + " " + full_response
                enhanced_response = self.personality_engine.adapt_response_style(enhanced_response)

                # Add intent-aware context
                if user_intent and user_intent.confidence > 0.7:
                    intent_context = f"\n\n🧠 **Intent detected:** {user_intent.type.replace('_', ' ').title()}"
                    if user_intent.parameters:
                        intent_context += f" (Parameters: {', '.join(f'{k}: {v}' for k, v in user_intent.parameters.items())})"
                    enhanced_response += intent_context

                # Add entity insights
                if user_entities:
                    unique_entities = list(set(getattr(e, 'text', str(e)) for e in user_entities))
                    if len(unique_entities) > 1:
                        enhanced_response += f"\n\n📊 **Entities identified:** {', '.join(unique_entities[:5])}"

                # Save response to context
                self.context_manager.add_message(
                    self.session_id, "assistant", enhanced_response
                )

                # Yield the enhanced content
                if enhanced_response != full_response:
                    for char in enhanced_response[len(full_response):]:
                        yield char

            except Exception as api_error:
                error_msg = f"API Error: {str(api_error)}"
                if status:
                    status.error(error_msg)
                yield error_msg

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if status:
                status.error(error_msg)
            yield error_msg

    def _chat_nonstreaming(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        show_status: Optional[bool] = None,
        context_limit: int = 5,
        prompt_file: Optional[str] = None,
        require_approval: Optional[bool] = None,
        user_intent=None,
        user_entities=None,
    ) -> str:
        """Non-streaming chat implementation."""
        try:
            # Build messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            history = self.context_manager.get_messages(
                self.session_id, limit=context_limit
            )
            messages.extend(
                [{"role": msg["role"], "content": msg["content"]} for msg in history]
            )

            # Add user message
            messages.append({"role": "user", "content": message})

            # Generate simple response for fallback
            if not self.client:
                simple_response = f"Hello! I received your message: '{message}'. This is a fallback response since OpenAI client is not available."
                
                # Apply personality enhancements
                personality_prefix = self.personality_engine.generate_response_prefix("response")
                if personality_prefix:
                    simple_response = personality_prefix + " " + simple_response
                enhanced_response = self.personality_engine.adapt_response_style(simple_response)
                
                # Add context information
                if user_intent and user_intent.confidence > 0.7:
                    intent_context = f"\n\n🧠 **Intent detected:** {user_intent.type.replace('_', ' ').title()}"
                    if user_intent.parameters:
                        intent_context += f" (Parameters: {', '.join(f'{k}: {v}' for k, v in user_intent.parameters.items())})"
                    enhanced_response += intent_context

                # Add entity insights
                if user_entities:
                    unique_entities = list(set(getattr(e, 'text', str(e)) for e in user_entities))
                    if len(unique_entities) > 1:
                        enhanced_response += f"\n\n📊 **Entities identified:** {', '.join(unique_entities[:5])}"

                # Save response to context
                self.context_manager.add_message(
                    self.session_id, "assistant", enhanced_response
                )
                return enhanced_response

            # If we have a client, make actual API call
            selected_model = self.model_router.select_model(message, [])
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            response_text = response.choices[0].message.content

            # Apply personality enhancements to the final response
            personality_prefix = self.personality_engine.generate_response_prefix("response")
            enhanced_response = personality_prefix + " " + response_text
            enhanced_response = self.personality_engine.adapt_response_style(enhanced_response)

            # Add intent-aware context
            if user_intent and user_intent.confidence > 0.7:
                intent_context = f"\n\n🧠 **Intent detected:** {user_intent.type.replace('_', ' ').title()}"
                if user_intent.parameters:
                    intent_context += f" (Parameters: {', '.join(f'{k}: {v}' for k, v in user_intent.parameters.items())})"
                enhanced_response += intent_context

            # Add entity insights
            if user_entities:
                unique_entities = list(set(getattr(e, 'text', str(e)) for e in user_entities))
                if len(unique_entities) > 1:
                    enhanced_response += f"\n\n📊 **Entities identified:** {', '.join(unique_entities[:5])}"

            # Save response to context
            self.context_manager.add_message(
                self.session_id, "assistant", enhanced_response
            )

            return enhanced_response

        except Exception as e:
            return f"Error: {str(e)}"

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history for the current session."""
        return self.context_manager.get_messages(self.session_id)

    def get_action_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.action_executor.get_action_history(limit)

    def get_action_summary(self) -> Dict[str, Any]:
        return self.action_executor.get_action_summary()

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List available tools, optionally filtered by category."""
        if hasattr(self, "tool_registry") and self.tool_registry:
            return self.tool_registry.list_tools()
        return []

    @cached_method(max_size=10, ttl_seconds=300)  # Cache for 5 minutes
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the assistant."""
        return {
            "session_id": self.session_id,
            "messages": len(self.context_manager.get_messages(self.session_id)),
            "rag_enabled": self.enable_rag,
            "tools_enabled": self.enable_tools,
            "value_system_enabled": self.enable_value_system,
            "knowledge_graph_enabled": self.enable_knowledge_graph,
            "multimodal_resonance_enabled": self.enable_multimodal_resonance,
            "legal_safeguards_enabled": self.enable_legal_safeguards,
            "glimpse_enabled": self.enable_glimpse,
            "external_contact_enabled": self.enable_external_contact,
            "actions": self.get_action_summary(),
        }

    # Inventory methods
    def action_add_inventory(self, sku: str, name: str, category: str, quantity: int, location: str) -> Dict[str, Any]:
        """Add a new inventory item."""
        try:
            # Initialize inventory storage if needed
            if not hasattr(self, '_inventory'):
                self._inventory = {}

            # Create inventory item
            item = InventoryItem(
                sku=sku,
                name=name,
                category=category,
                quantity=quantity,
                location=location,
                created_at=utc_now_iso(),
                updated_at=utc_now_iso()
            )

            # Store item
            self._inventory[sku] = item

            return {
                "success": True,
                "action_id": f"inv_add_{sku}_{int(time.time())}",
                "item": item.to_dict()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add inventory item: {str(e)}"
            }

    def action_list_inventory(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List inventory items, optionally filtered by category."""
        try:
            # Initialize inventory storage if needed
            if not hasattr(self, '_inventory'):
                self._inventory = {}

            # Filter items by category if specified
            items = []
            for sku, item in self._inventory.items():
                if category is None or item.category == category:
                    items.append(item.to_dict())

            # Group by category for better display
            by_category = {}
            for item in items:
                cat = item['category']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

            return {
                "success": True,
                "total_items": len(items),
                "categories": list(by_category.keys()),
                "items_by_category": by_category,
                "all_items": items
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list inventory: {str(e)}"
            }

    def action_generate_report(self, report_type: str = "summary") -> Dict[str, Any]:
        """Generate inventory reports."""
        try:
            # Initialize inventory storage if needed
            if not hasattr(self, '_inventory'):
                self._inventory = {}

            items = list(self._inventory.values())

            if report_type == "summary":
                # Basic summary report
                total_items = len(items)
                total_quantity = sum(item.quantity for item in items)
                categories = set(item.category for item in items)
                locations = set(item.location for item in items)

                # Low stock items (quantity <= min_stock)
                low_stock = [item for item in items if item.quantity <= item.min_stock]

                report = {
                    "total_items": total_items,
                    "total_quantity": total_quantity,
                    "categories_count": len(categories),
                    "locations_count": len(locations),
                    "categories": list(categories),
                    "locations": list(locations),
                    "low_stock_items": len(low_stock),
                    "low_stock_list": [item.to_dict() for item in low_stock]
                }

            elif report_type == "low_stock":
                # Focus on low stock items
                low_stock = [item for item in items if item.quantity <= item.min_stock]
                report = {
                    "low_stock_count": len(low_stock),
                    "items": [item.to_dict() for item in low_stock]
                }

            elif report_type == "by_category":
                # Group by category with totals
                by_category = {}
                for item in items:
                    cat = item.category
                    if cat not in by_category:
                        by_category[cat] = {
                            "count": 0,
                            "total_quantity": 0,
                            "items": []
                        }
                    by_category[cat]["count"] += 1
                    by_category[cat]["total_quantity"] += item.quantity
                    by_category[cat]["items"].append(item.to_dict())

                report = {
                    "categories": by_category,
                    "total_categories": len(by_category)
                }

            else:
                report = {"error": f"Unknown report type: {report_type}"}

            return {
                "success": True,
                "report_type": report_type,
                "generated_at": utc_now_iso(),
                "data": report
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate report: {str(e)}"
            }

# ============================================================================
# INTERACTIVE MODE
# ============================================================================
def interactive_mode(system_prompt=None):
    print("\nCommands:")
    print("  'exit' or 'quit'     - Exit the assistant")
    print("  'history'            - Show conversation history")
    print("  'clear'              - Clear conversation history")
    print("  'tools'              - List available tools")
    print("  'stats'              - Show statistics")
    print("  'actions'            - Show action history")
    print("  'stream on/off'      - Toggle streaming")
    print("  'status on/off'      - Toggle status indicators")
    print("  'action add <sku> <name> <category> <quantity> <location> - Add inventory item")
    print("  'action list [category]' - List inventory items")
    print("  'action report [type]' - Generate inventory report")
    print("=" * 60 + "\n")

    try:
        assistant = EchoesAssistantV2(
            enable_rag=RAG_AVAILABLE,
            enable_tools=True,
            enable_streaming=True,
            enable_status=True,
        )

        streaming_enabled = True
        status_enabled = True

        # Initialize debug counter
        prompt_count = 1

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                command = user_input.lower()

                if command in ("exit", "quit"):
                    print("\n✓ Exiting Echoes Assistant V2...")
                    break

                if command == "history":
                    history = assistant.get_conversation_history()
                    print(f"\n📝 Conversation History ({len(history)} messages):")
                    for msg in history[-10:]:  # Show last 10
                        print(f"  {msg['role']}: {msg['content'][:100]}...")
                    continue

                if command == "clear":
                    assistant.context_manager.clear_session(assistant.session_id)
                    print("\n✓ Conversation history cleared")
                    continue

                if command == "tools":
                    tools = assistant.list_tools()
                    print(f"\n🔧 Available Tools ({len(tools)}):")
                    for tool in tools:
                        print(f"  • {tool}")
                    continue

                if command == "stats":
                    stats = assistant.get_stats()
                    print("\n📊 Statistics:")
                    print(json.dumps(stats, indent=2))
                    continue

                if command == "actions":
                    history = assistant.get_action_history(limit=10)
                    print(f"\n📋 Action History ({len(history)} actions):")
                    for action in history:
                        status_icon = "✓" if action.get("success", False) else "✗"
                        print(
                            f"  {status_icon} {action.get('action_id', 'unknown')}: {action.get('action_type', 'unknown')} ({action.get('duration_ms', 0):.1f}ms)"
                        )
                    summary = assistant.get_action_summary()
                    print("\n📊 Action Summary:")
                    print(
                        f"  Total: {summary.get('total_actions', 0)} | Success: {summary.get('successful', 0)} | Failed: {summary.get('failed', 0)}"
                    )
                    print(
                        f"  Success Rate: {summary.get('success_rate', 0):.1f}% | Avg Duration: {summary.get('avg_duration_ms', 0):.1f}ms"
                    )
                    continue

                if command.startswith("action "):
                    parts = command.split(maxsplit=1)[1].split()
                    if not parts:
                        print("Usage: action <add|list|report> [args]")
                        continue

                    subcommand = parts[0].lower() if parts else None
                    args = parts[1:] if len(parts) > 1 else []

                    if subcommand == "add":
                        # action add <sku> <name> <category> <quantity> <location>
                        if len(args) < 5:
                            print("Usage: action add <sku> <name> <category> <quantity> <location>")
                            continue
                        sku, name, category, quantity_str, location = args[0], ' '.join(args[1:-3]), args[-3], args[-2], args[-1]
                        try:
                            quantity = int(quantity_str)
                            result = assistant.action_add_inventory(sku, name, category, quantity, location)
                        except ValueError:
                            result = {"success": False, "error": "Invalid quantity - must be a number"}
                    elif subcommand == "list":
                        # action list [category]
                        category = args[0] if args else None
                        result = assistant.action_list_inventory(category)
                    elif subcommand == "report":
                        # action report [type]
                        report_type = args[0] if args else "summary"
                        result = assistant.action_generate_report(report_type)
                    else:
                        result = {"success": False, "error": f"Unknown subcommand: {subcommand}"}

                    # Display result
                    if result["success"]:
                        print(f"\n📊 Result:\n{json.dumps(result, indent=2)}")
                    else:
                        print(f"  Error: {result['error']}")
                    continue

                if command == "stream on":
                    streaming_enabled = True
                    assistant.enable_streaming = True
                    print("✓ Streaming enabled")
                    continue

                if command == "stream off":
                    streaming_enabled = False
                    assistant.enable_streaming = False
                    print("✓ Streaming disabled")
                    continue

                if command == "status on":
                    status_enabled = True
                    assistant.enable_status = True
                    print("✓ Status indicators enabled")
                    continue

                if command == "status off":
                    status_enabled = False
                    assistant.enable_status = False
                    print("✓ Status indicators disabled")
                    continue

                system_prompt_var = (
                    system_prompt if "system_prompt" in locals() else None
                )

                # DEBUG: Track entry into chat processing
                print(f"\n[DEBUG] Processing prompt {prompt_count}: '{user_input[:50]}...'")
                print(f"[DEBUG] Streaming enabled: {assistant.enable_streaming}")

                # Track context size before call
                try:
                    messages = assistant.context_manager.get_messages(assistant.session_id)
                    print(f"[DEBUG] Context size before call: {len(messages)} messages")
                    total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)
                    print(f"[DEBUG] Total context characters: {total_chars}")
                except Exception as ctx_e:
                    print(f"[DEBUG] Error getting context: {ctx_e}")

                # Track timing
                import time
                call_start_time = time.time()
                print(f"[DEBUG] Calling assistant.chat at {time.strftime('%H:%M:%S')}...")

                # Initialize response to prevent UnboundLocalError
                response = None

                try:
                    response = assistant.chat(
                        user_input,
                        system_prompt=system_prompt_var,
                        stream=assistant.enable_streaming,
                        show_status=assistant.enable_status,
                        context_limit=5,
                        require_approval=assistant.hitl_enabled,
                    )

                    call_duration = time.time() - call_start_time
                    print(f"[DEBUG] assistant.chat returned in {call_duration:.2f}s")
                    print(f"[DEBUG] Response type: {type(response)}")

                    if assistant.enable_streaming:
                        print("[DEBUG] Entering streaming output loop...")
                        try:
                            chunk_count = 0
                            stream_start = time.time()

                            for chunk in response:
                                chunk_count += 1
                                if chunk_count == 1:
                                    first_chunk_time = time.time() - stream_start
                                    print(f"[DEBUG] First chunk received after {first_chunk_time:.2f}s")

                                if chunk_count <= 5 or chunk_count % 100 == 0:
                                    print(f"[DEBUG] Chunk {chunk_count}: '{str(chunk)[:30]}...'")

                                print(chunk, end="", flush=True)

                            stream_duration = time.time() - stream_start
                            print(f"\n[DEBUG] Streaming completed: {chunk_count} chunks in {stream_duration:.2f}s")

                            if chunk_count == 0:
                                print("[DEBUG] No chunks received from stream!")
                                print("[No response received]", end="", flush=True)

                        except Exception as stream_error:
                            print(f"\n[DEBUG] Stream error after {time.time() - stream_start:.2f}s: {stream_error}")
                            print(f"[Stream error: {stream_error}]")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("[DEBUG] Non-streaming response received:")
                        print(f"[DEBUG] Response length: {len(str(response))} characters")
                        print(f"[DEBUG] Response preview: '{str(response)[:100]}...'")
                        print(response)

                except Exception as chat_error:
                    print(f"[DEBUG] Chat method error after {time.time() - call_start_time:.2f}s: {chat_error}")
                    print(f"[Error in chat: {chat_error}]")
                    import traceback
                    traceback.print_exc()

                # Track context size after call
                try:
                    messages_after = assistant.context_manager.get_messages(assistant.session_id)
                    print(f"[DEBUG] Context size after call: {len(messages_after)} messages")
                except Exception as ctx_after_e:
                    print(f"[DEBUG] Error getting context after: {ctx_after_e}")

                print(f"[DEBUG] Prompt {prompt_count} processing completed at {time.strftime('%H:%M:%S')}")
                prompt_count += 1

            except KeyboardInterrupt:
                print("\n\nUse 'exit' or 'quit' to end the session.")
                continue
            except Exception as e:
                print(f"\nError: {str(e)}")

    except Exception as e:
        print(f"Failed to initialize assistant: {str(e)}")
        sys.exit(1)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Echoes AI Assistant V2")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    chat_parser = subparsers.add_parser("chat", help="Start interactive chat mode")
    chat_parser.add_argument("--prompt", "-p", help="Prompt file name (without .yaml)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze a directory structure"
    )
    analyze_parser.add_argument("directory", help="Directory to analyze")
    analyze_parser.add_argument(
        "--output", "-o", help="File to write the analysis JSON"
    )
    analyze_parser.add_argument(
        "--depth", "-d", type=int, default=10, help="Maximum directory depth"
    )

    default_parser = subparsers.add_parser("run", help="Run a single prompt")
    default_parser.add_argument(
        "message", nargs=argparse.REMAINDER, help="Message to send to the assistant"
    )
    default_parser.add_argument(
        "--prompt", "-p", help="Prompt file name (without .yaml)"
    )

    args = parser.parse_args()

    if not args.command:
        interactive_mode()
        sys.exit(0)

    if args.command == "chat":
        prompt_content = load_prompt(args.prompt) if args.prompt else None
        interactive_mode(system_prompt=prompt_content)
    elif args.command == "run":
        if not args.message:
            print(
                "No message provided. Use: python atlas.py run <your message>"
            )
            sys.exit(1)
        try:
            assistant = EchoesAssistantV2()
            system_prompt = load_prompt(args.prompt) if args.prompt else None
            response = assistant.chat(
                " ".join(args.message), system_prompt=system_prompt, stream=False
            )
            print(response)
        except Exception as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        parser.print_help()
