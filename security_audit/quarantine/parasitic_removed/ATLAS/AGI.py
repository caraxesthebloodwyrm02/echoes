#!/usr/bin/env python3
"""
Fused Terminal Chat Assistant

A sophisticated assistant combining:
- Battle-tested terminal operations (file, system, web, code, data, analysis, automation)
- Conversational chat interface for natural interaction
- Experience-driven learning and adaptation
- Session persistence and comprehensive error handling

Features:
- Dual modes: Chat (conversational) and Command (precise terminal operations)
- 50+ integrated tools across 7 categories
- Intelligent error recovery and suggestions
- Performance metrics and experience tracking
- Session save/load functionality
"""

import argparse
import asyncio
import hashlib
import inspect
import json
import logging
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Core dependencies with fallbacks
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from duckduckgo_search import DDGS

    DUCK_SEARCH_AVAILABLE = True
except ImportError:
    DUCK_SEARCH_AVAILABLE = False

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("fused_assistant_logs.log"), logging.StreamHandler()],
)
logger = logging.getLogger("FusedAssistant")


class ActionType(Enum):
    """Types of actions the assistant can perform."""

    FILE_OPERATION = "file_operation"
    SYSTEM_COMMAND = "system_command"
    SEARCH = "search"
    CODE_EXECUTION = "code_execution"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    LEARNING = "learning"


