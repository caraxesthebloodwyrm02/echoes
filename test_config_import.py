#!/usr/bin/env python
"""Test that api/config.py imports correctly after Pydantic V2 migration."""

from api.config import get_config

c = get_config()
print(f"Config loaded successfully: {c.api.host}:{c.api.port}")
print(f"Environment: {c.environment}")
