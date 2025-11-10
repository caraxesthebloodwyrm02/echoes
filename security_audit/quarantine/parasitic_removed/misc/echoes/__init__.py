"""
Echoes Package
=============

Main package for Echoes AI Assistant.
"""

try:
    from core.ethos import enforce as _echoes_enforce_ethos

    _echoes_enforce_ethos()
except Exception:
    pass
