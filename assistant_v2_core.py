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
# CRITICAL: Force stdlib path precedence to avoid shadowed modules
# ============================================================================
import sys
from pathlib import Path as _Path

_stdlib_path = _Path(sys.executable).parent / "Lib"
if str(_stdlib_path) not in sys.path:
    sys.path.insert(0, str(_stdlib_path))

# Now safe to import stdlib modules
import os
import json
import time
from typing import Dict, Any, Optional, List, Iterator, Union
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  Missing: pyyaml. Install with: pip install pyyaml")
    sys.exit(1)

# Core dependencies
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# Tool Framework
from tools.registry import get_registry
from tools.examples import *  # Load all built-in tools

# Action Execution
from app.actions import ActionExecutor

# Knowledge Management
from app.knowledge import KnowledgeManager

# Filesystem Tools
from app.filesystem import FilesystemTools

# Agent Workflow System
from app.agents import AgentWorkflow

# RAG System V2
try:
    from echoes.core.rag_v2 import create_rag_system

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAG V2 not available. Install with: pip install sentence-transformers faiss-cpu")

# Load environment variables
load_dotenv()


# Load prompts
def list_available_prompts() -> List[str]:
    """List all available YAML prompt files."""
    prompts_dir = Path("prompts")
    if not prompts_dir.exists():
        print(f"No prompts directory found at {prompts_dir}")
        return []

    return [f.stem for f in prompts_dir.glob("*.yaml")]


def show_prompt_content(prompt_name: str) -> None:
    """Display the content of a prompt file."""
    prompt_path = Path("prompts") / f"{prompt_name}.yaml"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"\n=== {prompt_name} ===\n{content}\n" + "=" * 40)
    except Exception as e:
        print(f"Error loading prompt {prompt_name}: {e}")


def load_prompt(prompt_name: str) -> str:
    """Load a prompt from the prompts directory."""
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
STATUS_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
STATUS_COMPLETE = "✓"
STATUS_ERROR = "✗"
STATUS_WORKING = "⚙"
STATUS_SEARCH = "🔍"
STATUS_TOOL = "🔧"


