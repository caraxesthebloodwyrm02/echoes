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
        return getattr(mod, "app")  # noqa: B009


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
