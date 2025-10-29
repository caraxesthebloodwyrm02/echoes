"""Echoes Application Package."""

__version__ = "2.0.0"

try:
    from core.ethos import enforce as _echoes_enforce_ethos
    _echoes_enforce_ethos()
except Exception:
    pass
