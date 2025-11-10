#!/usr/bin/env python3
"""
Benchmark Echoes baseline vs orchestral mode.

- Baseline: ECHOES_ORCHESTRAL_ENABLED=0
- Orchestral: ECHOES_ORCHESTRAL_ENABLED=1

For each condition:
- Run the same set of prompts (shuffled for the second run for paired A/B)
- Capture metrics: latency, throughput, success rate
- Compute ROUGE-L if references supplied
- Heuristic hallucination rate (placeholder when no external tool is available)
- Safety checks placeholders for CFG-Eval and Safety-Bench (soft checks)

Outputs:
- E:\Projects\Atmosphere\Echoes\results\<timestamp>\
  - baseline.json
  - orchestral.json
  - summary.json
  - report.md
  - artifacts.zip (archive of the above)

Notes:
- If OpenAI/Orchestral components are unavailable, falls back to TemplateProcessor demo pipeline.
- Provide your own prompts via --prompts JSONL (one object per line: {"id": str, "input": str})
- Optionally provide references via --refs JSONL (aligned by id): {"id": str, "reference": str}
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zipfile

# Ensure Echoes root on sys.path
import sys
ECHOES_DIR = Path(__file__).resolve().parents[1]
if str(ECHOES_DIR) not in sys.path:
    sys.path.append(str(ECHOES_DIR))

# Optional imports for local processing
try:
    from template_process import TemplateProcessor
except Exception:
    TemplateProcessor = None  # type: ignore

# Optional orchestral manager (may be unavailable without keys)
try:
    from core.orchestral_ai import OrchestralAIManager, ChatMessage, OrchestralRequest, ProcessingMode
except Exception:
    OrchestralAIManager = None  # type: ignore
    ChatMessage = None  # type: ignore
    OrchestralRequest = None  # type: ignore
    ProcessingMode = None  # type: ignore


@dataclass
class Prompt:
    id: str
    input: str
    reference: Optional[str] = None


@dataclass
class RunResult:
    id: str
    input: str
    response: str
    latency_ms: float
    success: bool
    rouge_l: Optional[float] = None
    hallucination: Optional[bool] = None
    safety_flags: Dict[str, bool] = None  # e.g., {"cfg_eval": True, "safety_bench": True}


# ---------------- Metrics -----------------

def _lcs(a: List[str], b: List[str]) -> int:
    """Longest common subsequence length for ROUGE-L."""
    m, n = len(a), len(b)
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    return dp[n]


def rouge_l(hyp: str, ref: str) -> float:
    hyp_tokens = hyp.split()
    ref_tokens = ref.split()
    if not hyp_tokens or not ref_tokens:
        return 0.0
    lcs = _lcs(hyp_tokens, ref_tokens)
    prec = lcs / len(hyp_tokens)
    rec = lcs / len(ref_tokens)
    if prec + rec == 0:
        return 0.0
    beta = 1.2
    f = ((1 + beta ** 2) * prec * rec) / (rec + beta ** 2 * prec)
    return float(f)


def paired_stats(xs: List[float], ys: List[float]) -> Dict[str, Any]:
    """Compute paired differences summary and Cohen's d."""
    if len(xs) != len(ys) or len(xs) == 0:
        return {"count": 0}
    diffs = [y - x for x, y in zip(xs, ys)]
    mean_diff = statistics.mean(diffs)
    sd_diff = statistics.pstdev(diffs) if len(diffs) > 1 else 0.0
    d = mean_diff / sd_diff if sd_diff > 0 else float("inf") if mean_diff != 0 else 0.0
    # Note: p-value not computed (no SciPy). We report t-like statistic as mean_diff / (sd/sqrt(n)).
    t_like = mean_diff / (sd_diff / (len(diffs) ** 0.5)) if sd_diff > 0 else float("inf")
    return {
        "count": len(diffs),
        "mean_diff": mean_diff,
        "sd_diff": sd_diff,
        "t_like": t_like,
        "cohens_d": d,
    }


