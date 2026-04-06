"""Unified runtime for class-of-21 profile/policy/reward generation and scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core_modules.unified_contracts import validate_bundle

DEFAULT_THRESHOLD = 0.55


@dataclass(frozen=True)
class RuntimeBundle:
    profile: dict[str, Any]
    policy: dict[str, Any]
    reward: dict[str, Any]
    examples: list[dict[str, Any]]
    bundle_dir: Path


@dataclass(frozen=True)
class RuntimeResult:
    output: str
    score: float
    refined: bool
    context: dict[str, Any]


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML must decode to dict: {path}")
    return data


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for idx, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{idx}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"JSONL record must be object at {path}:{idx}")
            rows.append(row)
    return rows


def load_bundle(bundle_dir: str | Path) -> RuntimeBundle:
    root = Path(bundle_dir).resolve()
    profile = _read_yaml(root / "profile.yaml").get("profile", {})
    policy = _read_yaml(root / "policy.yaml").get("policy", {})
    reward = _read_yaml(root / "reward.yaml").get("reward", {})
    examples = _read_jsonl(root / "canonical.jsonl")

    validate_bundle(profile, examples, policy, reward, strict=True)
    return RuntimeBundle(
        profile=profile,
        policy=policy,
        reward=reward,
        examples=examples,
        bundle_dir=root,
    )


def extract_intent(user_input: str) -> str:
    text = user_input.strip().lower()
    if "explain" in text:
        return "explanation"
    if "compare" in text:
        return "comparison"
    if "how" in text:
        return "how_to"
    return "direct_answer"


def infer_constraints(user_input: str) -> dict[str, Any]:
    text = user_input.lower()
    if any(token in text for token in ("brief", "short", "direct", "tldr")):
        length = "short"
    elif any(token in text for token in ("detailed", "deep", "thorough")):
        length = "long"
    else:
        length = "medium"

    output_format = "direct" if "direct" in text else ("explanation" if "explain" in text else "response")
    freshness = any(token in text for token in ("latest", "today", "current", "recent"))

    return {
        "length": length,
        "tone": "clear",
        "format": output_format,
        "freshness_required": freshness,
    }


def build_context(user_input: str, bundle: RuntimeBundle) -> dict[str, Any]:
    return {
        "input": user_input,
        "intent": extract_intent(user_input),
        "constraints": infer_constraints(user_input),
        "profile": bundle.profile,
    }


def _intent_overlap_score(intent: str, example: dict[str, Any]) -> int:
    example_intent = str(example.get("user_intent", "")).lower()
    if intent == "explanation" and "explain" in example_intent:
        return 3
    if intent == "direct_answer" and "direct" in example_intent:
        return 3
    if intent in example_intent:
        return 2
    return 1


def _select_example(context: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    intent = str(context.get("intent", ""))
    ranked = sorted(
        examples,
        key=lambda ex: (
            -_intent_overlap_score(intent, ex),
            str(ex.get("example_id", "")),
        ),
    )
    return ranked[0]


def generate_candidate(context: dict[str, Any], bundle: RuntimeBundle) -> str:
    selected = _select_example(context, bundle.examples)
    constraints = context["constraints"]
    user_input = str(context["input"]).strip()

    if constraints["format"] == "explanation":
        return (
            f"{selected['output']} "
            f"Applied to your prompt: '{user_input}'."
        )

    if constraints["length"] == "short":
        return selected["output"]

    return f"{selected['output']} Assumption: response optimized for clarity."


def _contains_fluff(text: str) -> bool:
    fluff_markers = ("basically", "honestly", "super", "very very", "just to be clear")
    lowered = text.lower()
    return any(marker in lowered for marker in fluff_markers)


def _has_explicit_assumption(text: str) -> bool:
    lowered = text.lower()
    return "assumption:" in lowered or "assume" in lowered


def score_candidate(output: str, reward_spec: dict[str, Any]) -> float:
    base = reward_spec["base"]
    bonus = reward_spec["bonus"]
    penalty = reward_spec["penalty"]

    score = 0.0
    score += float(base["correctness"])
    score += float(base["groundedness"]) if len(output.split()) >= 4 else 0.0
    score += float(base["structure"]) if "." in output else 0.0

    if len(output.split()) <= 40:
        score += float(base["conciseness"])
    if "assumption" in output.lower() or "unknown" in output.lower():
        score += float(base["uncertainty"])

    if output.strip().lower().startswith(("yes", "no")):
        score += float(bonus.get("direct_answer", 0.0))
    if "Applied to your prompt:" in output:
        score += float(bonus.get("reusable_format", 0.0))

    if _contains_fluff(output):
        score += float(penalty.get("fluff", 0.0))
    if not _has_explicit_assumption(output):
        score += float(penalty.get("hidden_assumptions", 0.0))
    if len(output.split()) > 80:
        score += float(penalty.get("verbosity", 0.0))

    return round(score, 6)


def refine(output: str, policy: dict[str, Any]) -> str:
    refined = output.strip()
    if "no_fluff" in policy.get("hard_rules", []):
        refined = " ".join(refined.split())

    if "explicit_assumptions_if_needed" in policy.get("hard_rules", []) and not _has_explicit_assumption(refined):
        refined = f"{refined} Assumption: standard context."

    return refined


def run_once(user_input: str, bundle: RuntimeBundle, threshold: float = DEFAULT_THRESHOLD) -> RuntimeResult:
    context = build_context(user_input, bundle)
    draft = generate_candidate(context, bundle)
    score = score_candidate(draft, bundle.reward)

    if score < threshold:
        refined_output = refine(draft, bundle.policy)
        refined_score = score_candidate(refined_output, bundle.reward)
        return RuntimeResult(
            output=refined_output,
            score=refined_score,
            refined=True,
            context=context,
        )

    return RuntimeResult(
        output=draft,
        score=score,
        refined=False,
        context=context,
    )
