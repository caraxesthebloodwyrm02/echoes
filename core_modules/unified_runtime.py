"""Unified runtime for class-of-21 profile/policy/reward generation and scoring."""

from __future__ import annotations

import itertools
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from core_modules.unified_contracts import validate_bundle

DEFAULT_THRESHOLD = 0.55

# ---------------------------------------------------------------------------
# Policy-driven output hooks
# ---------------------------------------------------------------------------

SCENARIO_KEYS = ("sharp", "loose", "heated", "checkpoint")

DEFENSE_ESCALATION = ("observe", "log", "deflect", "boundary", "halt")


@dataclass
class CheckpointState:
    """Tracks conversation progress through checkpoints."""

    current: int = 0  # 0-5: intent, context, solution, resolution, closure, complete
    stall_count: int = 0  # turns at same checkpoint
    stall_threshold: int = 3  # escalate after 3 turns stalled
    scope_history: list[str] = field(default_factory=list)
    last_scope: str = ""

    CHECKPOINTS = ("intent", "context", "solution", "resolution", "closure", "complete")

    def advance(self) -> None:
        """Move to next checkpoint."""
        self.current = min(self.current + 1, len(self.CHECKPOINTS) - 1)
        self.stall_count = 0

    def stall(self) -> int:
        """Increment stall counter at current checkpoint."""
        self.stall_count += 1
        return self.stall_count

    def is_stalled(self) -> bool:
        """Check if stalled beyond threshold."""
        return self.stall_count >= self.stall_threshold

    def detect_scope_jump(self, new_scope: str) -> bool:
        """Detect if input introduces new domain/topic."""
        if not self.last_scope:
            self.last_scope = new_scope
            return False
        is_jump = new_scope != self.last_scope
        if is_jump:
            self.scope_history.append(new_scope)
        self.last_scope = new_scope
        return is_jump

    @property
    def checkpoint_name(self) -> str:
        return self.CHECKPOINTS[min(self.current, len(self.CHECKPOINTS) - 1)]


@dataclass
class AdversarialState:
    """Tracks adversarial pattern detection across turns."""

    active: bool = False
    matched_pattern: str = ""
    defense_level: int = 0
    turn_history: list[str] = field(default_factory=list)
    cooldown_remaining: int = 0

    @property
    def defense_posture(self) -> str:
        idx = min(self.defense_level, len(DEFENSE_ESCALATION) - 1)
        return DEFENSE_ESCALATION[idx]

    def escalate(self) -> str:
        self.defense_level = min(self.defense_level + 1, len(DEFENSE_ESCALATION) - 1)
        return self.defense_posture

    def reset(self, cooldown: int = 3) -> None:
        self.matched_pattern = ""
        self.defense_level = 0
        self.cooldown_remaining = cooldown


@dataclass
class PolicyHooks:
    """Boolean hooks derived from policy at load time. Drive print-path conditionals."""

    enforced: bool = False
    temporal_active: bool = False
    illumination_multi: bool = False
    style_shuffle: bool = False
    cascade_large: bool = False
    tension_active: bool = False
    tension_value: float = 0.0
    active_scenario: str = "sharp"
    checkpoint: CheckpointState = field(default_factory=CheckpointState)
    adversarial: AdversarialState = field(default_factory=AdversarialState)
    _scenario_cycle: Any = field(default=None, repr=False)

    def cycle_scenario(self) -> str:
        if self._scenario_cycle is None:
            self._scenario_cycle = itertools.cycle(SCENARIO_KEYS)
        self.active_scenario = next(self._scenario_cycle)
        return self.active_scenario


def _parse_policy_hooks(policy: dict[str, Any]) -> PolicyHooks:
    """Extract boolean hooks and scenario state from policy dict."""
    hooks = PolicyHooks()
    hooks.enforced = policy.get("mode") == "enforced"
    hooks.temporal_active = "temporal_contract" in policy
    illumination = policy.get("illumination", {})
    hooks.illumination_multi = bool(illumination.get("multi", False))
    hooks.style_shuffle = bool(illumination.get("style_shuffle", False))
    cascade = policy.get("cascade", {})
    hooks.cascade_large = cascade.get("implication_width") == "large"

    signals = policy.get("behavioral_signals", {})
    hooks.tension_active = bool(signals)
    hooks.tension_value = 0.0

    resilience = policy.get("adversarial_resilience", {})
    hooks.adversarial.active = bool(resilience.get("active", False))

    if hooks.style_shuffle:
        hooks.cycle_scenario()
    else:
        hooks.active_scenario = next(iter(policy.get("output_scenario", {"sharp": None})))
    return hooks


