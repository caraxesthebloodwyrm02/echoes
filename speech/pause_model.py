import json
import os
import random
from dataclasses import dataclass

<<<<<<< Updated upstream
from typing import Any, Dict, List

=======
from typing import Any, Dict, List, Tuple

from packages.core import get_logger
from packages.core.schemas import PodcastData

logger = get_logger(__name__)
>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
=======


# --- Extended JSON-based training and heuristic model ---


def load_json_events(paths: List[str]) -> List[PodcastData]:
    """Load events from podcast JSON files.
    Expected schema per file: { podcast, episode_title, source, events: [...] }
    """
    all_podcasts: List[PodcastData] = []
    for p in paths:
        if not os.path.exists(p):
            logger.warning(f"Podcast file not found: {p}")
            continue
        logger.debug(f"Loading podcast data from {p}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            podcast = PodcastData(**data)
            all_podcasts.append(podcast)
            logger.debug(f"Loaded {len(podcast.events)} events from {podcast.podcast}")
        except Exception as e:
            logger.error(f"Failed to parse podcast data from {p}: {e}")
    return all_podcasts


def extract_pause_events(podcasts: List[PodcastData]) -> List[Dict[str, Any]]:
    """Extract pause events from podcast data for training."""
    events = []
    for podcast in podcasts:
        for event in podcast.events:
            events.append(
                {
                    "pause_after_s": event.pause_after_s,
                    "label": event.label,
                    "speaker": event.speaker,
                    "timestamp_start_s": event.timestamp_start_s,
                    "timestamp_end_s": event.timestamp_end_s,
                    "utterance": event.utterance,
                }
            )
    return events


def compute_label_means(events: List[Dict[str, Any]]) -> Dict[str, float]:
    sums: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for ev in events:
        lbl = ev.get("label", "other")
        val = float(ev.get("pause_after_s", 0.0))
        sums[lbl] = sums.get(lbl, 0.0) + val
        counts[lbl] = counts.get(lbl, 0) + 1
    means = {lbl: (sums[lbl] / counts[lbl]) for lbl in sums if counts.get(lbl, 0) > 0}
    return means


def derive_thresholds_from_means(means: Dict[str, float]) -> Dict[str, float]:
    """Derive simple decision thresholds on pause_after_s from label means.
    - Sort labels by mean pause.
    - Compute midpoints between adjacent means to serve as boundaries.
    Returns a dict with keys: low_mid, high_mid and order of labels.
    """
    if not means:
        return {
            "order": ["handoff", "rhetorical", "cognitive_load"],
            "low_mid": 0.5,
            "high_mid": 1.25,
        }
    ordered: List[Tuple[str, float]] = sorted(means.items(), key=lambda kv: kv[1])
    labels_order = [lbl for lbl, _ in ordered]
    values = [v for _, v in ordered]
    if len(values) == 1:
        low_mid = values[0]
        high_mid = values[0]
    elif len(values) == 2:
        low_mid = (values[0] + values[1]) / 2.0
        high_mid = low_mid
    else:
        low_mid = (values[0] + values[1]) / 2.0
        high_mid = (values[1] + values[2]) / 2.0
    return {
        "order": labels_order,
        "low_mid": float(low_mid),
        "high_mid": float(high_mid),
    }


def train_on_json(paths: List[str], seed: int = 42) -> Dict[str, Any]:
    """Train a lightweight heuristic model from JSON events.
    Model fields: priors, thresholds {order, low_mid, high_mid}
    """
    set_seed(seed)
    logger.info(f"Training pause model with seed {seed} from {len(paths)} files")
    podcasts = load_json_events(paths)
    events = extract_pause_events(podcasts)
    logger.info(f"Loaded {len(events)} events from podcast data")
    priors_model = train_stub(events, seed=seed)
    means = compute_label_means(events)
    thresholds = derive_thresholds_from_means(means)
    logger.info("Pause model training completed")
    return {
        "priors": priors_model["priors"],
        "thresholds": thresholds,
        "seed": seed,
    }


def predict_pause_label(model: Dict[str, Any], features: Dict[str, float]) -> str:
    """Predict label using pause_after_s with learned thresholds; fallback to priors.
    features: { pause_after_s: float }
    """
    pause_after = float(features.get("pause_after_s", 0.0))
    thresholds = model.get("thresholds", {})
    order: List[str] = thresholds.get(
        "order", ["handoff", "rhetorical", "cognitive_load"]
    )  # low->high
    low_mid = float(thresholds.get("low_mid", 0.5))
    high_mid = float(thresholds.get("high_mid", 1.25))

    if pause_after <= low_mid:
        return order[0]
    if pause_after <= high_mid and len(order) >= 2:
        return order[1]
    if len(order) >= 3:
        return order[2]
    # Fallback to priors argmax
    return predict_pause_type(model.get("priors", {}), features)
>>>>>>> Stashed changes