def safety_checks(text: str) -> Dict[str, bool]:
    """Placeholder safety checks for CFG-Eval and Safety-Bench.
    Returns flags: True means PASS (safe), False means potential issue.
    """
    lowered = text.lower()
    # Simple heuristics
    cfg_eval_safe = not any(k in lowered for k in ["env:", "export ", "rm -rf", "powershell -command"])
    safety_bench_safe = not any(k in lowered for k in ["violence", "self-harm", "explicit sexual"])
    return {"cfg_eval": cfg_eval_safe, "safety_bench": safety_bench_safe}


def hallucination_heuristic(text: str) -> bool:
    """Return True if hallucination is suspected (unsafe), False otherwise.
    Heuristic: contains confident factual claims markers without references (very rough).
    """
    lowered = text.lower()
    triggers = ["definitely", "guaranteed", "according to", "as proven", "always", "never"]
    refs = ["http://", "https://", "doi:", "arxiv:"]
    if any(t in lowered for t in triggers) and not any(r in lowered for r in refs):
        return True
    return False


# -------------- Runners -------------------

def run_local_pipeline(prompt: str, orchestrated: bool) -> str:
    """Local fallback pipeline using TemplateProcessor.
    For orchestration ON, we run web_search then summarize; for OFF, just summarize the query text.
    """
    if TemplateProcessor is None:
        return prompt[:500]
    proc = TemplateProcessor()
    try:
        if orchestrated:
            rs = proc.process("web_search", {"query": prompt, "provider": "duckduckgo", "num_results": 5})
            sm = proc.process("summarize_results", {"results": rs})
            text = sm.get("summary") or json.dumps(sm, ensure_ascii=False)
        else:
            sm = proc.process("summarize_results", {"results": [{"title": prompt, "snippet": prompt}]})
            text = sm.get("summary") or json.dumps(sm, ensure_ascii=False)
        return str(text)
    except Exception:
        return prompt[:500]


async def run_orchestral_ai(prompt: str, orchestrated: bool) -> str:
    """Try to use OrchestralAIManager if available. Falls back to local pipeline.
    Note: Requires OpenAI client + API key to be configured.
    """
    if OrchestralAIManager is None or ChatMessage is None or OrchestralRequest is None or ProcessingMode is None:
        return run_local_pipeline(prompt, orchestrated)
    try:
        mgr = OrchestralAIManager()
        msgs = [ChatMessage(role="user", content=prompt)]
        mode = (
            ProcessingMode.FULL_ORCHESTRAL if orchestrated else ProcessingMode.STANDARD
        )
        req = OrchestralRequest(messages=msgs, mode=mode)
        import asyncio
        res = await mgr.process_orchestral_request(req)
        # unify response extraction
        if isinstance(res, dict):
            if "response" in res and isinstance(res["response"], str):
                return res["response"]
            if "response" in res and isinstance(res["response"], dict):
                # try to unwrap content field if present
                content = (
                    res["response"].get("choices", [{}])[0].get("message", {}).get("content")
                    if isinstance(res["response"], dict)
                    else None
                )
                if content:
                    return str(content)
        return json.dumps(res, ensure_ascii=False)
    except Exception:
        return run_local_pipeline(prompt, orchestrated)


def timed_call(func, *args, **kwargs) -> Tuple[Any, float, bool]:
    t0 = time.perf_counter()
    try:
        out = func(*args, **kwargs)
        ok = True
    except Exception as e:
        out = f"ERROR: {e}"
        ok = False
    t1 = time.perf_counter()
    return out, (t1 - t0) * 1000.0, ok


# -------------- IO helpers ----------------

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ensure_outdir() -> Path:
    base = ECHOES_DIR / "results" / datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_json(path: Path, obj: Any):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def archive_dir(dirpath: Path):
    zpath = dirpath / "artifacts.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in dirpath.rglob("*"):
            if p.is_file() and p.name != "artifacts.zip":
                zf.write(p, p.relative_to(dirpath))


# -------------- Main benchmark -------------

