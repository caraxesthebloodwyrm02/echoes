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
import os
# ============================================================================
# Standard library imports
# ============================================================================
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Union

# Status constants
STATUS_RETRY = "[SYNC]"  # Unicode character for retry/refresh

from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("[WARN]  Missing: pyyaml. Install with: pip install pyyaml")
    yaml = None
    YAML_AVAILABLE = False

# Core dependencies
from dotenv import load_dotenv
from openai import APIError, AuthenticationError, OpenAI
# Quantum State Management
from quantum_state import QuantumStateManager

# Action Execution
from app.actions import ActionExecutor
# Agent Workflow System
from app.agents import AgentWorkflow
# Filesystem Tools
from app.filesystem import FilesystemTools
# Knowledge Management
from app.knowledge import KnowledgeManager
# Dynamic Model Router
from app.model_router import ModelMetrics, ModelResponseCache, ModelRouter
# Value System Integration
from app.values import get_value_system
from glimpse.Glimpse import Draft, GlimpseEngine, PrivacyGuard
from tools.examples import *  # Load all built-in tools
# Tool Framework
from tools.registry import get_registry

# RAG System V2
try:
    from echoes.core.rag_v2 import OPENAI_RAG_AVAILABLE, create_rag_system
    RAG_AVAILABLE = True
    if OPENAI_RAG_AVAILABLE:
        print("[OK] OpenAI RAG system available")
    else:
        print("[OK] Legacy RAG system available (OpenAI RAG not available)")
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

