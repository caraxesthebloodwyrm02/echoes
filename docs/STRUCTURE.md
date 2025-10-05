# 📁 Project Structure - Educational Ecosystem

## ✅ Reorganized Codebase (v3.0)

**Date**: 2025-09-30  
**Status**: Clean, Maintainable, Production-Ready

---

## 📂 New Folder Structure

```
school/
├── config/                          # Configuration files
│   ├── .env                        # Environment variables (API keys)
│   └── MCP-CONFIG.JSON             # MCP server configuration
│
├── data/                            # Data storage
│   ├── ecosystem/                  # Ecosystem data
│   │   ├── zones.json             # Zone configurations
│   │   ├── stakeholders.json      # User profiles
│   │   ├── workshops.json         # Workshop data
│   │   ├── transparency_log.json  # Audit logs
│   │   └── analytics/             # AI-generated insights
│   │       ├── insights_*.json
│   │       └── feedback_analysis_*.json
│   └── logs/                       # Session logs
│       └── session_*.json         # Daily check-in sessions
│
├── docs/                            # Documentation
│   ├── AI_INTEGRATION_GUIDE.md    # AI features guide
│   ├── CHANGELOG.md               # Version history
│   ├── DESIGN_PHILOSOPHY.md       # Design principles
│   ├── ECOSYSTEM_README.md        # Ecosystem framework docs
│   ├── FINAL_SUMMARY.md           # Complete summary
│   ├── QUICKSTART.md              # Quick start guide
│   ├── TEST_REPORT.md             # Test results
│   └── time_guidelines.md         # Time management
│
├── scripts/                         # Utility scripts
│   └── generate_sample_data.py    # Data generator
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── ai/                         # AI engine
│   │   ├── __init__.py
│   │   ├── ai_engine.py           # AI engine (sentiment, recommendations)
│   │   └── inference.py           # HuggingFace inference
│   │
│   ├── core/                       # Core check-in system
│   │   ├── __init__.py
│   │   ├── checkin.py             # Main check-in system
│   │   └── orchestrator.py        # System orchestrator
│   │
│   ├── modules/                    # Ecosystem modules
│   │   ├── __init__.py
│   │   ├── adaptive_infrastructure.py  # Zone management
│   │   ├── community_engagement.py     # Stakeholder system
│   │   ├── data_analytics.py          # Analytics (pending)
│   │   ├── resource_optimizer.py      # Resources (pending)
│   │   ├── safe_ai.py                 # AI safety (pending)
│   │   └── time_manager.py            # Time management (pending)
│   │
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       ├── 500dos.py              # Legacy utility
│       ├── field_visualization.py  # Visualization tools
│       └── survey_system.py       # Survey system
│
├── tests/                           # Test files
│   ├── __init__.py
│   └── test_checkin.py            # Automated tests
│
├── .venv/                           # Virtual environment
├── .vscode/                         # VS Code settings
├── .windsurf/                       # Windsurf IDE settings
│
├── README.md                        # Main project README
├── STRUCTURE.md                     # This file
├── requirements.txt                 # Python dependencies
└── run_checkin.py                  # Main entry point
```

---

## 🎯 Key Changes from Previous Structure

### **Before (v2.5):**
```
school/
├── checkin.py                      # Root level
├── ecosystem_framework/            # Mixed structure
│   ├── modules/
│   ├── data/
│   └── logs/
├── huggingface/                    # Separate AI folder
├── [docs mixed in root]
└── [tests in root]
```

### **After (v3.0):**
```
school/
├── src/                            # All source code
│   ├── core/                      # Core system
│   ├── modules/                   # Ecosystem modules
│   ├── ai/                        # AI engine
│   └── utils/                     # Utilities
├── data/                           # All data
├── docs/                           # All documentation
├── tests/                          # All tests
├── scripts/                        # All scripts
└── config/                         # All configuration
```

---

## 🚀 How to Use

### **1. Run Check-In System:**
```bash
# Option 1: Use entry point script
python run_checkin.py

# Option 2: Direct execution
python src/core/checkin.py

# Option 3: From anywhere
cd d:/school/school
python -m src.core.checkin
```

### **2. Generate Sample Data:**
```bash
python scripts/generate_sample_data.py
```

### **3. Run Tests:**
```bash
python tests/test_checkin.py
```

### **4. View Documentation:**
```bash
# Quick start
cat docs/QUICKSTART.md

# AI integration
cat docs/AI_INTEGRATION_GUIDE.md

# Design philosophy
cat docs/DESIGN_PHILOSOPHY.md
```

---

## 📦 Import Paths

### **Updated Import Structure:**

**Before:**
```python
from ecosystem_framework.modules.adaptive_infrastructure import AdaptiveInfrastructure
from ecosystem_framework.modules.community_engagement import CommunityEngagement
from ecosystem_framework.modules.ai_engine import AIEngine
```