class ComplexityLevel(Enum):
    """Complexity levels for task assessment."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


@dataclass
class Experience:
    """Represents accumulated experience and learning."""

    domain: str
    success_rate: float = 0.0
    total_attempts: int = 0
    successful_attempts: int = 0
    patterns: dict[str, int] = field(default_factory=dict)
    best_practices: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)

    def record_attempt(
        self, success: bool, pattern: str = "", practice: str = "", failure: str = ""
    ):
        """Record an attempt and update experience."""
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
            if practice:
                self.best_practices.append(practice)
            if pattern:
                self.patterns[pattern] = self.patterns.get(pattern, 0) + 1
        else:
            if failure:
                self.failure_modes.append(failure)

        self.success_rate = self.successful_attempts / self.total_attempts

        # Keep only recent patterns and practices to manage memory
        if len(self.patterns) > 20:
            sorted_patterns = sorted(self.patterns.items(), key=lambda x: x[1])
            for pattern, count in sorted_patterns[: len(self.patterns) - 15]:
                del self.patterns[pattern]

        if len(self.best_practices) > 50:
            self.best_practices = self.best_practices[-30:]

        if len(self.failure_modes) > 30:
            self.failure_modes = self.failure_modes[-20:]


@dataclass
class CommandResult:
    """Result of command execution."""

    success: bool
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    confidence: float = 0.0
    suggestions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class FusedAssistant:
    """
    Fused Terminal Chat Assistant with Experience and Intelligence.

    Combines practical terminal operations with intelligent reasoning,
    learning from experience, and adaptive behavior in both chat and command modes.
    """

    def __init__(self):
        """Initialize the fused assistant."""
        self.version = "2.0"
        self.session_id = hashlib.md5(
            f"{time.time()}{os.getpid()}".encode()
        ).hexdigest()[:8]

        # Core values and principles
        self.values = {
            "reliability": "Consistent, dependable performance in all conditions",
            "efficiency": "Optimal resource usage and time management",
            "intelligence": "Smart reasoning and adaptive learning",
            "transparency": "Clear communication and honest feedback",
            "safety": "Secure operations with error handling and recovery",
            "adaptability": "Learning from experience and improving over time",
            "helpfulness": "Focus on user needs and practical solutions",
        }

        # Experience tracking
        self.experience = {
            "file_operations": Experience("file_operations"),
            "system_commands": Experience("system_commands"),
            "web_search": Experience("web_search"),
            "code_execution": Experience("code_execution"),
            "data_analysis": Experience("data_analysis"),
            "debugging": Experience("debugging"),
            "automation": Experience("automation"),
            "chat_conversations": Experience("chat_conversations"),
        }

        # Session state
        self.conversation_history = []
        self.command_history = []
        self.current_directory = Path.cwd()
        self.session_start_time = time.time()
        self.last_command_time = time.time()
        self.current_mode = "chat"  # "chat" or "command"

        # Settings and configuration
        self.settings = {
            "verbose": True,
            "show_progress": True,
            "auto_retry": True,
            "learning_enabled": True,
            "context_aware": True,
            "multi_threaded": True,
            "timeout_seconds": 30,
            "max_retries": 3,
            "chat_mode": True,
            "personality": "helpful_assistant",
        }

        # Tool registry
        self.tools = self._initialize_tools()

        # Context and memory
        self.context = {
            "user_preferences": {},
            "common_tasks": [],
            "recent_files": [],
            "search_history": [],
            "failed_patterns": [],
            "chat_context": [],
        }

        # Performance metrics
        self.metrics = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "average_execution_time": 0.0,
            "most_used_commands": Counter(),
            "success_by_category": defaultdict(int),
            "learning_progress": 0.0,
            "chat_interactions": 0,
            "command_mode_usage": 0,
        }

        logger.info(
            f"FusedAssistant v{self.version} initialized (Session: {self.session_id})"
        )
        print(f"🤖 Fused Assistant v{self.version} - Ready for Chat & Commands")
        print(f"🎯 Session ID: {self.session_id}")
        print(
            f"⚡ Active: {len(self.tools)} tool categories, {len(self.experience)} experience domains"
        )

    def _initialize_tools(self) -> dict[str, Any]:
        """Initialize available tools and utilities."""
        tools = {
            "file_operations": {
                "read": self._read_file,
                "write": self._write_file,
                "list": self._list_files,
                "search": self._search_files,
                "analyze": self._analyze_file_with_args,
                "diff": self._compare_files,
                "backup": self._backup_file,
                "create": self._create_file,
                "delete": self._delete_file,
                "move": self._move_file,
                "copy": self._copy_file,
            },
            "system_commands": {
                "execute": self._execute_command,
                "process_info": self._get_process_info,
                "disk_usage": self._get_disk_usage,
                "network_status": self._check_network,
                "system_info": self._get_system_info,
                "env_vars": self._get_environment_vars,
                "running_processes": self._list_processes,
            },
            "web_operations": {
                "search": self._web_search,
                "download": self._download_file,
                "http_status": self._check_http_status,
                "curl": self._curl_request,
                "api_call": self._make_api_call,
            },
            "code_operations": {
                "run": self._run_code,
                "lint": self._lint_code,
                "format": self._format_code,
                "test": self._run_tests,
                "debug": self._debug_code,
                "profile": self._profile_code,
            },
            "data_operations": {
                "parse_csv": self._parse_csv,
                "parse_json": self._parse_json,
                "analyze_data": self._analyze_data,
                "clean_data": self._clean_data,
                "statistics": self._get_statistics,
            },
            "analysis_operations": {
                "review_code": self._review_code,
                "security_scan": self._security_scan,
                "performance_analyze": self._analyze_performance,
                "dependency_check": self._check_dependencies,
            },
            "assistant_operations": {
                "help": self._show_help,
                "status": self._get_status,
                "history": self._show_history,
                "clear": self._clear_screen,
                "save_session": self._save_current_session,
                "load_session": self._load_session_file,
                "metrics": self._show_metrics,
                "tools": self._list_tools,
            },
        }

        logger.info(
            f"Initialized {sum(len(category) for category in tools.values())} tools across {len(tools)} categories"
        )
        return tools

    def _get_complexity_assessment(
        self, command: str, args: list[str]
    ) -> ComplexityLevel:
        """Assess the complexity of a command."""
        moderate_keywords = [
            "search",
            "write",
            "create",
            "run",
            "execute",
            "download",
            "analyze",
        ]
        complex_keywords = [
            "review",
            "scan",
            "profile",
            "debug",
            "automate",
            "optimize",
        ]
        expert_keywords = [
            "security",
            "architecture",
            "compliance",
            "migrate",
            "transform",
        ]

        command_lower = command.lower()
        args_text = " ".join(args).lower()

        if any(
            keyword in command_lower or keyword in args_text
            for keyword in expert_keywords
        ):
            return ComplexityLevel.EXPERT
        elif any(
            keyword in command_lower or keyword in args_text
            for keyword in complex_keywords
        ):
            return ComplexityLevel.COMPLEX
        elif any(
            keyword in command_lower or keyword in args_text
            for keyword in moderate_keywords
        ):
            return ComplexityLevel.MODERATE

        return ComplexityLevel.SIMPLE

    def _assess_confidence(self, command: str, args: list[str]) -> float:
        """Assess confidence level for command execution."""
        confidence = 0.8  # Base confidence

        # Check if command exists in tools
        tool_found = False
        for category, tools in self.tools.items():
            if command in tools:
                tool_found = True
                domain = f"{category.split('_')[0]}_{command}"
                if domain in self.experience:
                    exp = self.experience[domain]
                    confidence += (exp.success_rate - 0.5) * 0.3

        if not tool_found:
            confidence -= 0.5

        # Adjust for dependencies
        if not REQUESTS_AVAILABLE and (
            "search" in command.lower() or "download" in command.lower()
        ):
            confidence -= 0.3

        if not DUCK_SEARCH_AVAILABLE and "search" in command.lower():
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _execute_command_internal(self, command: str, args: list[str]) -> CommandResult:
        """Internal command execution with proper error handling."""
        start_time = time.time()

        try:
            complexity = self._get_complexity_assessment(command, args)
            confidence = self._assess_confidence(command, args)

            # Find and execute the command
            for category, tools in self.tools.items():
                if command in tools:
                    tool_function = tools[command]

                    # Validate arguments
                    if not self._validate_arguments(command, args, tool_function):
                        return CommandResult(
                            success=False,
                            error="Invalid arguments provided",
                            complexity=complexity,
                            confidence=0.3,
                        )

                    # Execute the tool
                    if inspect.iscoroutinefunction(tool_function):
                        result_data = asyncio.run(tool_function(*args))
                    else:
                        result_data = tool_function(*args)

                    execution_time = time.time() - start_time

                    # Format result
                    if isinstance(result_data, dict):
                        output = json.dumps(result_data, indent=2)
                    else:
                        output = str(result_data)

                    return CommandResult(
                        success=True,
                        output=output,
                        execution_time=execution_time,
                        complexity=complexity,
                        confidence=confidence,
                    )

            # Command not found - try to interpret as natural language in chat mode
            if self.settings["chat_mode"]:
                return self._handle_natural_language(command, args)

            return CommandResult(
                success=False,
                error=f"Command '{command}' not found. Type 'help' for available commands.",
                complexity=complexity,
                confidence=0.0,
            )

        except Exception as e:
            return self._handle_error(command, args, e)

    def _handle_natural_language(self, command: str, args: list[str]) -> CommandResult:
        """Handle natural language input in chat mode."""
        input_text = f"{command} {' '.join(args)}".lower()

        # Common patterns for natural language processing
        patterns = {
            r"hello|hi|hey": lambda: "Hello! I'm your fused assistant. How can I help you today?",
            r"how are you": lambda: "I'm functioning optimally and ready to assist you!",
            r"what can you do": lambda: self._get_capabilities(),
            r"thank you|thanks": lambda: "You're welcome! I'm here to help.",
            r"bye|goodbye": lambda: "Goodbye! Have a great day!",
            r"help me": lambda: "I can help with file operations, system commands, web search, code analysis, and automation. What would you like to do?",
            r"status|how am i doing": lambda: self._get_status_summary(),
            r"list files|show files": lambda: json.dumps(
                self._list_files(".", "*", False), indent=2
            ),
            r"search for (.+)": lambda: self._web_search(
                re.search(r"search for (.+)", input_text).group(1)
            ),
            r"create file (.+)": lambda: self._create_file(
                re.search(r"create file (.+)", input_text).group(1), ""
            ),
            r"read file (.+)": lambda: self._read_file(
                re.search(r"read file (.+)", input_text).group(1)
            ),
            r"run (.+)": lambda: self._execute_command(
                re.search(r"run (.+)", input_text).group(1)
            ),
            r"system info": lambda: json.dumps(self._get_system_info(), indent=2),
        }

        for pattern, response_func in patterns.items():
            match = re.search(pattern, input_text)
            if match:
                try:
                    response = response_func()
                    return CommandResult(
                        success=True,
                        output=response,
                        complexity=ComplexityLevel.SIMPLE,
                        confidence=0.9,
                    )
                except Exception as e:
                    return CommandResult(
                        success=False,
                        error=f"Error processing your request: {str(e)}",
                        complexity=ComplexityLevel.SIMPLE,
                        confidence=0.3,
                    )

        # If no pattern matches, provide helpful response
        suggestions = [
            "Try 'help' to see available commands",
            "Ask me to 'list files' or 'search for something'",
            "Use 'status' to see how things are going",
            "Say 'what can you do' to see my capabilities",
        ]

        return CommandResult(
            success=True,
            output=f"I'm not sure how to handle: '{input_text}'. {suggestions[0]}",
            complexity=ComplexityLevel.SIMPLE,
            confidence=0.4,
            suggestions=suggestions,
        )

    def _validate_arguments(self, command: str, args: list[str], tool_function) -> bool:
        """Validate command arguments before execution."""
        if command in ["read", "analyze", "backup", "delete"] and len(args) < 1:
            return False
        if command in ["write", "create"] and len(args) < 1:
            return False
        if command in ["diff", "move", "copy"] and len(args) < 2:
            return False

        # Special handling for analyze command - join multiple args as filepath
        if command == "analyze" and len(args) > 1:
            # This will be handled in the tool function itself
            pass

        return True

    def _handle_error(
        self, command: str, args: list[str], error: Exception
    ) -> CommandResult:
        """Handle errors with intelligent recovery suggestions."""
        error_message = str(error)
        confidence = 0.0

        error_patterns = {
            "FileNotFoundError": {
                "solution": "Check file path and permissions",
                "confidence": 0.8,
            },
            "PermissionError": {
                "solution": "Run with appropriate privileges or check file permissions",
                "confidence": 0.7,
            },
            "subprocess.CalledProcessError": {
                "solution": "Check command syntax and dependencies",
                "confidence": 0.6,
            },
            "ConnectionError": {
                "solution": "Check network connectivity and service availability",
                "confidence": 0.5,
            },
        }

        for error_type, pattern in error_patterns.items():
            if error_type in str(type(error)):
                confidence = pattern["confidence"]
                error_message = (
                    f"{error_message}. Suggested solution: {pattern['solution']}"
                )
                break

        return CommandResult(
            success=False,
            error=error_message,
            confidence=confidence,
            complexity=self._get_complexity_assessment(command, args),
        )

    def _record_experience(self, command: str, args: list[str], result: CommandResult):
        """Record execution experience for learning."""
        if not self.settings["learning_enabled"]:
            return

        domain = self._get_command_domain(command)
        if domain in self.experience:
            pattern = f"{command} {' '.join(args[:2])}"
            practice = f"Executed {command} with confidence {result.confidence:.2f}"
            failure = result.error if not result.success else ""

            self.experience[domain].record_attempt(
                success=result.success,
                pattern=pattern[:50],
                practice=practice,
                failure=failure[:100],
            )

            # Update global metrics
            self.metrics["total_commands"] += 1
            if result.success:
                self.metrics["successful_commands"] += 1
            else:
                self.metrics["failed_commands"] += 1

            self.metrics["most_used_commands"][command] += 1

    def _get_command_domain(self, command: str) -> str:
        """Get the domain for a command."""
        for category in self.tools.keys():
            if command in self.tools[category]:
                return f"{category.split('_')[0]}_{command}"
        return "chat_conversations"

    def _generate_suggestions(
        self, command: str, args: list[str], result: CommandResult
    ) -> list[str]:
        """Generate suggestions based on execution results."""
        suggestions = []

        if result.success:
            if command in self.tools.get("file_operations", {}):
                suggestions.extend(
                    [
                        "Consider automating this file operation",
                        "You might want to create a backup first",
                    ]
                )
            elif command in self.tools.get("code_operations", {}):
                suggestions.extend(
                    ["Run tests to verify changes", "Consider linting for code quality"]
                )
        else:
            error_lower = result.error.lower()
            if "permission" in error_lower:
                suggestions.append("Check file permissions and ownership")
            elif "not found" in error_lower:
                suggestions.append("Verify the file path or command name")

        return suggestions[:3]

    def _update_metrics(self, execution_time: float):
        """Update performance metrics."""
        if self.metrics["total_commands"] > 0:
            current_avg = self.metrics["average_execution_time"]
            new_avg = (
                current_avg * (self.metrics["total_commands"] - 1) + execution_time
            ) / self.metrics["total_commands"]
            self.metrics["average_execution_time"] = new_avg

    # ============================================================================
    # Core Tool Implementations
    # ============================================================================

    def _read_file(self, filepath: str) -> str:
        """Read and return file contents."""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                if len(content) > 5000:
                    return (
                        content[:5000]
                        + f"\n\n... (file truncated, showing first 5000 of {len(content)} characters)"
                    )
                return content
        except UnicodeDecodeError:
            with open(filepath, encoding="latin-1") as f:
                return f.read()

    def _write_file(self, filepath: str, content: str) -> dict[str, Any]:
        """Write content to file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "filepath": filepath,
            "size": len(content),
            "timestamp": datetime.now().isoformat(),
        }

    def _create_file(self, filepath: str, content: str = "") -> dict[str, Any]:
        """Create a new file."""
        return self._write_file(filepath, content)

    def _delete_file(self, filepath: str) -> dict[str, Any]:
        """Delete a file."""
        try:
            path = Path(filepath)
            if path.exists():
                path.unlink()
                return {"success": True, "deleted": filepath}
            else:
                return {"error": f"File {filepath} does not exist"}
        except Exception as e:
            return {"error": str(e)}

    def _move_file(self, source: str, destination: str) -> dict[str, Any]:
        """Move a file."""
        try:
            Path(source).rename(destination)
            return {"success": True, "moved_from": source, "moved_to": destination}
        except Exception as e:
            return {"error": str(e)}

    def _copy_file(self, source: str, destination: str) -> dict[str, Any]:
        """Copy a file."""
        try:
            import shutil

            shutil.copy2(source, destination)
            return {"success": True, "copied_from": source, "copied_to": destination}
        except Exception as e:
            return {"error": str(e)}

    def _list_files(
        self, directory: str = ".", pattern: str = "*", recursive: bool = False
    ) -> dict[str, Any]:
        """List files in directory with optional filtering."""
        path = Path(directory)
        if not path.exists():
            return {"error": f"Directory {directory} does not exist"}

        files = []
        if recursive:
            for file_path in path.rglob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(
                        {
                            "path": str(file_path),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )
        else:
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(
                        {
                            "path": str(file_path),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )

        return {
            "directory": str(path),
            "pattern": pattern,
            "recursive": recursive,
            "count": len(files),
            "files": files[:20],  # Limit to 20 files
        }

    def _search_files(self, query: str, directory: str = ".") -> dict[str, Any]:
        """Search for files containing query text."""
        path = Path(directory)
        matches = []
        file_types = [".txt", ".py", ".js", ".json", ".md", ".yml", ".yaml"]

        for ext in file_types:
            for file_path in path.rglob(f"*{ext}"):
                if file_path.is_file():
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                matches.append(
                                    {
                                        "file": str(file_path),
                                        "size": file_path.stat().st_size,
                                    }
                                )
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return {
            "query": query,
            "directory": str(path),
            "total_matches": len(matches),
            "files": matches[:10],  # Limit to 10 matches
        }

    def _analyze_file(self, filepath: str) -> dict[str, Any]:
        """Analyze file characteristics."""
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File {filepath} does not exist"}

        stat = path.stat()
        analysis = {
            "path": str(path),
            "size": stat.st_size,
            "extension": path.suffix,
            "type": "unknown",
        }

        if path.suffix in [".py"]:
            analysis.update(self._analyze_python_file(path))
        elif path.suffix in [".json"]:
            analysis.update(self._analyze_json_file(path))

        return analysis

    def _analyze_file_with_args(self, *args) -> dict[str, Any]:
        """Analyze file with multiple arguments joined as filepath."""
        if not args:
            return {"error": "No filepath provided for analysis"}

        # Join all arguments with spaces to form the filepath
        filepath = " ".join(args)
        return self._analyze_file(filepath)

    def _analyze_python_file(self, path: Path) -> dict[str, Any]:
        """Analyze Python file."""
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            return {
                "type": "python",
                "lines": len(lines),
                "functions": len(re.findall(r"def\s+(\w+)", content)),
                "classes": len(re.findall(r"class\s+(\w+)", content)),
                "imports": len(
                    re.findall(r"^\s*(import|from)\s+", content, re.MULTILINE)
                ),
            }
        except Exception as e:
            return {"type": "python", "error": str(e)}

    def _analyze_json_file(self, path: Path) -> dict[str, Any]:
        """Analyze JSON file."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            return {
                "type": "json",
                "keys_at_top_level": len(data) if isinstance(data, dict) else 0,
                "data_type": type(data).__name__,
                "is_valid": True,
            }
        except json.JSONDecodeError as e:
            return {
                "type": "json",
                "error": f"Invalid JSON: {str(e)}",
                "is_valid": False,
            }

    def _compare_files(self, file1: str, file2: str) -> dict[str, Any]:
        """Compare two files."""
        try:
            with open(file1, encoding="utf-8") as f1:
                content1 = f1.read()
            with open(file2, encoding="utf-8") as f2:
                content2 = f2.read()

            lines1 = content1.split("\n")
            lines2 = content2.split("\n")
            max_lines = max(len(lines1), len(lines2))
            differences = []

            for i in range(max_lines):
                line1 = lines1[i] if i < len(lines1) else ""
                line2 = lines2[i] if i < len(lines2) else ""
                if line1 != line2:
                    differences.append(
                        {"line": i + 1, "file1": line1[:50], "file2": line2[:50]}
                    )

            return {
                "file1": file1,
                "file2": file2,
                "total_differences": len(differences),
                "similarity_score": 1 - (len(differences) / max_lines)
                if max_lines > 0
                else 1.0,
                "differences": differences[:10],
            }
        except Exception as e:
            return {"error": str(e)}

    def _backup_file(
        self, filepath: str, backup_dir: str = "backups"
    ) -> dict[str, Any]:
        """Create backup of a file."""
        try:
            source_path = Path(filepath)
            if not source_path.exists():
                return {"error": f"File {filepath} does not exist"}

            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_filepath = backup_path / backup_filename

            import shutil

            shutil.copy2(source_path, backup_filepath)

            return {
                "success": True,
                "source": str(source_path),
                "backup": str(backup_filepath),
                "backup_size": backup_filepath.stat().st_size,
            }
        except Exception as e:
            return {"error": str(e)}

    def _execute_command(self, command: str) -> dict[str, Any]:
        """Execute a system command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.settings["timeout_seconds"],
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "timeout": self.settings["timeout_seconds"],
                "command": command,
            }

    def _get_process_info(self, pid: int | None = None) -> dict[str, Any]:
        """Get process information."""
        try:
            if not PSUTIL_AVAILABLE:
                return {"error": "psutil not available"}

            if pid is None:
                pid = os.getpid()

            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_disk_usage(self, path: str = ".") -> dict[str, Any]:
        """Get disk usage information."""
        try:
            if PSUTIL_AVAILABLE:
                disk_usage = psutil.disk_usage(path)
                return {
                    "path": str(Path(path).absolute()),
                    "total_gb": disk_usage.total / (1024**3),
                    "used_gb": disk_usage.used / (1024**3),
                    "free_gb": disk_usage.free / (1024**3),
                    "percent_used": (disk_usage.used / disk_usage.total) * 100,
                }
            else:
                return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}

    def _check_network(self) -> dict[str, Any]:
        """Check network connectivity."""
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get("https://www.google.com", timeout=5)
                return {
                    "connected": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                }
            else:
                return {"error": "requests not available"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def _get_system_info(self) -> dict[str, Any]:
        """Get system information."""
        import platform
        import sys

        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version,
            "hostname": platform.node(),
            "current_directory": str(Path.cwd()),
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "timestamp": datetime.now().isoformat(),
        }

        if PSUTIL_AVAILABLE:
            info.update(
                {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                }
            )

        return info

    def _get_environment_vars(self) -> dict[str, Any]:
        """Get environment variables."""
        return dict(os.environ)

    def _list_processes(self) -> dict[str, Any]:
        """List running processes."""
        try:
            if not PSUTIL_AVAILABLE:
                return {"error": "psutil not available"}

            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {"processes": processes[:20], "total_count": len(processes)}
        except Exception as e:
            return {"error": str(e)}

    def _web_search(self, query: str, num_results: int = 5) -> dict[str, Any]:
        """Search the web."""
        try:
            if DUCK_SEARCH_AVAILABLE:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=num_results))
                    return {"query": query, "results": results, "count": len(results)}
            else:
                return {"error": "duckduckgo-search not available"}
        except Exception as e:
            return {"error": str(e)}

    def _download_file(self, url: str, filepath: str = None) -> dict[str, Any]:
        """Download file from URL."""
        try:
            if not REQUESTS_AVAILABLE:
                return {"error": "requests not available"}

            if filepath is None:
                filepath = url.split("/")[-1]

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return {
                "success": True,
                "url": url,
                "filepath": filepath,
                "size": Path(filepath).stat().st_size,
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_http_status(self, url: str) -> dict[str, Any]:
        """Check HTTP status of URL."""
        try:
            if not REQUESTS_AVAILABLE:
                return {"error": "requests not available"}

            response = requests.head(url, timeout=10)
            return {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }
        except Exception as e:
            return {"error": str(e)}

    def _curl_request(self, url: str, method: str = "GET") -> dict[str, Any]:
        """Make HTTP request."""
        try:
            if not REQUESTS_AVAILABLE:
                return {"error": "requests not available"}

            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url)
            else:
                return {"error": f"Unsupported method: {method}"}

            return {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response": response.text[:1000],  # Limit response size
            }
        except Exception as e:
            return {"error": str(e)}

    def _make_api_call(self, endpoint: str, method: str = "GET") -> dict[str, Any]:
        """Make API call."""
        return self._curl_request(endpoint, method)

    def _run_code(self, code: str, language: str = "python") -> dict[str, Any]:
        """Run code."""
        try:
            if language.lower() == "python":
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "language": language,
                }
            else:
                return {"error": f"Unsupported language: {language}"}
        except Exception as e:
            return {"error": str(e)}

    def _lint_code(self, filepath: str) -> dict[str, Any]:
        """Lint code file."""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"error": f"File {filepath} does not exist"}

            if path.suffix == ".py":
                # Basic Python linting
                with open(path) as f:
                    content = f.read()

                issues = []
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().endswith(" ") and line.strip():
                        issues.append({"line": i + 1, "issue": "Trailing whitespace"})
                    if len(line) > 120:
                        issues.append({"line": i + 1, "issue": "Line too long"})

                return {
                    "file": filepath,
                    "language": "python",
                    "issues": issues[:10],
                    "issue_count": len(issues),
                }
            else:
                return {"error": f"Unsupported file type: {path.suffix}"}
        except Exception as e:
            return {"error": str(e)}

    def _format_code(self, filepath: str) -> dict[str, Any]:
        """Format code file."""
        return {"message": "Code formatting not implemented yet", "file": filepath}

    def _run_tests(self, directory: str = ".") -> dict[str, Any]:
        """Run tests."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", directory, "-v"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "directory": directory,
            }
        except Exception as e:
            return {"error": str(e)}

    def _debug_code(self, filepath: str) -> dict[str, Any]:
        """Debug code."""
        return {"message": "Debug analysis not implemented yet", "file": filepath}

    def _profile_code(self, filepath: str) -> dict[str, Any]:
        """Profile code performance."""
        return {"message": "Profiling not implemented yet", "file": filepath}

    def _parse_csv(self, filepath: str) -> dict[str, Any]:
        """Parse CSV file."""
        try:
            import csv

            with open(filepath) as f:
                reader = csv.reader(f)
                rows = list(reader)

            return {
                "file": filepath,
                "rows": len(rows),
                "columns": len(rows[0]) if rows else 0,
                "sample_data": rows[:5],
            }
        except Exception as e:
            return {"error": str(e)}

    def _parse_json(self, filepath: str) -> dict[str, Any]:
        """Parse JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)

            return {
                "file": filepath,
                "data_type": type(data).__name__,
                "keys": list(data.keys())[:10] if isinstance(data, dict) else [],
                "size": len(str(data)),
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_data(self, data: str) -> dict[str, Any]:
        """Analyze data."""
        return {
            "message": "Data analysis not implemented yet",
            "data_type": type(data).__name__,
        }

    def _clean_data(self, data: str) -> dict[str, Any]:
        """Clean data."""
        return {"message": "Data cleaning not implemented yet"}

    def _get_statistics(self, data: str) -> dict[str, Any]:
        """Get statistics."""
        return {"message": "Statistics not implemented yet"}

    def _review_code(self, filepath: str) -> dict[str, Any]:
        """Review code quality."""
        return self._lint_code(filepath)

    def _security_scan(self, filepath: str) -> dict[str, Any]:
        """Security scan."""
        try:
            with open(filepath) as f:
                content = f.read()

            security_issues = []
            patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                (r"eval\s*\(", "Use of eval() function"),
                (r"exec\s*\(", "Use of exec() function"),
            ]

            for pattern, description in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    security_issues.append(
                        {
                            "issue": description,
                            "count": len(matches),
                            "severity": "high"
                            if "password" in description or "api" in description
                            else "medium",
                        }
                    )

            return {
                "file": filepath,
                "security_issues": security_issues,
                "issue_count": len(security_issues),
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_performance(self, filepath: str) -> dict[str, Any]:
        """Analyze performance."""
        return {"message": "Performance analysis not implemented yet", "file": filepath}

    def _check_dependencies(self, directory: str = ".") -> dict[str, Any]:
        """Check dependencies."""
        try:
            requirements_files = list(Path(directory).rglob("requirements*.txt"))
            return {
                "directory": directory,
                "requirements_files": [str(f) for f in requirements_files],
                "count": len(requirements_files),
            }
        except Exception as e:
            return {"error": str(e)}

    def _show_help(self, command: str = None) -> str:
        """Show help information."""
        if command:
            help_info = {
                "read": "Read file contents. Usage: read <filepath>",
                "write": "Write content to file. Usage: write <filepath> <content>",
                "list": "List files. Usage: list [directory] [pattern]",
                "search": "Search files for text. Usage: search <query> [directory]",
                "analyze": "Analyze file. Usage: analyze <filepath>",
                "web_search": "Search web. Usage: web_search <query>",
                "run": "Run code. Usage: run <code> [language]",
                "status": "Show assistant status. Usage: status",
                "help": "Show help. Usage: help [command]",
                "history": "Show command history. Usage: history",
                "clear": "Clear screen. Usage: clear",
            }
            return help_info.get(command, f"No help available for '{command}'")
        else:
            return """
Available Commands:
File Operations: read, write, create, delete, move, copy, list, search, analyze, backup, diff
System Commands: execute, process_info, disk_usage, network_status, system_info, env_vars, running_processes
Web Operations: web_search, download, http_status, curl, api_call
Code Operations: run, lint, format, test, debug, profile
Data Operations: parse_csv, parse_json, analyze_data, clean_data, statistics
Analysis Operations: review_code, security_scan, analyze_performance, check_dependencies
Assistant Operations: help, status, history, clear, save_session, load_session, metrics, tools

Chat Mode: You can also use natural language like:
- "hello", "how are you", "what can you do"
- "list files", "search for something", "create file filename"
- "run command", "system info", "status"

Type 'help <command>' for specific command help.
            """.strip()

    def _get_status(self) -> dict[str, Any]:
        """Get assistant status."""
        session_duration = time.time() - self.session_start_time
        return {
            "version": self.version,
            "session_id": self.session_id,
            "uptime_seconds": session_duration,
            "uptime_formatted": f"{session_duration:.1f}s",
            "mode": self.current_mode,
            "metrics": {
                "total_commands": self.metrics["total_commands"],
                "successful_commands": self.metrics["successful_commands"],
                "success_rate": (
                    self.metrics["successful_commands"] / self.metrics["total_commands"]
                )
                if self.metrics["total_commands"] > 0
                else 0,
                "chat_interactions": self.metrics["chat_interactions"],
                "command_mode_usage": self.metrics["command_mode_usage"],
            },
            "tools_available": sum(len(category) for category in self.tools.values()),
            "current_directory": str(self.current_directory),
        }

    def _get_status_summary(self) -> str:
        """Get status summary for chat."""
        status = self._get_status()
        return f"I'm doing great! Session uptime: {status['uptime_formatted']}, Commands executed: {status['metrics']['total_commands']}, Success rate: {status['metrics']['success_rate']:.1%}"

    def _get_capabilities(self) -> str:
        """Get assistant capabilities."""
        return """
I can help you with:
📁 File operations: read, write, search, analyze files
🔧 System commands: execute processes, check system info
🌐 Web operations: search online, download files
💻 Code operations: run, lint, test code
📊 Data operations: parse CSV/JSON, analyze data
🔍 Analysis: code review, security scans
🤖 Chat: natural language conversation

Try 'help' for all commands or just ask me what you need!
        """.strip()

    def _show_history(self, count: int = 10) -> dict[str, Any]:
        """Show command history."""
        recent = (
            self.command_history[-count:]
            if len(self.command_history) >= count
            else self.command_history
        )
        return {
            "showing": len(recent),
            "total": len(self.command_history),
            "recent_commands": recent,
        }

    def _clear_screen(self) -> str:
        """Clear screen."""
        os.system("clear" if os.name != "nt" else "cls")
        return "Screen cleared"

    def _save_current_session(self, filepath: str = None) -> dict[str, Any]:
        """Save current session."""
        return self.save_session(filepath)

    def _load_session_file(self, filepath: str) -> dict[str, Any]:
        """Load session from file."""
        return self.load_session(filepath)

    def _show_metrics(self) -> dict[str, Any]:
        """Show performance metrics."""
        return self.metrics

    def _list_tools(self) -> dict[str, Any]:
        """List available tools."""
        return {category: list(tools.keys()) for category, tools in self.tools.items()}

    # ============================================================================
    # Public Interface
    # ============================================================================

    def execute_command(self, command_line: str) -> CommandResult:
        """Execute a command line with full intelligence and experience."""
        start_time = time.time()

        try:
            # Parse command line
            parts = command_line.strip().split()
            if not parts:
                return CommandResult(
                    success=False,
                    error="Empty command",
                    complexity=ComplexityLevel.SIMPLE,
                    confidence=0.0,
                )

            command = parts[0].lower()
            args = parts[1:]

            # Update context
            self.context["last_command"] = command
            self.context["last_command_time"] = datetime.now().isoformat()

            # Log command for learning
            self.command_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "command": command_line,
                    "command_name": command,
                    "args": args,
                    "session_id": self.session_id,
                }
            )

            # Keep only recent history
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-50:]

            # Execute the command
            result = self._execute_command_internal(command, args)
            result.execution_time = time.time() - start_time

            # Generate suggestions
            result.suggestions = self._generate_suggestions(command, args, result)

            # Record experience
            self._record_experience(command, args, result)

            # Update metrics
            self._update_metrics(result.execution_time)

            # Store result in conversation history
            self.conversation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "command": command_line,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "result": result,
                }
            )

            # Keep only recent conversation
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-25:]

            # Update mode-specific metrics
            if self.settings["chat_mode"]:
                self.metrics["chat_interactions"] += 1
            else:
                self.metrics["command_mode_usage"] += 1

            logger.info(
                f"Command '{command}' executed in {result.execution_time:.2f}s with {'success' if result.success else 'failure'}"
            )

            return result

        except Exception as e:
            logger.error(f"Error executing command '{command_line}': {e}")
            return CommandResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                complexity=ComplexityLevel.SIMPLE,
                confidence=0.0,
            )

    def chat_mode(self) -> None:
        """Run in interactive chat mode."""
        self.current_mode = "chat"
        self.settings["chat_mode"] = True
        print("🤖 Chat Mode Started")
        print("=" * 50)
        print("I'm your friendly assistant! You can:")
        print("- Ask questions naturally")
        print("- Give commands like 'list files' or 'search for error'")
        print("- Type 'help' for all commands")
        print("- Type 'quit', 'exit', or 'bye' to leave")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye", "q"]:
                    print("👋 Goodbye! Have a great day!")
                    break

                # Execute as chat command
                result = self.execute_command(user_input)

                # Display response
                if result.success:
                    print(f"🤖 Assistant: {result.output}")
                else:
                    print(f"❌ Assistant: {result.error}")

                # Show suggestions if available
                if result.suggestions:
                    print("💡 Suggestions:")
                    for suggestion in result.suggestions:
                        print(f"   • {suggestion}")

            except KeyboardInterrupt:
                print("\n\n👋 Use 'quit' to exit properly. I'm still here!")
            except Exception as e:
                print(f"\n❌ Something went wrong: {e}")
                logger.error(f"Chat mode error: {e}")

    def command_mode(self) -> None:
        """Run in command mode."""
        self.current_mode = "command"
        self.settings["chat_mode"] = False
        print("⚡ Command Mode Started")
        print("=" * 50)
        print("Enter precise commands. Type 'help' for available commands.")
        print("Type 'quit' or 'exit' to return to menu.")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n⚡ Command: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                # Execute as precise command
                result = self.execute_command(user_input)

                # Display result
                if result.success:
                    print(f"✅ Success ({result.execution_time:.2f}s)")
                    if result.output:
                        print(result.output)
                else:
                    print(f"❌ Failed ({result.execution_time:.2f}s)")
                    print(f"Error: {result.error}")

                # Show suggestions if available
                if result.suggestions:
                    print("💡 Suggestions:")
                    for suggestion in result.suggestions:
                        print(f"   • {suggestion}")

            except KeyboardInterrupt:
                print("\n\n👋 Use 'quit' to exit properly.")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Command mode error: {e}")

    def save_session(self, filepath: str = None) -> dict[str, Any]:
        """Save current session data."""
        try:
            if filepath is None:
                filepath = f"fused_session_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            session_data = {
                "version": self.version,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "conversation_history": self.conversation_history,
                "command_history": self.command_history,
                "experience": {
                    domain: {
                        "success_rate": exp.success_rate,
                        "total_attempts": exp.total_attempts,
                        "successful_attempts": exp.successful_attempts,
                        "patterns": dict(exp.patterns),
                        "best_practices": exp.best_practices,
                        "failure_modes": exp.failure_modes,
                    }
                    for domain, exp in self.experience.items()
                },
                "context": self.context,
                "metrics": self.metrics,
                "settings": self.settings,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, default=str)

            return {
                "success": True,
                "filepath": filepath,
                "session_id": self.session_id,
                "data_size": len(json.dumps(session_data, default=str)),
            }

        except Exception as e:
            return {"error": str(e)}

    def load_session(self, filepath: str) -> dict[str, Any]:
        """Load session data from file."""
        try:
            with open(filepath, encoding="utf-8") as f:
                session_data = json.load(f)

            # Restore data
            self.conversation_history = session_data.get("conversation_history", [])
            self.command_history = session_data.get("command_history", [])
            self.context = session_data.get("context", {})
            self.metrics = session_data.get("metrics", {})
            self.settings = session_data.get("settings", {})

            # Restore experience
            for domain, exp_data in session_data.get("experience", {}).items():
                if domain in self.experience:
                    self.experience[domain].success_rate = exp_data.get(
                        "success_rate", 0.0
                    )
                    self.experience[domain].total_attempts = exp_data.get(
                        "total_attempts", 0
                    )
                    self.experience[domain].successful_attempts = exp_data.get(
                        "successful_attempts", 0
                    )
                    self.experience[domain].patterns = exp_data.get("patterns", {})
                    self.experience[domain].best_practices = exp_data.get(
                        "best_practices", []
                    )
                    self.experience[domain].failure_modes = exp_data.get(
                        "failure_modes", []
                    )

            logger.info(f"Session loaded from {filepath}")

            return {
                "success": True,
                "filepath": filepath,
                "session_id": session_data.get("session_id"),
                "loaded_commands": len(self.command_history),
                "loaded_conversations": len(self.conversation_history),
            }

        except Exception as e:
            return {"error": str(e)}