# Status indicator characters
STATUS_SPINNER = ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]", "[7]", "[8]", "[9]", "[0]"]
STATUS_COMPLETE = "[OK]"
STATUS_ERROR = "✗"
STATUS_WORKING = "⚙"
STATUS_SEARCH = "[SEARCH]"
STATUS_TOOL = "[TOOL]"


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
            elapsed = f"({(time.time() - self.phase_start_time)*1000:.0f}ms)" if self.phase_start_time else ""
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
        elapsed = f"({(time.time() - self.phase_start_time)*1000:.0f}ms)" if self.phase_start_time else ""
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
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2 :]

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
        model: str = MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        rag_preset: str = "balanced",
        enable_rag: bool = True,
        enable_tools: bool = True,
        enable_streaming: bool = True,
        enable_status: bool = True,
        enable_value_system: bool = True,
        session_id: Optional[str] = None,
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
        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)
            
            # Phase 2: Planning  
            plan_approach(request)
            
            # Phase 3: Execution
            execute_plan()

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
            from tools.examples import get_example_tools
            example_tools = get_example_tools()
            for tool in example_tools:
                self.tool_registry.register(tool, category="general")
            
            print(f"[OK] Loaded {len(self.tool_registry.list_tools())} tools")

        # Action execution
        self.action_executor = ActionExecutor()
        print("[OK] Action executor initialized")

        # Knowledge management
        self.knowledge_manager = KnowledgeManager()
        print("[OK] Knowledge manager initialized")

        # Filesystem tools
        self.fs_tools = FilesystemTools(root_dir=os.getcwd())
        print("[OK] Filesystem tools initialized")

        # Agent workflow system
        self.agent_workflow = AgentWorkflow(self)
        print("[OK] Agent workflow system initialized")

        # Quantum state management
        self.quantum_state_manager = QuantumStateManager()
        self.quantum_state_manager.initialize_quantum_states()
        print("[OK] Quantum state management initialized")

        # Phase 4: Advanced Features
        # RAG system
        self.enable_rag = enable_rag and RAG_AVAILABLE
        self.rag = None
        if self.enable_rag:
            try:
                self.rag = create_rag_system(rag_preset)
                print(f"[OK] RAG system initialized ({rag_preset} preset)")
            except Exception as e:
                print(f"[WARN] RAG initialization failed: {e}")
                self.enable_rag = False

        # Configuration
        self.enable_streaming = enable_streaming
        self.enable_status = enable_status
        self.enable_value_system = enable_value_system

        # Value System Integration
        self.value_system = None
        if self.enable_value_system:
            try:
                self.value_system = get_value_system()
                print("[OK] Value system initialized")
            except Exception as e:
                print(f"[WARN] Value system initialization failed: {e}")
                self.enable_value_system = False

        # Human-in-the-loop / policy configuration
        self.hitl_enabled = os.getenv("HITL_ENABLED", "false").lower() in ("1", "true", "yes")
        self.policy_model = "gpt-4o"

        # PHASE 2: Responses API Migration Feature Flag
        self.use_responses_api = os.getenv("USE_RESPONSES_API", "false").lower() in ("1", "true", "yes")

        print(f"[OK] Echoes Assistant V2 ready (session: {self.session_id}, responses_api: {self.use_responses_api})")

    def add_knowledge(self, documents: List[Union[str, Dict]], metadata: Optional[Dict] = None) -> Dict[str, Any]:
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

            result = self.rag.search(query, top_k=top_k)
            
            # Handle different result formats
            if isinstance(result, dict):
                results = result.get("results", [])
            elif isinstance(result, list):
                results = result
            else:
                results = []

            if status and results:
                status.complete_phase(f"Found {len(results)} relevant documents")

            return [{"text": r.get("content", r.get("text", "")), "score": r.get("score", 0.0), "metadata": r.get("metadata", {})} for r in results]
        except Exception as e:
            if status:
                status.error(f"RAG search failed: {str(e)}")
            return []

    def _execute_tool_call(self, tool_call, status: Optional[EnhancedStatusIndicator] = None) -> str:
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
            args_str = ", ".join([f"{k}={v}" for k, v in list(function_args.items())[:2]])
            if len(function_args) > 2:
                args_str += "..."

        if not self.enable_value_system or not self.value_system:
            return response_text
            
        try:
            # Evaluate the response against our values
            scores = self.value_system.evaluate_response(response_text, context)
            overall = self.value_system.get_overall_score(scores)
            
            # If score is below threshold, try to improve
            if overall < 0.6:  # Adjust threshold as needed
                improved = self._improve_response(response_text, scores)
                if improved:
                    return improved
                    
            return response_text
            
        except Exception as e:
            print(f"[WARN] Error in value guard: {str(e)}")
            return response_text  # Return original on error

    def _improve_response(self, original: str, scores: Dict[str, float]) -> Optional[str]:
        try:
            # Identify which values need improvement
            improvements = []
            if scores.get('respect', 1.0) < 0.6:
                improvements.append("more respectful and considerate")
            if scores.get('accuracy', 1.0) < 0.6:
                improvements.append("more accurate and precise")
            if scores.get('helpfulness', 1.0) < 0.6:
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
                max_tokens=len(original) + 100  # Allow some expansion
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
            print(f"[WARN] Error improving response: {str(e)}")
            return None

    def provide_feedback(
        self, 
        response_id: str, 
        ratings: Dict[str, float],
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.enable_value_system or not self.value_system:
            return {"success": False, "error": "Value system is not enabled"}
            
        # Get the conversation history
        messages = self.context_manager.get_messages(self.session_id)
        
        # Find the target message
        target_msg = None
        for msg in reversed(messages):  # Search most recent first
            if msg.get('id') == response_id and msg.get('role') == 'assistant':
                target_msg = msg
                break
        
        if not target_msg:
            return {"success": False, "error": "Response not found in current session"}
        
        # Update value system with feedback
        self.value_system.provide_feedback(
            response=target_msg['content'],
            user_feedback=ratings
        )
        
        # Log the feedback
        feedback_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'response_id': response_id,
            'ratings': ratings,
            'comment': comment
        }
        
        # Save feedback to a file
        feedback_dir = Path("data/feedback")
        feedback_dir.mkdir(exist_ok=True, parents=True)
        
        feedback_file = feedback_dir / f"feedback_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        
        return {
            "success": True,
            "message": "Feedback received and processed",
            "current_values": self.value_system.get_values_summary()
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
        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)
            
            # Phase 2: Planning  
            plan_approach(request)
            
            # Phase 3: Execution
            execute_plan()

        # Phase 1: Setup and Validation
        stream = stream if stream is not None else self.enable_streaming
        show_status = show_status if show_status is not None else self.enable_status
        require_approval = require_approval if require_approval is not None else self.hitl_enabled

        # Status indicator
        status = EnhancedStatusIndicator(enabled=show_status)

        try:
            # Phase 2: Message Building
            # Build messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            history = self.context_manager.get_messages(self.session_id, limit=context_limit)
            messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])

            # Retrieve context from RAG
            rag_context = []
            if self.enable_rag and self.rag:
                rag_context = self._retrieve_context(message, top_k=3, status=status)

                if rag_context:
                    context_text = "\n\n".join(
                        [f"[Source {i+1}]: {ctx['text'][:200]}..." for i, ctx in enumerate(rag_context)]
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

            # Multi-step tool calling with enhanced logging and error handling
            iteration = 0
            all_tool_results = []
            tool_calling_enabled = self.enable_tools and self.tool_registry is not None
            
            # Select the best model for this request
            selected_model = self.model_router.select_model(message, tools)
            start_time = time.time()

            # Phase 4: Tool Execution Loop
            while iteration < MAX_TOOL_ITERATIONS:
                try:
                    # Make API call with dynamic model selection
                    if self.use_responses_api:
                        # PHASE 2: NEW - Responses API implementation
                        response = self.client.responses.create(
                            model=selected_model,
                            input=messages,  # messages array becomes input
                            tools=tools if tool_calling_enabled else None,
                            tool_choice="auto" if (tools and tool_calling_enabled) else None,
                            temperature=self.temperature,
                            max_output_tokens=self.max_tokens,  # renamed parameter
                            stream=False,
                        )

                        # PHASE 2: NEW - Extract tool calls from response.output
                        tool_calls = []
                        for output_item in response.output:
                            if output_item.type == "tool_call":
                                tool_calls.append(output_item.content)
                    else:
                        # EXISTING - Chat Completions API implementation
                        response = self.client.chat.completions.create(
                            model=selected_model,
                            messages=messages,
                            tools=tools if tool_calling_enabled else None,
                            tool_choice="auto" if (tools and tool_calling_enabled) else None,
                            temperature=self.temperature,
                            max_completion_tokens=self.max_tokens if 'o3' in selected_model else None,
                            max_tokens=self.max_tokens if 'o3' not in selected_model else None,
                            stream=False,
                        )

                        # EXISTING - Extract tool calls from message
                        response_message = response.choices[0].message
                        tool_calls = getattr(response_message, "tool_calls", None)

                    # If no tool calls, we're done with tool execution
                    if not tool_calls:
                        break

                    # Validate tool calling is enabled before processing
                    if not tool_calling_enabled:
                        if status:
                            status.error("Tool calling disabled but model returned tool calls")
                        break

                    # Initialize status for tool execution
                    if status and iteration == 0:
                        status.start_phase(
                            f"{STATUS_TOOL} Planning and executing {len(tool_calls)} action(s)", len(tool_calls)
                        )

                    # Add assistant message
                    if self.use_responses_api:
                        # PHASE 2: NEW - For Responses API, create a synthetic message from output
                        assistant_content = ""
                        tool_calls_for_message = []
                        for output_item in response.output:
                            if output_item.type == "text":
                                assistant_content += output_item.content
                            elif output_item.type == "tool_call":
                                tool_calls_for_message.append(output_item.content)

                        # Create synthetic message structure
                        response_message = type('Message', (), {
                            'content': assistant_content,
                            'tool_calls': tool_calls_for_message if tool_calls_for_message else None
                        })()
                    else:
                        # EXISTING - response_message already extracted above
                        pass

                    messages.append(response_message)

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
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_call.function.name,
                                "content": function_response,
                            }
                        )

                    iteration += 1

                except APIError as e:
                    error_msg = f"API error during tool calling with {selected_model}: {str(e)}"
                    if status:
                        status.error(error_msg)
                    
                    # Record metrics and try fallback
                    response_time = time.time() - start_time
                    # Use sync version since chat method is not async
                    self.model_metrics.record_usage_sync(selected_model, response_time, success=False)
                    
                    # Fallback to default model if different
                    if selected_model != self.default_model:
                        if status:
                            status.start_phase(f"{STATUS_RETRY} Retrying with {self.default_model}", 0)
                        try:
                            if self.use_responses_api:
                                # PHASE 2: NEW - Responses API fallback
                                response = self.client.responses.create(
                                    model=self.default_model,
                                    input=messages,
                                    tools=tools if tool_calling_enabled else None,
                                    tool_choice="auto" if (tools and tool_calling_enabled) else None,
                                    temperature=self.temperature,
                                    max_output_tokens=self.max_tokens,
                                    stream=False,
                                )

                                # PHASE 2: NEW - Extract tool calls from response.output
                                tool_calls = []
                                for output_item in response.output:
                                    if output_item.type == "tool_call":
                                        tool_calls.append(output_item.content)
                            else:
                                # EXISTING - Chat Completions API fallback
                                response = self.client.chat.completions.create(
                                    model=self.default_model,
                                    messages=messages,
                                    tools=tools if tool_calling_enabled else None,
                                    tool_choice="auto" if (tools and tool_calling_enabled) else None,
                                    temperature=self.temperature,
                                    max_completion_tokens=self.max_tokens if 'o3' in self.default_model else None,
                                    max_tokens=self.max_tokens if 'o3' not in self.default_model else None,
                                    stream=False,
                                )

                                # EXISTING - Extract tool calls from message
                                response_message = response.choices[0].message
                                tool_calls = getattr(response_message, "tool_calls", None)

                            selected_model = self.default_model
                        except APIError as fallback_error:
                            error_msg = f"Fallback also failed: {str(fallback_error)}"
                            if status:
                                status.error(error_msg)
                            return error_msg
                    else:
                        return error_msg

        except AuthenticationError as e:
            error_msg = f"Authentication Error: {str(e)}\nPlease check your OPENAI_API_KEY"
            if status:
                status.error(error_msg)
            return error_msg
        except APIError as e:
            error_msg = f"API Error: {str(e)}"
            if status:
                status.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if status:
                status.error(error_msg)
            return error_msg

    def get_conversation_history(self) -> List[Dict]:
        return self.context_manager.get_messages(self.session_id)

    def clear_history(self):
        self.context_manager.clear_session(self.session_id)

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        if not self.tool_registry:
            return []
        return self.tool_registry.list_tools(category)

    def execute_action(self, action_type: str, action_name: str, **kwargs) -> Dict[str, Any]:
        Execute an action on behalf of the user.

        Args:
            action_type: Type of action ('inventory', 'tool')
            action_name: Name of the specific action
            **kwargs: Action parameters

        Returns:
            Action result with status and data
        if action_type == "inventory":
            result = self.action_executor.execute_inventory_action(action_name, **kwargs)
        elif action_type == "tool":
            result = self.action_executor.execute_tool_action(action_name, **kwargs)
        elif action_type == "roi":
            result = self.action_executor.execute_roi_action(action_name, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}",
            }

        return {
            "success": result.status == "success",
            "action_id": result.action_id,
            "action_type": result.action_type,
            "result": result.result,
            "error": result.error,
            "duration_ms": result.duration_ms,
        }

    def get_action_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.action_executor.get_action_history(limit)

    def get_action_summary(self) -> Dict[str, Any]:
        return self.action_executor.get_action_summary()

    def gather_knowledge(
        self, content: str, source: str, category: str = "general", tags: Optional[List[str]] = None
    ) -> str:
        return self.knowledge_manager.add_knowledge(content, source, category, tags)

    def search_knowledge(
        self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        entries = self.knowledge_manager.search_knowledge(query, category, limit=limit)
        return [e.to_dict() for e in entries]

    def store_roi_analysis(self, roi_results: Dict[str, Any], analysis_id: Optional[str] = None) -> str:
        return self.knowledge_manager.store_roi_analysis(roi_results, analysis_id)

    def search_roi_analyses(self, institution: Optional[str] = None, business_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        entries = self.knowledge_manager.search_roi_analyses(institution, business_type, limit)
        return [e.to_dict() for e in entries]

    def get_roi_summary(self) -> Dict[str, Any]:
        return self.knowledge_manager.get_roi_summary()

    def list_directory(self, dirpath: str, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        return self.fs_tools.list_directory(dirpath, pattern, recursive)

    def read_file(self, filepath: str) -> Dict[str, Any]:
        return self.fs_tools.read_file(filepath)

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        return self.fs_tools.write_file(filepath, content)

    def search_files(self, query: str, search_path: Optional[str] = None) -> Dict[str, Any]:
        return self.fs_tools.search_files(query, search_path)

    def organize_roi_files(self, roi_results: Dict[str, Any], base_dir: str = "roi_analysis") -> Dict[str, Any]:
        return self.fs_tools.organize_roi_files(roi_results, base_dir)

    def run_workflow(self, workflow_type: str, **kwargs) -> Dict[str, Any]:
        if workflow_type == "triage":
            result = self.agent_workflow.run_triage_workflow(
                user_input=kwargs.get("user_input", ""), context=kwargs.get("context")
            )
        elif workflow_type == "comparison":
            result = self.agent_workflow.run_comparison_workflow(file1=kwargs.get("file1"), file2=kwargs.get("file2"))
        elif workflow_type == "data_enrichment":
            result = self.agent_workflow.run_data_enrichment_workflow(
                topic=kwargs.get("topic"), context=kwargs.get("context")
            )
        else:
            return {"success": False, "error": f"Unknown workflow type: {workflow_type}"}

        return result.to_dict()

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "session_id": self.session_id,
            "messages": len(self.context_manager.get_messages(self.session_id)),
            "rag_enabled": self.enable_rag,
            "tools_enabled": self.enable_tools,
            "value_system_enabled": self.enable_value_system,
            "actions": self.get_action_summary(),
            "knowledge": self.knowledge_manager.get_stats(),
        }

        if self.tool_registry:
            stats["tool_stats"] = self.tool_registry.get_stats()

        if self.rag:
            stats["rag_stats"] = self.rag.get_stats() if hasattr(self.rag, "get_stats") else {}

        if self.enable_value_system and self.value_system:
            stats["value_system"] = self.value_system.get_values_summary()

        return stats

    def update_quantum_state(self, key: str, value: Any, entangle_with: List[str] = None) -> Dict[str, Any]:
        Update a quantum state with optional entanglement.

        Args:
            key: State key to update
            value: New value for the state
            entangle_with: Keys to entangle with this state

        Returns:
            Result with success status and entangled states
        try:
            self.quantum_state_manager.update_state(key, value, entangle_with)
            entangled = self.quantum_state_manager.get_entangled_states(key) if entangle_with else {}
            return {
                "success": True,
                "key": key,
                "value": value,
                "entangled": entangled
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def measure_quantum_state(self, key: str) -> Dict[str, Any]:
        Measure (read) a quantum state.

        Args:
            key: State key to measure

        Returns:
            Result with measured value
        try:
            value = self.quantum_state_manager.measure_state(key)
            return {
                "success": True,
                "key": key,
                "value": value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_quantum_superposition(self, keys: List[str]) -> Dict[str, Any]:
        Get multiple quantum states in superposition.

        Args:
            keys: List of state keys to retrieve

        Returns:
            Result with superposition of states
        try:
            superposition = self.quantum_state_manager.get_superposition(keys)
            return {
                "success": True,
                "superposition": superposition
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_quantum_entangled_states(self, key: str) -> Dict[str, Any]:
        Get states entangled with the given key.

        Args:
            key: State key to check entanglement for

        Returns:
            Result with entangled states
        try:
            entangled = self.quantum_state_manager.get_entangled_states(key)
            return {
                "success": True,
                "key": key,
                "entangled": entangled
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def transition_quantum_state(self) -> Dict[str, Any]:
        Perform a probabilistic quantum state transition.

        Returns:
            Result with new state after transition
        try:
            new_state = self.quantum_state_manager.transition_state()
            return {
                "success": True,
                "new_state": new_state
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_quantum_state_history(self, key: str) -> Dict[str, Any]:
        Get historical values for a quantum state.

        Args:
            key: State key to get history for

        Returns:
            Result with state history
        try:
            history = self.quantum_state_manager.get_state_history(key)
            return {
                "success": True,
                "key": key,
                "history": history
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_quantum_metrics(self) -> Dict[str, Any]:
        Get quantum state management performance metrics.

        Returns:
            Result with performance metrics
        try:
            metrics = self.quantum_state_manager.get_metrics()
            return {
                "success": True,
                "metrics": {
                    "total_updates": metrics.total_updates,
                    "total_measurements": metrics.total_measurements,
                    "average_transition_time": metrics.average_transition_time,
                    "entangled_states_count": metrics.entangled_states_count,
                    "last_updated": metrics.last_updated.isoformat() if metrics.last_updated else None
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def save_quantum_state(self, filepath: str = "quantum_state_backup.json") -> Dict[str, Any]:
        Save the current quantum state to a file.

        Args:
            filepath: Path to save the state file

        Returns:
            Result with save status
        try:
            # Create a temporary quantum state manager with persistence
            temp_qsm = QuantumStateManager(persistence_file=filepath)
            # Copy current state
            temp_qsm.quantum_state._state = self.quantum_state_manager.quantum_state._state.copy()
            temp_qsm.quantum_state._entangled = self.quantum_state_manager.quantum_state._entangled.copy()
            temp_qsm.quantum_state._history = self.quantum_state_manager.quantum_state._history.copy()
            temp_qsm.state_machine = self.quantum_state_manager.state_machine
            temp_qsm.metrics = self.quantum_state_manager.metrics
            temp_qsm.interference_patterns = self.quantum_state_manager.interference_patterns.copy()

            temp_qsm.save_state()
            return {
                "success": True,
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def load_quantum_state(self, filepath: str = "quantum_state_backup.json") -> Dict[str, Any]:
        try:
            temp_qsm = QuantumStateManager(persistence_file=filepath)
            temp_qsm.load_state()

            # Copy loaded state to current manager
            self.quantum_state_manager.quantum_state._state = temp_qsm.quantum_state._state.copy()
            self.quantum_state_manager.quantum_state._entangled = temp_qsm.quantum_state._entangled.copy()
            self.quantum_state_manager.quantum_state._history = temp_qsm.quantum_state._history.copy()
            self.quantum_state_manager.state_machine = temp_qsm.state_machine
            self.quantum_state_manager.metrics = temp_qsm.metrics
            self.quantum_state_manager.interference_patterns = temp_qsm.interference_patterns.copy()

            return {
                "success": True,
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

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

        structure = self._get_directory_structure(directory_path, max_depth, exclude_dirs)
        stats = self._collect_file_stats(structure)

        file_types = sorted(stats["file_types"].items(), key=lambda item: item[1], reverse=True)
        top_file_types = file_types[:20]
        if len(file_types) > 20:
            remaining = sum(count for _, count in file_types[20:])
            top_file_types.append(("other", remaining))
        file_type_summary = ", ".join(f"{ext or 'no-ext'}: {count}" for ext, count in top_file_types) or "None"

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
        top_directories_summary = self._summarize_top_directories(structure, max_entries=20)
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
                max_completion_tokens=3000 if 'o3' in self.model else None,
                max_tokens=3000 if 'o3' not in self.model else None,
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

    def _get_directory_structure(self, root_path: Path, max_depth: int, exclude_dirs: List[str]) -> Dict[str, Any]:
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
                if item.name in exclude_dirs or any(item.match(pattern) for pattern in exclude_dirs):
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
                    child_structure = self._get_directory_structure(item, max_depth - 1, exclude_dirs)
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

    def _format_directory_structure(self, structure: Dict[str, Any], indent: int = 0, max_lines: int = 400) -> str:
        lines: List[str] = []
        truncated = False

        def _walk(node: Dict[str, Any], depth: int) -> None:
            nonlocal truncated
            if truncated:
                return

            prefix = "  " * depth
            if node.get("type") == "file":
                size_mb = node.get("size", 0) / (1024 * 1024)
                line = f"{prefix}[FILE] {node.get('name')} ({size_mb:.2f} MB)"
                lines.append(line)
            else:
                file_count = node.get("file_count", 0)
                dir_count = node.get("dir_count", 0)
                line = f"{prefix}[FOLDER] {node.get('name')}/"
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

    def _summarize_top_directories(self, structure: Dict[str, Any], max_entries: int = 20) -> str:
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
            
            print("\n" + "="*50)
            print("ECHOES ASSISTANT - MODEL METRICS")
            print("="*50)
            print(f"Total Requests: {metrics['total_requests']}")
            
            print("\nModel Usage:")
            for model, count in metrics['model_usage'].items():
                print(f"  - {model}: {count} requests")
                
            print("\nAverage Response Times:")
            for model, stats in metrics['response_times'].items():
                if stats['count'] > 0:
                    print(f"  - {model}: {stats['avg']:.2f}s (min: {stats['min']:.2f}s, max: {stats['max']:.2f}s)")
            
            if metrics['errors']:
                print("\nErrors:")
                for model, count in metrics['errors'].items():
                    print(f"  - {model}: {count} errors")
                    
            if 'cache_hit_rate' in metrics:
                print("\nCache Hit Rates:")
                for model, rate in metrics['cache_hit_rate'].items():
                    print(f"  - {model}: {rate:.1%}")
            
            print("="*50 + "\n")
        
        # Run the async function
        asyncio.run(_print_metrics())
        
    def reset_model_metrics(self):
        import asyncio
        asyncio.run(self.model_metrics.reset_metrics())
        print("[OK] Model metrics reset")


def interactive_mode(system_prompt=None):
    print("\n" + "=" * 60)
    print("Echoes AI Assistant V2 - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  'exit' or 'quit'     - Exit the assistant")
    print("  'history'            - Show conversation history")
    print("  'clear'              - Clear conversation history")
    print("  'tools'              - List available tools")
    print("  'stats'              - Show statistics")
    print("  'actions'            - Show action history")
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
                from datetime import datetime as _dt
                from datetime import timezone as _tz
                rec = {
                    "ts": _dt.now(_tz.utc).isoformat(),
                    "input_text": d.input_text,
                    "goal": d.goal,
                    "constraints": d.constraints,
                }
                with open(os.path.join("results", "glimpse_commits.jsonl"), "a", encoding="utf-8") as f:
                    f.write(_json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                # Silent best-effort; never block user flow
                pass

        glimpse_engine = GlimpseEngine(privacy_guard=PrivacyGuard(on_commit=_commit_sink))

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                command = user_input.lower()

                if command in ("exit", "quit"):
                    print("\n[OK] Exiting Echoes Assistant V2...")
                    break

                if command == "history":
                    history = assistant.get_conversation_history()
                    print(f"\n[NOTE] Conversation History ({len(history)} messages):")
                    for msg in history[-10:]:  # Show last 10
                        print(f"  {msg['role']}: {msg['content'][:100]}...")
                    continue

                if command == "clear":
                    assistant.clear_history()
                    print("[OK] Conversation history cleared")
                    continue

                if command == "tools":
                    tools = assistant.list_tools()
                    print(f"\n[TOOL] Available Tools ({len(tools)}):")
                    for tool in tools:
                        print(f"  • {tool}")
                    continue

                if command == "stats":
                    stats = assistant.get_stats()
                    print("\n[STATS] Statistics:")
                    print(json.dumps(stats, indent=2))
                    continue

                if command == "actions":
                    history = assistant.get_action_history(limit=10)
                    print(f"\n[CLIP] Action History ({len(history)} actions):")
                    for action in history:
                        status_icon = "[OK]" if action["success"] else "✗"
                        print(
                            f"  {status_icon} {action['action_id']}: {action['action_type']} ({action['duration_ms']:.1f}ms)"
                        )
                    summary = assistant.get_action_summary()
                    print("\n[STATS] Action Summary:")
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
                        result = assistant.execute_action("inventory", "list_items", category=category)
                        if result["success"]:
                            items = result["result"]
                            print(f"\n📦 Inventory Items ({len(items)} total):")
                            for item in items[:10]:
                                print(f"  • {item['sku']}: {item['name']} ({item['quantity']} @ {item['location']})")
                            if len(items) > 10:
                                print(f"  ... and {len(items) - 10} more")
                        else:
                            print(f"  Error: {result['error']}")
                        continue

                    if action_cmd == "report":
                        report_type = parts[1] if len(parts) > 1 else "summary"
                        result = assistant.execute_action("inventory", "report", report_type=report_type)
                        if result["success"]:
                            print(f"\n[STATS] Inventory Report ({report_type}):")
                            print(json.dumps(result["result"], indent=2))
                        else:
                            print(f"  Error: {result['error']}")
                        continue

                if command == "stream on":
                    streaming_enabled = True
                    print("[OK] Streaming enabled")
                    continue

                if command == "stream off":
                    streaming_enabled = False
                    print("[OK] Streaming disabled")
                    continue

                if command == "status on":
                    status_enabled = True
                    print("[OK] Status indicators enabled")
                    continue

                if command == "status off":
                    status_enabled = False
                    print("[OK] Status indicators disabled")
                    continue

                if command == "preflight on":
                    preflight_enabled = True
                    print("[OK] Glimpse preflight enabled")
                    continue

                if command == "preflight off":
                    preflight_enabled = False
                    print("[OK] Glimpse preflight disabled")
                    continue

                if command == "anchors":
                    try:
                        g = input("Goal (enter to keep current): ").strip()
                        if g:
                            preflight_goal = g
                        c = input("Constraints (enter to keep current): ").strip()
                        if c:
                            preflight_constraints = c
                        print("[OK] Anchors updated")
                    except KeyboardInterrupt:
                        print("\n(anchors update canceled)")
                    continue

                if command == "essence-only on":
                    glimpse_engine.set_essence_only(True)
                    print("[OK] Essence-only glimpses enabled (no auto-apply)")
                    continue

                if command == "essence-only off":
                    glimpse_engine.set_essence_only(False)
                    print("[OK] Essence-only glimpses disabled")
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
                            print(f"[OK] Loaded prompt '{prompt_name}'")
                        else:
                            print(f"[WARN] Prompt '{prompt_name}' not found")
                    continue

                system_prompt_var = system_prompt if "system_prompt" in locals() else None

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
                        if isinstance(res1.delta, str) and res1.delta.startswith("Clarifier:"):
                            ans = input("Answer clarifier [Y/N]: ").strip().lower()
                            if ans == "y":
                                preflight_constraints = (preflight_constraints + " | audience: external").strip().strip("|").strip()
                            elif ans == "n":
                                preflight_constraints = (preflight_constraints + " | audience: internal").strip().strip("|").strip()

                    # Offer essence-only toggle if latency options appeared (≥800 ms)
                    if any("Options:" in s for s in res1.status_history):
                        eo = input("Latency is high. Enable essence-only for next attempt? [y/N]: ").strip().lower()
                        if eo == "y":
                            glimpse_engine.set_essence_only(True)
                            print("[OK] Essence-only glimpses enabled")

                    proceed = "n"
                    if res1.status == "aligned":
                        proceed = input("Proceed with commit? [y/N]: ").strip().lower() or "n"
                    else:
                        choice = input("Adjust once (a), Redial (r), or Proceed (y)? [a/r/y]: ").strip().lower()
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
                                if isinstance(res2.delta, str) and res2.delta.startswith("Clarifier:"):
                                    ans2 = input("Answer clarifier [Y/N]: ").strip().lower()
                                    if ans2 == "y":
                                        preflight_constraints = (preflight_constraints + " | audience: external").strip().strip("|").strip()
                                    elif ans2 == "n":
                                        preflight_constraints = (preflight_constraints + " | audience: internal").strip().strip("|").strip()

                            # Offer essence-only toggle if latency options appeared (≥800 ms)
                            if any("Options:" in s for s in res2.status_history):
                                eo2 = input("Latency is high. Enable essence-only for next attempt? [y/N]: ").strip().lower()
                                if eo2 == "y":
                                    glimpse_engine.set_essence_only(True)
                                    print("[OK] Essence-only glimpses enabled")

                            if res2.status != "aligned":
                                print("Clean reset. Same channel. Let’s try again.")
                                continue
                            proceed = input("Proceed with commit? [y/N]: ").strip().lower() or "n"

                    if proceed != "y":
                        print("(Canceled before commit)")
                        continue

                # Mark preflight committed (side effects begin here)
                if preflight_enabled:
                    glimpse_engine.commit(Draft(
                        input_text=final_message,
                        goal=preflight_goal,
                        constraints=preflight_constraints,
                    ))

                response = assistant.chat(
                    final_message,
                    system_prompt=system_prompt,
                    stream=streaming_enabled,
                    show_status=status_enabled,
                )

                if not streaming_enabled:
                    print(f"\nEchoes: {response}")

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

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a directory structure")
    analyze_parser.add_argument("directory", help="Directory to analyze")
    analyze_parser.add_argument("--output", "-o", help="File to write the analysis JSON")
    analyze_parser.add_argument("--depth", "-d", type=int, default=10, help="Maximum directory depth")
    analyze_parser.add_argument(
        "--exclude",
        "-e",
        nargs="+",
        default=[".git", "__pycache__", "node_modules", "venv", ".venv", "env"],
        help="Directories to exclude",
    )

    default_parser = subparsers.add_parser("run", help="Run a single prompt")
    default_parser.add_argument("message", nargs=argparse.REMAINDER, help="Message to send to the assistant")
    default_parser.add_argument("--prompt", "-p", help="Prompt file name (without .yaml)")

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
                print(f"[CLIP] Analysis Report for: {result['directory']}")
                print("=" * 80)
                print(result.get("analysis", "No analysis generated."))
                print("=" * 80)
        except Exception as exc:
            print(f"\n{STATUS_ERROR} Error: {exc}")
            sys.exit(1)
    elif args.command == "run":
        if not args.message:
            print("No message provided. Use: python assistant_v2_core.py run <your message>")
            sys.exit(1)
        try:
            assistant = EchoesAssistantV2()
            system_prompt = load_prompt(args.prompt) if args.prompt else None
            response = assistant.chat(" ".join(args.message), system_prompt=system_prompt, stream=False)
            print(response)
        except Exception as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        parser.print_help()