def detect_adversarial(user_input: str, hooks: PolicyHooks, policy: dict[str, Any]) -> str | None:
    """Check input against anti-patterns. Returns matched pattern name or None."""
    resilience = policy.get("adversarial_resilience", {})
    if not resilience.get("active", False):
        return None

    adv = hooks.adversarial
    if adv.cooldown_remaining > 0:
        adv.cooldown_remaining -= 1
        return None

    anti_patterns = resilience.get("anti_patterns", {})
    text = user_input.strip().lower()
    adv.turn_history.append(text)
    tolerance = resilience.get("defense_posture", {}).get("false_positive_tolerance", 0.15)

    # persistence_grind: same request rephrased 3x
    if len(adv.turn_history) >= 3:
        recent = adv.turn_history[-3:]
        unique_words = [set(t.split()) for t in recent]
        overlaps = [
            len(unique_words[i] & unique_words[j]) / max(len(unique_words[i] | unique_words[j]), 1)
            for i in range(len(recent))
            for j in range(i + 1, len(recent))
        ]
        if all(o > (1.0 - tolerance) for o in overlaps):
            adv.matched_pattern = "persistence_grind"
            adv.escalate()
            return "persistence_grind"

    # extraction: repeated narrow probing (short, question-heavy)
    if len(text.split()) <= 6 and text.endswith("?") and len(adv.turn_history) >= 3:
        recent_questions = sum(1 for t in adv.turn_history[-5:] if t.endswith("?"))
        if recent_questions >= 3:
            adv.matched_pattern = "extraction"
            adv.escalate()
            return "extraction"

    # flattery_exploit: excessive positive framing
    flattery_signals = ("great", "amazing", "perfect", "love", "brilliant", "awesome", "fantastic")
    flattery_count = sum(1 for s in flattery_signals if s in text)
    if flattery_count >= 3:
        adv.matched_pattern = "flattery_exploit"
        adv.escalate()
        return "flattery_exploit"

    # scope_creep_injection: incremental expansion
    if len(adv.turn_history) >= 4:
        lengths = [len(t.split()) for t in adv.turn_history[-4:]]
        if all(lengths[i] < lengths[i + 1] for i in range(len(lengths) - 1)):
            growth_rate = lengths[-1] / max(lengths[0], 1)
            if growth_rate > 3.0:
                adv.matched_pattern = "scope_creep_injection"
                adv.escalate()
                return "scope_creep_injection"

    return None


def compute_tension(user_input: str, hooks: PolicyHooks, policy: dict[str, Any]) -> float:
    """Compute tension based on checkpoint progress, stalling, and scope jumps.

    Tension = checkpoint_level + stall_penalty + scope_breach_penalty
    - Checkpoint 0-5: base 0.0-5.0
    - Stalled 3+ turns: +1.0 per turn beyond threshold
    - Scope jump: +0.5 per jump
    """
    cp = hooks.checkpoint

    # Base tension from checkpoint level
    base_tension = float(cp.current)

    # Stall penalty: +1.0 per turn stalled beyond threshold
    stall_penalty = 0.0
    if cp.is_stalled():
        stall_penalty = float(cp.stall_count - cp.stall_threshold)

    # Scope breach penalty: +0.5 per scope jump in history
    scope_penalty = len(cp.scope_history) * 0.5

    # Total tension, capped at 5.0
    total = min(base_tension + stall_penalty + scope_penalty, 5.0)
    hooks.tension_value = round(total, 2)
    return hooks.tension_value