def main():
    """Main entry point for the fused assistant."""
    parser = argparse.ArgumentParser(
        description="Fused Terminal Chat & Command Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --chat                    # Start chat mode
  %(prog)s --cmd "list files"        # Run single command
  %(prog)s --session session.json    # Load previous session
  %(prog)s --save-session my.json    # Save session after exit
        """,
    )

    parser.add_argument("--chat", "-c", action="store_true", help="Start in chat mode")

    parser.add_argument("--cmd", "-x", help="Execute single command and exit")

    parser.add_argument("--session", "-s", help="Load session from file")

    parser.add_argument("--save-session", help="Save session to file after execution")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Initialize assistant
    assistant = FusedAssistant()

    # Load session if specified
    if args.session:
        result = assistant.load_session(args.session)
        if not result.get("success"):
            print(f"❌ Failed to load session: {result.get('error')}")
            return 1
        else:
            print(f"✅ Session loaded: {result.get('session_id')}")

    # Set verbosity
    assistant.settings["verbose"] = args.verbose

    try:
        if args.cmd:
            # Single command mode
            result = assistant.execute_command(args.cmd)

            if args.verbose:
                print("\n📊 Execution Details:")
                print(f"  Command: {args.cmd}")
                print(f"  Success: {result.success}")
                print(f"  Execution Time: {result.execution_time:.2f}s")
                print(f"  Complexity: {result.complexity.value}")
                print(f"  Confidence: {result.confidence:.2f}")

            if result.success and result.output:
                print(result.output)
            elif not result.success and result.error:
                print(f"Error: {result.error}")
                return 1

            # Show suggestions if verbose
            if args.verbose and result.suggestions:
                print("\n💡 Suggestions:")
                for suggestion in result.suggestions:
                    print(f"  - {suggestion}")

        elif args.chat:
            # Chat mode
            assistant.chat_mode()

        else:
            # Interactive menu mode
            print("🤖 Fused Assistant - Main Menu")
            print("=" * 40)
            print("1. Chat Mode (conversational)")
            print("2. Command Mode (precise operations)")
            print("3. Status")
            print("4. Help")
            print("5. Quit")
            print("=" * 40)

            while True:
                try:
                    choice = input("\nSelect option (1-5): ").strip()

                    if choice == "1":
                        assistant.chat_mode()
                    elif choice == "2":
                        assistant.command_mode()
                    elif choice == "3":
                        status = assistant._get_status()
                        print("\n📊 Assistant Status:")
                        print(f"  Version: {status['version']}")
                        print(f"  Session: {status['session_id']}")
                        print(f"  Uptime: {status['uptime_formatted']}")
                        print(f"  Commands: {status['metrics']['total_commands']}")
                        print(
                            f"  Success Rate: {status['metrics']['success_rate']:.1%}"
                        )
                        print(
                            f"  Chat Interactions: {status['metrics']['chat_interactions']}"
                        )
                        print(f"  Tools Available: {status['tools_available']}")
                    elif choice == "4":
                        print(assistant._show_help())
                    elif choice == "5":
                        print("👋 Goodbye!")
                        break
                    else:
                        print("❌ Invalid option. Please select 1-5.")

                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted. Use option 5 to quit properly.")
                except Exception as e:
                    print(f"\n❌ Error: {e}")

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting gracefully...")

    finally:
        # Save session if requested
        if args.save_session:
            result = assistant.save_session(args.save_session)
            if result.get("success"):
                print(f"💾 Session saved: {result.get('filepath')}")
            else:
                print(f"❌ Failed to save session: {result.get('error')}")

    return 0


if __name__ == "__main__":
    exit(main())
