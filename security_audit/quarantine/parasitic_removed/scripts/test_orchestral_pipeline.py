#!/usr/bin/env python3
"""
Smoke test for Echoes orchestral pipeline.
- Runs template_process.main() and orchestral_strategy.strategy()
- Collects outputs
- Picks top 4 by simplicity/impact heuristics
- If ECHOES_ORCHESTRAL_ENABLED=1: routes via Routing to Arcade
"""

import os
import json
from pathlib import Path
from datetime import datetime
import sys

# Ensure Echoes package path is available for imports
ECHOES_DIR = Path(__file__).resolve().parents[1]
if str(ECHOES_DIR) not in sys.path:
    sys.path.append(str(ECHOES_DIR))

# Local imports
from template_process import main as tpl_main
from orchestral_strategy import main as orch_main, strategy as orch_strategy

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def rank_top4(results: list[dict]) -> list[dict]:
    # Simple heuristic: prefer entries with keys 'status', then shorter payloads
    scored = []
    for r in results:
        score = 0
        if isinstance(r, dict):
            score += 2 if r.get("status") == "success" else 0
            score += 1 if "summary" in r or "providers" in r else 0
            size = len(json.dumps(r, default=str))
        else:
            size = len(str(r))
        scored.append((score, size, r))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [r for _, _, r in scored[:4]]


def main() -> dict:
    report: dict = {"timestamp": datetime.utcnow().isoformat(), "steps": []}

    # 1) Run template demo
    tpl_results = tpl_main()
    report["template_results"] = tpl_results

    # 2) Run orchestral strategy (returns dict)
    orch_results = orch_main()
    report["orchestral_summary"] = orch_results

    # 3) Compute strategy text
    plan = orch_strategy()
    report["strategy"] = plan

    # 4) Select top 4 outputs
    # Flatten potential nested results into list for ranking
    candidates = []
    if isinstance(tpl_results, list):
        candidates.extend(tpl_results)
    if isinstance(orch_results, dict):
        candidates.append(orch_results.get("execution_summary", {}))
    top4 = rank_top4(candidates)
    report["top4"] = top4

    # 5) If enabled, route via Routing to Arcade
    if os.getenv("ECHOES_ORCHESTRAL_ENABLED", "").lower() in ("1", "true", "yes", "on"):
        try:
            import sys

            base = Path(__file__).resolve().parents[2]
            sys.path.append(str(base / "Routing"))
            sys.path.append(str(base / "Arcade"))
            from orchestral_connector import route_orchestral_data  # type: ignore
            from orchestral_channel import receive_orchestral_data  # type: ignore

            routed = []
            for item in top4:
                payload = item if isinstance(item, dict) else {"data": item}
                res = __import__("asyncio").run(
                    route_orchestral_data(payload, "hybrid_processing")
                )
                arc = __import__("asyncio").run(receive_orchestral_data(res))
                routed.append({"routing": res, "arcade": arc})
            report["routed"] = routed
        except Exception as e:  # keep smoke test resilient
            report["routing_error"] = str(e)

    # 6) Persist report
    out_file = (
        RESULTS_DIR
        / f"orchestral_smoke_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    out_file.write_text(json.dumps(report, indent=2, default=str))

    return report


if __name__ == "__main__":
    resp = main()
    print(json.dumps({"ok": True, "saved": True, "keys": list(resp.keys())}, indent=2))
