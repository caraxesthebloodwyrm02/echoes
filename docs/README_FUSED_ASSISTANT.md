# Fused Terminal Chat & Command Assistant

A sophisticated Python assistant that combines battle-tested terminal operations with an intelligent conversational interface.

## Features

### 🤖 Dual Mode Operation
- **Chat Mode**: Natural language conversation with smart command interpretation
- **Command Mode**: Precise terminal operations with full tool access
- **Menu Mode**: Interactive selection between modes and utilities

### 🛠️ 50+ Integrated Tools
- **File Operations**: read, write, create, delete, move, copy, list, search, analyze, backup, diff
- **System Commands**: execute, process_info, disk_usage, network_status, system_info, env_vars, running_processes
- **Web Operations**: web_search, download, http_status, curl, api_call
- **Code Operations**: run, lint, format, test, debug, profile
- **Data Operations**: parse_csv, parse_json, analyze_data, clean_data, statistics
- **Analysis Operations**: review_code, security_scan, analyze_performance, check_dependencies
- **Assistant Operations**: help, status, history, clear, save_session, load_session, metrics, tools

### 🧠 Intelligent Features
- **Experience-driven learning**: Adapts based on success patterns
- **Natural language processing**: Understands conversational commands
- **Error recovery**: Smart suggestions and auto-retry logic
- **Performance metrics**: Tracks execution time and success rates
- **Session persistence**: Save and restore sessions
- **Context awareness**: Remembers conversation history

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The fused assistant specifically needs:
```bash
pip install psutil duckduckgo-search
```

## Usage

### Chat Mode (Conversational)
```bash
python fused_assistant.py --chat
```

In chat mode, you can use natural language:
- "hello" or "how are you"
- "list files" or "show files in current directory"
- "search for error in logs"
- "create file test.py"
- "run python --version"
- "what can you do?"
- "status" or "help"

### Command Mode (Precise Operations)
```bash
python fused_assistant.py --cmd "list files *.py"
python fused_assistant.py --cmd "web_search python tutorial"
python fused_assistant.py --cmd "analyze_file script.py"
```

### Interactive Menu
```bash
python fused_assistant.py
```

This provides a menu to choose between:
1. Chat Mode
2. Command Mode  
3. Status view
4. Help system
5. Quit

### Session Management
```bash
# Save session
python fused_assistant.py --save-session my_session.json

# Load previous session
python fused_assistant.py --session my_session.json
```

## Command Reference

### File Operations
- `read <filepath>` - Read file contents
- `write <filepath> <content>` - Write content to file
- `create <filepath> [content]` - Create new file
- `delete <filepath>` - Delete file
- `move <source> <destination>` - Move file
- `copy <source> <destination>` - Copy file
- `list [directory] [pattern]` - List files
- `search <query> [directory]` - Search files for text
- `analyze <filepath>` - Analyze file characteristics
- `backup <filepath> [backup_dir]` - Create backup
- `diff <file1> <file2>` - Compare files

### System Commands
- `execute <command>` - Run system command
- `process_info [pid]` - Get process information
- `disk_usage [path]` - Check disk usage
- `network_status` - Check connectivity
- `system_info` - Get system information
- `env_vars` - List environment variables
- `running_processes` - List processes

### Web Operations
- `web_search <query> [num_results]` - Search web with DuckDuckGo
- `download <url> [filepath]` - Download file
- `http_status <url>` - Check HTTP status
- `curl <url> [method]` - Make HTTP request
- `api_call <endpoint> [method]` - Make API call

### Code Operations
- `run <code> [language]` - Execute code
- `lint <filepath>` - Lint code file
- `format <filepath>` - Format code
- `test [directory]` - Run tests
- `debug <filepath>` - Debug code
- `profile <filepath>` - Profile performance

### Data Operations
- `parse_csv <filepath>` - Parse CSV file
- `parse_json <filepath>` - Parse JSON file
- `analyze_data <data>` - Analyze data
- `clean_data <data>` - Clean data
- `statistics <data>` - Get statistics

### Analysis Operations
- `review_code <filepath>` - Review code quality
- `security_scan <filepath>` - Security vulnerability scan
- `analyze_performance <filepath>` - Performance analysis
- `check_dependencies [directory]` - Check project dependencies

### Assistant Operations
- `help [command]` - Show help information
- `status` - Show assistant status
- `history [count]` - Show command history
- `clear` - Clear screen
- `save_session [filepath]` - Save session
- `load_session <filepath>` - Load session
- `metrics` - Show performance metrics
- `tools` - List available tools

## Natural Language Examples

The chat mode understands conversational commands:

```
You: hello
Assistant: Hello! I'm your fused assistant. How can I help you today?

You: what can you do?
Assistant: I can help you with:
📁 File operations: read, write, search, analyze files
🔧 System commands: execute processes, check system info
🌐 Web operations: search online, download files
💻 Code operations: run, lint, test code
📊 Data operations: parse CSV/JSON, analyze data
🔍 Analysis: code review, security scans
🤖 Chat: natural language conversation

You: list files
Assistant: [Returns JSON with file listing]

You: search for error in .py files
Assistant: [Returns search results]

You: create file test.py with some python code
Assistant: [Creates file and confirms]

You: run python test.py
Assistant: [Executes the command and shows output]
```

## Configuration

The assistant tracks:
- **Experience**: Success rates and patterns for each command type
- **Metrics**: Execution times, success rates, most used commands
- **Context**: Recent commands, search history, user preferences
- **Sessions**: Complete conversation and command history

## Error Handling

The assistant provides intelligent error recovery:
- Automatic retry for transient failures
- Specific suggestions based on error types
- Graceful fallbacks for missing dependencies
- Clear error messages with actionable advice

## Examples

### File Management
```bash
# Chat mode
You: read the config.json file
You: create a backup of important.txt
You: search for TODO comments in all python files

# Command mode  
python fused_assistant.py --cmd "read config.json"
python fused_assistant.py --cmd "backup important.txt"
python fused_assistant.py --cmd "search TODO ."
```

### System Monitoring
```bash
# Chat mode
You: check system info
You: show running processes
You: how much disk space is left?

# Command mode
python fused_assistant.py --cmd "system_info"
python fused_assistant.py --cmd "running_processes"
python fused_assistant.py --cmd "disk_usage"
```

### Web Operations
```bash
# Chat mode
You: search for python tutorials
You: download the latest version from github.com/user/repo
You: check if google.com is accessible

# Command mode
python fused_assistant.py --cmd "web_search python tutorials"
python fused_assistant.py --cmd "download https://github.com/user/repo/archive/main.zip"
python fused_assistant.py --cmd "http_status https://google.com"
```

## Development

The assistant is built with:
- **Python 3.7+** compatibility
- **Modular architecture** for easy extension
- **Comprehensive error handling** and logging
- **Type hints** for better code quality
- **Session persistence** for continuity

## Contributing

To add new tools:
1. Implement the method in `FusedAssistant` class
2. Add it to `_initialize_tools()` registry
3. Update help text and documentation
4. Add error handling and validation

## License

This fused assistant combines open-source components and follows the project's licensing terms.