class EnhancedStatusIndicator:
    """Enhanced status indicator with phase tracking and timing."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.current_phase = None
        self.current_step = 0
        self.total_steps = 0
        self.spinner_index = 0
        self.phase_start_time = None

    def start_phase(self, phase_name: str, total_steps: int = 0):
        """Start a new phase of execution."""
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
        """Update current step with progress."""
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
        """Mark the phase as complete."""
        if not self.enabled:
            return
        elapsed = f"({(time.time() - self.phase_start_time)*1000:.0f}ms)" if self.phase_start_time else ""
        print(f"\r{STATUS_COMPLETE} {message} {elapsed}")

    def error(self, message: str):
        """Mark the phase as failed."""
        if not self.enabled:
            return
        print(f"\r{STATUS_ERROR} Error: {message}")


class ContextManager:
    """Manages conversation context and history."""

    def __init__(self, max_history: int = 10, max_tokens: int = 8000):
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.conversations = {}  # session_id → messages

    def add_message(self, session_id: str, role: str, content: str):
        """Add message to conversation history."""
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
        """Get messages for a session."""
        if session_id not in self.conversations:
            return []

        messages = self.conversations[session_id]
        if limit:
            return messages[-limit * 2 :]  # * 2 for user + assistant pairs
        return messages[-self.max_history * 2 :]

    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]


class MemoryStore:
    """Simple memory store for persistence (Phase 1: JSON-based)."""

    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_conversation(self, session_id: str, messages: List[Dict]):
        """Save conversation to disk."""
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
        """Load conversation from disk."""
        file_path = self.storage_path / f"{session_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])

    def list_conversations(self) -> List[str]:
        """List all saved conversation IDs."""
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
            session_id: Session ID for conversation persistence
        """
        # OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Session management
        self.session_id = session_id or f"session_{int(time.time())}"

        # Context management
        self.context_manager = ContextManager()
        self.memory_store = MemoryStore()

        # Load existing conversation if available
        saved_messages = self.memory_store.load_conversation(self.session_id)
        if saved_messages:
            self.context_manager.conversations[self.session_id] = saved_messages

        # Tool framework
        self.enable_tools = enable_tools
        self.tool_registry = None
        if enable_tools:
            self.tool_registry = get_registry()
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

        # RAG system
        self.enable_rag = enable_rag and RAG_AVAILABLE
        self.rag = None
        if self.enable_rag:
            try:
                self.rag = create_rag_system(rag_preset)
                print(f"✓ RAG system initialized ({rag_preset} preset)")
            except Exception as e:
                print(f"⚠ RAG initialization failed: {e}")
                self.enable_rag = False

        # Configuration
        self.enable_streaming = enable_streaming
        self.enable_status = enable_status

        print(f"✓ Echoes Assistant V2 ready (session: {self.session_id})")

    def add_knowledge(self, documents: List[Union[str, Dict]], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add documents to the knowledge base.

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

    def _retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        status: Optional[EnhancedStatusIndicator] = None,
    ) -> List[Dict]:
        """Retrieve relevant context from knowledge base."""
        if not self.enable_rag or not self.rag:
            return []

        try:
            if status:
                status.start_phase(f"{STATUS_SEARCH} Searching knowledge base", 0)

            result = self.rag.search(query, top_k=top_k)

            if status and result.results:
                status.complete_phase(f"Found {len(result.results)} relevant documents")

            return [{"text": r.text, "score": r.score, "metadata": r.metadata} for r in result.results]
        except Exception as e:
            if status:
                status.error(f"RAG search failed: {str(e)}")
            return []

    def _execute_tool_call(self, tool_call, status: Optional[EnhancedStatusIndicator] = None) -> str:
        """Execute a tool call using the registry with enhanced logging and error handling."""
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
            status.update_step(f"{STATUS_TOOL} Executing {function_name}({args_str})")

        try:
            # Validate tool exists
            if not self.tool_registry.has_tool(function_name):
                error_msg = f"Tool '{function_name}' not found in registry"
                if status:
                    status.error(error_msg)
                return f"Error: {error_msg}"

            # Execute the tool
            result = self.tool_registry.execute(function_name, **function_args)

            if status:
                status.update_step(f"Completed {function_name}", completed=True)

            if result.success:
                return json.dumps(result.data)
            else:
                return f"Error: {result.error}"

        except Exception as e:
            error_msg = f"Exception executing {function_name}: {str(e)}"
            if status:
                status.error(error_msg)
            return f"Error: {error_msg}"

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        stream: Optional[bool] = None,
        show_status: Optional[bool] = None,
        context_limit: int = 5,
        prompt_file: Optional[str] = None,
    ) -> Union[str, Iterator[str]]:
        """
        Chat with the assistant.

        Args:
            message: User message
            system_prompt: Optional system prompt (overrides prompt_file if both provided)
            prompt_file: Name of the YAML file in prompts/ to use as system prompt
            system_prompt: Optional system prompt
            stream: Override streaming setting
            show_status: Override status indicator setting
            context_limit: Number of previous exchanges to include

        Returns:
            Response string or iterator (if streaming)
        """
        stream = stream if stream is not None else self.enable_streaming
        show_status = show_status if show_status is not None else self.enable_status

        # Status indicator
        status = EnhancedStatusIndicator(enabled=show_status)

        try:
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

            # Get available tools
            tools = None
            if self.enable_tools and self.tool_registry:
                tools = self.tool_registry.get_openai_schemas()

            # Multi-step tool calling with enhanced logging and error handling
            iteration = 0
            all_tool_results = []
            tool_calling_enabled = self.enable_tools and self.tool_registry is not None

            while iteration < MAX_TOOL_ITERATIONS:
                # Make API call
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools if tool_calling_enabled else None,
                        tool_choice="auto" if (tools and tool_calling_enabled) else None,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stream=False,
                    )
                except APIError as e:
                    error_msg = f"API error during tool calling: {str(e)}"
                    if status:
                        status.error(error_msg)
                    return error_msg

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

            if status and iteration > 0:
                successful = sum(1 for r in all_tool_results if r.get("success", False))
                status.complete_phase(
                    f"Completed {iteration} action round(s) ({successful}/{len(all_tool_results)} successful)"
                )

            # Get final response
            if stream:
                if status:
                    print(f"\n{STATUS_WORKING} Generating response...\n")
                    print("Echoes: ", end="", flush=True)

                response_stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    stream=True,
                )

                # Stream response
                full_response = ""
                for chunk in response_stream:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        chunk_content = delta.content
                        print(chunk_content, end="", flush=True)
                        full_response += chunk_content
                print()

                assistant_response = full_response
            else:
                final_response = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=self.temperature
                )
                assistant_response = final_response.choices[0].message.content

            # Update conversation history
            self.context_manager.add_message(self.session_id, "user", message)
            self.context_manager.add_message(self.session_id, "assistant", assistant_response)

            # Save to persistent storage
            self.memory_store.save_conversation(self.session_id, self.context_manager.conversations[self.session_id])

            return assistant_response if not stream else ""

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
        """Get conversation history for current session."""
        return self.context_manager.get_messages(self.session_id)

    def clear_history(self):
        """Clear conversation history for current session."""
        self.context_manager.clear_session(self.session_id)

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List available tools."""
        if not self.tool_registry:
            return []
        return self.tool_registry.list_tools(category)

    def execute_action(self, action_type: str, action_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an action on behalf of the user.

        Args:
            action_type: Type of action ('inventory', 'tool')
            action_name: Name of the specific action
            **kwargs: Action parameters

        Returns:
            Action result with status and data
        """
        if action_type == "inventory":
            result = self.action_executor.execute_inventory_action(action_name, **kwargs)
        elif action_type == "tool":
            result = self.action_executor.execute_tool_action(action_name, **kwargs)
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
        """Get recent action history."""
        return self.action_executor.get_action_history(limit)

    def get_action_summary(self) -> Dict[str, Any]:
        """Get summary of actions executed."""
        return self.action_executor.get_action_summary()

    def gather_knowledge(
        self, content: str, source: str, category: str = "general", tags: Optional[List[str]] = None
    ) -> str:
        """Gather and store knowledge."""
        return self.knowledge_manager.add_knowledge(content, source, category, tags)

    def search_knowledge(
        self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        entries = self.knowledge_manager.search_knowledge(query, category, limit=limit)
        return [e.to_dict() for e in entries]

    def update_context(self, key: str, value: Any):
        """Update assistant context."""
        self.knowledge_manager.update_context(key, value)

    def get_context_summary(self) -> str:
        """Get context summary."""
        return self.knowledge_manager.build_context_summary()

    def list_directory(self, dirpath: str, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        """List directory contents."""
        return self.fs_tools.list_directory(dirpath, pattern, recursive)

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read file contents."""
        return self.fs_tools.read_file(filepath)

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write file contents."""
        return self.fs_tools.write_file(filepath, content)

    def search_files(self, query: str, search_path: Optional[str] = None) -> Dict[str, Any]:
        """Search files."""
        return self.fs_tools.search_files(query, search_path)

    def get_directory_tree(self, dirpath: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get directory tree."""
        return self.fs_tools.get_directory_tree(dirpath, max_depth)

    def run_workflow(self, workflow_type: str, **kwargs) -> Dict[str, Any]:
        """Run an agent workflow."""
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
        """Get assistant statistics."""
        stats = {
            "session_id": self.session_id,
            "messages": len(self.context_manager.get_messages(self.session_id)),
            "rag_enabled": self.enable_rag,
            "tools_enabled": self.enable_tools,
            "actions": self.get_action_summary(),
            "knowledge": self.knowledge_manager.get_stats(),
        }

        if self.tool_registry:
            stats["tool_stats"] = self.tool_registry.get_stats()

        if self.rag:
            stats["rag_stats"] = self.rag.get_stats() if hasattr(self.rag, "get_stats") else {}

        return stats

    def analyze_directory(
        self,
        directory_path: str,
        output_file: Optional[str] = None,
        max_depth: int = 10,
        exclude_dirs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Analyze a directory structure and generate a comprehensive report."""
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
                max_tokens=3000,
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
        """Recursively gather directory structure details."""
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
        """Collect aggregate statistics from directory structure."""
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
        """Format the directory structure into a human-readable tree with optional truncation."""
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

    def _summarize_top_directories(self, structure: Dict[str, Any], max_entries: int = 20) -> str:
        """Summarize the most significant directories by file count."""
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


def interactive_mode(system_prompt: Optional[str] = None) -> None:
    """Run the assistant in interactive mode."""
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
                            print(f"\n📊 Inventory Report ({report_type}):")
                            print(json.dumps(result["result"], indent=2))
                        else:
                            print(f"  Error: {result['error']}")
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

                system_prompt_var = system_prompt if "system_prompt" in locals() else None

                response = assistant.chat(
                    user_input,
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
                print(f"📋 Analysis Report for: {result['directory']}")
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
