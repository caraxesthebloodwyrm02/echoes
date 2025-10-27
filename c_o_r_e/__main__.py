# Consent-Based License
#
# Version 1.0
# Effective Date: October 27, 2025
#
# This module is part of the Echoes AI Assistant project and requires explicit consent for use.
# Please read the main LICENSE file and contact the licensor for usage terms.
#
# Author Contact Information
# Erfan Kabir
# irfankabir02@gmail.com
# GitHub: caraxesthebloodwyrm02

"""
System Orchestrator - Main Entry Point
Run with: python -m system_orchestrator
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_orchestrator.core.bootstrap import main

if __name__ == "__main__":
    main()
