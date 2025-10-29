# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Deep Theory Mindmap for Python Development and Data Processing

Visual representation of the interconnected concepts from the NotebookLM briefing.
"""

# Text-based mindmap representation (ASCII safe)
MINDMAP_TEXT = """
Python Development & Data Processing - Deep Theory Mindmap
==========================================================

Central Concept: Robust Python Development Environment
|
+-- CLI Implementation
|   +-- Command-Line Arguments
|   |   +-- sys.argv List
|   |   +-- Flag Detection (--break)
|   |   +-- List Comprehension Iteration
|   +-- Advanced Breakpoint
|   |   +-- Libraries: sys, pexpect, curses
|   |   +-- Process Control
|   |   +-- Terminal Interaction
|   |   +-- User Input Validation
|   +-- Validation Logic
|       +-- try/except Blocks
|       +-- Positive Integer Checks
|
+-- JSON Data Handling
|   +-- Core Concepts
|   |   +-- Lightweight Format
|   |   +-- Easy-to-Read
|   |   +-- Data Interchange
|   +-- Data Types
|   |   +-- Strings
|   |   +-- Numbers
|   |   +-- Booleans
|   |   +-- Complex Structures
|   +-- Serialization/Deserialization
|       +-- json.dumps() -> JSON String
|       +-- json.loads() -> Python Object
|
+-- Data Analysis Workflow
|   +-- Step 1: Define Data Types
|   |   +-- Built-in Types (int, float, str)
|   +-- Step 2: Input Datasets
|   |   +-- CSV Files
|   +-- Step 3: Convert to DataFrames
|   |   +-- pandas Library
|   +-- Step 4: Explore & Clean
|   |   +-- Missing Values (nulls)
|   |   +-- Imputation (mean, median)
|   |   +-- Outlier Treatment
|   +-- Step 5: Data Manipulation
|   |   +-- Aggregation
|   |   +-- Statistical Analysis
|   |   +-- Libraries: numpy, scikit-learn, pandas
|   +-- Step 6: Visualizations
|       +-- Histograms, Scatter Plots, Boxplots
|       +-- Libraries: matplotlib, seaborn
|       +-- Chart Types: Line Graphs, Bar Charts
|
+-- Development Environment Configuration
    +-- Custom Scripts (PowerShell 7.5.3)
    |   +-- pyenv - Activate Environment
    |   +-- pyenv-create - Create/Re-create
    |   +-- pyenv-list - Show Available
    |   +-- pyenv-remove - Delete Environment
    +-- VS Code Workspace Settings
    |   +-- Python Integration
    |   |   +-- Interpreter Path: .venv/Scripts/python.exe
    |   |   +-- Auto-activate Venv in Terminal
    |   |   +-- .env File Loading
    |   +-- Linting & Formatting
    |   |   +-- Flake8 Enabled
    |   |   +-- Ruff Enabled
    |   |   +-- Pylint Disabled
    |   |   +-- Black Formatter (--line-length 88)
    |   +-- Testing
    |   |   +-- Pytest Enabled
    |   +-- Terminal & Shell
    |   |   +-- Default Profile: PowerShell (project)
    |   |   +-- Ubuntu WSL Profile
    |   |   +-- PATH Additions
    |   +-- Editor Settings
    |   |   +-- Font Size: 16
    |   |   +-- Line Height: 26
    |   |   +-- Word Wrap: On
    |   |   +-- Rulers: [88, 120]
    |   +-- UI Enhancements
    |       +-- Sticky Scroll
    |       +-- Zoom Level: 1.5
    +-- Integration Features
        +-- Extension Settings
        |   +-- Codeium Enabled
        |   +-- Chat MCP Discovery
        +-- Code Actions on Save
            +-- Organize Imports
            +-- Fix All Issues
"""

# Mermaid diagram for mindmap
MINDMAP_MERMAID = """
```mermaid
mindmap
  root((Python Dev & Data Processing))
    CLI Implementation
      Command-Line Arguments
        sys.argv List
        Flag Detection
        List Comprehension
      Advanced Breakpoint
        Libraries
          sys
          pexpect
          curses
        Features
          Process Control
          Terminal Interaction
          Input Validation
    JSON Data Handling
      Core Concepts
        Lightweight Format
        Easy-to-Read
        Data Interchange
      Data Types
        Strings
        Numbers
        Booleans
        Complex Structures
      Operations
        Serialization (dumps)
        Deserialization (loads)
    Data Analysis Workflow
      Define Data Types
        Built-in Types
      Input Datasets
        CSV Files
      Convert to DataFrames
        pandas
      Explore & Clean
        Missing Values
        Imputation
        Outliers
      Data Manipulation
        Aggregation
        Statistics
        Libraries
          numpy
          scikit-learn
          pandas
      Visualizations
        Chart Types
          Histograms
          Scatter Plots
          Boxplots
          Line Graphs
        Libraries
          matplotlib
          seaborn
    Dev Environment Config
      Custom Scripts
        pyenv
        pyenv-create
        pyenv-list
        pyenv-remove
      VS Code Settings
        Python Integration
          Interpreter Path
          Venv Activation
          .env Loading
        Linting & Formatting
          Flake8
          Ruff
          Black
        Testing
          Pytest
        Terminal
          PowerShell Profile
          WSL Profile
        Editor
          Font Settings
          Word Wrap
          Rulers
        UI
          Sticky Scroll
          Zoom Level
      Extensions
        Codeium
        Chat MCP
```
"""


def display_mindmap():
    """Display the deep theory mindmap"""
    print("Deep Theory Mindmap: Python Development & Data Processing")
    print("=" * 60)
    print(MINDMAP_TEXT)

    print("\n\nMermaid Diagram Representation:")
    print("=" * 40)
    print(MINDMAP_MERMAID)


if __name__ == "__main__":
    display_mindmap()
