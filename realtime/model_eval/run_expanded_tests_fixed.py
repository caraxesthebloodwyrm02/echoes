#!/usr/bin/env python3
"""
Thin wrapper that forwards execution to the core implementation.

Keeping the heavy logic in ``run_expanded_tests_fixed_content.py`` makes the
code easier to import from unit‑tests or other tools.
"""

# Import the entry‑point from the core module
from run_expanded_tests_fixed_content import main

if __name__ == "__main__":
    # When this file is executed directly we simply call the imported main().
    main()
