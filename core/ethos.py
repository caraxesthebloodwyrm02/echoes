"""Echoes ethos enforcement.

Validates that the runtime environment meets Echoes' operational
requirements (e.g. required env vars, Python version guards).
Called automatically on package import via app/__init__.py.
"""


def enforce() -> None:
    """Run lightweight startup-time checks.

    Extend with additional pre-flight checks (env vars, feature flags) as
    needed.  The minimum Python version (>=3.12) is enforced by
    ``requires-python`` in pyproject.toml.
    """
