# Smart Terminal - Intelligent Command Assistant

An intelligent terminal assistant that learns from your command usage and provides smart suggestions, feedback collection, and enhanced command-line experience.

## Features

- **Smart Command Suggestions**: Learns from your command history and suggests the most relevant commands
- **User Feedback System**: Collect ratings and feedback to improve suggestions over time
- **Cross-Platform**: Works on Windows, macOS, and Linux with graceful fallbacks
- **Privacy-Focused**: All data stored locally, no external communication
- **Persistent Learning**: Remembers your preferences between sessions

## Installation

1. Ensure you have Python 3.7+ installed
2. Install prompt_toolkit for enhanced features (optional):
   ```bash
   pip install prompt_toolkit
   ```

## Usage

### Running the Terminal

```bash
cd smart_terminal
python main.py
```

### Available Commands

- `help` - Show available commands
- `suggest` - Get command suggestions based on partial input
- `feedback` - Provide feedback on suggestions and ratings
- `exit` - Exit the terminal

### Example Session

```
Intelligent Terminal - Type 'help' for commands
> help

Available commands:
  help     - Show this help
  suggest  - Show command suggestions
  feedback - Provide feedback
  exit     - Exit the terminal

> ls
Executing: ls
> cd Documents
Executing: cd Documents
> suggest
Enter partial command: c
Suggestions:
  1. cd
> feedback

Feedback Options:
1. Rate last command
2. Report a suggestion issue
3. Back to terminal
Select an option (1-3): 1
Rate your last command (1-5): 5
Thank you for your feedback!
> exit
```

## Architecture

### Core Components

- **CommandPredictor**: Learns command frequencies and provides suggestions
- **FeedbackHandler**: Manages user feedback and ratings
- **TerminalInterface**: Handles user interaction and display

### Data Storage

- `data/commands.json`: Stores command frequencies and history
- `data/feedback.json`: Stores user feedback and ratings

## Development

### Running Tests

```bash
python test_all.py
```

### Project Structure

```
smart_terminal/
├── core/
│   ├── __init__.py
│   ├── predictor.py      # Command prediction logic
│   └── feedback.py       # User feedback handling
├── interface/
│   ├── __init__.py
│   └── terminal.py       # Terminal UI and interaction
├── data/                 # Data storage (created automatically)
├── main.py              # Entry point
└── test_all.py          # Comprehensive tests
```

## Features in Detail

### Smart Suggestions

The terminal learns from your command usage patterns and suggests the most frequently used commands that match your input. Suggestions are sorted by usage frequency.

### Feedback System

- **Command Ratings**: Rate commands 1-5 stars
- **Suggestion Feedback**: Report issues with suggestions
- All feedback is used to improve future suggestions

### Cross-Platform Support

- **Windows**: Uses basic input with prompt_toolkit if available
- **macOS/Linux**: Full readline/prompt_toolkit support
- Graceful degradation when dependencies are missing

## Privacy & Security

- All data is stored locally in JSON files
- No external network communication
- No telemetry or data collection
- Data can be deleted by removing the `data/` directory

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the `smart_terminal` directory:

```bash
cd smart_terminal
python main.py
```

### Missing Dependencies

The terminal works without additional dependencies, but for the best experience:

```bash
pip install prompt_toolkit
```

### Data Issues

If you encounter data loading errors, you can reset by deleting the data files:

```bash
rm -rf data/
```

## Contributing

This is a simple, focused project. Feel free to submit issues or pull requests for improvements.

## License

MIT License - feel free to use and modify as needed.
