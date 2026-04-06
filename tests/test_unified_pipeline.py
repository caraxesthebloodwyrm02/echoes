from __future__ import annotations

import json
from pathlib import Path

from core_modules.report_ingest import (
    apply_delta_candidates,
    extract_claims,
    propose_deltas,
    stage_report,
)
from core_modules.unified_runtime import load_bundle, run_once


def test_load_bundle_and_run_once():
    bundle_dir = Path(__file__).resolve().parents[1] / "data" / "class-of-21" / "canonical"
    bundle = load_bundle(bundle_dir)

    result = run_once("Explain recursion simply", bundle)

    assert result.output
    assert isinstance(result.score, float)
    assert result.context["constraints"]["format"] == "explanation"


def test_report_stage_extract_propose_apply_with_conflict(tmp_path, monkeypatch):
    monkeypatch.setenv("ECHOES_AUDIT_PATH", str(tmp_path / "audit.ndjson"))

    report = tmp_path / "report.md"
    report.write_text(
        """
- Route candidate to /plugins/atlas-echoes
- Route candidate to /plugins/atlas-echoes
""".strip()
        + "\n",
        encoding="utf-8",
    )

    staged_id = stage_report(report)
    claims_path = Path(extract_claims(staged_id))
    delta_path = Path(propose_deltas(claims_path))

    payload = json.loads(delta_path.read_text(encoding="utf-8"))
    assert payload["candidate_count"] >= 2

    result = apply_delta_candidates(delta_path)

    assert result["delta_candidates_path"] == str(delta_path)
    assert result["conflicts_resolved"] >= 1
    assert result["blocked_count"] >= 1
