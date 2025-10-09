import random
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PauseEvent:
    start_s: float
    end_s: float
    label: str  # cognitive_load | rhetorical | handoff | other


def set_seed(seed: int) -> None:
    random.seed(seed)


def train_stub(samples: List[Dict[str, Any]], seed: int = 42) -> Dict[str, Any]:
    set_seed(seed)
    # Placeholder training: compute simple priors over labels
    counts: Dict[str, int] = {}
    for s in samples:
        lbl = s.get("label", "other")
        counts[lbl] = counts.get(lbl, 0) + 1
    total = sum(counts.values()) or 1
    priors = {k: v / total for k, v in counts.items()}
    return {"priors": priors, "seed": seed}


def predict_pause_type(priors: Dict[str, float], features: Dict[str, float]) -> str:
    # Simple argmax over priors (placeholder)
    if not priors:
        return "other"
    return max(priors.items(), key=lambda kv: kv[1])[0]
