from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

BASE_RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def _list_runs(limit: int = 10) -> List[Path]:
    if not BASE_RESULTS_DIR.exists():
        return []
    dirs = [p for p in BASE_RESULTS_DIR.iterdir() if p.is_dir()]
    dirs.sort(key=lambda p: p.name, reverse=True)
    return dirs[:limit]


def _read_json(p: Path) -> Dict[str, Any] | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_monitor_summary(limit: int = 10) -> Dict[str, Any]:
    runs: List[Dict[str, Any]] = []
    for d in _list_runs(limit):
        summary = _read_json(d / "summary.json")
        if not summary:
            continue
        decision = summary.get("decision", {})
        baseline = summary.get("baseline", {})
        orchestral = summary.get("orchestral", {})
        runs.append(
            {
                "timestamp": d.name,
                "rollout": bool(decision.get("rollout", False)),
                "reason": decision.get("reason", {}),
                "baseline": {
                    "avg_latency_ms": baseline.get("avg_latency_ms"),
                    "throughput_rps": baseline.get("throughput_rps"),
                    "success_rate": baseline.get("success_rate"),
                },
                "orchestral": {
                    "avg_latency_ms": orchestral.get("avg_latency_ms"),
                    "throughput_rps": orchestral.get("throughput_rps"),
                    "success_rate": orchestral.get("success_rate"),
                },
            }
        )
    latest = runs[0] if runs else None
    return {"generated": datetime.utcnow().isoformat() + "Z", "latest": latest, "history": runs}


def get_monitor_dashboard_html() -> str:
    return (
        """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Echoes Orchestral Monitoring</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 20px; }
    h1 { font-size: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 14px; }
    th { background: #f4f4f4; text-align: left; }
    code { background: #f7f7f7; padding: 2px 4px; }
  </style>
</head>
<body>
  <h1>Echoes Orchestral Monitoring</h1>
  <div id="latest"></div>
  <h2>Recent Runs</h2>
  <table id="runs"><thead>
    <tr><th>Timestamp</th><th>Rollout</th><th>Baseline avg(ms)</th><th>Orchestral avg(ms)</th><th>Baseline succ</th><th>Orchestral succ</th></tr>
  </thead><tbody></tbody></table>
  <script>
    async function load() {
      const r = await fetch('/monitor/summary');
      const data = await r.json();
      const latest = data.latest || {};
      const el = document.getElementById('latest');
      if (latest && latest.timestamp) {
        el.innerHTML = `<p><b>Latest:</b> ${latest.timestamp} &mdash; rollout: <code>${latest.rollout}</code></p>`;
      } else {
        el.innerHTML = '<p>No runs found.</p>';
      }
      const tbody = document.querySelector('#runs tbody');
      tbody.innerHTML = '';
      (data.history || []).forEach(x => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${x.timestamp}</td>
          <td>${x.rollout}</td>
          <td>${(x.baseline||{}).avg_latency_ms ?? ''}</td>
          <td>${(x.orchestral||{}).avg_latency_ms ?? ''}</td>
          <td>${(x.baseline||{}).success_rate ?? ''}</td>
          <td>${(x.orchestral||{}).success_rate ?? ''}</td>
        `;
        tbody.appendChild(tr);
      });
    }
    load();
  </script>
</body>
</html>
        """
    )