**After:**
```python
from src.modules.adaptive_infrastructure import AdaptiveInfrastructure
from src.modules.community_engagement import CommunityEngagement
from src.ai.ai_engine import AIEngine
```

### **Path Setup in Files:**
```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent  # Adjust based on file location
sys.path.insert(0, str(project_root))

# Now imports work
from src.modules.adaptive_infrastructure import AdaptiveInfrastructure
```

---

## 📊 Data Paths

### **Updated Data Locations:**

**Before:**
```python
data_dir = "ecosystem_framework/data"
log_dir = "ecosystem_framework/logs"
```

**After:**
```python
data_dir = "data/ecosystem"
log_dir = "data/logs"
```

### **File Locations:**
- **User Data**: `data/ecosystem/stakeholders.json`
- **Zone Data**: `data/ecosystem/zones.json`
- **Session Logs**: `data/logs/session_YYYYMMDD.json`
- **AI Insights**: `data/ecosystem/analytics/insights_YYYYMMDD.json`
- **Feedback Analysis**: `data/ecosystem/analytics/feedback_analysis_YYYYMMDD.json`

---

## 🔧 Configuration

### **Environment Variables:**
Location: `config/.env`
```
HUGGINGFACE_API_KEY=your_key_here
```

### **MCP Configuration:**
Location: `config/MCP-CONFIG.JSON`
```json
{
  "version": "1.0.0",
  "environment": "development",
  "servers": {
    "huggingface": {...},
    "gitkraken": {...}
  }
}
```

---

## 🧪 Testing

### **Test Structure:**
```
tests/
├── __init__.py
└── test_checkin.py         # All tests
```

### **Run Tests:**
```bash
# Run all tests
python tests/test_checkin.py

# Expected output:
# ✅ PASSED: Inference Logic
# ✅ PASSED: Data Structure
# ✅ PASSED: User Registration
# ✅ PASSED: Session Logging
# ✅ PASSED: Returning User
# 🎯 Overall: 5/5 tests passed (100%)
```

---

## 📚 Documentation

### **Available Docs:**
1. **README.md** - Main project overview
2. **STRUCTURE.md** - This file (folder structure)
3. **docs/QUICKSTART.md** - Quick start guide
4. **docs/AI_INTEGRATION_GUIDE.md** - AI features
5. **docs/DESIGN_PHILOSOPHY.md** - Design principles
6. **docs/ECOSYSTEM_README.md** - Ecosystem framework
7. **docs/FINAL_SUMMARY.md** - Complete summary
8. **docs/TEST_REPORT.md** - Test results
9. **docs/CHANGELOG.md** - Version history
10. **docs/time_guidelines.md** - Time management

---

## 🎯 Benefits of New Structure

### **1. Clear Separation of Concerns:**
- ✅ Source code in `src/`
- ✅ Documentation in `docs/`
- ✅ Tests in `tests/`
- ✅ Data in `data/`
- ✅ Configuration in `config/`

### **2. Logical Grouping:**
- ✅ Core system (`src/core/`)
- ✅ Ecosystem modules (`src/modules/`)
- ✅ AI engine (`src/ai/`)
- ✅ Utilities (`src/utils/`)

### **3. Easy Navigation:**
- ✅ Intuitive folder names
- ✅ Consistent structure
- ✅ Clear file purposes

### **4. Maintainability:**
- ✅ Easy to find files
- ✅ Clear dependencies
- ✅ Simple to extend

### **5. Professional Structure:**
- ✅ Industry-standard layout
- ✅ Scalable architecture
- ✅ Clean codebase

---

## 🔄 Migration Notes

### **What Changed:**
1. ✅ All source files moved to `src/`
2. ✅ All docs moved to `docs/`
3. ✅ All data moved to `data/`
4. ✅ All tests moved to `tests/`
5. ✅ All scripts moved to `scripts/`
6. ✅ All config moved to `config/`
7. ✅ Import paths updated
8. ✅ Data paths updated
9. ✅ Entry point created (`run_checkin.py`)

### **What Stayed the Same:**
- ✅ All functionality preserved
- ✅ No code logic changed
- ✅ All features working
- ✅ Data structure intact
- ✅ API unchanged

---

## ✅ Verification

### **Check Structure:**
```bash
# List main folders
ls -la

# Should see:
# config/
# data/
# docs/
# scripts/
# src/
# tests/
# README.md
# requirements.txt
# run_checkin.py
```

### **Test Functionality:**
```bash
# 1. Run check-in
python run_checkin.py

# 2. Generate data
python scripts/generate_sample_data.py

# 3. Run tests
python tests/test_checkin.py

# All should work without errors!
```

---

## 🎉 Summary

**The codebase is now:**
- ✅ Clean and organized
- ✅ Easy to navigate
- ✅ Professional structure
- ✅ Maintainable
- ✅ Scalable
- ✅ Fully functional

**Version**: 3.0.0 (Reorganized)  
**Status**: Production Ready  
**Structure**: Clean & Maintainable  
**All Tests**: Passing ✅
