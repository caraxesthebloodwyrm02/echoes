import os
from pathlib import Path

import yaml  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]

DOC_PATH = REPO_ROOT / "app" / "domains" / "arts" / "investlab" / "HARMONYHUB_INTEGRATION_STRATEGY.md"
EXAMPLES_YAML = REPO_ROOT / "configs" / "integration_examples.yaml"
EXAMPLES_SH = REPO_ROOT / "cli" / "examples.sh"

DOC_LINKS = [
    REPO_ROOT / "README_HARMONYHUB.md",
    REPO_ROOT / "HARMONYHUB_WORKFLOW_GUIDE.md",
    REPO_ROOT / "HARMONYHUB_INTEGRATION_COMPLETE.md",
    REPO_ROOT / "HARMONYHUB_AUDIT_TOOL_DESIGN.md",
]

EXPECTED_COMMANDS = [
    "python engines/realtime_valuation_engine.py --analyze --profile finance",
    "python innovation_engines/novelty_engine.py --seed \"theme\" --mode suggestions",
    "python -m app.cli.main audit full --domain finance --white-box",
]


def test_referenced_files_exist():
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"
    for p in DOC_LINKS:
        assert p.exists(), f"Missing referenced file: {p}"


def test_examples_artifacts_exist():
    assert EXAMPLES_YAML.exists(), f"Missing YAML: {EXAMPLES_YAML}"
    assert EXAMPLES_SH.exists(), f"Missing script: {EXAMPLES_SH}"


def test_commands_present_in_yaml_and_script():
    with open(EXAMPLES_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    profiles = data.get("profiles", {})
    commands = [profiles[k]["command"] for k in profiles if "command" in profiles[k]]
    for cmd in EXPECTED_COMMANDS:
        assert cmd in commands, f"Command not found in YAML: {cmd}"

    with open(EXAMPLES_SH, "r", encoding="utf-8") as f:
        sh_text = f.read()
    for cmd in EXPECTED_COMMANDS:
        assert cmd in sh_text, f"Command not found in examples.sh: {cmd}"