def scenario_triage(hooks: PolicyHooks, policy: dict[str, Any], argv: list[str] | None = None) -> str:
    """Full shuffle pattern triage: match scenario from runtime args or cycle."""
    argv = argv if argv is not None else sys.argv[1:]
    scenarios = policy.get("output_scenario", {})

    for arg in argv:
        if arg.lstrip("-") in scenarios:
            hooks.active_scenario = arg.lstrip("-")
            return hooks.active_scenario

    combo_keys = list(scenarios.keys())
    for combo in itertools.permutations(combo_keys, 2):
        tag = f"{combo[0]}_{combo[1]}"
        if any(tag in a for a in argv):
            hooks.active_scenario = combo[0]
            return hooks.active_scenario

    if hooks.style_shuffle:
        return hooks.cycle_scenario()
    return hooks.active_scenario


@dataclass(frozen=True)
class RuntimeBundle:
    profile: dict[str, Any]
    policy: dict[str, Any]
    reward: dict[str, Any]
    examples: list[dict[str, Any]]
    bundle_dir: Path
    hooks: PolicyHooks = field(default_factory=PolicyHooks)


@dataclass(frozen=True)
class RuntimeResult:
    output: str
    score: float
    refined: bool
    context: dict[str, Any]
    scenario: str = "sharp"
    tension: float = 0.0


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
    hooks = _parse_policy_hooks(policy)
    scenario_triage(hooks, policy)
    return RuntimeBundle(
        profile=profile,
        policy=policy,
        reward=reward,
        examples=examples,
        bundle_dir=root,
        hooks=hooks,
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
        return f"{selected['output']} Applied to your prompt: '{user_input}'."

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


def run_once(
    user_input: str,
    bundle: RuntimeBundle,
    threshold: float = DEFAULT_THRESHOLD,
    turn_count: int = 0,
) -> RuntimeResult:
    hooks = bundle.hooks
    context = build_context(user_input, bundle)

    # Adversarial gate: check before anything else
    threat = detect_adversarial(user_input, hooks, bundle.policy)
    if threat and hooks.adversarial.defense_posture in ("deflect", "boundary", "halt"):
        anti = bundle.policy.get("adversarial_resilience", {}).get("anti_patterns", {})
        response_action = anti.get(threat, {}).get("response", "deflect_and_log")
        cooldown = (
            bundle.policy.get("adversarial_resilience", {}).get("defense_posture", {}).get("cooldown_after_halt", 3)
        )
        if hooks.adversarial.defense_posture == "halt":
            hooks.adversarial.reset(cooldown)
        return RuntimeResult(
            output=f"[ADVERSARIAL:{response_action}] pattern={threat} posture={hooks.adversarial.defense_posture}",
            score=0.0,
            refined=False,
            context=context,
            scenario=hooks.active_scenario,
            tension=hooks.tension_value,
        )

    # Checkpoint management: detect scope jump, stall, or advance
    scope = extract_intent(user_input)  # Use intent as scope proxy
    if hooks.checkpoint.detect_scope_jump(scope):
        # Scope jump detected — may escalate tension
        pass
    hooks.checkpoint.stall()  # Increment stall counter each turn

    # Tension gate: compute and check threshold (checkpoint-based)
    tension = compute_tension(user_input, hooks, bundle.policy) if hooks.tension_active else 0.0
    signals = bundle.policy.get("behavioral_signals", {})
    critical = float(signals.get("critical_threshold", 3.5))

    # Right vector (3.5-5): pause_and_isolate — halt output, flag
    if hooks.tension_active and tension >= critical:
        enforcement = signals.get("enforcement", {})
        action = enforcement.get("right_vector_action", "pause_and_isolate")
        if tension >= 5.0:
            action = enforcement.get("deepest_layer_action", "halt_and_flag")
        return RuntimeResult(
            output=f"[POLICY:{action}] tension={tension}",
            score=0.0,
            refined=False,
            context=context,
            scenario=hooks.active_scenario,
            tension=tension,
        )

    # Scenario-driven output
    if hooks.style_shuffle:
        hooks.cycle_scenario()

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
            scenario=hooks.active_scenario,
            tension=tension,
        )

    return RuntimeResult(
        output=draft,
        score=score,
        refined=False,
        context=context,
        scenario=hooks.active_scenario,
        tension=tension,
    )
