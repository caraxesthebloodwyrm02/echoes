"""Append-only log + empirical outcome rates for simulation predictions."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from core_modules.helpers import utc_now_iso_ms

logger = logging.getLogger(__name__)

OutcomeLabel = Literal["success", "partial_success", "failure"]

DEFAULT_PRIOR: dict[str, float] = {
    "success": 0.65,
    "partial_success": 0.25,
    "failure": 0.10,
}

MIN_ACTION_SAMPLES = 3
MIN_GLOBAL_SAMPLES = 5

# Cap total JSONL lines (prediction + feedback rows) to bound disk use on long runs.
MAX_JSONL_LINES_DEFAULT = 10_000


def normalize_action_key(action: str) -> str:
    """Stable key for aggregating outcomes (bounded length)."""
    s = " ".join(action.strip().lower().split())
    return s[:256] if s else "_empty"


def canonical_outcome_label(raw: str) -> OutcomeLabel:
    """Normalize user/API outcome aliases to stored labels."""
    aliases = {
        "success": "success",
        "partial": "partial_success",
        "partial_success": "partial_success",
        "failure": "failure",
        "fail": "failure",
    }
    key = raw.strip().lower().replace("-", "_")
    if key not in aliases:
        raise ValueError(
            "outcome must be success, partial_success (partial), or failure (fail)",
        )
    return cast(OutcomeLabel, aliases[key])


@dataclass(frozen=True)
class EmpiricalProbabilities:
    """Probability vector with provenance for outcome prediction."""

    probs: dict[str, float]
    source: Literal["default_prior", "global_empirical", "action_empirical", "smoothed_blend"]
    action_samples: int
    global_samples: int
    action_key: str


class OutcomePredictionStore:
    """JSONL-backed store: feedback rows train empirical outcome probabilities."""

    def __init__(
        self,
        log_path: Path | None = None,
        *,
        max_jsonl_lines: int | None = None,
    ) -> None:
        self.log_path = log_path or Path("data/simulation_outcomes.jsonl")
        self._max_jsonl_lines = max_jsonl_lines if max_jsonl_lines is not None else MAX_JSONL_LINES_DEFAULT

    def append_prediction_record(
        self,
        *,
        action_key: str,
        probabilities: dict[str, float],
        simulation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a prediction pass for audit (does not affect empirical counts)."""
        row = {
            "event": "prediction",
            "action_key": action_key,
            "probabilities": probabilities,
            "simulation_id": simulation_id,
            "metadata": metadata or {},
        }
        self._append_row(row)

    def append_feedback(self, action_key: str, outcome: OutcomeLabel) -> None:
        """Record an observed outcome for future empirical estimates."""
        if outcome not in DEFAULT_PRIOR:
            raise ValueError(f"outcome must be one of {list(DEFAULT_PRIOR)}, got {outcome!r}")
        row = {"event": "feedback", "action_key": action_key, "outcome": outcome}
        self._append_row(row)

    def _append_row(self, row: dict[str, Any]) -> None:
        row["recorded_at"] = utc_now_iso_ms()
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
            self._maybe_trim_log()
        except OSError as e:
            logger.warning("Could not append outcome log row: %s", e)

    def _maybe_trim_log(self) -> None:
        """Keep at most ``_max_jsonl_lines`` lines by dropping oldest records."""
        if self._max_jsonl_lines <= 0 or not self.log_path.is_file():
            return
        try:
            text = self.log_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.warning("Could not read outcome log for trim: %s", e)
            return
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if len(lines) <= self._max_jsonl_lines:
            return
        keep = lines[-self._max_jsonl_lines :]
        tmp = self.log_path.with_suffix(self.log_path.suffix + ".tmp")
        try:
            tmp.write_text("\n".join(keep) + "\n", encoding="utf-8")
            tmp.replace(self.log_path)
        except OSError as e:
            logger.warning("Could not trim outcome log: %s", e)
            try:
                if tmp.is_file():
                    tmp.unlink()
            except OSError:
                pass

    def _load_feedback_counts(self) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
        """Returns (per_action outcome tallies, global outcome tallies)."""
        per_action: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        global_counts: dict[str, int] = defaultdict(int)

        if not self.log_path.is_file():
            return {}, {}

        try:
            with self.log_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("event") != "feedback":
                        continue
                    key = obj.get("action_key") or "_empty"
                    oc = obj.get("outcome")
                    if oc not in DEFAULT_PRIOR:
                        continue
                    per_action[key][oc] += 1
                    global_counts[oc] += 1
        except OSError as e:
            logger.warning("Could not read outcome log: %s", e)

        return dict(per_action), dict(global_counts)

    @staticmethod
    def _counts_to_probs(counts: dict[str, int]) -> dict[str, float]:
        total = sum(counts.get(k, 0) for k in DEFAULT_PRIOR)
        if total <= 0:
            return dict(DEFAULT_PRIOR)
        return {k: counts.get(k, 0) / total for k in DEFAULT_PRIOR}

    def empirical_probabilities(self, action: str) -> EmpiricalProbabilities:
        """Derive outcome probabilities from logged feedback with fallback hierarchy."""
        action_key = normalize_action_key(action)
        per_action, global_counts = self._load_feedback_counts()

        action_counts = dict(per_action.get(action_key, {}))
        n_action = sum(action_counts.get(k, 0) for k in DEFAULT_PRIOR)
        n_global = sum(global_counts.get(k, 0) for k in DEFAULT_PRIOR)

        if n_action >= MIN_ACTION_SAMPLES:
            probs = self._counts_to_probs(action_counts)
            return EmpiricalProbabilities(
                probs=probs,
                source="action_empirical",
                action_samples=n_action,
                global_samples=n_global,
                action_key=action_key,
            )

        if n_global >= MIN_GLOBAL_SAMPLES:
            probs = self._counts_to_probs(global_counts)
            return EmpiricalProbabilities(
                probs=probs,
                source="global_empirical",
                action_samples=n_action,
                global_samples=n_global,
                action_key=action_key,
            )

        # Blend sparse feedback with prior (simple pseudocount / Laplace-style smoothing)
        if n_action > 0 or n_global > 0:
            blended = dict(DEFAULT_PRIOR)
            counts = action_counts if n_action > 0 else global_counts
            total_obs = sum(counts.get(k, 0) for k in DEFAULT_PRIOR)
            if total_obs > 0:
                for k in DEFAULT_PRIOR:
                    blended[k] = (counts.get(k, 0) + DEFAULT_PRIOR[k] * 2) / (total_obs + 2)
                s = sum(blended.values())
                blended = {k: blended[k] / s for k in blended}
            return EmpiricalProbabilities(
                probs=blended,
                source="smoothed_blend",
                action_samples=n_action,
                global_samples=n_global,
                action_key=action_key,
            )

        return EmpiricalProbabilities(
            probs=dict(DEFAULT_PRIOR),
            source="default_prior",
            action_samples=n_action,
            global_samples=n_global,
            action_key=action_key,
        )
