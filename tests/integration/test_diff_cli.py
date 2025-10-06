# tests/integration/test_diff_cli.py
import subprocess
import json
from pathlib import Path
import yaml


def test_cli_json_output():
    p = subprocess.run([
        "python", "-m", "app.harmony.cli",
        "--harmony", "tests/fixtures/harmony_finance.json",
        "--melody", "tests/fixtures/melody_finance.json",
        "--format", "json", "--epsilon", "0.01"
    ], capture_output=True, text=True, check=True)
    out = json.loads(p.stdout)
    assert "metrics" in out
    assert out["metrics"]["modified_count"] >= 0


def test_cli_yaml_output():
    p = subprocess.run([
        "python", "-m", "app.harmony.cli",
        "--harmony", "tests/fixtures/harmony_finance.json",
        "--melody", "tests/fixtures/melody_finance.json",
        "--format", "yaml"
    ], capture_output=True, text=True, check=True)
    parsed = yaml.safe_load(p.stdout)
    assert "metrics" in parsed
