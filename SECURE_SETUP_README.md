# Echoes AI Assistant - Secure API Configuration

## 🔐 Security-First API Key Management

**Echoes is designed with security as the top priority.** API keys are loaded from environment variables and are never stored in files.

### ✅ Secure Setup (Recommended)

1. **Set Environment Variable:**
   ```powershell
   # PowerShell (permanent - User level)
   [Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-actual-key-here', 'User')

   # Or for current session only:
   $env:OPENAI_API_KEY='sk-your-actual-key-here'
   ```

2. **Verify Configuration:**
   ```bash
   python check_api_key.py
   ```

3. **Run the Unified Demo:**
   ```bash
   python demo_unified_scenario.py
   ```

### ❌ Insecure Setup (Not Recommended)

The `.env` file contains only placeholders and configuration examples. **Never store actual API keys in files.**

```env
# This is just documentation - DO NOT put real keys here
OPENAI_API_KEY=your_openai_api_key_here  # PLACEHOLDER ONLY
```

### 🛡️ Security Features

- ✅ **Runtime-only credentials** - Keys exist only in memory during execution
- ✅ **No file storage** - Credentials never persisted to disk
- ✅ **Environment isolation** - Keys scoped to user/system environment
- ✅ **Secure verification** - Test connectivity without logging credentials
- ✅ **Automatic cleanup** - Keys removed when process terminates

### 🧪 Verification Options

**Safe Verification (No API calls):**
```bash
python check_api_key.py
```

**Full API Test (Makes real call - costs apply):**
```python
# Uncomment the test_minimal_api_call() line in check_api_key.py
python check_api_key.py
```

### 🚀 Ready to Demo

With your API key securely configured via environment variables, you're ready to experience the complete Echoes AI Assistant ecosystem!

```bash
# Run the comprehensive 7-phase unified demo
python demo_unified_scenario.py
```

**The demo showcases:**
- 🧠 Parallel simulation for possibility exploration
- 💾 Intelligent caching with conversation continuity
- 🎯 Intent awareness and entity extraction
- 💭 Advanced thought tracking and relationships
- 🎭 Adaptive personality and emotional intelligence
- 😄 Context-aware humor and pressure management
- 🔗 Dynamic cross-referencing and knowledge connection
- 💎 Values-grounded ethical reasoning

All systems working together in a cohesive, intelligent, and secure AI assistant! 🌟⚡🔐
