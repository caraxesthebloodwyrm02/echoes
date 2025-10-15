# Batch Processing System

This directory contains the Step-2: Batch Mode & Compounding Engine implementation with tight budget protection and cost optimization.

## 🚀 Quick Start

```bash
# Navigate to src directory
cd src

# Dry run first (no API calls, simulates behavior)
python batch_processor.py --task summarize --dry-run

# Run for real (requires OPENAI_API_KEY in .env)
python batch_processor.py --task summarize

# Launch web demo (requires streamlit)
streamlit run web_demo.py
```

## 🌐 Web Demo Interface

The system includes a Streamlit web interface for easy sharing and demonstration:

```bash
# Install streamlit (if not already installed)
pip install streamlit

# Launch the web demo
cd src
streamlit run web_demo.py
```

**Web Demo Features:**
- 📁 **File Upload**: Drag & drop .txt files or paste text directly
- 🎯 **Task Selection**: Choose from summarize, rephrase, or extract_actions
- 💰 **Budget Monitoring**: Real-time budget status and cost estimation
- ⚡ **Dry Run Mode**: Test processing without API costs
- 📊 **Live Results**: View processing results and cost breakdowns
- 📋 **Processing History**: See detailed logs and output files

**Access the demo at:** `http://localhost:8501`

## 📁 Directory Structure

```
src/
├── batch_processor.py      # Main batch processing script
├── web_demo.py            # Streamlit web interface
├── modules/
│   └── transformer.py      # OpenAI integration wrapper
├── utils/
│   └── budget_guard.py     # Budget protection & cost optimization
├── data/
│   ├── input_samples/      # Place .txt files here
│   └── outputs/            # Processed outputs appear here
└── logs/
    └── budget.json         # Budget tracking ledger
```

## 🎯 Available Tasks

- `summarize`: Create concise summaries of input text
- `rephrase`: Rewrite content in different words
- `extract_actions`: Pull out actionable items from text

## 💰 Budget Protection

- **Default Budget**: $5.00 USD
- **Real-time Tracking**: All API calls logged and costed
- **Smart Model Selection**: Automatically chooses cheapest viable model
- **Cost Optimization**: Uses token estimates to select appropriate models

### Model Pricing (per 1,000 tokens, input rate)
- `gpt-4o-mini`: $0.15
- `gpt-3.5-turbo`: $0.50
- `gpt-4o`: $2.50

## 🔧 Configuration

Edit `src/utils/budget_guard.py` to adjust:
- `DEFAULT_BUDGET`: Change total budget limit
- `MODEL_COST_PER_1K`: Update pricing if rates change

## 📊 Monitoring

Check `src/logs/budget.json` for spending:
```json
{
  "spent": 0.35,
  "calls": 3
}
```

## 🛡️ Safety Features

- **Dry Run Mode**: Test without spending credits
- **Budget Enforcement**: Stops processing when limit reached
- **Throttle Control**: Prevents rapid API calls
- **Fallback Estimates**: Uses heuristics if usage data unavailable

## 🎨 Integration Options

The system is designed to be integrated with the main Echoes platform:

1. **Direct CLI Usage**: As shown above
2. **API Integration**: Import modules into existing workflows
3. **Web Interface**: Streamlit web demo now available (see above)
4. **REPL Integration**: Integrated with main.py REPL system

## 📈 Performance

- **Token Estimation**: ~4 characters = 1 token heuristic
- **Model Selection**: Cost-aware automatic optimization
- **Batch Processing**: Handles multiple files efficiently
- **Output Formatting**: Structured results with metadata