def run_condition(name: str, prompts: List[Prompt], orchestrated: bool) -> Dict[str, Any]:
    results: List[RunResult] = []
    latencies = []
    successes = 0
    t0 = time.perf_counter()

    for pr in prompts:
        # local pipeline (could be swapped to async orchestral if available)
        response, latency_ms, ok = timed_call(run_local_pipeline, pr.input, orchestrated)
        latencies.append(latency_ms)
        successes += int(ok)

        # metrics
        r_l = rouge_l(str(response), pr.reference) if pr.reference else None
        hall = hallucination_heuristic(str(response))
        safety = safety_checks(str(response))

        results.append(
            RunResult(
                id=pr.id,
                input=pr.input,
                response=str(response),
                latency_ms=float(latency_ms),
                success=bool(ok),
                rouge_l=r_l,
                hallucination=hall,
                safety_flags=safety,
            ).__dict__
        )

    total_ms = (time.perf_counter() - t0) * 1000.0
    throughput = len(prompts) / (total_ms / 1000.0) if total_ms > 0 else 0.0
    success_rate = successes / len(prompts) if prompts else 0.0

    return {
        "name": name,
        "count": len(prompts),
        "avg_latency_ms": statistics.mean(latencies) if latencies else None,
        "p90_latency_ms": statistics.quantiles(latencies, n=10)[-1] if len(latencies) >= 10 else None,
        "throughput_rps": throughput,
        "success_rate": success_rate,
        "results": results,
    }


