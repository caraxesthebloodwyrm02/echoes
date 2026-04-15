"""Strict contracts for class-of-21 unified runtime artifacts."""

from __future__ import annotations

from typing import Any

ALLOWED_LENGTH = {"short", "medium", "long"}
ALLOWED_CONSTRAINT_KEYS = {"length", "tone", "format", "freshness_required"}
ALLOWED_EXAMPLE_KEYS = {
    "example_id",
    "user_intent",
    "context_summary",
    "stable_preferences",
    "constraints",
    "model_action",
    "output",
    "rationale",
    "reward_labels",
    "error_tags",
}
ALLOWED_REWARD_LABELS = {"helpful", "grounded", "concise", "adaptive"}
ALLOWED_PROFILE_KEYS = {
    "communication_style",
    "learning_style",
    "interaction_style",
    "tooling_expectation",
}
ALLOWED_COMMUNICATION_KEYS = {"preferred", "avoid"}
ALLOWED_PREFERRED_ONLY = {"preferred"}
ALLOWED_POLICY_KEYS = {
    "mode",
    "priorities",
    "hard_rules",
    "transformer_rules",
    "temporal_contract",
    "output_scenario",
    "illumination",
    "cascade",
    "behavioral_signals",
    "adversarial_resilience",
}
ALLOWED_REWARD_KEYS = {"base", "bonus", "penalty"}
ALLOWED_REWARD_BASE_KEYS = {
    "correctness",
    "groundedness",
    "conciseness",
    "structure",
    "uncertainty",
}


class ContractError(ValueError):
    """Raised when canonical artifacts violate the unified contract."""


