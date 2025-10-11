from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import BaseExpert

_REGISTRY: Dict[str, BaseExpert] = {}
_MANIFEST: List[dict] = []


def _manifest_entry(name: str, version: str, instance: BaseExpert) -> dict:
    request_schema = getattr(instance, "request_schema", None)
    response_schema = getattr(instance, "response_schema", None)
    return {
        "name": name,
        "version": version,
        "request_schema": request_schema.__name__ if request_schema else None,
        "response_schema": response_schema.__name__ if response_schema else None,
    }


def expert(name: str, version: str = "0.1.0"):
    """Class decorator to register an expert implementation."""

    def wrapper(cls: Type[BaseExpert]) -> Type[BaseExpert]:
        if not issubclass(cls, BaseExpert):
            raise TypeError("Expert must inherit BaseExpert")
        instance = cls()
        instance.name = name
        instance.version = version
        _REGISTRY[name] = instance

        entry = _manifest_entry(name, version, instance)
        for idx, existing in enumerate(_MANIFEST):
            if existing["name"] == name:
                _MANIFEST[idx] = entry
                break
        else:
            _MANIFEST.append(entry)
        return cls

    return wrapper


def load_all_experts() -> None:
    """Import all submodules under experts/ to trigger registration."""

    package_path = Path(__file__).parent
    for module in pkgutil.iter_modules([str(package_path)]):
        if module.name.endswith("__pycache__"):
            continue
        if module.name in {"registry", "base", "__init__"}:
            continue
        importlib.import_module(f"experts.{module.name}")


def get_expert(name: str) -> Optional[BaseExpert]:
    return _REGISTRY.get(name)


def list_experts() -> List[str]:
    return sorted(_REGISTRY.keys())


def export_manifest(path: Path | None = None) -> List[dict]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "docs" / "expert_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(_MANIFEST, fh, indent=2)
    return _MANIFEST.copy()


__all__ = [
    "expert",
    "load_all_experts",
    "get_expert",
    "list_experts",
    "export_manifest",
]