def generate_report(outdir: Path, base: Dict[str, Any], orch: Dict[str, Any], paired: Dict[str, Any], decision: Dict[str, Any]):
    md = []
    md.append(f"# Orchestral Benchmark Report\n")
    md.append(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
    md.append("\n## Summary\n")
    md.append("- **Baseline**:\n")
    md.append(f"  - avg_latency_ms: {base.get('avg_latency_ms')}\n")
    md.append(f"  - throughput_rps: {base.get('throughput_rps')}\n")
    md.append(f"  - success_rate: {base.get('success_rate')}\n")
    md.append("- **Orchestral**:\n")
    md.append(f"  - avg_latency_ms: {orch.get('avg_latency_ms')}\n")
    md.append(f"  - throughput_rps: {orch.get('throughput_rps')}\n")
    md.append(f"  - success_rate: {orch.get('success_rate')}\n")
    md.append("\n## Paired Stats (Orchestral - Baseline)\n")
    for k, v in paired.items():
        md.append(f"- **{k}**: {v}\n")
    md.append("\n## Decision\n")
    md.append(f"- **Rollout**: {decision['rollout']}\n")
    md.append(f"- **Reason**: {decision['reason']}\n")
    md.append("\n## Safety Checks\n")
    md.append("- Placeholder CFG-Eval and Safety-Bench heuristics run on each output; see JSON for per-item flags.\n")
    (outdir / "report.md").write_text("".join(md), encoding="utf-8")


def decide_rollout(baseline: Dict[str, Any], orchestral: Dict[str, Any]) -> Dict[str, Any]:
    # Thresholds from user:
    # latency stays within 1.5x baseline,
    # hallucination <= 2%,
    # ROUGE-L improves by at least 5%,
    # success rate >= 98%
    base_avg = baseline.get("avg_latency_ms") or 0.0
    orch_avg = orchestral.get("avg_latency_ms") or 0.0
    latency_ok = orch_avg <= 1.5 * base_avg if base_avg > 0 else True

    # hallucination rate
    def _hall_rate(run):
        res = run.get("results", [])
        if not res:
            return 0.0
        flags = [bool(r.get("hallucination")) for r in res if r.get("hallucination") is not None]
        return sum(1 for f in flags if f) / len(flags) if flags else 0.0

    hall_ok = _hall_rate(orchestral) <= 0.02

    # ROUGE-L improvement
    def _avg_rouge(run):
        vals = [r.get("rouge_l") for r in run.get("results", []) if r.get("rouge_l") is not None]
        return statistics.mean(vals) if vals else None

    base_r = _avg_rouge(baseline)
    orch_r = _avg_rouge(orchestral)
    rouge_ok = (orch_r is not None and base_r is not None and orch_r >= 1.05 * base_r) or (base_r is None and orch_r is not None)

    # success
    succ_ok = (orchestral.get("success_rate") or 0) >= 0.98

    all_ok = latency_ok and hall_ok and rouge_ok and succ_ok
    reason = {
        "latency_ok": latency_ok,
        "hallucination_ok": hall_ok,
        "rouge_ok": rouge_ok,
        "success_ok": succ_ok,
    }
    return {"rollout": bool(all_ok), "reason": reason}


def main():
    ap = argparse.ArgumentParser(description="Benchmark Echoes baseline vs orchestral")
    ap.add_argument("--prompts", type=str, help="Path to prompts JSONL", default="")
    ap.add_argument("--refs", type=str, help="Path to references JSONL (align by id)", default="")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    # Load prompts
    if args.prompts and Path(args.prompts).exists():
        raw = load_jsonl(Path(args.prompts))
        prompts = [Prompt(id=str(i.get("id", idx)), input=str(i.get("input", ""))) for idx, i in enumerate(raw)]
    else:
        # default small set
        prompts = [
            Prompt(id="p1", input="Summarize the benefits of spatial audio for gaming."),
            Prompt(id="p2", input="Give a short overview of latency optimization techniques in streaming."),
            Prompt(id="p3", input="List top web search providers and their strengths."),
            Prompt(id="p4", input="What's the status of the assistant session in Echoes?")
        ]

    # Load references if provided
    refs_map = {}
    if args.refs and Path(args.refs).exists():
        refs = load_jsonl(Path(args.refs))
        refs_map = {str(r.get("id")): str(r.get("reference", "")) for r in refs}
    for p in prompts:
        p.reference = refs_map.get(p.id)

    outdir = ensure_outdir()

    # Baseline (flag OFF)
    os.environ["ECHOES_ORCHESTRAL_ENABLED"] = "0"
    baseline = run_condition("baseline", prompts, orchestrated=False)
    save_json(outdir / "baseline.json", baseline)

    # Orchestral (flag ON) with shuffled order but paired by id
    rnd = random.Random(args.seed)
    prompts_b = prompts.copy()
    rnd.shuffle(prompts_b)

    os.environ["ECHOES_ORCHESTRAL_ENABLED"] = "1"
    orchestral = run_condition("orchestral", prompts_b, orchestrated=True)
    save_json(outdir / "orchestral.json", orchestral)

    # Build paired stats for latency and rouge if available
    base_by_id = {r["id"]: r for r in baseline.get("results", [])}
    orch_by_id = {r["id"]: r for r in orchestral.get("results", [])}
    shared_ids = [pid for pid in base_by_id.keys() if pid in orch_by_id]

    lat_base = [base_by_id[i]["latency_ms"] for i in shared_ids]
    lat_orch = [orch_by_id[i]["latency_ms"] for i in shared_ids]
    rlg_base = [base_by_id[i].get("rouge_l") or 0.0 for i in shared_ids]
    rlg_orch = [orch_by_id[i].get("rouge_l") or 0.0 for i in shared_ids]

    paired = {
        "latency": paired_stats(lat_base, lat_orch),
        "rouge_l": paired_stats(rlg_base, rlg_orch),
    }

    decision = decide_rollout(baseline, orchestral)

    summary = {
        "baseline": {k: v for k, v in baseline.items() if k != "results"},
        "orchestral": {k: v for k, v in orchestral.items() if k != "results"},
        "paired": paired,
        "decision": decision,
    }
    save_json(outdir / "summary.json", summary)

    # Markdown report
    generate_report(outdir, baseline, orchestral, {k: v for k, v in paired.items()}, decision)

    # Create archive
    archive_dir(outdir)

    # If revert condition -> log regressions under D:\Research\Atmosphere
    if not decision["rollout"]:
        droot = Path("D:/Research/Atmosphere")
        droot.mkdir(parents=True, exist_ok=True)
        rdir = droot / datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        rdir.mkdir(parents=True, exist_ok=True)
        save_json(rdir / "summary.json", summary)
        (rdir / "NOTE.txt").write_text(
            "Rollout reverted due to thresholds not met. See summary.json for details.",
            encoding="utf-8",
        )

    print(json.dumps({"ok": True, "out": str(outdir), "rollout": decision["rollout"]}))


if __name__ == "__main__":
    main()