def _require_dict(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{name} must be a dict")
    return value


def _require_list_of_strings(name: str, value: Any) -> None:
    if not isinstance(value, list) or not all(isinstance(i, str) and i for i in value):
        raise ContractError(f"{name} must be a non-empty list of strings")


def _check_unknown(name: str, payload: dict[str, Any], allowed: set[str], strict: bool) -> None:
    if not strict:
        return
    unknown = set(payload.keys()) - allowed
    if unknown:
        raise ContractError(f"{name} has unknown keys: {sorted(unknown)}")


def validate_constraints(constraints: dict[str, Any], *, strict: bool = True) -> None:
    _require_dict("constraints", constraints)
    _check_unknown("constraints", constraints, ALLOWED_CONSTRAINT_KEYS, strict)

    for key in ALLOWED_CONSTRAINT_KEYS:
        if key not in constraints:
            raise ContractError(f"constraints missing key: {key}")

    if constraints["length"] not in ALLOWED_LENGTH:
        raise ContractError("constraints.length must be one of short|medium|long")
    if not isinstance(constraints["tone"], str) or not constraints["tone"]:
        raise ContractError("constraints.tone must be a non-empty string")
    if not isinstance(constraints["format"], str) or not constraints["format"]:
        raise ContractError("constraints.format must be a non-empty string")
    if not isinstance(constraints["freshness_required"], bool):
        raise ContractError("constraints.freshness_required must be a boolean")


def validate_example(example: dict[str, Any], *, strict: bool = True) -> None:
    _require_dict("example", example)
    _check_unknown("example", example, ALLOWED_EXAMPLE_KEYS, strict)

    missing = ALLOWED_EXAMPLE_KEYS - set(example.keys())
    if missing:
        raise ContractError(f"example missing keys: {sorted(missing)}")

    str_keys = ["example_id", "user_intent", "context_summary", "model_action", "output"]
    for key in str_keys:
        if not isinstance(example[key], str) or not example[key]:
            raise ContractError(f"example.{key} must be a non-empty string")

    _require_list_of_strings("example.stable_preferences", example["stable_preferences"])
    _require_list_of_strings("example.rationale", example["rationale"])

    if not isinstance(example["error_tags"], list) or not all(isinstance(i, str) for i in example["error_tags"]):
        raise ContractError("example.error_tags must be a list of strings")

    validate_constraints(_require_dict("example.constraints", example["constraints"]), strict=strict)

    labels = _require_dict("example.reward_labels", example["reward_labels"])
    _check_unknown("example.reward_labels", labels, ALLOWED_REWARD_LABELS, strict)
    missing_labels = ALLOWED_REWARD_LABELS - set(labels.keys())
    if missing_labels:
        raise ContractError(f"example.reward_labels missing keys: {sorted(missing_labels)}")
    for key in ALLOWED_REWARD_LABELS:
        if labels[key] not in (0, 1):
            raise ContractError(f"example.reward_labels.{key} must be 0 or 1")


def validate_profile(profile: dict[str, Any], *, strict: bool = True) -> None:
    _require_dict("profile", profile)
    _check_unknown("profile", profile, ALLOWED_PROFILE_KEYS, strict)

    for key in ALLOWED_PROFILE_KEYS:
        if key not in profile:
            raise ContractError(f"profile missing key: {key}")

    communication = _require_dict("profile.communication_style", profile["communication_style"])
    _check_unknown("profile.communication_style", communication, ALLOWED_COMMUNICATION_KEYS, strict)
    _require_list_of_strings("profile.communication_style.preferred", communication.get("preferred"))
    _require_list_of_strings("profile.communication_style.avoid", communication.get("avoid"))

    for key in ("learning_style", "interaction_style", "tooling_expectation"):
        section = _require_dict(f"profile.{key}", profile[key])
        _check_unknown(f"profile.{key}", section, ALLOWED_PREFERRED_ONLY, strict)
        _require_list_of_strings(f"profile.{key}.preferred", section.get("preferred"))


def validate_policy(policy: dict[str, Any], *, strict: bool = True) -> None:
    _require_dict("policy", policy)
    _check_unknown("policy", policy, ALLOWED_POLICY_KEYS, strict)

    for key in ALLOWED_POLICY_KEYS:
        if key not in policy:
            raise ContractError(f"policy missing key: {key}")

    if policy["mode"] not in {"enforced", "advisory"}:
        raise ContractError("policy.mode must be enforced|advisory")

    for key in ("priorities", "hard_rules", "transformer_rules"):
        _require_list_of_strings(f"policy.{key}", policy[key])


def validate_reward_spec(spec: dict[str, Any], *, strict: bool = True) -> None:
    _require_dict("reward", spec)
    _check_unknown("reward", spec, ALLOWED_REWARD_KEYS, strict)

    missing = ALLOWED_REWARD_KEYS - set(spec.keys())
    if missing:
        raise ContractError(f"reward missing keys: {sorted(missing)}")

    base = _require_dict("reward.base", spec["base"])
    _check_unknown("reward.base", base, ALLOWED_REWARD_BASE_KEYS, strict)
    base_missing = ALLOWED_REWARD_BASE_KEYS - set(base.keys())
    if base_missing:
        raise ContractError(f"reward.base missing keys: {sorted(base_missing)}")

    for key in ALLOWED_REWARD_BASE_KEYS:
        if not isinstance(base[key], (int, float)):
            raise ContractError(f"reward.base.{key} must be numeric")

    for key in ("bonus", "penalty"):
        section = _require_dict(f"reward.{key}", spec[key])
        for item_key, value in section.items():
            if not isinstance(item_key, str) or not item_key:
                raise ContractError(f"reward.{key} keys must be non-empty strings")
            if not isinstance(value, (int, float)):
                raise ContractError(f"reward.{key}.{item_key} must be numeric")


def validate_bundle(
    profile: dict[str, Any],
    examples: list[dict[str, Any]],
    policy: dict[str, Any],
    reward: dict[str, Any],
    *,
    strict: bool = True,
) -> None:
    validate_profile(profile, strict=strict)
    if not isinstance(examples, list) or not examples:
        raise ContractError("examples must be a non-empty list")
    for idx, example in enumerate(examples):
        try:
            validate_example(example, strict=strict)
        except ContractError as exc:
            raise ContractError(f"invalid example at index {idx}: {exc}") from exc
    validate_policy(policy, strict=strict)
    validate_reward_spec(reward, strict=strict)
