# Echoes Development Environment Setup

## 🚀 Quick Setup (One Command)

```bash
# Complete automated setup
python setup_complete.py

# Or for quick setup (skip profile alignment)
python setup_complete.py --quick
```

## 📋 Manual Setup Steps

### 1. Bootstrap Environment
```bash
python bootstrap.py
```
- Creates/upgrades virtual environment
- Installs all dependencies
- Validates OpenAI integration
- Generates startup scripts

### 2. Align IDE Profiles (Optional but Recommended)
```bash
python setup_profiles.py --all
```
- Backs up existing settings
- Aligns VS Code & Windsurf profiles
- Sets up automatic startup

### 3. Activate Environment
```powershell
# PowerShell (recommended)
.\activate_environment.ps1

# Or manually
.venv\Scripts\activate
```

### 4. Start Development
```bash
python main.py
```

## 🔧 Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup_complete.py` | One-command full setup | First time setup |
| `bootstrap.py` | Environment & dependencies | Re-bootstrap after changes |
| `setup_profiles.py` | IDE profile alignment | Profile issues or new machine |
| `startup.py` | Quick validation | Daily startup check |
| `activate_environment.ps1` | Environment activation | Daily development start |

## ⚙️ Configuration Files

### Environment Variables (.env)
Copy `.env.template` to `.env` and configure:
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30
```

### IDE Settings
- **Workspace**: `.vscode/settings.json` (project-specific)
- **User**: `~/AppData/Roaming/Code/User/settings.json` (global)
- **Windsurf**: `~/AppData/Roaming/Windsurf/User/settings.json` (global)

## 🔍 Validation & Troubleshooting

### Check Environment Status
```bash
python tools/validate_configuration.py
```

### Test All Integrations
```bash
python -c "
from utils.safe_imports import get_import_status
from utils.openai_integration import validate_openai_setup
import json
print('Import Status:', json.dumps(get_import_status(), indent=2))
validate_openai_setup()
"
```

### Common Issues

#### "Python version not found"
- Ensure Python 3.12+ is installed
- Check `python --version`

#### "OpenAI integration failed"
- Check `OPENAI_API_KEY` in `.env`
- Verify API key is valid

#### "Permission denied" on scripts
```bash
# Fix script permissions
chmod +x *.py
```

#### "Module not found" errors
```bash
# Reinstall dependencies
python bootstrap.py
```

## 🏗️ Architecture

### Safe Import System
- `utils/safe_imports.py`: Graceful degradation for optional dependencies
- Prevents cascade failures from missing packages
- Automatic fallback to basic functionality

### Unified Configuration
- `packages/core/config/__init__.py`: Pydantic-based config with validation
- `config/settings.py`: Application settings management
- Environment-aware configuration loading

### OpenAI Integration
- `utils/openai_integration.py`: Unified API interface
- Automatic configuration from environment
- Agents SDK support with fallbacks

### IDE Integration
- VS Code launch configurations for debugging
- Extension recommendations
- Profile alignment for consistent experience

## 📊 System Status

After successful setup, you should see:
- ✅ Python 3.12+ detected
- ✅ Virtual environment active
- ✅ Dependencies installed
- ✅ OpenAI integration configured
- ✅ Configuration validation passed
- ✅ Safe imports working
- ✅ All core modules functional

## 🎯 Development Workflow

1. **Daily Start**: `.\activate_environment.ps1`
2. **Code**: Edit in VS Code/Windsurf with full IntelliSense
3. **Debug**: Use F5 or launch configurations
4. **Test**: `python -m pytest`
5. **Validate**: `python tools/validate_configuration.py`

## 🔐 Security Features

- **Configuration Validation**: Strict schema validation
- **API Key Protection**: Environment variable only access
- **Import Safety**: Controlled dependency loading
- **Profile Isolation**: Workspace vs user setting separation

## 📞 Support

If setup fails:
1. Check the error output carefully
2. Run `python tools/validate_configuration.py` for diagnostics
3. Ensure Python 3.12+ and git are installed
4. Verify `.env` file exists with valid OpenAI API key
5. Try `python bootstrap.py` to re-bootstrap environment
