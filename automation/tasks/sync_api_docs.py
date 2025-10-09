"""
Sync API documentation from FastAPI app to docs/ using OpenAPI schema.
Task name: "Sync API Docs" -> function: sync_api_docs(context)
"""

from __future__ import annotations

import json
from pathlib import Path

from automation.core.logger import AutomationLogger


def _load_app():
    try:
        from app.main import app  # type: ignore

        return app
    except Exception:
        # Fallback if tests/sys.path place `app/` at top level
        import importlib

        mod = importlib.import_module("main")
        return getattr(mod, "app")


def _markdown_for_routes(app) -> str:
    lines = [
        "# API Reference",
        "",
        "> Auto-generated from FastAPI routes.",
        "",
        "## Endpoints",
        "",
    ]
    for route in getattr(app, "routes", []):
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not methods or not path:
            continue
        methods_str = ", ".join(sorted(methods - {"HEAD", "OPTIONS"}))
        if not methods_str:
            continue
        doc = getattr(route.endpoint, "__doc__", "") or ""
        first = doc.strip().split("\n")[0] if doc else "No description"
        lines.append(f"### `{methods_str} {path}`")
        lines.append("")
        lines.append(f"{first}")
        lines.append("")
        lines.append("---\n")
    return "\n".join(lines)


def sync_api_docs(context):
    log = AutomationLogger()
    app = _load_app()

    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    openapi_path = Path(
        context.extra_data.get("output_json", docs_dir / "openapi.json")
    )
    api_md_path = Path(
        context.extra_data.get("output_md", docs_dir / "API_REFERENCE.md")
    )

    # Generate OpenAPI
    schema = app.openapi()
    md = _markdown_for_routes(app)

    if context.dry_run:
        log.info(f"[DRY-RUN] Would write OpenAPI to: {openapi_path}")
        log.info(f"[DRY-RUN] Would write API markdown to: {api_md_path}")
        return

    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    with open(api_md_path, "w", encoding="utf-8") as f:
        f.write(md)

    log.info(f"✅ Updated {openapi_path}")
    log.info(f"✅ Updated {api_md_path}")
