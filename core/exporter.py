import json
from pathlib import Path
from typing import Any


def export_text(text: str, output_path: str) -> None:
    Path(output_path).write_text(text, encoding="utf-8")


def export_json(data: Any, output_path: str) -> None:
    Path(output_path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
