# Custom AI Agent for Windsurf

A Python-based AI agent that integrates with OpenAI's function calling capabilities, customized for the Windsurf development environment.

## Features

- **Weather Queries**: Get current weather for any city
- **Stock Prices**: Retrieve real-time stock prices
- **Math Calculations**: Safe mathematical expression evaluation
- **Python REPL**: Execute Python code snippets
- **Windsurf Integration**: Designed to work with Windsurf's terminal and Python settings

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   - Edit the `.env` file with your API keys:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `OPENWEATHERMAP_API_KEY`: Get from [OpenWeatherMap](https://openweathermap.org/api)
     - `ALPHA_VANTAGE_API_KEY`: Get from [Alpha Vantage](https://www.alphavantage.co)

3. **Run the Agent**:
   ```bash
   python ai_agent_custom.py
   ```

## Usage

The agent supports natural language queries that can combine multiple tools:

- `"What's the weather in Tokyo?"`
- `"Get me the stock price for AAPL"`
- `"Calculate 15 * 23 + 7"`
- `"Execute this Python code: print('Hello, Windsurf!')"`
- `"Weather in New York and stock price of Apple"`

## Integration with Windsurf

This agent is designed to work seamlessly with Windsurf's settings:
- Respects `python.REPL.enableREPLSmartSend` for code execution
- Compatible with `terminal.integrated.shellIntegration.enabled`
- Works with `python.terminal.activateEnvironment` for virtual environments
- Follows `editor.inlineSuggest.enabled` patterns for suggestions

## Customization

Add new tools by:
1. Defining the tool schema in the `tools` list
2. Implementing the executor function
3. Adding it to the `tool_executors` dictionary

## Troubleshooting

- Ensure all API keys are properly set in `.env`
- Check that you're using Python 3.8+
- Verify internet connection for API calls
- If using a virtual environment, make sure it's activated
