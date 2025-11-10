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

# ============================================================================
# Standard library imports
# ============================================================================
import os
import sys
import json
import hashlib
import uuid
import time

# Import numpy for calculations
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    print("Warning: numpy not available, using fallback calculations")
    NUMPY_AVAILABLE = False

    # Fallback mean function
    def mean(data):
        return sum(data) / len(data) if data else 0

    np = type("obj", (object,), {"mean": mean})()
import re
import asyncio

# Import timedelta from datetime
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Iterator, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from core_modules.caching import cached_method
from core_modules.context_manager import ContextManager
from core_modules.model_router import ModelRouter
from core_modules.metrics import ModelMetrics
from core_modules.dynamic_error_handler import error_handler
from core_modules.personality_engine import personality_engine
from core_modules.cross_reference_system import cross_reference_system
from core_modules.intent_awareness_engine import intent_engine, IntentType, EntityType
from core_modules.train_of_thought_tracker import thought_tracker, ThoughtType, LinkType
from core_modules.humor_engine import humor_engine, PressureLevel, HumorType
from core_modules.catch_release_system import catch_release, CacheLevel, ContentType
from core_modules.parallel_simulation_engine import (
    parallel_simulation,
    SimulationType,
    SimulationStatus,
)
from functools import wraps
from enum import Enum

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    print("⚠️  Missing: pyyaml. Install with: pip install pyyaml")
    yaml = None
    YAML_AVAILABLE = False

# Core dependencies
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# Tool Framework
try:
    from tools.registry import get_registry
    from tools.examples import *  # Load all built-in tools

    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Tools module not available: {e}")
    TOOLS_AVAILABLE = False

    # Fallback dummy registry
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
    from glimpse import (
        GlimpseEngine,
        Draft,
        PrivacyGuard,
        GlimpseResult,
        ClarifierEngine,
    )

    GLIMPSE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Glimpse system unavailable: {e}")
    GLIMPSE_AVAILABLE = False

    # Fallback dummy classes
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

    class PrivacyGuard:
        def commit(self, result):
            pass

    class GlimpseEngine:
        def __init__(self, **kwargs):
            self.privacy_guard = PrivacyGuard()

        async def glimpse(self, draft: Draft) -> GlimpseResult:
            return GlimpseResult(
                sample=(
                    draft.input_text[:100] + "..."
                    if len(draft.input_text) > 100
                    else draft.input_text
                ),
                essence=f"Intent: {draft.goal}; constraints: {draft.constraints or 'none'}",
            )


# Action Execution
try:
    from app.actions import ActionExecutor

    ACTIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Action executor not available: {e}")
    ACTIONS_AVAILABLE = False

    class ActionExecutor:
        def execute_tool_action(self, *args, **kwargs):
            return None


# Knowledge Management
try:
    from app.knowledge import KnowledgeManager

    KNOWLEDGE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Knowledge manager not available: {e}")
    KNOWLEDGE_AVAILABLE = False

    class KnowledgeManager:
        pass


# Filesystem Tools
try:
    from app.filesystem import FilesystemTools

    FILESYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Filesystem tools not available: {e}")
    FILESYSTEM_AVAILABLE = False

    class FilesystemTools:
        def __init__(self, *args, **kwargs):
            pass


# Agent Workflow System
try:
    from app.agents import AgentWorkflow

    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent workflow not available: {e}")
    AGENTS_AVAILABLE = False

    class AgentWorkflow:
        def __init__(self, *args, **kwargs):
            pass


# Dynamic Model Router
try:
    from app.model_router import ModelRouter, ModelResponseCache, ModelMetrics

    MODEL_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Model router not available: {e}")
    MODEL_ROUTER_AVAILABLE = False

    class ModelRouter:
        pass

    class ModelResponseCache:
        pass

    class ModelMetrics:
        pass


# Quantum State Management
try:
    from misc.quantum_state.quantum_state_manager import QuantumStateManager

    QUANTUM_STATE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Quantum state manager not available: {e}")
    QUANTUM_STATE_AVAILABLE = False

    # Fallback dummy class
    class QuantumStateManager:
        def initialize_quantum_states(self):
            pass


# Value System Integration
try:
    from app.values import get_value_system

    VALUES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Value system not available: {e}")
    VALUES_AVAILABLE = False

    def get_value_system():
        return None


# Knowledge Graph Integration
try:
    from knowledge_graph import (
        get_knowledge_graph,
        KnowledgeNode,
        KnowledgeRelation,
        MemoryFragment,
    )

    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Knowledge graph not available: {e}")
    KNOWLEDGE_GRAPH_AVAILABLE = False

    def get_knowledge_graph():
        return None

    KnowledgeNode = None
    KnowledgeRelation = None
    MemoryFragment = None

# Multimodal Resonance Glimpse
try:
    from multimodal_resonance import (
        get_multimodal_resonance_engine,
        ModalityVector,
        MultimodalMemory,
    )

    MULTIMODAL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Multimodal resonance not available: {e}")
    MULTIMODAL_AVAILABLE = False

    def get_multimodal_resonance_engine():
        return None

    ModalityVector = None
    MultimodalMemory = None

# Legal Safeguards & Enhanced Accounting
try:
    from legal_safeguards import (
        get_cognitive_accounting,
        CognitiveEffortMetrics,
        ConsentType,
        ProtectionLevel,
    )

    LEGAL_SAFEGUARDS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Legal safeguards not available: {e}")
    LEGAL_SAFEGUARDS_AVAILABLE = False

    def get_cognitive_accounting():
        return None

    CognitiveEffortMetrics = None
    ConsentType = None
    ProtectionLevel = None

try:
    from enhanced_accounting import get_enhanced_accounting, ValueType, AccountingPeriod

    ENHANCED_ACCOUNTING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced accounting not available: {e}")
    ENHANCED_ACCOUNTING_AVAILABLE = False

    def get_enhanced_accounting():
        return None

    ValueType = None
    AccountingPeriod = None

# API Integration for External Contact
try:
    import aiohttp
    import asyncio
    from typing import Dict, Any, Optional, List, Iterator, Union

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("Warning: aiohttp not available. External API contact disabled.")

# RAG System V2
try:
    from echoes.core.rag_v2 import create_rag_system, OPENAI_RAG_AVAILABLE

    RAG_AVAILABLE = True
    if OPENAI_RAG_AVAILABLE:
        print("")
    else:
        print("")
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAG V2 not available")

# Load environment variables
load_dotenv()


# Load prompts
def list_available_prompts() -> List[str]:
    prompts_dir = Path("prompts")
    if not prompts_dir.exists():
        print(f"No prompts directory found at {prompts_dir}")
        return []

    return [f.stem for f in prompts_dir.glob("*.yaml")]


def show_prompt_content(prompt_name: str) -> None:
    prompt_path = Path("prompts") / f"{prompt_name}.yaml"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
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
        with open(prompt_path, "r", encoding="utf-8") as f:
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


# Configuration
MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000
MAX_TOOL_ITERATIONS = 5

# Status constants
STATUS_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
STATUS_COMPLETE = "✅"
STATUS_ERROR = ""
STATUS_WORKING = ""
STATUS_SEARCH = ""
STATUS_TOOL = ""


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
            print(f"\n{STATUS_WORKING} {phase_name}")
        else:
            print(f"\n{STATUS_WORKING} {phase_name}...", end="", flush=True)

    def update_step(self, message: str, completed: bool = False):
        if not self.enabled:
            return

        if completed:
            self.current_step += 1
            icon = STATUS_COMPLETE
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
            icon = STATUS_SPINNER[self.spinner_index % len(STATUS_SPINNER)]
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
        print(f"\r{STATUS_COMPLETE} {message} {elapsed}")

    def error(self, message: str):
        if not self.enabled:
            return
        print(f"\r{STATUS_ERROR} Error: {message}")


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
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep only recent messages
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_history * 2 :
            ]

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
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

    def save_conversation(self, session_id: str, messages: List[Dict]):
        file_path = self.storage_path / f"{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "session_id": session_id,
                    "messages": messages,
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                },
                f,
                indent=2,
            )

    def load_conversation(self, session_id: str) -> Optional[List[Dict]]:
        file_path = self.storage_path / f"{session_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])

    def list_conversations(self) -> List[str]:
        return [f.stem for f in self.storage_path.glob("*.json")]


class EchoesAssistantV2:
    """
    Enhanced AI Assistant with Tool Framework, RAG, and Context Management.

    Features:
    - Tool Framework Integration (50+ tools)
    - RAG V2 Knowledge Retrieval
    - Context Management
    - Streaming Responses
    - Status Indicators
    - Memory Persistence
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
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the enhanced assistant.

        Args:
            model: OpenAI model to use
            temperature: Response randomness (0-1)
            max_tokens: Maximum response length
            rag_preset: RAG configuration (fast/balanced/accurate)
            enable_rag: Enable semantic knowledge retrieval
            enable_tools: Enable tool framework
            enable_streaming: Enable streaming responses
            enable_status: Enable status indicators
            enable_value_system: Enable value-based response filtering
            session_id: Session ID for conversation persistence
        """
        # Phase 1: Core Configuration
        # OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Dynamic Model Router
        self.model_router = ModelRouter()
        self.response_cache = ModelResponseCache()
        self.model_metrics = ModelMetrics()

        # Available models for dynamic selection
        self.available_models = {
            "mini": "gpt-4o-mini",
            "standard": "gpt-4o",
            "search": "gpt-4o-search-preview",
            "specialist": "o3",
            "specialist_mini": "o3-mini",
        }
        self.default_model = self.available_models["mini"]

        # Phase 2: Session Management
        # Session management
        self.session_id = session_id or f"session_{int(time.time())}"

        # Context management
        self.context_manager = ContextManager()
        self.memory_store = MemoryStore()

        # Load existing conversation if available
        saved_messages = self.memory_store.load_conversation(self.session_id)
        if saved_messages:
            self.context_manager.conversations[self.session_id] = saved_messages

        # Phase 3: Component Initialization
        # Tool framework
        self.enable_tools = enable_tools
        self.tool_registry = None
        if enable_tools:
            self.tool_registry = get_registry()

            # Register all available tools
            if TOOLS_AVAILABLE:
                try:
                    from tools.examples import get_example_tools

                    example_tools = get_example_tools()
                    for name, desc, func in example_tools:
                        self.tool_registry.register_tool(name, desc, func)
                except ImportError:
                    pass

            print(f"✓ Loaded {len(self.tool_registry.list_tools())} tools")

        # Action execution
        self.action_executor = ActionExecutor()
        print("✓ Action executor initialized")

        # Knowledge management
        self.knowledge_manager = KnowledgeManager()
        print("✓ Knowledge manager initialized")

        # Filesystem tools
        self.fs_tools = FilesystemTools(root_dir=os.getcwd())
        print("✓ Filesystem tools initialized")

        # Agent workflow system
        self.agent_workflow = AgentWorkflow(self)
        print("✓ Agent workflow system initialized")

        # Quantum state management
        self.quantum_state_manager = QuantumStateManager()
        if QUANTUM_STATE_AVAILABLE:
            self.quantum_state_manager.initialize_quantum_states()
            print("✓ Quantum state management initialized")
        else:
            print("⚠ Quantum state management not available")

        # Phase 4: Advanced Features
        # RAG system
        self.enable_rag = enable_rag  # Enable by default if requested
        self.rag = None
        if self.enable_rag:
            if RAG_AVAILABLE:
                try:
                    rag_preset = "balanced"  # Default preset
                    self.rag = create_rag_system(rag_preset)
                    print(f"✓ RAG system initialized ({rag_preset} preset)")
                except Exception as e:
                    print(f"⚠ RAG initialization failed: {e}")
                    self.enable_rag = False
            else:
                print("⚠ RAG system not available")
                self.enable_rag = False

        # Configuration
        self.enable_streaming = enable_streaming
        self.enable_status = enable_status
        self.enable_value_system = enable_value_system

        # Value System Integration
        self.value_system = None
        self.enable_value_system = enable_value_system  # Enable by default if requested
        if self.enable_value_system:
            if VALUES_AVAILABLE:
                try:
                    self.value_system = get_value_system()
                    if self.value_system:
                        print("✓ Value system initialized")
                    else:
                        print("⚠ Value system returned None")
                        self.enable_value_system = False
                except Exception as e:
                    print(f"⚠ Value system initialization failed: {e}")
                    self.enable_value_system = False
            else:
                print("⚠ Value system not available")
                self.enable_value_system = False

        # Knowledge Graph Integration
        self.enable_knowledge_graph = KNOWLEDGE_GRAPH_AVAILABLE
        if self.enable_knowledge_graph:
            self.knowledge_graph = get_knowledge_graph()
            if self.knowledge_graph:
                print("✓ Knowledge graph system initialized")
            else:
                print("⚠ Knowledge graph system returned None")
                self.enable_knowledge_graph = False
        else:
            self.knowledge_graph = None
            print("⚠ Knowledge graph not available")

        # Multimodal Resonance Glimpse
        self.enable_multimodal_resonance = MULTIMODAL_AVAILABLE
        if self.enable_multimodal_resonance:
            self.multimodal_engine = get_multimodal_resonance_engine()
            if self.multimodal_engine:
                print("✓ Multimodal resonance Glimpse initialized")
            else:
                print("⚠ Multimodal resonance engine returned None")
                self.enable_multimodal_resonance = False
        else:
            self.multimodal_engine = None
            print("⚠ Multimodal resonance not available")

        # Legal Safeguards & Enhanced Accounting
        self.enable_legal_safeguards = (
            LEGAL_SAFEGUARDS_AVAILABLE and ENHANCED_ACCOUNTING_AVAILABLE
        )
        if self.enable_legal_safeguards:
            self.legal_system = get_cognitive_accounting()
            self.accounting_system = get_enhanced_accounting()
            if self.legal_system and self.accounting_system:
                print("✓ Legal safeguards and enhanced accounting initialized")
            else:
                print("⚠ Legal safeguards or accounting system returned None")
                self.enable_legal_safeguards = False
        else:
            self.legal_system = None
            self.accounting_system = None
            print("⚠ Legal safeguards and enhanced accounting not available")

        # Human-in-the-loop / policy configuration
        self.hitl_enabled = os.getenv("HITL_ENABLED", "false").lower() in (
            "1",
            "true",
            "yes",
        )
        self.policy_model = "gpt-4o"

        # Glimpse Preflight System Integration
        self.enable_glimpse = True  # Enable by default
        self.glimpse_engine = None
        self.glimpse_goal = ""
        self.glimpse_constraints = ""
        self.glimpse_enabled = False

        if self.enable_glimpse:
            # Initialize Glimpse Glimpse with privacy guard
            def _glimpse_commit_handler(draft: Draft) -> None:
                # Store committed glimpses for analysis
                try:
                    os.makedirs("results", exist_ok=True)
                    import json as _json
                    from datetime import datetime as _dt, timezone as _tz

                    rec = {
                        "ts": _dt.now(_tz.utc).isoformat(),
                        "input_text": draft.input_text,
                        "goal": draft.goal,
                        "constraints": draft.constraints,
                        "session_id": self.session_id,
                    }
                    with open(
                        os.path.join("results", "glimpse_commits.jsonl"),
                        "a",
                        encoding="utf-8",
                    ) as f:
                        f.write(_json.dumps(rec, ensure_ascii=False) + "\n")
                except Exception:
                    # Silent best-effort; never block user flow
                    pass

            try:
                self.glimpse_engine = GlimpseEngine(
                    privacy_guard=PrivacyGuard(on_commit=_glimpse_commit_handler),
                    enable_clarifiers=True,
                )
                # Update the clarifier engine to use enhanced mode
                if (
                    hasattr(self.glimpse_engine, "_clarifier_engine")
                    and self.glimpse_engine._clarifier_engine
                ):
                    self.glimpse_engine._clarifier_engine = ClarifierEngine(
                        use_enhanced_mode=True
                    )
                print("✓ Glimpse preflight system initialized")
            except Exception as e:
                print(f"⚠ Glimpse initialization failed: {e}")
                self.enable_glimpse = False

        # External API Contact System
        self.enable_external_contact = (
            enable_external_contact  # Enable by default if requested
        )
        self.api_endpoints = {
            "echoes_api": os.getenv("ECHOES_API_URL", "http://localhost:8000"),
            "patterns_endpoint": "/api/patterns/detect",
            "truth_endpoint": "/api/truth/verify",
            "websocket_endpoint": "/ws/stream",
        }

        if self.enable_external_contact:
            if API_AVAILABLE:
                print("✓ External API contact system initialized")
            else:
                print("⚠ External API contact not available (aiohttp missing)")
                self.enable_external_contact = False

        # API Configuration
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Default to Responses API (new standard) - migration complete!
        # Set USE_RESPONSES_API=false to use Chat Completions API if needed
        self.use_responses_api = os.getenv("USE_RESPONSES_API", "true").lower() in (
            "1",
            "true",
            "yes",
        )

        print(
            f"✓ Echoes Assistant V2 ready (session: {self.session_id}, responses_api: {self.use_responses_api}, glimpse: {self.enable_glimpse}, external_contact: {self.enable_external_contact})"
        )

    def add_knowledge(
        self, documents: List[Union[str, Dict]], metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add documents to the knowledge base.

        Args:
            documents: List of documents (strings or dicts with text/metadata)
            metadata: Optional metadata for all documents

        Returns:
            Result with statistics
        """
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

    def _convert_tools_to_responses_format(self, tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI tool schemas to Responses API format."""
        if not tools:
            return None

        responses_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                responses_tools.append(
                    {
                        "type": "function",
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {}),
                        "strict": func.get("strict", False),
                    }
                )

        return responses_tools

    def _convert_to_responses_input(self, messages: List[Dict]) -> List[Dict]:
        """Convert messages format to Responses API input format."""
        responses_input = []

        for msg in messages:
            if msg["role"] == "system":
                # System messages become developer messages in Responses API
                responses_input.append(
                    {"role": "developer", "type": "message", "content": msg["content"]}
                )
            elif msg["role"] == "user":
                responses_input.append(
                    {"role": "user", "type": "message", "content": msg["content"]}
                )
            elif msg["role"] == "assistant":
                # Check if it has tool calls
                if "tool_calls" in msg and msg["tool_calls"]:
                    # Assistant message with tool calls
                    content = [{"type": "output_text", "text": msg.get("content", "")}]
                    for tool_call in msg["tool_calls"]:
                        content.append(
                            {
                                "type": "tool_call",
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            }
                        )
                    responses_input.append(
                        {"role": "assistant", "type": "message", "content": content}
                    )
                else:
                    # Regular assistant message
                    responses_input.append(
                        {
                            "role": "assistant",
                            "type": "message",
                            "content": [
                                {"type": "output_text", "text": msg.get("content", "")}
                            ],
                        }
                    )
            elif msg["role"] == "tool":
                # Tool response messages
                responses_input.append(
                    {
                        "role": "tool",
                        "type": "message",
                        "content": [{"type": "result", "result": msg["content"]}],
                        "tool_call_id": msg.get("tool_call_id", ""),
                        "name": msg.get("name", ""),
                    }
                )

        return responses_input

    def _convert_to_chat_messages(self, responses_input: List[Dict]) -> List[Dict]:
        """Convert Responses API input format back to chat messages format."""
        messages = []

        for item in responses_input:
            if item["role"] == "developer":
                messages.append({"role": "system", "content": item["content"]})
            elif item["role"] == "user":
                messages.append({"role": "user", "content": item["content"]})
            elif item["role"] == "assistant":
                if isinstance(item["content"], list):
                    # Parse complex content
                    text_content = ""
                    tool_calls = []
                    for content_item in item["content"]:
                        if content_item["type"] == "output_text":
                            text_content = content_item["text"]
                        elif content_item["type"] == "tool_call":
                            # Convert to old format
                            tool_call = type(
                                "ToolCall",
                                (),
                                {
                                    "id": content_item["id"],
                                    "function": type(
                                        "Function",
                                        (),
                                        {
                                            "name": content_item["name"],
                                            "arguments": content_item["arguments"],
                                        },
                                    )(),
                                },
                            )()
                            tool_calls.append(tool_call)

                    msg = {"role": "assistant", "content": text_content}
                    if tool_calls:
                        msg["tool_calls"] = tool_calls
                    messages.append(msg)
                else:
                    messages.append({"role": "assistant", "content": item["content"]})
            elif item["role"] == "tool":
                messages.append(
                    {
                        "role": "tool",
                        "content": (
                            item["content"][0]["result"] if item["content"] else ""
                        ),
                        "tool_call_id": item.get("tool_call_id", ""),
                        "name": item.get("name", ""),
                    }
                )

        return messages

    def update_context(self, key: str, value: Any) -> Dict[str, Any]:
        """Update context information for the assistant.

        Args:
            key: Context key (e.g., 'current_project', 'working_directory')
            value: Context value

        Returns:
            Updated context dictionary
        """
        if not hasattr(self, "_context"):
            self._context = {}

        self._context[key] = value

        # Clear caches that depend on context
        if hasattr(self.get_context, "clear_cache"):
            self.get_context.clear_cache()
        if hasattr(self.get_stats, "clear_cache"):
            self.get_stats.clear_cache()

        return self._context.copy()

    @cached_method(max_size=20, ttl_seconds=60)  # Cache for 1 minute
    def get_context(self, key: Optional[str] = None) -> Any:
        """Get context information.

        Args:
            key: Specific context key to retrieve, or None for all context

        Returns:
            Context value or entire context dictionary
        """
        if not hasattr(self, "_context"):
            self._context = {}

        if key is None:
            return self._context.copy()
        return self._context.get(key)

    def get_context_summary(self) -> str:
        """Get a formatted summary of current context.

        Returns:
            Formatted string with context information
        """
        context = self.get_context()
        if not context:
            return "No context set"

        summary_lines = ["Current Context:"]
        for key, value in context.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            summary_lines.append(f"  {key}: {value_str}")

        return "\n".join(summary_lines)

    def save_context(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Save current context to a JSON file.

        Args:
            filepath: Optional path to save context. If None, uses default location.

        Returns:
            Result with success status and filepath
        """
        if filepath is None:
            # Default location in data directory
            data_dir = Path("data/context")
            data_dir.mkdir(parents=True, exist_ok=True)
            filepath = data_dir / f"context_{self.session_id}.json"

        try:
            context = self.get_context()
            context_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "metadata": {
                    "version": "1.0",
                    "assistant_version": getattr(self, "__version__", "unknown"),
                },
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(context_data, f, indent=2, default=str)

            return {
                "success": True,
                "filepath": str(filepath),
                "context_saved": len(context),
                "timestamp": context_data["timestamp"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_context(
        self, filepath: Optional[str] = None, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load context from a JSON file.

        Args:
            filepath: Optional path to load context from. If None, uses default location.
            session_id: Optional session ID to load. If provided, loads from default location.

        Returns:
            Result with success status and loaded context
        """
        if filepath is None and session_id is None:
            session_id = self.session_id

        if filepath is None:
            data_dir = Path("data/context")
            filepath = data_dir / f"context_{session_id}.json"

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                context_data = json.load(f)

            if "context" in context_data:
                context = context_data["context"]
                self._context = context.copy()

                return {
                    "success": True,
                    "filepath": str(filepath),
                    "context_loaded": len(context),
                    "timestamp": context_data.get("timestamp"),
                    "session_id": context_data.get("session_id"),
                }
            else:
                # Legacy format - context is at root level
                self._context = context_data.copy()
                return {
                    "success": True,
                    "filepath": str(filepath),
                    "context_loaded": len(context_data),
                    "legacy_format": True,
                }

        except FileNotFoundError:
            return {"success": False, "error": f"Context file not found: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        status: Optional[EnhancedStatusIndicator] = None,
    ) -> List[Dict]:
        if not self.enable_rag or not self.rag:
            return []

        try:
            if status:
                status.start_phase(f"{STATUS_SEARCH} Searching knowledge base", 0)

            # Try with top_k first, fallback if not supported
            try:
                result = self.rag.search(query, top_k=top_k)
            except (TypeError, ValueError) as e:
                # Fallback for RAG systems that don't support top_k
                if "top_k" in str(e) or "unexpected keyword argument" in str(e):
                    result = self.rag.search(query)
                else:
                    raise

            # Handle different result formats
            if isinstance(result, dict):
                results = result.get("results", [])
            elif isinstance(result, list):
                results = result
            else:
                results = []

            if status and results:
                status.complete_phase(f"Found {len(results)} relevant documents")

            return [
                {
                    "text": r.get("content", r.get("text", "")),
                    "score": r.get("score", 0.0),
                    "metadata": r.get("metadata", {}),
                }
                for r in results
            ]
        except Exception as e:
            if status:
                status.error(f"RAG search failed: {str(e)}")
            return []

    def _execute_tool_call(
        self, tool_call, status: Optional[EnhancedStatusIndicator] = None
    ) -> str:
        if not self.enable_tools or not self.tool_registry:
            error_msg = "Tool calling is disabled or registry not available"
            if status:
                status.error(error_msg)
            return f"Error: {error_msg}"

        function_name = tool_call.function.name
        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid tool arguments JSON: {str(e)}"
            if status:
                status.error(error_msg)
            return f"Error: {error_msg}"

        if status:
            args_str = ", ".join(
                [f"{k}={v}" for k, v in list(function_args.items())[:2]]
            )
            if len(function_args) > 2:
                args_str += "..."
            status.start_phase(
                f"{STATUS_TOOL} Executing {function_name}({args_str})", 0
            )

        try:
            tool = self.tool_registry.get_tool(function_name)
            if not tool:
                error_msg = f"Tool '{function_name}' not found in registry"
                if status:
                    status.error(error_msg)
                return f"Error: {error_msg}"

            result = tool.execute(**function_args)

            if status:
                status.complete_phase(f"{function_name} executed successfully")

            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            if status:
                status.error(error_msg)
            return f"Error: {error_msg}"

    def _improve_response(
        self, original: str, scores: Dict[str, float]
    ) -> Optional[str]:
        """Attempt to improve a response that scored poorly on values.

        Args:
            original: The original response text
            scores: Dictionary of value scores

        Returns:
            Improved response or None if improvement fails
        """
        try:
            # Identify which values need improvement
            improvements = []
            if scores.get("respect", 1.0) < 0.6:
                improvements.append("more respectful and considerate")
            if scores.get("accuracy", 1.0) < 0.6:
                improvements.append("more accurate and precise")
            if scores.get("helpfulness", 1.0) < 0.6:
                improvements.append("more helpful and actionable")

            if not improvements:
                return None

            # Create improvement prompt
            prompt = f"""Improve this response to be {', '.join(improvements)}.
            Keep the core meaning but enhance the tone and clarity.
            Preserve any code blocks or technical details exactly.
            
            Original response:
            {original}
            
            Improved response:"""

            # Get improved version
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temp for more conservative improvements
                max_tokens=len(original) + 100,  # Allow some expansion
            )

            improved = response.choices[0].message.content.strip()

            # Verify improvement
            new_scores = self.value_system.evaluate_response(improved)
            new_overall = self.value_system.get_overall_score(new_scores)

            # Only return if actually improved
            if new_overall > 0.6:  # Better than threshold
                return improved
            return None

        except Exception as e:
            print(f"⚠ Error improving response: {str(e)}")
            return None

    def provide_feedback(
        self, response_id: str, ratings: Dict[str, float], comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provide feedback on a specific assistant response.

        Args:
            response_id: ID of the response to rate
            ratings: Dictionary of value scores (0.0-1.0)
                    Example: {'respect': 0.8, 'accuracy': 0.9, 'helpfulness': 0.7}
            comment: Optional comment about the feedback

        Returns:
            Dictionary with status and any messages
        """
        if not self.enable_value_system or not self.value_system:
            return {"success": False, "error": "Value system is not enabled"}

        # Get the conversation history
        messages = self.context_manager.get_messages(self.session_id)

        # Find the target message
        target_msg = None
        for msg in reversed(messages):  # Search most recent first
            if msg.get("id") == response_id and msg.get("role") == "assistant":
                target_msg = msg
                break

        if not target_msg:
            return {"success": False, "error": "Response not found in current session"}

        # Update value system with feedback
        self.value_system.provide_feedback(
            response=target_msg["content"], user_feedback=ratings
        )

        # Log the feedback
        feedback_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "ratings": ratings,
            "comment": comment,
        }

        # Save feedback to a file
        feedback_dir = Path("data/feedback")
        feedback_dir.mkdir(exist_ok=True, parents=True)

        feedback_file = (
            feedback_dir / f"feedback_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        return {
            "success": True,
            "message": "Feedback received and processed",
            "current_values": self.value_system.get_values_summary(),
        }

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
        """Chat with the assistant.

        Args:
            message: User message
            system_prompt: Optional system prompt (overrides prompt_file if both provided)
            prompt_file: Name of the YAML file in prompts/ to use as system prompt
            stream: Override streaming setting
            show_status: Override status indicator setting
            context_limit: Number of previous exchanges to include

        Returns:
            Response string or iterator (if streaming)
        """
        try:
            # Update personality from user message
            personality_engine.update_from_interaction(message)

            # Analyze context for cross-references
            context = cross_reference_system.analyze_context(message)

            # Detect user intent and extract entities
            user_intent = intent_engine.detect_intent(message)
            user_entities = intent_engine.extract_entities(message)

            # Create thought node for user message
            user_thought = thought_tracker.add_thought(
                thought_id=f"user_{len(thought_tracker.thought_metadata) + 1}_{int(time.time())}",
                content=message,
                thought_type=(
                    ThoughtType.QUESTION
                    if user_intent.type == IntentType.QUESTION
                    else ThoughtType.OBSERVATION
                ),
                entities=[e.text for e in user_entities],
                parent_thoughts=(
                    list(thought_tracker.thought_metadata.keys())[-3:]
                    if thought_tracker.thought_metadata
                    else None
                ),
            )

            # Catch conversation context for quick cross-referencing
            conversation_context = {
                "message": message,
                "intent": user_intent.type.value,
                "entities": [e.text for e in user_entities],
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
            }

            # Cache the conversation context
            conv_cache_key = catch_release.catch(
                content=conversation_context,
                content_type=ContentType.CONVERSATION,
                cache_level=CacheLevel.SESSION,
                tags={"user_message", user_intent.type.value},
                importance=0.7,
                context={"entities": [e.text for e in user_entities]},
            )

            # Quick cross-reference lookup for relevant context
            if user_entities:
                entity_names = [e.text for e in user_entities[:3]]  # Top 3 entities
                cross_refs = catch_release.cross_reference(
                    query=" ".join(entity_names),
                    content_types=[ContentType.CONVERSATION, ContentType.CONTEXT],
                    max_results=3,
                )

                if cross_refs:
                    # Add cross-reference context to response generation
                    context["cached_references"] = [ref.content for ref in cross_refs]

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
                            "context": {"entities": [e.text for e in user_entities]},
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
                            "context": {"intent": user_intent.type.value},
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
                            "topic": " ".join([e.text for e in user_entities[:2]]),
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
                catch_release.catch(
                    content={
                        "text": entity.text,
                        "type": entity.type.value,
                        "context": entity.context,
                        "confidence": entity.confidence,
                    },
                    content_type=ContentType.ENTITY,
                    cache_level=CacheLevel.SHORT_TERM,
                    tags={"entity", entity.type.value},
                    importance=entity.confidence,
                )

            # Phase 1: Setup and Validation
            stream = stream if stream is not None else self.enable_streaming
            show_status = show_status if show_status is not None else self.enable_status
            require_approval = (
                require_approval if require_approval is not None else self.hitl_enabled
            )

            # If streaming, delegate to streaming method
            if stream:
                return self._chat_streaming(
                    message,
                    system_prompt,
                    show_status,
                    context_limit,
                    prompt_file,
                    require_approval,
                    user_intent,
                    user_entities,
                )
            else:
                return self._chat_nonstreaming(
                    message,
                    system_prompt,
                    show_status,
                    context_limit,
                    prompt_file,
                    require_approval,
                    user_intent,
                    user_entities,
                )
        except Exception as e:
            error_msg = f"Error in chat method: {str(e)}"
            if show_status:
                status = EnhancedStatusIndicator(enabled=show_status)
                status.error(error_msg)
            return f"Error: {error_msg}"

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
        # Status indicator
        status = EnhancedStatusIndicator(
            enabled=show_status if show_status is not None else self.enable_status
        )

        try:
            # Phase 2: Message Building
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

            # Retrieve context from RAG
            rag_context = []
            if self.enable_rag and self.rag:
                rag_context = self._retrieve_context(message, top_k=3, status=status)

                if rag_context:
                    context_text = "\n\n".join(
                        [
                            f"[Source {i+1}]: {ctx['text'][:200]}..."
                            for i, ctx in enumerate(rag_context)
                        ]
                    )
                    messages.append(
                        {
                            "role": "system",
                            "content": f"Relevant context from knowledge base:\n{context_text}",
                        }
                    )

            # Add user message
            messages.append({"role": "user", "content": message})

            # Phase 3: Tool Preparation
            # Get available tools
            tools = None
            if self.enable_tools and self.tool_registry:
                tools = self.tool_registry.get_openai_schemas()

            tool_calling_enabled = self.enable_tools and self.tool_registry is not None

            # Select the best model for this request
            selected_model = self.model_router.select_model(message, tools)
            start_time = time.time()

            # Convert messages to appropriate format
            if self.use_responses_api:
                api_input = self._convert_to_responses_input(messages)
                api_tools = self._convert_tools_to_responses_format(tools)
            else:
                api_input = messages
                api_tools = tools

            # Phase 4: Tool Execution Loop
            iteration = 0
            all_tool_results = []

            while iteration < MAX_TOOL_ITERATIONS:
                try:
                    # Make API call with dynamic model selection (NON-STREAMING)
                    if self.use_responses_api:
                        # Responses API
                        response = self.client.responses.create(
                            model=selected_model,
                            input=api_input,
                            tools=api_tools if tool_calling_enabled else None,
                            tool_choice=(
                                "auto" if (api_tools and tool_calling_enabled) else None
                            ),
                            temperature=self.temperature,
                            max_output_tokens=self.max_tokens,
                            stream=False,
                        )

                        # Extract content and tool calls from response.output
                        response_text = ""
                        tool_calls = []
                        for output_item in response.output:
                            if output_item.type == "message":
                                # Parse message content
                                for content_item in output_item.content:
                                    if content_item.type == "output_text":
                                        response_text += content_item.text
                                    elif content_item.type == "tool_call":
                                        # Convert to old format for compatibility
                                        tool_call = type(
                                            "ToolCall",
                                            (),
                                            {
                                                "id": content_item.id,
                                                "function": type(
                                                    "Function",
                                                    (),
                                                    {
                                                        "name": content_item.name,
                                                        "arguments": content_item.arguments,
                                                    },
                                                )(),
                                            },
                                        )()
                                        tool_calls.append(tool_call)
                    else:
                        # Chat Completions API
                        response = self.client.chat.completions.create(
                            model=selected_model,
                            messages=api_input,
                            tools=tools if tool_calling_enabled else None,
                            tool_choice=(
                                "auto" if (tools and tool_calling_enabled) else None
                            ),
                            temperature=self.temperature,
                            max_completion_tokens=(
                                self.max_tokens if "o3" in selected_model else None
                            ),
                            max_tokens=(
                                self.max_tokens if "o3" not in selected_model else None
                            ),
                            stream=False,
                        )

                        # Extract content and tool calls
                        response_message = response.choices[0].message
                        response_text = response_message.content or ""
                        tool_calls = getattr(response_message, "tool_calls", None) or []

                    # If no tool calls, we're done
                    if not tool_calls:
                        break

                    # Validate tool calling is enabled before processing
                    if not tool_calling_enabled:
                        if status:
                            status.error(
                                "Tool calling disabled but model returned tool calls"
                            )
                        break

                    # Add assistant message to conversation
                    if self.use_responses_api:
                        # For Responses API, convert back to chat format and add to input
                        api_input.append(
                            {
                                "role": "assistant",
                                "type": "message",
                                "content": [
                                    {"type": "output_text", "text": response_text}
                                ],
                            }
                        )
                        # Add tool calls to the message
                        if tool_calls:
                            api_input[-1]["content"].extend(
                                [
                                    {
                                        "type": "tool_call",
                                        "id": tc.id,
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments,
                                    }
                                    for tc in tool_calls
                                ]
                            )
                    else:
                        # For Chat Completions API, use the actual message
                        messages.append(
                            {
                                "role": "assistant",
                                "content": response_text,
                                "tool_calls": tool_calls,
                            }
                        )
                        api_input = messages

                    # Execute all tool calls
                    for tool_call in tool_calls:
                        function_response = self._execute_tool_call(tool_call, status)
                        all_tool_results.append(
                            {
                                "function": tool_call.function.name,
                                "result": function_response,
                                "success": not function_response.startswith("Error"),
                            }
                        )

                        if self.use_responses_api:
                            # Add tool response in Responses API format
                            api_input.append(
                                {
                                    "role": "tool",
                                    "type": "message",
                                    "content": [
                                        {"type": "result", "result": function_response}
                                    ],
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                }
                            )
                        else:
                            # Add tool response in Chat Completions format
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": tool_call.function.name,
                                    "content": function_response,
                                }
                            )
                            api_input = messages

                    iteration += 1

                except APIError as e:
                    error_msg = (
                        f"API error during tool calling with {selected_model}: {str(e)}"
                    )
                    if status:
                        status.error(error_msg)

                    # Try fallback to default model
                    if selected_model != self.default_model:
                        if status:
                            status.start_phase(
                                f"{STATUS_RETRY} Retrying with {self.default_model}", 0
                            )
                        try:
                            selected_model = self.default_model
                            # Retry the entire loop with default model
                            continue
                        except APIError as fallback_error:
                            error_msg = f"Fallback also failed: {str(fallback_error)}"
                            if status:
                                status.error(error_msg)
                            return error_msg
                    else:
                        return error_msg

            # Generate final response after tool execution
            if status:
                status.start_phase(f"{STATUS_WORKING} Generating final response", 0)

            if self.use_responses_api:
                # Responses API final response
                final_response = self.client.responses.create(
                    model=selected_model,
                    input=api_input,
                    tools=None,  # No tools for final response
                    tool_choice=None,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    stream=False,
                )

                # Extract final response content
                assistant_response = ""
                for output_item in final_response.output:
                    if output_item.type == "message":
                        # Parse message content
                        for content_item in output_item.content:
                            if content_item.type == "output_text":
                                assistant_response += content_item.text
            else:
                # Chat Completions API final response
                final_response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=api_input,
                    tools=None,  # No tools for final response
                    tool_choice=None,
                    temperature=self.temperature,
                    max_completion_tokens=(
                        self.max_tokens if "o3" in selected_model else None
                    ),
                    max_tokens=self.max_tokens if "o3" not in selected_model else None,
                    stream=False,
                )

                # Extract final response content
                assistant_response = final_response.choices[0].message.content

            # Record metrics for successful completion
            response_time = time.time() - start_time
            self.model_metrics.record_usage_sync(
                selected_model, response_time, success=True
            )

            if status:
                status.complete_phase("Response generated")

            # Add final assistant response to conversation history
            self.context_manager.add_message(
                self.session_id, "assistant", assistant_response
            )

            # Create thought node for assistant response
            response_thought_type = (
                ThoughtType.ANALYSIS
                if user_intent.type == IntentType.QUESTION
                else ThoughtType.SYNTHESIS
            )
            response_entities = intent_engine.extract_entities(assistant_response)

            response_thought = thought_tracker.add_thought(
                thought_id=f"assistant_{len(thought_tracker.thought_metadata) + 1}_{int(time.time())}",
                content=assistant_response,
                thought_type=response_thought_type,
                entities=[e.text for e in response_entities],
                parent_thoughts=[user_thought] if "user_thought" in locals() else None,
            )

            # Catch assistant response for continuity
            response_context = {
                "message": assistant_response,
                "thought_type": response_thought_type.value,
                "entities": [e.text for e in response_entities],
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "in_response_to": message[:100],  # First 100 chars of user message
            }

            # Cache the response context
            resp_cache_key = catch_release.catch(
                content=response_context,
                content_type=ContentType.RESPONSE,
                cache_level=CacheLevel.SESSION,
                tags={"assistant_response", response_thought_type.value},
                importance=0.6,
                context={"entities": [e.text for e in response_entities]},
            )

            # Create relationship between user message and assistant response
            if "conv_cache_key" in locals() and "resp_cache_key" in locals():
                catch_release.create_relationship(
                    conv_cache_key, resp_cache_key, strength=0.9
                )

            # Track conversation flow for cross-reference system
            cross_reference_system.track_conversation_flow(message, assistant_response)

            # Apply personality enhancements
            personality_prefix = personality_engine.generate_response_prefix("response")
            enhanced_response = personality_prefix + " " + assistant_response
            enhanced_response = personality_engine.adapt_response_style(
                enhanced_response
            )

            # Add intent-aware context
            if user_intent.confidence > 0.7:
                intent_context = f"\n\n🧠 **Intent detected:** {user_intent.type.value.replace('_', ' ').title()}"
                if user_intent.parameters:
                    intent_context += f" (Parameters: {', '.join(f'{k}: {v}' for k, v in user_intent.parameters.items())})"
                enhanced_response += intent_context

            # Add entity insights
            if user_entities:
                unique_entities = list(set(e.text for e in user_entities))
                if len(unique_entities) > 1:
                    enhanced_response += f"\n\n📊 **Entities identified:** {', '.join(unique_entities[:5])}"

            # Add cross-reference suggestions if relevant
            cross_refs = cross_reference_system.generate_cross_references(context)
            if (
                cross_refs
                and personality_engine.traits[
                    personality_engine.PersonalityTrait.CURIOSITY
                ]
                > 0.7
            ):
                suggestions = "\n\n💡 **Related connections to explore:**\n"
                for ref in cross_refs[:2]:
                    suggestions += f"• {ref['explanation']}\n"
                enhanced_response += suggestions

            # Add cached cross-references if available
            if context.get("cached_references"):
                cached_refs = context["cached_references"]
                if cached_refs and len(cached_refs) > 0:
                    enhanced_response += (
                        "\n\n🗂️ **Quick context from previous conversations:**"
                    )
                    for i, ref in enumerate(cached_refs[:2], 1):
                        if isinstance(ref, dict) and "message" in ref:
                            enhanced_response += (
                                f"\n{i}. Earlier discussed: {ref['message'][:100]}..."
                            )
                        elif isinstance(ref, str):
                            enhanced_response += (
                                f"\n{i}. Related context: {ref[:100]}..."
                            )

            # Add parallel simulation insights
            if context.get("active_simulations"):
                active_sim_ids = context["active_simulations"]
                simulation_insights = []

                # Wait for simulations to complete with timeout
                for sim_id in active_sim_ids:
                    result = parallel_simulation.wait_for_simulation(
                        sim_id, timeout=5.0
                    )
                    if result and result.confidence > 0.6:
                        simulation_insights.append(result)

                if simulation_insights:
                    enhanced_response += "\n\n🧠 **Parallel simulation insights:**"

                    for insight in simulation_insights[:3]:  # Top 3 insights
                        sim_type = insight.simulation_type.value.replace(
                            "_", " "
                        ).title()
                        enhanced_response += f"\n• **{sim_type}**: {insight.reasoning}"

                        # Add top possibility from simulation
                        if insight.possibilities:
                            top_possibility = insight.possibilities[0]
                            if isinstance(top_possibility, dict):
                                desc = top_possibility.get(
                                    "description", str(top_possibility)
                                )
                            else:
                                desc = str(top_possibility)
                            enhanced_response += f"\n  → {desc[:80]}..."

                        # Add confidence
                        enhanced_response += f" (confidence: {insight.confidence:.1%})"

                    # Add cross-reference enhancement if available
                    if any(
                        insight.simulation_type
                        == SimulationType.CROSS_REFERENCE_ENHANCEMENT
                        for insight in simulation_insights
                    ):
                        enhanced_response += "\n🔗 **Cross-references enhanced with simulation insights**"

            # Add thought chain insights if available
            critical_insights = thought_tracker.get_critical_insights()
            if critical_insights and user_intent.type in [
                IntentType.ANALYSIS,
                IntentType.EXPLORATION,
            ]:
                enhanced_response += (
                    "\n\n🔗 **Critical connections detected in our conversation:**"
                )
                for insight in critical_insights[:2]:
                    if insight.get("insight_type") == "cross_chain_connector":
                        enhanced_response += (
                            f"\n• Linked concepts across different discussion threads"
                        )

            # Update pressure metrics and add humor if appropriate
            pressure_level = humor_engine.update_pressure_metrics(
                request_count=1,
                error_occurred=False,
                response_time=(time.time() - start_time),
            )

            # Determine context for humor
            humor_context = ""
            if "error" in assistant_response.lower():
                humor_context = "error_occurred"
            elif (
                "completed" in assistant_response.lower()
                or "success" in assistant_response.lower()
            ):
                humor_context = "task_completed"
            elif pressure_level in [
                PressureLevel.HIGH,
                PressureLevel.CRITICAL,
                PressureLevel.OVERWHELMED,
            ]:
                humor_context = "high_load"

            # Add humor if appropriate
            if humor_engine.should_use_humor(pressure_level, humor_context):
                humor_response = humor_engine.generate_humor_response(
                    pressure_level, humor_context
                )
                if humor_response and humor_response.appropriateness > 0.7:
                    # Format humor based on delivery style
                    if humor_response.delivery_style == "playful":
                        humor_text = f"\n\n😄 **{humor_response.text}**"
                    elif humor_response.delivery_style == "gentle":
                        humor_text = f"\n\n💙 *{humor_response.text}*"
                    elif humor_response.delivery_style == "enthusiastic":
                        humor_text = f"\n\n🎉 **{humor_response.text}**"
                    else:
                        humor_text = f"\n\n😊 {humor_response.text}"

                    enhanced_response += humor_text

            # Add pressure indicator for very high load
            if pressure_level == PressureLevel.CRITICAL:
                enhanced_response += f"\n\n⚡ **Running at maximum capacity!** I'm handling this like a boss! 💪"
            elif pressure_level == PressureLevel.OVERWHELMED:
                enhanced_response += f"\n\n🔥 **Things are heating up!** Thanks for your patience - we're crushing this together! 🤝"

            return enhanced_response

        except AuthenticationError as e:
            error_msg = (
                f"Authentication Error: {str(e)}\nPlease check your OPENAI_API_KEY"
            )
            if status:
                status.error(error_msg)
            return error_msg
        except APIError as e:
            error_msg = f"API Error: {str(e)}"
            if status:
                status.error(error_msg)
            return error_msg
        except Exception as e:
            # Use dynamic error handler
            error_result = error_handler.handle_error(
                e,
                {
                    "method": "_chat_nonstreaming",
                    "message": message[:100],  # First 100 chars of message
                },
            )

            error_msg = f"Error: {str(e)}"
            if status:
                status.error(error_msg)

            # Update pressure metrics with error
            pressure_level = humor_engine.update_pressure_metrics(
                request_count=1,
                error_occurred=True,
                response_time=(time.time() - start_time),
            )

            # Add pressure-relief humor for errors
            if humor_engine.should_use_humor(pressure_level, "error_occurred"):
                humor_response = humor_engine.generate_humor_response(
                    pressure_level, "error_occurred"
                )
                if humor_response and humor_response.appropriateness > 0.6:
                    error_msg += f"\n\n😅 **{humor_response.text}**"

            # If auto-fix is available, suggest it
            if error_result.get("fix_attempted") and error_result.get("fix_result"):
                fix = error_result["fix_result"]
                if fix.get("auto_applicable"):
                    error_msg += (
                        f"\n\n🔧 **Auto-fix available:** {fix.get('suggestion', '')}"
                    )
                    if fix.get("code_fix"):
                        error_msg += f"\n```{fix.get('code_fix')}```"

            return error_msg

    def _chat_streaming(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        show_status: Optional[bool] = None,
        context_limit: int = 5,
        prompt_file: Optional[str] = None,
        require_approval: Optional[bool] = None,
    ) -> Iterator[str]:
        """Streaming chat implementation."""
        # Status indicator
        status = EnhancedStatusIndicator(
            enabled=show_status if show_status is not None else self.enable_status
        )

        try:
            # Phase 2: Message Building
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

            # Retrieve context from RAG
            rag_context = []
            if self.enable_rag and self.rag:
                rag_context = self._retrieve_context(message, top_k=3, status=status)

                if rag_context:
                    context_text = "\n\n".join(
                        [
                            f"[Source {i+1}]: {ctx['text'][:200]}..."
                            for i, ctx in enumerate(rag_context)
                        ]
                    )
                    messages.append(
                        {
                            "role": "system",
                            "content": f"Relevant context from knowledge base:\n{context_text}",
                        }
                    )

            # Add user message
            messages.append({"role": "user", "content": message})

            # Phase 3: Tool Preparation
            # Get available tools
            tools = None
            if self.enable_tools and self.tool_registry:
                tools = self.tool_registry.get_openai_schemas()

            tool_calling_enabled = self.enable_tools and self.tool_registry is not None

            # Select the best model for this request
            selected_model = self.model_router.select_model(message, tools)
            start_time = time.time()

            # Convert messages to appropriate format
            if self.use_responses_api:
                api_input = self._convert_to_responses_input(messages)
                api_tools = self._convert_tools_to_responses_format(tools)
            else:
                api_input = messages
                api_tools = tools

            # Phase 4: Tool Execution Loop
            iteration = 0
            all_tool_results = []

            while iteration < MAX_TOOL_ITERATIONS:
                try:
                    # Handle streaming with tool calling
                    response_text = ""
                    tool_calls = []

                    if self.use_responses_api:
                        # Responses API streaming
                        response = self.client.responses.create(
                            model=selected_model,
                            input=api_input,
                            tools=api_tools if tool_calling_enabled else None,
                            tool_choice=(
                                "auto" if (api_tools and tool_calling_enabled) else None
                            ),
                            temperature=self.temperature,
                            max_output_tokens=self.max_tokens,
                            stream=True,
                        )

                        # Stream responses from output
                        for chunk in response:
                            # Handle different chunk types in Responses API
                            if hasattr(chunk, "type"):
                                if chunk.type == "response.output_text.done":
                                    # Final text chunk
                                    if hasattr(chunk, "text"):
                                        response_text += chunk.text
                                        yield chunk.text
                                elif chunk.type == "response.output_item.added":
                                    # New output item added
                                    if hasattr(chunk, "item") and hasattr(
                                        chunk.item, "content"
                                    ):
                                        for content_item in chunk.item.content:
                                            if content_item.type == "output_text":
                                                response_text += content_item.text
                                                yield content_item.text
                                            elif content_item.type == "tool_call":
                                                # Convert to old format for compatibility
                                                tool_call = type(
                                                    "ToolCall",
                                                    (),
                                                    {
                                                        "id": content_item.id,
                                                        "function": type(
                                                            "Function",
                                                            (),
                                                            {
                                                                "name": content_item.name,
                                                                "arguments": content_item.arguments,
                                                            },
                                                        )(),
                                                    },
                                                )()
                                                tool_calls.append(tool_call)
                            elif hasattr(chunk, "output"):
                                # Fallback to old format if needed
                                for output_item in chunk.output:
                                    if output_item.type == "message":
                                        for content_item in output_item.content:
                                            if content_item.type == "output_text":
                                                response_text += content_item.text
                                                yield content_item.text
                                            elif content_item.type == "tool_call":
                                                # Convert to old format for compatibility
                                                tool_call = type(
                                                    "ToolCall",
                                                    (),
                                                    {
                                                        "id": content_item.id,
                                                        "function": type(
                                                            "Function",
                                                            (),
                                                            {
                                                                "name": content_item.name,
                                                                "arguments": content_item.arguments,
                                                            },
                                                        )(),
                                                    },
                                                )()
                                                tool_calls.append(tool_call)
                    else:
                        # Chat Completions API streaming
                        response = self.client.chat.completions.create(
                            model=selected_model,
                            messages=api_input,
                            tools=tools if tool_calling_enabled else None,
                            tool_choice=(
                                "auto" if (tools and tool_calling_enabled) else None
                            ),
                            temperature=self.temperature,
                            max_completion_tokens=(
                                self.max_tokens if "o3" in selected_model else None
                            ),
                            max_tokens=(
                                self.max_tokens if "o3" not in selected_model else None
                            ),
                            stream=True,
                        )

                        # Stream response chunks
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                response_text += chunk.choices[0].delta.content
                                yield chunk.choices[0].delta.content

                    # After streaming, check for tool calls in the accumulated response
                    if tool_calls:
                        # Process tool calls after streaming completes
                        # Validate tool calling is enabled before processing
                        if not tool_calling_enabled:
                            if status:
                                status.error(
                                    "Tool calling disabled but model returned tool calls"
                                )
                            # Save response and return
                            self.context_manager.add_message(
                                self.session_id, "assistant", response_text
                            )
                            self.model_metrics.record_usage_sync(
                                selected_model, time.time() - start_time, success=True
                            )
                            return  # Already yielded content

                        # Initialize status for tool execution
                        if status and iteration == 0:
                            status.start_phase(
                                f"{STATUS_TOOL} Planning and executing {len(tool_calls)} action(s)",
                                len(tool_calls),
                            )

                        # Add assistant message to conversation
                        if self.use_responses_api:
                            # For Responses API, convert back to chat format and add to input
                            api_input.append(
                                {
                                    "role": "assistant",
                                    "type": "message",
                                    "content": [
                                        {"type": "output_text", "text": response_text}
                                    ],
                                }
                            )
                            # Add tool calls to the message
                            if tool_calls:
                                api_input[-1]["content"].extend(
                                    [
                                        {
                                            "type": "tool_call",
                                            "id": tc.id,
                                            "name": tc.function.name,
                                            "arguments": tc.function.arguments,
                                        }
                                        for tc in tool_calls
                                    ]
                                )
                        else:
                            # For Chat Completions API, create a synthetic message since we streamed
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": response_text,
                                    "tool_calls": tool_calls,
                                }
                            )
                            api_input = messages

                        # Execute all tool calls
                        for tool_call in tool_calls:
                            function_response = self._execute_tool_call(
                                tool_call, status
                            )
                            all_tool_results.append(
                                {
                                    "function": tool_call.function.name,
                                    "result": function_response,
                                    "success": not function_response.startswith(
                                        "Error"
                                    ),
                                }
                            )

                            if self.use_responses_api:
                                # Add tool response in Responses API format
                                api_input.append(
                                    {
                                        "role": "tool",
                                        "type": "message",
                                        "content": [
                                            {
                                                "type": "result",
                                                "result": function_response,
                                            }
                                        ],
                                        "tool_call_id": tool_call.id,
                                        "name": tool_call.function.name,
                                    }
                                )
                            else:
                                # Add tool response in Chat Completions format
                                messages.append(
                                    {
                                        "tool_call_id": tool_call.id,
                                        "role": "tool",
                                        "name": tool_call.function.name,
                                        "content": function_response,
                                    }
                                )
                                api_input = messages

                        iteration += 1
                        continue  # Continue the tool calling loop
                    else:
                        # No tool calls, save response and return
                        self.context_manager.add_message(
                            self.session_id, "assistant", response_text
                        )
                        self.model_metrics.record_usage_sync(
                            selected_model, time.time() - start_time, success=True
                        )
                        return  # Already yielded content

                except APIError as e:
                    error_msg = (
                        f"API error during tool calling with {selected_model}: {str(e)}"
                    )
                    if status:
                        status.error(error_msg)

                    # Try fallback to default model
                    if selected_model != self.default_model:
                        if status:
                            status.start_phase(
                                f"{STATUS_RETRY} Retrying with {self.default_model}", 0
                            )
                        try:
                            selected_model = self.default_model
                            # Retry the entire loop with default model
                            continue
                        except APIError as fallback_error:
                            error_msg = f"Fallback also failed: {str(fallback_error)}"
                            if status:
                                status.error(error_msg)
                            yield error_msg
                            return
                    else:
                        yield error_msg
                        return

            # Generate final response after tool execution (streaming)
            if status:
                status.start_phase(f"{STATUS_WORKING} Generating final response", 0)

            if self.use_responses_api:
                # Responses API final response
                final_response = self.client.responses.create(
                    model=selected_model,
                    input=api_input,
                    tools=None,  # No tools for final response
                    tool_choice=None,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    stream=True,  # Stream the final response
                )

                # Stream final response content
                for chunk in final_response:
                    # Handle different chunk types in Responses API
                    if hasattr(chunk, "type"):
                        if chunk.type == "response.output_text.done":
                            # Final text chunk
                            if hasattr(chunk, "text"):
                                yield chunk.text
                        elif chunk.type == "response.output_item.added":
                            # New output item added
                            if hasattr(chunk, "item") and hasattr(
                                chunk.item, "content"
                            ):
                                for content_item in chunk.item.content:
                                    if content_item.type == "output_text":
                                        yield content_item.text
                    elif hasattr(chunk, "output"):
                        # Fallback to old format if needed
                        if chunk.output:
                            for output_item in chunk.output:
                                if output_item.type == "message":
                                    for content_item in output_item.content:
                                        if content_item.type == "output_text":
                                            yield content_item.text
            else:
                # Chat Completions API final response
                final_response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=api_input,
                    tools=None,  # No tools for final response
                    tool_choice=None,
                    temperature=self.temperature,
                    max_completion_tokens=(
                        self.max_tokens if "o3" in selected_model else None
                    ),
                    max_tokens=self.max_tokens if "o3" not in selected_model else None,
                    stream=True,  # Stream the final response
                )

                # Stream final response chunks
                for chunk in final_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            # Record metrics for successful completion
            response_time = time.time() - start_time
            self.model_metrics.record_usage_sync(
                selected_model, response_time, success=True
            )

            if status:
                status.complete_phase("Response generated")

        except AuthenticationError as e:
            error_msg = (
                f"Authentication Error: {str(e)}\nPlease check your OPENAI_API_KEY"
            )
            if status:
                status.error(error_msg)
            yield error_msg
        except APIError as e:
            error_msg = f"API Error: {str(e)}"
            if status:
                status.error(error_msg)
            yield error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if status:
                status.error(error_msg)
            yield error_msg

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history for the current session."""
        return self.context_manager.get_messages(self.session_id)

    def get_action_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.action_executor.get_action_history(limit)

    def get_action_summary(self) -> Dict[str, Any]:
        return self.action_executor.get_action_summary()

    def gather_knowledge(
        self,
        content: str,
        source: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
    ) -> str:
        return self.knowledge_manager.add_knowledge(content, source, category, tags)

    def search_knowledge(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        entries = self.knowledge_manager.search_knowledge(query, category, limit=limit)
        return [e.to_dict() for e in entries]

    def store_roi_analysis(
        self, roi_results: Dict[str, Any], analysis_id: Optional[str] = None
    ) -> str:
        return self.knowledge_manager.store_roi_analysis(roi_results, analysis_id)

    def search_roi_analyses(
        self,
        institution: Optional[str] = None,
        business_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        entries = self.knowledge_manager.search_roi_analyses(
            institution, business_type, limit
        )
        return [e.to_dict() for e in entries]

    def get_roi_summary(self) -> Dict[str, Any]:
        return self.knowledge_manager.get_roi_summary()

    def list_directory(
        self, dirpath: str, pattern: str = "*", recursive: bool = False
    ) -> Dict[str, Any]:
        return self.fs_tools.list_directory(dirpath, pattern, recursive)

    def get_directory_tree(
        self, dirpath: str, max_depth: int = 3, exclude_dirs: List[str] = None
    ) -> Dict[str, Any]:
        """Get a tree structure of a directory.

        Args:
            dirpath: Directory path to analyze
            max_depth: Maximum depth to traverse
            exclude_dirs: List of directory names to exclude

        Returns:
            Dictionary with tree structure and formatted output
        """
        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", ".pytest_cache", "node_modules"]

        try:
            path = Path(dirpath)
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {dirpath}"}

            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {dirpath}",
                }

            structure = self._get_directory_structure(path, max_depth, exclude_dirs)
            formatted = self._format_directory_structure(structure, max_lines=200)

            return {
                "success": True,
                "directory": dirpath,
                "structure": structure,
                "formatted_tree": formatted,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, filepath: str) -> Dict[str, Any]:
        return self.fs_tools.read_file(filepath)

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        return self.fs_tools.write_file(filepath, content)

    def search_files(
        self, query: str, search_path: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.fs_tools.search_files(query, search_path)

    def organize_roi_files(
        self, roi_results: Dict[str, Any], base_dir: str = "roi_analysis"
    ) -> Dict[str, Any]:
        return self.fs_tools.organize_roi_files(roi_results, base_dir)

    def run_workflow(self, workflow_type: str, **kwargs) -> Dict[str, Any]:
        if workflow_type == "triage":
            result = self.agent_workflow.run_triage_workflow(
                user_input=kwargs.get("user_input", ""), context=kwargs.get("context")
            )
        elif workflow_type == "comparison":
            result = self.agent_workflow.run_comparison_workflow(
                file1=kwargs.get("file1"), file2=kwargs.get("file2")
            )
        elif workflow_type == "data_enrichment":
            result = self.agent_workflow.run_data_enrichment_workflow(
                topic=kwargs.get("topic"), context=kwargs.get("context")
            )
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        return result

    @cached_method(max_size=10, ttl_seconds=300)  # Cache for 5 minutes
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the assistant."""
        stats = {
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
            "knowledge": self.knowledge_manager.get_stats(),
            "knowledge_graph_stats": (
                self.knowledge_graph.get_stats()
                if hasattr(self, "knowledge_graph")
                and hasattr(self.knowledge_graph, "get_stats")
                else {}
            ),
        }

        # Add multimodal resonance stats if available
        if self.enable_multimodal_resonance and hasattr(
            self.multimodal_engine, "get_resonance_statistics"
        ):
            mm_stats = self.multimodal_engine.get_resonance_statistics()
            if mm_stats["success"]:
                stats["multimodal_resonance_stats"] = mm_stats["statistics"]

        # Add legal safeguards and accounting stats if available
        if self.enable_legal_safeguards:
            legal_stats = self.get_legal_accounting_statistics()
            if legal_stats["success"]:
                stats["legal_safeguards_stats"] = legal_stats["legal_safeguards"]
                stats["enhanced_accounting_stats"] = legal_stats["enhanced_accounting"]
                stats["values_implementation"] = legal_stats["values_implementation"]

        if self.tool_registry and hasattr(self.tool_registry, "get_stats"):
            stats["tool_stats"] = self.tool_registry.get_stats()

        if self.rag:
            stats["rag_stats"] = (
                self.rag.get_stats() if hasattr(self.rag, "get_stats") else {}
            )

        if self.enable_value_system and self.value_system:
            stats["value_system"] = self.value_system.get_values_summary()

        return stats

    def update_quantum_state(
        self, key: str, value: Any, entangle_with: List[str] = None
    ) -> Dict[str, Any]:
        """Update a quantum state with optional entanglement.

        Args:
            key: State key to update
            value: New value for the state
            entangle_with: Keys to entangle with this state

        Returns:
            Result with success status and entangled states
        """
        try:
            self.quantum_state_manager.update_state(key, value, entangle_with)
            entangled = (
                self.quantum_state_manager.get_entangled_states(key)
                if entangle_with
                else {}
            )
            return {"success": True, "key": key, "value": value, "entangled": entangled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def measure_quantum_state(self, key: str) -> Dict[str, Any]:
        """Measure (read) a quantum state.

        Args:
            key: State key to measure

        Returns:
            Result with measured value
        """
        try:
            value = self.quantum_state_manager.measure_state(key)
            return {"success": True, "key": key, "value": value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_superposition(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple quantum states in superposition.

        Args:
            keys: List of state keys to retrieve

        Returns:
            Result with superposition of states
        """
        try:
            superposition = self.quantum_state_manager.get_superposition(keys)
            return {"success": True, "superposition": superposition}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_entangled_states(self, key: str) -> Dict[str, Any]:
        """Get states entangled with the given key.

        Args:
            key: State key to check entanglement for

        Returns:
            Result with entangled states
        """
        try:
            entangled = self.quantum_state_manager.get_entangled_states(key)
            return {"success": True, "key": key, "entangled": entangled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def transition_quantum_state(self) -> Dict[str, Any]:
        """Perform a probabilistic quantum state transition.

        Returns:
            Result with new state after transition
        """
        try:
            new_state = self.quantum_state_manager.transition_state()
            return {"success": True, "new_state": new_state}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_state_history(self, key: str) -> Dict[str, Any]:
        """Get historical values for a quantum state.

        Args:
            key: State key to get history for

        Returns:
            Result with state history
        """
        try:
            history = self.quantum_state_manager.get_state_history(key)
            return {"success": True, "key": key, "history": history}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_metrics(self) -> Dict[str, Any]:
        """Get quantum state management performance metrics.

        Returns:
            Result with performance metrics
        """
        try:
            metrics = self.quantum_state_manager.get_metrics()
            return {
                "success": True,
                "metrics": {
                    "total_updates": metrics.total_updates,
                    "total_measurements": metrics.total_measurements,
                    "average_transition_time": metrics.average_transition_time,
                    "entangled_states_count": metrics.entangled_states_count,
                    "last_updated": (
                        metrics.last_updated.isoformat()
                        if metrics.last_updated
                        else None
                    ),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List available tools, optionally filtered by category."""
        if hasattr(self, "tool_registry") and self.tool_registry:
            return self.tool_registry.list_tools()
        return []

    def save_quantum_state(
        self, filepath: str = "quantum_state_backup.json"
    ) -> Dict[str, Any]:
        """Save the current quantum state to a file.

        Args:
            filepath: Path to save the state file

        Returns:
            Result with save status
        """
        try:
            # Create a temporary quantum state manager with persistence
            temp_qsm = QuantumStateManager(persistence_file=filepath)
            # Copy current state
            temp_qsm.quantum_state._state = (
                self.quantum_state_manager.quantum_state._state.copy()
            )
            temp_qsm.quantum_state._entangled = (
                self.quantum_state_manager.quantum_state._entangled.copy()
            )
            temp_qsm.quantum_state._history = (
                self.quantum_state_manager.quantum_state._history.copy()
            )
            temp_qsm.state_machine = self.quantum_state_manager.state_machine
            temp_qsm.metrics = self.quantum_state_manager.metrics
            temp_qsm.interference_patterns = (
                self.quantum_state_manager.interference_patterns.copy()
            )

            temp_qsm.save_state()
            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_quantum_state(
        self, filepath: str = "quantum_state_backup.json"
    ) -> Dict[str, Any]:
        try:
            temp_qsm = QuantumStateManager(persistence_file=filepath)
            temp_qsm.load_state()

            # Copy loaded state to current manager
            self.quantum_state_manager.quantum_state._state = (
                temp_qsm.quantum_state._state.copy()
            )
            self.quantum_state_manager.quantum_state._entangled = (
                temp_qsm.quantum_state._entangled.copy()
            )
            self.quantum_state_manager.quantum_state._history = (
                temp_qsm.quantum_state._history.copy()
            )
            self.quantum_state_manager.state_machine = temp_qsm.state_machine
            self.quantum_state_manager.metrics = temp_qsm.metrics
            self.quantum_state_manager.interference_patterns = (
                temp_qsm.interference_patterns.copy()
            )

            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_directory(
        self,
        directory_path: str,
        output_file: Optional[str] = None,
        max_depth: int = 10,
        exclude_dirs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        exclude_dirs = exclude_dirs or [
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".venv",
            "env",
        ]
        directory_path = Path(directory_path).resolve()
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory not found: {directory_path}")

        system_prompt = load_prompt("directory_analyst")
        if not system_prompt:
            system_prompt = (
                "You are an expert codebase analyst. Analyze the directory structure and provide:\n"
                "1. Project structure overview\n"
                "2. Key components and their relationships\n"
                "3. Technology stack\n"
                "4. Potential issues and improvements\n"
                "5. Recommendations for better organization"
            )

        structure = self._get_directory_structure(
            directory_path, max_depth, exclude_dirs
        )
        stats = self._collect_file_stats(structure)

        file_types = sorted(
            stats["file_types"].items(), key=lambda item: item[1], reverse=True
        )
        top_file_types = file_types[:20]
        if len(file_types) > 20:
            remaining = sum(count for _, count in file_types[20:])
            top_file_types.append(("other", remaining))
        file_type_summary = (
            ", ".join(f"{ext or 'no-ext'}: {count}" for ext, count in top_file_types)
            or "None"
        )

        analysis = {
            "directory": str(directory_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_count": stats["file_count"],
            "dir_count": stats["dir_count"],
            "file_types": stats["file_types"],
            "structure": structure,
            "analysis": None,
        }

        directory_summary = self._format_directory_structure(structure, max_lines=400)
        top_directories_summary = self._summarize_top_directories(
            structure, max_entries=20
        )
        analysis_prompt = (
            f"Analyze this directory structure and provide a comprehensive report:\n\n"
            f"Directory: {directory_path}\n"
            f"Total Files: {analysis['file_count']}\n"
            f"Total Directories: {analysis['dir_count']}\n"
            f"File Types: {file_type_summary}\n\n"
            f"Top Directories:\n{top_directories_summary}\n\n"
            f"Directory Structure:\n{directory_summary}\n\n"
            "Please provide a detailed analysis including:\n"
            "1. Project structure overview\n"
            "2. Key components and their relationships\n"
            "3. Technology stack identification\n"
            "4. Potential issues and improvements\n"
            "5. Recommendations for better organization"
        )

        status = EnhancedStatusIndicator(enabled=self.enable_status)
        try:
            status.start_phase(f"{STATUS_WORKING} Preparing directory summary")
            status.complete_phase("Directory summary ready")
            status.start_phase(f"{STATUS_WORKING} Generating analysis")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
                max_completion_tokens=3000 if "o3" in self.model else None,
                max_tokens=3000 if "o3" not in self.model else None,
            )
            analysis["analysis"] = response.choices[0].message.content
            status.complete_phase("Analysis complete")

            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, indent=2)
                print(f"{STATUS_COMPLETE} Analysis saved to {output_path}")

            return analysis
        except Exception as e:
            status.error(str(e))
            raise

    def _get_directory_structure(
        self, root_path: Path, max_depth: int, exclude_dirs: List[str]
    ) -> Dict[str, Any]:
        root_path = root_path.resolve()
        structure = {
            "name": root_path.name,
            "type": "directory",
            "path": str(root_path),
            "size": 0,
            "file_count": 0,
            "dir_count": 0,
            "children": [],
        }

        if max_depth < 0:
            return structure

        try:
            for item in root_path.iterdir():
                if item.is_symlink():
                    continue
                if item.name in exclude_dirs or any(
                    item.match(pattern) for pattern in exclude_dirs
                ):
                    continue

                if item.is_file():
                    try:
                        size = item.stat().st_size
                    except (OSError, PermissionError):
                        size = 0
                    structure["size"] += size
                    structure["file_count"] += 1
                    structure["children"].append(
                        {
                            "name": item.name,
                            "type": "file",
                            "path": str(item),
                            "size": size,
                            "extension": item.suffix.lower(),
                        }
                    )
                elif item.is_dir():
                    child_structure = self._get_directory_structure(
                        item, max_depth - 1, exclude_dirs
                    )
                    structure["size"] += child_structure.get("size", 0)
                    structure["file_count"] += child_structure.get("file_count", 0)
                    structure["dir_count"] += 1 + child_structure.get("dir_count", 0)
                    structure["children"].append(child_structure)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not access {root_path}: {e}")

        return structure

    def _collect_file_stats(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        stats = {"file_count": 0, "dir_count": 0, "file_types": {}}

        def _walk(node: Dict[str, Any]):
            node_type = node.get("type")
            if node_type == "file":
                stats["file_count"] += 1
                ext = node.get("extension", "")
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
            elif node_type == "directory":
                stats["dir_count"] += 1
                for child in node.get("children", []):
                    _walk(child)

        _walk(structure)
        return stats

    def _format_directory_structure(
        self, structure: Dict[str, Any], indent: int = 0, max_lines: int = 400
    ) -> str:
        lines: List[str] = []
        truncated = False

        def _walk(node: Dict[str, Any], depth: int) -> None:
            nonlocal truncated
            if truncated:
                return

            prefix = "  " * depth
            if node.get("type") == "file":
                size_mb = node.get("size", 0) / (1024 * 1024)
                line = f"{prefix}📄 {node.get('name')} ({size_mb:.2f} MB)"
                lines.append(line)
            else:
                file_count = node.get("file_count", 0)
                dir_count = node.get("dir_count", 0)
                line = f"{prefix}📁 {node.get('name')}/"
                if file_count or dir_count:
                    line += f" ({file_count} files, {dir_count} dirs)"
                lines.append(line)
                for child in node.get("children", []):
                    if len(lines) >= max_lines:
                        truncated = True
                        return
                    _walk(child, depth + 1)

            if len(lines) >= max_lines:
                truncated = True

        _walk(structure, indent)

        if truncated:
            lines = lines[:max_lines]
            lines.append(f"... (truncated after {max_lines} lines)")

        return "\n".join(lines)

    def _summarize_top_directories(
        self, structure: Dict[str, Any], max_entries: int = 20
    ) -> str:
        entries: List[Dict[str, Any]] = []

        def _collect(node: Dict[str, Any]) -> None:
            if node.get("type") != "directory":
                return
            entries.append(
                {
                    "path": node.get("path"),
                    "name": node.get("name"),
                    "file_count": node.get("file_count", 0),
                    "dir_count": node.get("dir_count", 0),
                    "size": node.get("size", 0),
                }
            )
            for child in node.get("children", []):
                if child.get("type") == "directory":
                    _collect(child)

        _collect(structure)

        entries.sort(key=lambda item: item["file_count"], reverse=True)
        top_entries = entries[:max_entries]

        if not top_entries:
            return "(no directories found)"

        lines = []
        for idx, item in enumerate(top_entries, start=1):
            size_mb = item["size"] / (1024 * 1024)
            lines.append(
                f"{idx}. {item['path']} — files: {item['file_count']}, dirs: {item['dir_count']}, size: {size_mb:.2f} MB"
            )

        if len(entries) > max_entries:
            remaining = len(entries) - max_entries
            lines.append(f"... ({remaining} more directories)")

        return "\n".join(lines)

    async def get_model_metrics(self) -> Dict[str, Any]:
        return await self.model_metrics.get_metrics()

    def print_model_metrics(self):
        import asyncio

        async def _print_metrics():
            metrics = await self.model_metrics.get_metrics()

            print("\n" + "=" * 50)
            print("ECHOES ASSISTANT - MODEL METRICS")
            print("=" * 50)
            print(f"Total Requests: {metrics['total_requests']}")

            print("\nModel Usage:")
            for model, count in metrics["model_usage"].items():
                print(f"  - {model}: {count} requests")

            print("\nAverage Response Times:")
            for model, stats in metrics["response_times"].items():
                if stats["count"] > 0:
                    print(
                        f"  - {model}: {stats['avg']:.2f}s (min: {stats['min']:.2f}s, max: {stats['max']:.2f}s)"
                    )

            if metrics["errors"]:
                print("\nErrors:")
                for model, count in metrics["errors"].items():
                    print(f"  - {model}: {count} errors")

            if "cache_hit_rate" in metrics:
                print("\nCache Hit Rates:")
                for model, rate in metrics["cache_hit_rate"].items():
                    print(f"  - {model}: {rate:.1%}")

            print("=" * 50 + "\n")

        # Run the async function
        asyncio.run(_print_metrics())

    def reset_model_metrics(self):
        import asyncio

        asyncio.run(self.model_metrics.reset_metrics())
        print("✓ Model metrics reset")

    # ============================================================================
    # GLIMPSE PREFLIGHT SYSTEM METHODS
    # ============================================================================

    def enable_glimpse_preflight(self, enabled: bool = True) -> Dict[str, Any]:
        """Enable or disable Glimpse preflight system.

        Args:
            enabled: Whether to enable preflight checks

        Returns:
            Result with status
        """
        if not self.enable_glimpse:
            return {"success": False, "error": "Glimpse system not initialized"}

        self.glimpse_enabled = enabled
        return {
            "success": True,
            "glimpse_enabled": enabled,
            "message": f"Glimpse preflight {'enabled' if enabled else 'disabled'}",
        }

    def set_glimpse_anchors(
        self, goal: str = "", constraints: str = ""
    ) -> Dict[str, Any]:
        """Set goal and constraints for Glimpse preflight.

        Args:
            goal: The primary goal/intent
            constraints: Format, tone, audience constraints

        Returns:
            Result with status
        """
        if not self.enable_glimpse:
            return {"success": False, "error": "Glimpse system not initialized"}

        self.glimpse_goal = goal
        self.glimpse_constraints = constraints

        return {
            "success": True,
            "goal": goal,
            "constraints": constraints,
            "message": "Glimpse anchors updated",
        }

    async def glimpse_preflight(self, message: str) -> Dict[str, Any]:
        """Perform Glimpse preflight check on a message.

        Args:
            message: The message to preview

        Returns:
            Glimpse result with sample, essence, and alignment status
        """
        if not self.enable_glimpse or not self.glimpse_engine:
            return {"success": False, "error": "Glimpse system not initialized"}

        try:
            draft = Draft(
                input_text=message,
                goal=self.glimpse_goal,
                constraints=self.glimpse_constraints,
            )

            result = await self.glimpse_engine.glimpse(draft)

            return {
                "success": True,
                "attempt": result.attempt,
                "status": result.status,
                "sample": result.sample,
                "essence": result.essence,
                "delta": result.delta,
                "status_history": result.status_history,
                "stale": result.stale,
                "aligned": result.status == "aligned",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def commit_glimpse(self, message: str) -> Dict[str, Any]:
        """Commit a Glimpse preview (execute side effects).

        Args:
            message: The message to commit

        Returns:
            Result with commit status
        """
        if not self.enable_glimpse or not self.glimpse_engine:
            return {"success": False, "error": "Glimpse system not initialized"}

        try:
            draft = Draft(
                input_text=message,
                goal=self.glimpse_goal,
                constraints=self.glimpse_constraints,
            )

            self.glimpse_engine.commit(draft)

            return {
                "success": True,
                "message": "Glimpse committed successfully",
                "session_id": self.session_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # EXTERNAL API CONTACT METHODS
    # ============================================================================

    async def detect_patterns_external(
        self, text: str, context: Optional[Dict] = None, options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Detect patterns using external API.

        Args:
            text: Text to analyze for patterns
            context: Additional context
            options: Detection options

        Returns:
            Pattern detection results
        """
        if not self.enable_external_contact:
            return {"success": False, "error": "External API contact not enabled"}

        try:
            async with aiohttp.ClientSession() as session:
                url = (
                    self.api_endpoints["echoes_api"]
                    + self.api_endpoints["patterns_endpoint"]
                )

                payload = {
                    "text": text,
                    "context": context or {},
                    "options": options or {},
                }

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "patterns": result.get("patterns", []),
                            "confidence": result.get("confidence", 0.0),
                            "timestamp": result.get("timestamp"),
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {response.status}",
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_truth_external(
        self,
        claim: str,
        evidence: Optional[List[str]] = None,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Verify truth of a claim using external API.

        Args:
            claim: Claim to verify
            evidence: Supporting evidence
            context: Verification context

        Returns:
            Truth verification results
        """
        if not self.enable_external_contact:
            return {"success": False, "error": "External API contact not enabled"}

        try:
            async with aiohttp.ClientSession() as session:
                url = (
                    self.api_endpoints["echoes_api"]
                    + self.api_endpoints["truth_endpoint"]
                )

                payload = {
                    "claim": claim,
                    "evidence": evidence or [],
                    "context": context or {},
                }

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "verdict": result.get("verdict", "UNCERTAIN"),
                            "confidence": result.get("confidence", 0.0),
                            "explanation": result.get("explanation", ""),
                            "evidence_used": result.get("evidence_used", []),
                            "timestamp": result.get("timestamp"),
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {response.status}",
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def initiate_contact(
        self, message_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate contact with external API - BRIDGE FUNCTION.

        This is the main bridge between internal assistant and external APIs.

        Args:
            message_type: Type of message ("pattern_detection", "truth_verification", "analysis")
            data: Data to send

        Returns:
            Response from external API
        """
        if not self.enable_external_contact:
            return {"success": False, "error": "External API contact not enabled"}

        print(f"🌐 INITIATING CONTACT: {message_type}")

        try:
            if message_type == "pattern_detection":
                return await self.detect_patterns_external(
                    text=data.get("text", ""),
                    context=data.get("context"),
                    options=data.get("options"),
                )
            elif message_type == "truth_verification":
                return await self.verify_truth_external(
                    claim=data.get("claim", ""),
                    evidence=data.get("evidence"),
                    context=data.get("context"),
                )
            elif message_type == "analysis":
                # Combined analysis using both pattern detection and truth verification
                text = data.get("text", "")

                # Run both analyses in parallel
                patterns_task = self.detect_patterns_external(text, data.get("context"))
                truth_task = self.verify_truth_external(
                    text, data.get("evidence"), data.get("context")
                )

                patterns_result, truth_result = await asyncio.gather(
                    patterns_task, truth_task, return_exceptions=True
                )

                return {
                    "success": True,
                    "type": "combined_analysis",
                    "patterns": (
                        patterns_result
                        if not isinstance(patterns_result, Exception)
                        else {"success": False, "error": str(patterns_result)}
                    ),
                    "truth": (
                        truth_result
                        if not isinstance(truth_result, Exception)
                        else {"success": False, "error": str(truth_result)}
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown message type: {message_type}",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_external_status(self) -> Dict[str, Any]:
        """Get status of external API connections.

        Returns:
            Status of all external systems
        """
        status = {
            "glimpse_enabled": self.enable_glimpse,
            "glimpse_active": self.glimpse_enabled,
            "glimpse_anchors": {
                "goal": self.glimpse_goal,
                "constraints": self.glimpse_constraints,
            },
            "external_contact_enabled": self.enable_external_contact,
            "api_endpoints": self.api_endpoints if self.enable_external_contact else {},
            "api_available": API_AVAILABLE,
        }

        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ============================================================================
    # KNOWLEDGE GRAPH & MEANINGFUL COMMUNICATION METHODS
    # ============================================================================

    def add_knowledge_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        description: str = "",
        properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Add a knowledge node to the graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (person, place, concept, event, etc.)
            label: Display label for the node
            description: Optional description
            properties: Additional properties

        Returns:
            Result with node creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            node = KnowledgeNode(
                id=node_id,
                type=node_type,
                label=label,
                description=description,
                properties=properties or {},
            )

            self.knowledge_graph.add_node(node)

            return {
                "success": True,
                "node_id": node_id,
                "message": f"Knowledge node '{label}' added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_knowledge_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Add a relationship between knowledge nodes.

        Args:
            source_id: ID of source node
            target_id: ID of target node
            relation_type: Type of relationship
            weight: Relationship strength (0-1)
            properties: Additional properties

        Returns:
            Result with relation creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            relation = KnowledgeRelation(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                properties=properties or {},
            )

            relation_id = self.knowledge_graph.add_relation(relation)

            return {
                "success": True,
                "relation_id": relation_id,
                "message": f"Relation '{relation_type}' added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_memory_fragment(
        self, content: str, context: Dict[str, Any], importance: float = 1.0
    ) -> Dict[str, Any]:
        """Add a memory fragment to the knowledge system.

        Args:
            content: Memory content
            context: Context information
            importance: Importance score (0-1)

        Returns:
            Result with memory creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            # Extract entities and concepts from content
            entities, concepts = self.knowledge_graph.extract_entities_and_concepts(
                content
            )

            memory = MemoryFragment(
                id=f"mem_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}",
                content=content,
                context=context,
                entities=entities,
                concepts=concepts,
                importance=importance,
            )

            memory_id = self.knowledge_graph.add_memory(memory)

            return {
                "success": True,
                "memory_id": memory_id,
                "entities_found": entities,
                "concepts_found": concepts,
                "message": "Memory fragment added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def communicate_with_context(
        self, message: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enable meaningful communication using knowledge graph context.

        Args:
            message: User message
            system_prompt: Optional system prompt

        Returns:
            Rich response with context and insights
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            # Get communication context
            context = self.knowledge_graph.get_communication_context(message)

            # Build enhanced system prompt with context
            enhanced_prompt = self._build_contextual_prompt(system_prompt, context)

            # Generate response with context
            response = self.chat(message, system_prompt=enhanced_prompt, stream=False)

            # Learn from this conversation
            self.knowledge_graph.learn_from_conversation(
                message, response, confidence=0.8
            )

            return {
                "success": True,
                "response": response,
                "context": context,
                "context_used": {
                    "entities": len(context["entities"]),
                    "memories": len(context["memories"]),
                    "related_concepts": len(context["related_concepts"]),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_contextual_prompt(
        self, base_prompt: Optional[str], context: Dict[str, Any]
    ) -> str:
        """Build an enhanced prompt with knowledge graph context."""
        contextual_parts = []

        if base_prompt:
            contextual_parts.append(base_prompt)

        # Add entity context
        if context["entities"]:
            contextual_parts.append(
                f"Relevant entities mentioned: {', '.join(context['entities'])}"
            )

        # Add memory context
        if context["memories"]:
            memory_texts = [mem["content"] for mem in context["memories"][:2]]
            contextual_parts.append(f"Relevant memories: {' | '.join(memory_texts)}")

        # Add related concepts
        if context["related_concepts"]:
            contextual_parts.append(
                f"Related concepts: {', '.join(context['related_concepts'])}"
            )

        # Add conversation context
        if context["conversation_history"]:
            contextual_parts.append("Recent conversation context available")

        contextual_parts.append(
            "Use this context to provide more meaningful, personalized responses."
        )

        return "\n\n".join(contextual_parts)

    def search_knowledge_graph(
        self, query: str, node_type: Optional[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """Search the knowledge graph for relevant information.

        Args:
            query: Search query
            node_type: Optional node type filter
            limit: Maximum results

        Returns:
            Search results with nodes and relations
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            nodes = self.knowledge_graph.find_nodes(query, node_type, limit)

            results = []
            for node in nodes:
                # Get related nodes for each result
                related = self.knowledge_graph.get_related_nodes(node.id, max_depth=1)

                results.append(
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "description": node.description,
                        "properties": node.properties,
                        "related_nodes": [
                            {"id": r.id, "label": r.label, "type": r.type}
                            for r in related[:3]
                        ],
                    }
                )

            return {
                "success": True,
                "results": results,
                "total_found": len(results),
                "query": query,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_knowledge_relationships(
        self, node_id: str, relation_type: Optional[str] = None, max_depth: int = 2
    ) -> Dict[str, Any]:
        """Get relationships for a specific knowledge node.

        Args:
            node_id: ID of the node
            relation_type: Optional relation type filter
            max_depth: Maximum traversal depth

        Returns:
            Related nodes and relationships
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            related_nodes = self.knowledge_graph.get_related_nodes(
                node_id, relation_type, max_depth
            )

            return {
                "success": True,
                "node_id": node_id,
                "related_nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "description": node.description,
                    }
                    for node in related_nodes
                ],
                "total_related": len(related_nodes),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def retrieve_relevant_memories(
        self, query: str, context: Optional[Dict] = None, limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve memories relevant to a query.

        Args:
            query: Search query
            context: Optional context filter
            limit: Maximum results

        Returns:
            Relevant memory fragments
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            memories = self.knowledge_graph.retrieve_memories(query, context, limit)

            return {
                "success": True,
                "memories": [
                    {
                        "id": mem.id,
                        "content": mem.content,
                        "context": mem.context,
                        "importance": mem.importance,
                        "timestamp": mem.timestamp,
                        "entities": mem.entities,
                        "concepts": mem.concepts,
                    }
                    for mem in memories
                ],
                "total_found": len(memories),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def learn_from_interaction(
        self, user_message: str, assistant_response: str, confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Learn from user interactions to improve future communication.

        Args:
            user_message: The user's message
            assistant_response: The assistant's response
            confidence: Confidence in the interaction quality

        Returns:
            Learning results
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            self.knowledge_graph.learn_from_conversation(
                user_message, assistant_response, confidence
            )

            return {
                "success": True,
                "message": "Successfully learned from interaction",
                "conversation_turns": len(self.knowledge_graph.conversation_history),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph.

        Returns:
            Knowledge graph statistics
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            stats = self.knowledge_graph.get_stats()

            return {
                "success": True,
                "stats": stats,
                "message": "Knowledge graph statistics retrieved successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # MULTIMODAL RESONANCE Glimpse METHODS
    # ============================================================================

    def process_multimodal_file(
        self, file_path: str, extraction_target: str = "text"
    ) -> Dict[str, Any]:
        """Process a multimodal file with resonance-based understanding.

        Args:
            file_path: Path to the file to process
            extraction_target: Target modality for extraction (text, vision, audio, etc.)

        Returns:
            Processing result with resonance analysis
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            result = self.multimodal_engine.process_multimodal_file(
                file_path, extraction_target
            )

            # Add knowledge graph integration
            if result["success"]:
                # Extract entities from file path and add to knowledge graph
                file_name = Path(file_path).stem
                entities = self.knowledge_graph.extract_entities_and_concepts(file_name)

                # Add file as knowledge node
                node_id = f"file_{hash(file_path)}"
                self.add_knowledge_node(
                    node_id=node_id,
                    node_type="multimodal_file",
                    label=file_name,
                    description=f"Multimodal file: {Path(file_path).suffix}",
                    properties={
                        "file_path": file_path,
                        "modality": result["modality_vector"]["modality_type"],
                        "resonance_strength": result["resonance_analysis"][
                            "resonance_strength"
                        ],
                        "extraction_target": extraction_target,
                        "quality_factor": result["modality_vector"]["quality_factor"],
                    },
                )

                # Add memory about processing
                self.add_memory_fragment(
                    content=f"Processed multimodal file {file_name} with resonance {result['resonance_analysis']['resonance_strength']:.2f}",
                    context={
                        "file_path": file_path,
                        "processing_result": result,
                        "extraction_target": extraction_target,
                    },
                    importance=result["resonance_analysis"]["resonance_strength"],
                )

                result["knowledge_graph_integration"] = {
                    "node_id": node_id,
                    "entities_extracted": entities,
                    "memory_created": True,
                }

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_multimodal_directory(
        self, directory_path: str, extraction_target: str = "text"
    ) -> Dict[str, Any]:
        """Analyze all files in a directory with multimodal resonance.

        Args:
            directory_path: Path to directory to analyze
            extraction_target: Target modality for extraction

        Returns:
            Comprehensive analysis of directory multimodal content
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            directory = Path(directory_path)
            if not directory.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}",
                }

            # Get all files
            files = []
            for ext in self.multimodal_engine.modality_vectors.keys():
                files.extend(directory.glob(f"*{ext}"))

            if not files:
                return {
                    "success": False,
                    "error": f"No supported multimodal files found in {directory_path}",
                }

            # Process files and optimize strategy
            file_paths = [str(f) for f in files]
            optimization_strategy = self.multimodal_engine.optimize_processing_strategy(
                file_paths, extraction_target
            )

            # Process high resonance files first
            processed_files = []
            modality_distribution = {}
            total_resonance = 0

            for file_analysis in optimization_strategy["strategy"]["file_analyses"]:
                file_path = file_analysis["file_path"]
                result = self.process_multimodal_file(file_path, extraction_target)

                if result["success"]:
                    processed_files.append(
                        {
                            "file_path": file_path,
                            "processing_result": result,
                            "analysis": file_analysis,
                        }
                    )

                    # Track modality distribution
                    modality = result["modality_vector"]["modality_type"]
                    modality_distribution[modality] = (
                        modality_distribution.get(modality, 0) + 1
                    )
                    total_resonance += result["resonance_analysis"][
                        "resonance_strength"
                    ]

            # Create summary memory
            self.add_memory_fragment(
                content=f"Analyzed {len(processed_files)} multimodal files in {directory_path}",
                context={
                    "directory": directory_path,
                    "files_processed": len(processed_files),
                    "modality_distribution": modality_distribution,
                    "average_resonance": (
                        total_resonance / len(processed_files) if processed_files else 0
                    ),
                    "extraction_target": extraction_target,
                },
                importance=0.8,
            )

            return {
                "success": True,
                "directory_analysis": {
                    "directory_path": directory_path,
                    "total_files_found": len(files),
                    "files_processed": len(processed_files),
                    "modality_distribution": modality_distribution,
                    "average_resonance": (
                        total_resonance / len(processed_files) if processed_files else 0
                    ),
                    "optimization_strategy": optimization_strategy["strategy"],
                    "processed_files": processed_files,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cross_modal_insights(self, file_path: str) -> Dict[str, Any]:
        """Get cross-modal transformation insights for a file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Cross-modal insights and recommendations
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            insights = self.multimodal_engine.get_cross_modal_insights(file_path)

            if insights["success"]:
                # Enhance with knowledge graph context
                file_name = Path(file_path).stem
                related_knowledge = self.search_knowledge_graph(file_name, limit=3)

                insights["knowledge_graph_context"] = related_knowledge

                # Get resonant files for each recommended transformation
                for rec in insights["insights"]["recommended_transformations"]:
                    target_modality = rec["transformation"].split("_to_")[-1]
                    resonant_files = self.multimodal_engine.find_resonant_files(
                        target_modality, 0.6
                    )
                    rec["similar_files"] = resonant_files[:3]  # Top 3 similar files

            return insights

        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_resonant_content(
        self, target_modality: str, min_resonance: float = 0.5
    ) -> Dict[str, Any]:
        """Find content that resonates with target modality.

        Args:
            target_modality: Target modality to find resonant content for
            min_resonance: Minimum resonance threshold

        Returns:
            List of resonant files and content
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            resonant_files = self.multimodal_engine.find_resonant_files(
                target_modality, min_resonance
            )

            # Enhance with knowledge graph information
            enhanced_results = []
            for file_info in resonant_files:
                file_name = Path(file_info["file_path"]).stem

                # Search knowledge graph for related entities
                related_knowledge = self.search_knowledge_graph(file_name, limit=2)

                # Get relevant memories
                relevant_memories = self.retrieve_relevant_memories(file_name, limit=2)

                enhanced_results.append(
                    {
                        **file_info,
                        "knowledge_context": related_knowledge,
                        "related_memories": relevant_memories,
                    }
                )

            return {
                "success": True,
                "target_modality": target_modality,
                "min_resonance": min_resonance,
                "resonant_files": enhanced_results,
                "total_found": len(enhanced_results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_resonant_understanding(
        self, query: str, modality_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create understanding by resonating across multiple modalities.

        Args:
            query: Query or topic to understand
            modality_preference: Preferred modality for understanding

        Returns:
            Multimodal understanding with resonance analysis
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            # Search knowledge graph for entities
            knowledge_results = self.search_knowledge_graph(query, limit=5)

            # Find resonant multimodal content
            target_modality = modality_preference or "text"
            resonant_content = self.find_resonant_content(target_modality, 0.6)

            # Retrieve relevant memories
            relevant_memories = self.retrieve_relevant_memories(query, limit=3)

            # Build multimodal context
            multimodal_context = {
                "query": query,
                "target_modality": target_modality,
                "knowledge_entities": knowledge_results.get("results", []),
                "resonant_files": resonant_content.get("resonant_files", []),
                "relevant_memories": relevant_memories.get("memories", []),
                "resonance_strength": (
                    np.mean(
                        [
                            f["resonance_strength"]
                            for f in resonant_content.get("resonant_files", [])
                        ]
                    )
                    if resonant_content.get("resonant_files")
                    else 0
                ),
            }

            # Generate enhanced response with multimodal context
            enhanced_prompt = f"""You are an AI assistant with advanced multimodal understanding capabilities.
            
Query: {query}
Target Modality: {target_modality}
Resonance Strength: {multimodal_context['resonance_strength']:.2f}

Knowledge Context:
- Entities found: {len(multimodal_context['knowledge_entities'])}
- Resonant files: {len(multimodal_context['resonant_files'])}
- Relevant memories: {len(multimodal_context['relevant_memories'])}

Provide a comprehensive response that leverages this multimodal understanding. Consider the different types of content (vision, text, audio, structured data) and their relationships."""

            response = self.chat(query, system_prompt=enhanced_prompt, stream=False)

            # Create memory of this multimodal understanding
            self.add_memory_fragment(
                content=f"Created multimodal understanding for query: {query}",
                context={
                    "query": query,
                    "modality_preference": modality_preference,
                    "resonance_strength": multimodal_context["resonance_strength"],
                    "entities_used": len(multimodal_context["knowledge_entities"]),
                    "files_used": len(multimodal_context["resonant_files"]),
                },
                importance=multimodal_context["resonance_strength"],
            )

            return {
                "success": True,
                "multimodal_understanding": {
                    "query": query,
                    "response": response,
                    "context": multimodal_context,
                    "resonance_analysis": {
                        "overall_resonance": multimodal_context["resonance_strength"],
                        "modality_preference": target_modality,
                        "cross_modal_insights": len(
                            resonant_content.get("resonant_files", [])
                        ),
                    },
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_multimodal_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about multimodal resonance Glimpse.

        Returns:
            Multimodal processing statistics
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            stats = self.multimodal_engine.get_resonance_statistics()

            return {
                "success": True,
                "multimodal_stats": stats["statistics"],
                "message": "Multimodal resonance statistics retrieved successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def optimize_multimodal_workflow(
        self, files: List[str], objective: str = "comprehensive_analysis"
    ) -> Dict[str, Any]:
        """Optimize multimodal processing workflow for specific objectives.

        Args:
            files: List of files to process
            objective: Processing objective (comprehensive_analysis, quick_insights, deep_understanding)

        Returns:
            Optimized workflow strategy
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            # Determine optimal target modality based on objective
            target_modality_map = {
                "comprehensive_analysis": "text",
                "visual_insights": "vision",
                "data_extraction": "structured",
                "pattern_recognition": "geometric",
                "content_synthesis": "text",
            }

            target_modality = target_modality_map.get(objective, "text")

            # Get optimization strategy
            strategy = self.multimodal_engine.optimize_processing_strategy(
                files, target_modality
            )

            if strategy["success"]:
                workflow_strategy = strategy["strategy"]

                # Add processing recommendations based on objective
                if objective == "comprehensive_analysis":
                    workflow_strategy["recommendations"] = [
                        "Process high resonance files first for initial insights",
                        "Use cross-modal bridges to extract hidden relationships",
                        "Leverage knowledge graph for entity connections",
                    ]
                elif objective == "quick_insights":
                    workflow_strategy["recommendations"] = [
                        "Focus on files with extraction complexity < 0.6",
                        "Prioritize text and structured modalities",
                        "Use semantic enhancement for faster understanding",
                    ]
                elif objective == "deep_understanding":
                    workflow_strategy["recommendations"] = [
                        "Process all files regardless of resonance strength",
                        "Apply cross-modal mapping for comprehensive insights",
                        "Integrate with knowledge graph for contextual depth",
                    ]

                # Add estimated processing time
                total_complexity = sum(
                    f["complexity"] for f in workflow_strategy["file_analyses"]
                )
                workflow_strategy["estimated_complexity"] = total_complexity
                workflow_strategy["processing_tier"] = (
                    "fast"
                    if total_complexity < 5
                    else "medium" if total_complexity < 15 else "complex"
                )

            return {
                "success": True,
                "objective": objective,
                "target_modality": target_modality,
                "workflow_strategy": workflow_strategy,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # LEGAL SAFEGUARDS & ENHANCED ACCOUNTING METHODS
    # ============================================================================

    def track_user_cognitive_effort(
        self,
        user_id: str,
        session_duration_minutes: float,
        complexity_score: float,
        creativity_score: float,
        innovation_score: float,
        thought_processes: List[str],
        insights_generated: int,
        problems_solved: int,
    ) -> Dict[str, Any]:
        """Track user's cognitive efforts and calculate value.

        Args:
            user_id: Unique user identifier
            session_duration_minutes: Duration of cognitive work session
            complexity_score: Complexity of work (0.0-1.0)
            creativity_score: Creativity level (0.0-1.0)
            innovation_score: Innovation potential (0.0-1.0)
            thought_processes: List of thought patterns used
            insights_generated: Number of insights created
            problems_solved: Number of problems solved

        Returns:
            Cognitive effort tracking result with value calculation
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Track cognitive effort through legal system
            effort_metrics = self.legal_system.track_cognitive_effort(
                user_id=user_id,
                session_id=self.session_id,
                effort_duration_minutes=session_duration_minutes,
                cognitive_complexity_score=complexity_score,
                creativity_score=creativity_score,
                innovation_potential=innovation_score,
                thought_processes=thought_processes,
                insights_generated=insights_generated,
                problems_solved=problems_solved,
            )

            # Record transaction in accounting system
            transaction = self.accounting_system.record_cognitive_transaction(
                user_id=user_id,
                session_id=self.session_id,
                effort_metrics=effort_metrics,
                value_type=ValueType.COGNITIVE_JOULES,
            )

            # Add to knowledge graph as memory
            self.add_memory_fragment(
                content=f"User {user_id} completed cognitive session: {session_duration_minutes}min, complexity {complexity_score:.2f}",
                context={
                    "user_id": user_id,
                    "session_id": self.session_id,
                    "cognitive_joules": effort_metrics.joules_of_work,
                    "value_created": float(effort_metrics.value_created),
                    "insights_generated": insights_generated,
                    "problems_solved": problems_solved,
                },
                importance=min(
                    effort_metrics.value_created / 100, 1.0
                ),  # Scale importance to 0-1
            )

            return {
                "success": True,
                "effort_metrics": {
                    "user_id": effort_metrics.user_id,
                    "session_id": effort_metrics.session_id,
                    "cognitive_joules": effort_metrics.joules_of_work,
                    "value_created": float(effort_metrics.value_created),
                    "complexity_score": effort_metrics.cognitive_complexity_score,
                    "creativity_score": effort_metrics.creativity_score,
                    "innovation_score": effort_metrics.innovation_potential,
                },
                "transaction": {
                    "transaction_id": transaction.transaction_id,
                    "gross_value": float(transaction.gross_value),
                    "net_value": float(transaction.net_value),
                    "tax_amount": float(transaction.gross_value * transaction.tax_rate),
                    "platform_fee": float(
                        transaction.gross_value * transaction.platform_cut
                    ),
                },
                "values_alignment": {
                    "integrity": "Transparent tracking of cognitive efforts",
                    "trust": "Fair compensation based on value created",
                    "creativity": "Recognition and reward for creative contributions",
                    "freedom_of_thought": "Protection of cognitive privacy and rights",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_user_consent_agreement(
        self,
        user_id: str,
        consent_type: str = "personal_development",
        purpose_description: str = "AI assistance and cognitive work",
        scope_of_use: str = "general_assistance",
    ) -> Dict[str, Any]:
        """Create user consent agreement aligned with LICENSE values.

        Args:
            user_id: Unique user identifier
            consent_type: Type of consent (personal_development, commercial_use, research, etc.)
            purpose_description: Description of purpose for using the system
            scope_of_use: Scope of permitted usage

        Returns:
            Consent agreement creation result
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Convert string to enum
            consent_enum = ConsentType(consent_type)

            # Create consent record
            consent = self.legal_system.create_consent_record(
                user_id=user_id,
                consent_type=consent_enum,
                purpose_description=purpose_description,
                scope_of_use=scope_of_use,
                duration="perpetual",
                protection_level=ProtectionLevel.ENHANCED,
                compensation_terms={
                    "cognitive_effort_tracked": True,
                    "value_based_compensation": True,
                    "tax_and_deductions_applied": True,
                    "payout_threshold": 10.0,
                },
            )

            # Create user account in accounting system
            user_account = self.accounting_system.create_user_account(
                user_id, consent_enum
            )

            # Add to knowledge graph
            self.add_knowledge_node(
                node_id=f"user_{user_id}",
                node_type="user",
                label=f"User {user_id}",
                description=f"User with consent agreement for {consent_type}",
                properties={
                    "user_id": user_id,
                    "consent_type": consent_type,
                    "purpose": purpose_description,
                    "scope": scope_of_use,
                    "protection_level": "enhanced",
                    "created_at": consent.granted_at,
                },
            )

            return {
                "success": True,
                "consent_agreement": {
                    "consent_id": consent.consent_id,
                    "user_id": consent.user_id,
                    "consent_type": consent.consent_type.value,
                    "purpose_description": consent.purpose_description,
                    "scope_of_use": consent.scope_of_use,
                    "protection_level": consent.protection_level.value,
                    "granted_at": consent.granted_at,
                    "terms_accepted": consent.terms_accepted,
                },
                "user_account": {
                    "user_id": user_account.user_id,
                    "created_at": user_account.created_at,
                    "consent_records": user_account.consent_records,
                },
                "values_protection": {
                    "integrity": "Transparent consent process with clear terms",
                    "trust": "Reliable agreement enforcement and compliance",
                    "creativity": "Protection for creative and innovative work",
                    "freedom_of_thought": "Cognitive liberty and privacy safeguards",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_user_financial_statement(
        self, user_id: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive financial statement for user.

        Args:
            user_id: Unique user identifier
            period_days: Number of days for the statement period

        Returns:
            Detailed financial statement with values alignment
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Calculate period dates
            period_end = datetime.now(timezone.utc).isoformat()
            period_start = (
                datetime.now(timezone.utc) - timedelta(days=period_days)
            ).isoformat()

            # Generate statement from accounting system
            statement = self.accounting_system.generate_user_statement(
                user_id=user_id, period_start=period_start, period_end=period_end
            )

            if "error" in statement:
                return statement

            # Calculate payout eligibility
            payout_info = self.accounting_system.calculate_payout_eligibility(user_id)

            # Get legal compliance status
            legal_compliance = self.legal_system.generate_legal_compliance_report()

            return {
                "success": True,
                "financial_statement": statement,
                "payout_eligibility": payout_info,
                "legal_compliance": {
                    "consent_status": "Active",
                    "compliance_rate": legal_compliance["license_compliance"][
                        "compliance_rate"
                    ],
                    "values_alignment": statement["values_alignment"],
                },
                "values_reflection": {
                    "integrity": f"Transparent accounting of {statement['summary']['total_transactions']} transactions",
                    "trust": f"Fair net value of ${statement['summary']['net_value']:.2f} after taxes and fees",
                    "creativity": f"Creative contributions valued through bonus multipliers",
                    "delightful_humor": f"Positive engagement reflected in value scores",
                    "freedom_of_thought": f"Cognitive rights protected with {legal_compliance['license_compliance']['compliance_rate']:.1f}% compliance",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_license_compliance(
        self, operation_type: str, user_id: str, scope: str
    ) -> Dict[str, Any]:
        """Verify compliance with Consent-Based License.

        Args:
            operation_type: Type of operation being performed
            user_id: User performing the operation
            scope: Scope of the operation

        Returns:
            License compliance verification result
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Verify consent compliance
            consent_check = self.legal_system.verify_consent_compliance(
                user_id=user_id, action=operation_type, scope=scope
            )

            # Check responsible use principles compliance
            responsible_use_check = {
                "ethical_consideration": self._check_ethical_compliance(
                    operation_type, scope
                ),
                "transparency": self._check_transparency_compliance(operation_type),
                "professional_standards": self._check_professional_compliance(
                    operation_type
                ),
                "community_benefit": self._check_community_benefit(scope),
                "continuous_learning": True,  # Always enabled
                "collaboration": self._check_collaboration_compliance(scope),
                "fairness": self._check_fairness_compliance(user_id, scope),
            }

            # Overall compliance score
            consent_score = 100 if consent_check["compliant"] else 0
            principle_scores = [
                100 if responsible_use_check[principle] else 0
                for principle in responsible_use_check
                if isinstance(responsible_use_check[principle], bool)
            ]
            overall_compliance = (
                sum([consent_score] + principle_scores) / len(principle_scores) + 1
            )

            return {
                "success": True,
                "license_compliance": {
                    "operation_type": operation_type,
                    "user_id": user_id,
                    "scope": scope,
                    "consent_compliant": consent_check["compliant"],
                    "consent_details": consent_check,
                    "responsible_use_principles": responsible_use_check,
                    "overall_compliance_score": overall_compliance,
                    "compliance_status": (
                        "Fully Compliant"
                        if overall_compliance >= 95
                        else (
                            "Mostly Compliant"
                            if overall_compliance >= 80
                            else (
                                "Needs Attention"
                                if overall_compliance >= 60
                                else "Non-Compliant"
                            )
                        )
                    ),
                },
                "values_upheld": {
                    "integrity": "Ethical considerations and transparency maintained",
                    "trust": "Professional standards and fairness enforced",
                    "creativity": "Collaboration and community benefit promoted",
                    "freedom_of_thought": "Continuous learning and cognitive liberty protected",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_ethical_compliance(self, operation_type: str, scope: str) -> bool:
        """Check ethical compliance for operation"""
        # Simplified ethical check
        harmful_operations = ["exploitation", "manipulation", "deception"]
        return not any(
            harmful in operation_type.lower() or harmful in scope.lower()
            for harmful in harmful_operations
        )

    def _check_transparency_compliance(self, operation_type: str) -> bool:
        """Check transparency compliance"""
        # All operations should be transparent
        return True

    def _check_professional_compliance(self, operation_type: str) -> bool:
        """Check professional standards compliance"""
        unprofessional_operations = ["spam", "harassment", "abuse"]
        return not any(
            unprof in operation_type.lower() for unprof in unprofessional_operations
        )

    def _check_community_benefit(self, scope: str) -> bool:
        """Check if operation benefits community"""
        beneficial_keywords = [
            "learning",
            "development",
            "research",
            "collaboration",
            "innovation",
        ]
        return any(benefit in scope.lower() for benefit in beneficial_keywords)

    def _check_collaboration_compliance(self, scope: str) -> bool:
        """Check collaboration compliance"""
        return "collaboration" in scope.lower() or "cooperation" in scope.lower()

    def _check_fairness_compliance(self, user_id: str, scope: str) -> bool:
        """Check fairness compliance"""
        # All users should be treated fairly
        return True

    def get_legal_accounting_statistics(self) -> Dict[str, Any]:
        """Get comprehensive legal and accounting statistics.

        Returns:
            Legal safeguards and accounting statistics
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Get legal compliance report
            legal_report = self.legal_system.generate_legal_compliance_report()

            # Get accounting summary
            accounting_stats = {
                "total_users": len(self.accounting_system.user_accounts),
                "total_transactions": len(self.accounting_system.transactions),
                "total_cognitive_joules": sum(
                    tx.cognitive_joules
                    for tx in self.accounting_system.transactions.values()
                ),
                "total_gross_value": sum(
                    tx.gross_value
                    for tx in self.accounting_system.transactions.values()
                ),
                "total_net_value": sum(
                    tx.net_value for tx in self.accounting_system.transactions.values()
                ),
                "total_tax_collected": sum(
                    tx.gross_value * tx.tax_rate
                    for tx in self.accounting_system.transactions.values()
                ),
                "total_platform_fees": sum(
                    tx.gross_value * tx.platform_cut
                    for tx in self.accounting_system.transactions.values()
                ),
            }

            return {
                "success": True,
                "legal_safeguards": legal_report,
                "enhanced_accounting": accounting_stats,
                "values_implementation": {
                    "integrity": {
                        "consent_compliance_rate": legal_report["license_compliance"][
                            "compliance_rate"
                        ],
                        "transparent_operations": True,
                    },
                    "trust": {
                        "reliable_compensation": accounting_stats["total_net_value"]
                        > 0,
                        "fair_deductions": True,
                    },
                    "creativity": {
                        "creative_work_valued": True,
                        "innovation_rewards_enabled": True,
                    },
                    "delightful_humor": {
                        "positive_engagement": True,
                        "joyful_interactions": True,
                    },
                    "freedom_of_thought": {
                        "cognitive_rights_protected": True,
                        "privacy_safeguards_active": True,
                    },
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def interactive_mode():
    print("\nCommands:")
    print("  'exit' or 'quit'     - Exit the assistant")
    print("  'history'            - Show conversation history")
    print("  'clear'              - Clear conversation history")
    print("  'tools'              - List available tools")
    print("  'stats'              - Show statistics")
    print("  'actions'            - Show action history")
    print("  'personality'        - Show personality stats and mood")
    print("  'fixes'              - Show error fix statistics")
    print("  'crossref <topic>'   - Get cross-reference suggestions")
    print("  'intent [text]'      - Analyze intent or show intent flow")
    print("  'thoughts'           - Show thought chain analysis")
    print("  'links'              - Show critical links between thoughts")
    print("  'export'             - Export thought network to JSON")
    print("  'humor'              - Show humor and pressure management status")
    print("  'pressure'           - Show detailed pressure analysis")
    print("  'joke [level]'       - Tell a joke (low/medium/high/critical/overwhelmed)")
    print("  'cache'              - Show catch & release cache statistics")
    print("  'xref <query>'       - Quick cross-reference lookup")
    print("  'continuity'         - Show conversation continuity")
    print("  'catch <content>'    - Manually catch content in cache")
    print("  'release <key>'      - Release content from cache")
    print("  'clearcache <level>' - Clear cache (session/short/long/permanent/all)")
    print(
        "  'simulate <query>'   - Run parallel simulations for possibility exploration"
    )
    print("  'sims'               - Show parallel simulation statistics")
    print("  'sim <id>'           - Get specific simulation result")
    print("  'clearsims'          - Clear completed simulations")
    print("  'possibilities <topic>' - Explore entire possibility space")
    print("  'add knowledge'      - Add documents to knowledge base")
    print("  'stream on/off'      - Toggle streaming")
    print("  'preflight on/off'   - Toggle Glimpse preflight (default: on)")
    print("  'anchors'            - Set preflight goal and constraints")
    print("  'essence-only on/off'- Toggle essence-only glimpse (user-chosen)")
    print("  'prompt <name>'      - Load prompt from prompts/<name>.yaml")
    print("  'prompt list'        - List available prompts")
    print("  'prompt show <name>' - Show content of a prompt")
    print("  'status on/off'      - Toggle status indicators")
    print("  'action add <sku> <name> <cat> <qty> <loc>' - Add inventory item")
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
        preflight_enabled = True  # Intent verification before commit: ON by default
        preflight_goal = ""
        preflight_constraints = ""

        # Minimal, safe persistence on commit
        def _commit_sink(d: Draft) -> None:
            try:
                os.makedirs("results", exist_ok=True)
                import json as _json
                from datetime import datetime as _dt, timezone as _tz

                rec = {
                    "ts": _dt.now(_tz.utc).isoformat(),
                    "input_text": d.input_text,
                    "goal": d.goal,
                    "constraints": d.constraints,
                }
                with open(
                    os.path.join("results", "glimpse_commits.jsonl"),
                    "a",
                    encoding="utf-8",
                ) as f:
                    f.write(_json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                # Silent best-effort; never block user flow
                pass

        glimpse_engine = GlimpseEngine(
            privacy_guard=PrivacyGuard(on_commit=_commit_sink), enable_clarifiers=True
        )
        # Update to use enhanced clarifier engine
        if (
            hasattr(glimpse_engine, "_clarifier_engine")
            and glimpse_engine._clarifier_engine
        ):
            glimpse_engine._clarifier_engine = ClarifierEngine(use_enhanced_mode=True)

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
                    assistant.clear_history()
                    print("✓ Conversation history cleared")
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
                        status_icon = "✓" if action["success"] else "✗"
                        print(
                            f"  {status_icon} {action['action_id']}: {action['action_type']} ({action['duration_ms']:.1f}ms)"
                        )
                    summary = assistant.get_action_summary()
                    print("\n📊 Action Summary:")
                    print(
                        f"  Total: {summary['total_actions']} | Success: {summary['successful']} | Failed: {summary['failed']}"
                    )
                    print(
                        f"  Success Rate: {summary['success_rate']:.1f}% | Avg Duration: {summary['avg_duration_ms']:.1f}ms"
                    )
                    continue

                if command.startswith("action "):
                    parts = command.split(maxsplit=1)[1].split()
                    if not parts:
                        print("Usage: action <add|list|report> [args]")
                        continue

                    action_cmd = parts[0]

                    if action_cmd == "add" and len(parts) >= 6:
                        result = assistant.execute_action(
                            "inventory",
                            "add_item",
                            sku=parts[1],
                            name=parts[2],
                            category=parts[3],
                            quantity=int(parts[4]),
                            location=parts[5],
                            min_stock=int(parts[6]) if len(parts) > 6 else 0,
                            max_stock=int(parts[7]) if len(parts) > 7 else 0,
                        )
                        print(f"\n{STATUS_COMPLETE} Item added: {result['action_id']}")
                        if result["success"]:
                            print(f"  SKU: {result['result'].get('sku')}")
                            print(f"  Quantity: {result['result'].get('quantity')}")
                        else:
                            print(f"  Error: {result['error']}")
                        continue

                    if action_cmd == "list":
                        category = parts[1] if len(parts) > 1 else None
                        result = assistant.execute_action(
                            "inventory", "list_items", category=category
                        )
                        if result["success"]:
                            items = result["result"]
                            print(f"\n📦 Inventory Items ({len(items)} total):")
                            for item in items[:10]:
                                print(
                                    f"  • {item['sku']}: {item['name']} ({item['quantity']} @ {item['location']})"
                                )
                            if len(items) > 10:
                                print(f"  ... and {len(items) - 10} more")
                        else:
                            print(f"  Error: {result['error']}")
                        continue

                    if action_cmd == "report":
                        try:
                            report_type = parts[1] if len(parts) > 1 else "summary"
                            result = assistant.execute_action(
                                "inventory", "report", report_type=report_type
                            )
                            if result["success"]:
                                print(
                                    f"\n📊 Report:\n{json.dumps(result['result'], indent=2)}"
                                )
                            else:
                                print(f"  Error: {result['error']}")
                        except Exception as e:
                            print(f"  Error: {str(e)}")
                        continue

                if command == "stream on":
                    streaming_enabled = True
                    print("✓ Streaming enabled")
                    continue

                if command == "stream off":
                    streaming_enabled = False
                    print("✓ Streaming disabled")
                    continue

                if command == "status on":
                    status_enabled = True
                    print("✓ Status indicators enabled")
                    continue

                if command == "status off":
                    status_enabled = False
                    print("✓ Status indicators disabled")
                    continue

                if command == "preflight on":
                    preflight_enabled = True
                    print("✓ Glimpse preflight enabled")
                    continue

                if command == "preflight off":
                    preflight_enabled = False
                    print("✓ Glimpse preflight disabled")
                    continue

                if command == "anchors":
                    try:
                        g = input("Goal (enter to keep current): ").strip()
                        if g:
                            preflight_goal = g
                        c = input("Constraints (enter to keep current): ").strip()
                        if c:
                            preflight_constraints = c
                        print("✓ Anchors updated")
                    except KeyboardInterrupt:
                        print("\n(anchors update canceled)")
                    continue

                if command == "essence-only on":
                    glimpse_engine.set_essence_only(True)
                    print("✓ Essence-only glimpses enabled (no auto-apply)")
                    continue

                if command == "essence-only off":
                    glimpse_engine.set_essence_only(False)
                    print("✓ Essence-only glimpses disabled")
                    continue

                if command.startswith("prompt "):
                    prompt_name = command.split(maxsplit=1)[1]
                    if prompt_name == "list":
                        prompts = list_available_prompts()
                        print(f"\nAvailable prompts ({len(prompts)}):")
                        for prompt in prompts:
                            print(f"  - {prompt}")
                    elif prompt_name.startswith("show "):
                        show_prompt_content(prompt_name.split(maxsplit=1)[1])
                    else:
                        system_prompt = load_prompt(prompt_name)
                        if system_prompt:
                            print(f"✓ Loaded prompt '{prompt_name}'")
                        else:
                            print(f"⚠ Prompt '{prompt_name}' not found")
                    continue

                if command.startswith("simulate "):
                    # Run parallel simulations
                    query = (
                        command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
                    )
                    if query:
                        # Create simulation configs
                        sim_configs = [
                            {
                                "type": SimulationType.SCENARIO_EXPLORATION,
                                "input_data": {"scenario": query, "context": {}},
                                "parameters": {"priority": 0.7, "timeout": 15},
                            },
                            {
                                "type": SimulationType.OUTCOME_PREDICTION,
                                "input_data": {"action": query, "context": {}},
                                "parameters": {"priority": 0.8, "timeout": 20},
                            },
                            {
                                "type": SimulationType.ALTERNATIVE_PATHS,
                                "input_data": {
                                    "problem": query,
                                    "current_approach": "",
                                },
                                "parameters": {"priority": 0.6, "timeout": 25},
                            },
                        ]

                        print(f"\n🧠 **Running parallel simulations for:** {query}")
                        print("  This may take a moment...")

                        # Run simulations
                        results = parallel_simulation.run_parallel_simulations(
                            sim_configs
                        )

                        if results:
                            print(f"\n📊 **Simulation Results:**")
                            for i, result in enumerate(results, 1):
                                sim_type = result.simulation_type.value.replace(
                                    "_", " "
                                ).title()
                                print(f"\n  {i}. {sim_type}:")
                                print(f"     Confidence: {result.confidence:.1%}")
                                print(
                                    f"     Execution time: {result.execution_time:.2f}s"
                                )
                                print(f"     Reasoning: {result.reasoning}")

                                if result.possibilities:
                                    print(
                                        f"     Top possibility: {result.possibilities[0]}"
                                    )

                                if result.insights:
                                    print(
                                        f"     Insights: {', '.join(result.insights[:2])}"
                                    )
                        else:
                            print("  No simulation results available.")
                    else:
                        print("  Usage: simulate <query>")
                    continue

                if command == "sims":
                    # Show simulation statistics
                    sim_stats = parallel_simulation.get_simulation_statistics()

                    print(f"\n🧠 **Parallel Simulation Statistics:**")
                    print(f"  Total simulations: {sim_stats['total_simulations']}")
                    print(f"  Active simulations: {sim_stats['active_simulations']}")
                    print(f"  Queue size: {sim_stats['queue_size']}")

                    print(f"\n  Status breakdown:")
                    for status, count in sim_stats["status_breakdown"].items():
                        print(f"    {status}: {count}")

                    print(f"\n  Type breakdown:")
                    for sim_type, count in sim_stats["type_breakdown"].items():
                        print(f"    {sim_type}: {count}")

                    print(f"\n  Performance:")
                    perf = sim_stats["performance"]
                    print(f"    Success rate: {perf['success_rate']:.1%}")
                    print(
                        f"    Average execution time: {perf['average_execution_time']:.2f}s"
                    )
                    print(f"    Average confidence: {perf['average_confidence']:.1%}")
                    print(f"    Average relevance: {perf['average_relevance']:.1%}")

                    print(f"\n  Configuration:")
                    print(f"    Max workers: {sim_stats['max_workers']}")
                    print(f"    Max concurrent: {sim_stats['max_concurrent']}")
                    continue

                if command.startswith("sim "):
                    # Get specific simulation result
                    sim_id = (
                        command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
                    )
                    if sim_id:
                        result = parallel_simulation.get_simulation_result(sim_id)

                        if result:
                            print(f"\n🧠 **Simulation Result:**")
                            print(f"  ID: {result.instance_id}")
                            print(f"  Type: {result.simulation_type.value}")
                            print(f"  Confidence: {result.confidence:.1%}")
                            print(f"  Execution time: {result.execution_time:.2f}s")
                            print(f"  Reasoning: {result.reasoning}")

                            print(f"\n  Outcome:")
                            for key, value in result.outcome.items():
                                if isinstance(value, list) and len(value) > 0:
                                    print(f"    {key}: {len(value)} items")
                                    for item in value[:2]:
                                        print(f"      - {item}")
                                else:
                                    print(f"    {key}: {value}")

                            if result.insights:
                                print(f"\n  Insights:")
                                for insight in result.insights:
                                    print(f"    • {insight}")

                            if result.cross_references:
                                print(
                                    f"\n  Cross-references: {len(result.cross_references)}"
                                )

                            if result.possibilities:
                                print(f"\n  Possibilities: {len(result.possibilities)}")
                                for i, poss in enumerate(result.possibilities[:3], 1):
                                    if isinstance(poss, dict):
                                        desc = poss.get("description", str(poss))
                                    else:
                                        desc = str(poss)
                                    print(f"    {i}. {desc[:60]}...")
                        else:
                            print(f"  No result found for simulation ID: {sim_id}")
                    else:
                        print("  Usage: sim <simulation_id>")
                    continue

                if command == "clearsims":
                    # Clear completed simulations
                    parallel_simulation.clear_completed_simulations()
                    print(f"\n🗑️ **Cleared completed simulations**")
                    continue

                if command.startswith("possibilities "):
                    # Explore possibility space for a topic
                    topic = (
                        command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
                    )
                    if topic:
                        print(f"\n🌌 **Exploring possibility space for:** {topic}")
                        print("  Running comprehensive simulation...")

                        sim_id = parallel_simulation.create_simulation(
                            simulation_type=SimulationType.POSSIBILITY_SPACE,
                            input_data={"topic": topic, "constraints": {}},
                            parameters={"priority": 0.8, "timeout": 30},
                        )

                        result = parallel_simulation.wait_for_simulation(
                            sim_id, timeout=35.0
                        )

                        if result and result.outcome:
                            outcome = result.outcome
                            print(f"\n📊 **Possibility Space Analysis:**")
                            print(
                                f"  Total dimensions: {outcome.get('total_dimensions', 0)}"
                            )
                            print(
                                f"  Total combinations: {outcome.get('total_combinations', 0)}"
                            )
                            print(
                                f"  Recommendation: {outcome.get('exploration_recommendation', '')}"
                            )

                            space = outcome.get("possibility_space", [])
                            if space:
                                print(f"\n  Dimensions:")
                                for dim in space:
                                    print(
                                        f"    • {dim.get('name', 'unknown')}: {dim.get('complexity', '')} complexity, {dim.get('impact', '')} impact"
                                    )
                                    possibilities = dim.get("possibilities", [])
                                    for poss in possibilities[:3]:
                                        print(f"      - {poss}")

                            if result.insights:
                                print(f"\n  Insights:")
                                for insight in result.insights:
                                    print(f"    • {insight}")
                        else:
                            print("  Failed to explore possibility space.")
                    else:
                        print("  Usage: possibilities <topic>")
                    continue

                system_prompt_var = (
                    system_prompt if "system_prompt" in locals() else None
                )

                # Optional Glimpse preflight before sending to model
                final_message = user_input
                if preflight_enabled:
                    draft = Draft(
                        input_text=final_message,
                        goal=preflight_goal,
                        constraints=preflight_constraints,
                    )
                    # First glimpse
                    res1 = asyncio.run(glimpse_engine.glimpse(draft))
                    print("\n— Glimpse 1 —")
                    if res1.status_history:
                        print("Status:", " | ".join(res1.status_history))
                    if res1.sample:
                        print("Sample:", res1.sample)
                    if res1.essence:
                        print("Essence:", res1.essence)
                    if res1.delta:
                        print("Delta:", res1.delta)
                        if isinstance(res1.delta, str) and res1.delta.startswith(
                            "Clarifier:"
                        ):
                            ans = input("Answer clarifier [Y/N]: ").strip().lower()
                            if ans == "y":
                                # Add audience constraint to prevent repeated clarifiers
                                if preflight_constraints:
                                    preflight_constraints = (
                                        preflight_constraints + " | audience: external"
                                    )
                                else:
                                    preflight_constraints = "audience: external"
                                print("✓ Added audience: external constraint")
                            elif ans == "n":
                                # Add audience constraint to prevent repeated clarifiers
                                if preflight_constraints:
                                    preflight_constraints = (
                                        preflight_constraints + " | audience: internal"
                                    )
                                else:
                                    preflight_constraints = "audience: internal"
                                print("✓ Added audience: internal constraint")

                    # Offer essence-only toggle if latency options appeared (≥800 ms)
                    if any("Options:" in s for s in res1.status_history):
                        eo = (
                            input(
                                "Latency is high. Enable essence-only for next attempt? [y/N]: "
                            )
                            .strip()
                            .lower()
                        )
                        if eo == "y":
                            glimpse_engine.set_essence_only(True)
                            print("✓ Essence-only glimpses enabled")

                    proceed = "n"
                    if res1.status == "aligned":
                        proceed = (
                            input("Proceed with commit? [y/N]: ").strip().lower() or "n"
                        )
                    else:
                        choice = (
                            input(
                                "Adjust once (a), Redial (r), or Proceed (y)? [a/r/y]: "
                            )
                            .strip()
                            .lower()
                        )
                        if choice == "r":
                            print("Clean reset. Same channel. Let’s try again.")
                            continue
                        elif choice == "y":
                            proceed = "y"
                        else:
                            # Adjust once
                            try:
                                edited = input("Edit message (enter to keep): ").strip()
                                if edited:
                                    final_message = edited
                                g2 = input("Edit goal (enter to keep): ").strip()
                                if g2:
                                    preflight_goal = g2
                                c2 = input("Edit constraints (enter to keep): ").strip()
                                if c2:
                                    preflight_constraints = c2
                            except KeyboardInterrupt:
                                print("\n(adjustment canceled)")
                                continue

                            draft = Draft(
                                input_text=final_message,
                                goal=preflight_goal,
                                constraints=preflight_constraints,
                            )
                            res2 = asyncio.run(glimpse_engine.glimpse(draft))
                            print("\n— Glimpse 2 —")
                            if res2.status_history:
                                print("Status:", " | ".join(res2.status_history))
                            if res2.sample:
                                print("Sample:", res2.sample)
                            if res2.essence:
                                print("Essence:", res2.essence)
                            if res2.delta:
                                print("Delta:", res2.delta)
                                if isinstance(
                                    res2.delta, str
                                ) and res2.delta.startswith("Clarifier:"):
                                    ans2 = (
                                        input("Answer clarifier [Y/N]: ")
                                        .strip()
                                        .lower()
                                    )
                                    if ans2 == "y":
                                        # Add audience constraint to prevent repeated clarifiers
                                        if preflight_constraints:
                                            preflight_constraints = (
                                                preflight_constraints
                                                + " | audience: external"
                                            )
                                        else:
                                            preflight_constraints = "audience: external"
                                        print("✓ Added audience: external constraint")
                                    elif ans2 == "n":
                                        # Add audience constraint to prevent repeated clarifiers
                                        if preflight_constraints:
                                            preflight_constraints = (
                                                preflight_constraints
                                                + " | audience: internal"
                                            )
                                        else:
                                            preflight_constraints = "audience: internal"
                                        print("✓ Added audience: internal constraint")

                            # Offer essence-only toggle if latency options appeared (≥800 ms)
                            if any("Options:" in s for s in res2.status_history):
                                eo2 = (
                                    input(
                                        "Latency is high. Enable essence-only for next attempt? [y/N]: "
                                    )
                                    .strip()
                                    .lower()
                                )
                                if eo2 == "y":
                                    glimpse_engine.set_essence_only(True)
                                    print("✓ Essence-only glimpses enabled")

                            if res2.status != "aligned":
                                print("Clean reset. Same channel. Let’s try again.")
                                continue
                            proceed = (
                                input("Proceed with commit? [y/N]: ").strip().lower()
                                or "n"
                            )

                    if proceed != "y":
                        print("(Canceled before commit)")
                        continue

                # Mark preflight committed (side effects begin here)
                if preflight_enabled:
                    glimpse_engine.commit(
                        Draft(
                            input_text=final_message,
                            goal=preflight_goal,
                            constraints=preflight_constraints,
                        )
                    )

                response = assistant.chat(
                    final_message,
                    system_prompt=system_prompt_var,
                    stream=streaming_enabled,
                    show_status=status_enabled,
                )

                if not streaming_enabled:
                    print(f"\nEchoes: {response}")
                else:
                    # Handle streaming response
                    print("\nEchoes: ", end="", flush=True)
                    for chunk in response:
                        print(chunk, end="", flush=True)
                    print()  # New line after stream completes

            except KeyboardInterrupt:
                print("\n\nUse 'exit' or 'quit' to end the session.")
                continue
            except Exception as e:
                print(f"\nError: {str(e)}")

    except Exception as e:
        print(f"Failed to initialize assistant: {str(e)}")
        sys.exit(1)


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
    analyze_parser.add_argument(
        "--exclude",
        "-e",
        nargs="+",
        default=[".git", "__pycache__", "node_modules", "venv", ".venv", "env"],
        help="Directories to exclude",
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
    elif args.command == "analyze":
        try:
            assistant = EchoesAssistantV2()
            print(f"{STATUS_SEARCH} Analyzing directory: {args.directory}")
            result = assistant.analyze_directory(
                directory_path=args.directory,
                output_file=args.output,
                max_depth=args.depth,
                exclude_dirs=args.exclude,
            )
            if not args.output:
                print("\n" + "=" * 80)
                print(f"📋 Analysis Report for: {result['directory']}")
                print("=" * 80)
                print(result.get("analysis", "No analysis generated."))
                print("=" * 80)
        except Exception as exc:
            print(f"\n{STATUS_ERROR} Error: {exc}")
            sys.exit(1)
    elif args.command == "run":
        if not args.message:
            print(
                "No message provided. Use: python assistant_v2_core.py run <your message>"
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
