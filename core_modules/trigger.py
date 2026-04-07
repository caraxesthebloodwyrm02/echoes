"""
Trigger: geometric boundary trigger with G-graded notification delivery.

Entity G-scores are mapped to polar coordinates using (G, dimension_score)
as the (x, y) plane. This draws on three primary geometric foundations:

  Pythagorean theorem  r = √(G² + score²)         — distance from origin
  Polar angle          θ = atan2(score, G)          — angular position [0°, 90°]
  Triangle inequality  |AB| + |BC| > |AC|           — structural boundary validity
  Golden ratio         φ = 1.618 → G = 0.618        — natural threshold marker

Entities sort by θ. Those within angular tolerance and Pythagorean radius
form co-clusters. The trigger fires when a watched entity's G crosses
its threshold, then snapshots the angular map at that moment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

# ── Aggression levels ──────────────────────────────────────────────────────────


class AggressionLevel(StrEnum):
    TRACE = "trace"  # fire only at G = 1.0 (fully attested)
    WATCH = "watch"  # fire at G ≥ 0.618 (golden ratio cut)
    ACTIVE = "active"  # fire at G ≥ 0.42  (session gate threshold)
    OPEN = "open"  # fire on any G > 0


_AGGRESSION_FLOOR: dict[AggressionLevel, float] = {
    AggressionLevel.TRACE: 1.0,
    AggressionLevel.WATCH: 1.0 / 1.618,  # φ⁻¹ ≈ 0.618
    AggressionLevel.ACTIVE: 0.42,
    AggressionLevel.OPEN: 0.0,
}


# ── Preset ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TriggerPreset:
    """
    Control flags for depth and aggressiveness.

    depth              — BFS hop radius in the entity graph when resolving siblings
    aggression         — minimum G floor before the trigger is even evaluated
    snapshot_on_fire   — capture angular map state when trigger fires
    angular_tolerance  — ± degrees; entities within this arc are co-clustered
    distance_radius    — Pythagorean radius in (G, score) space for grouping
    """

    name: str
    depth: int = 2
    aggression: AggressionLevel = AggressionLevel.WATCH
    snapshot_on_fire: bool = True
    angular_tolerance: float = 15.0  # degrees
    distance_radius: float = 0.20  # in normalised (0–1) G-space


PRESETS: dict[str, TriggerPreset] = {
    "sentinel": TriggerPreset(
        "sentinel",
        depth=1,
        aggression=AggressionLevel.TRACE,
        snapshot_on_fire=True,
        angular_tolerance=5.0,
        distance_radius=0.10,
    ),
    "watchman": TriggerPreset(
        "watchman",
        depth=2,
        aggression=AggressionLevel.WATCH,
        snapshot_on_fire=True,
        angular_tolerance=15.0,
        distance_radius=0.35,
    ),
    "explorer": TriggerPreset(
        "explorer",
        depth=3,
        aggression=AggressionLevel.ACTIVE,
        snapshot_on_fire=False,
        angular_tolerance=30.0,
        distance_radius=0.60,
    ),
    "open": TriggerPreset(
        "open",
        depth=5,
        aggression=AggressionLevel.OPEN,
        snapshot_on_fire=False,
        angular_tolerance=90.0,
        distance_radius=1.0,
    ),
}


# ── Angular map ────────────────────────────────────────────────────────────────

LAYER_LABELS: dict[int, str] = {
    0: "collective",  # shared priors
    1: "context",  # mood / consent / history
    2: "agentic",  # intent / rule-pack / governance
    3: "hierarchy",  # records → entities → relations → patterns
}


@dataclass
class EntityPoint:
    """
    Entity projected into layered polar space.

    The x-axis is G (grounding score, 0–1).
    The y-axis is score (dimension score, 0–1).
    The z-axis is layer (atlas stack depth, 0–3).

    Each layer draws its own narrow arc. Entities don't merge across layers —
    they form separate angular windows stacked vertically.

    Pythagorean radius r = √(G² + score²) measures distance from the origin.
    Polar angle θ = atan2(score, G) positions the entity on its layer's arc.
    """

    entity_id: str
    g: float
    score: float
    layer: int = 0

    @property
    def layer_label(self) -> str:
        return LAYER_LABELS.get(self.layer, f"layer-{self.layer}")

    @property
    def r(self) -> float:
        return math.hypot(self.g, self.score)

    @property
    def theta(self) -> float:
        return math.degrees(math.atan2(self.score, self.g))

    def distance_to(self, other: EntityPoint) -> float:
        """Pythagorean distance in (G, score) plane."""
        return math.hypot(self.g - other.g, self.score - other.score)

    def angular_distance_to(self, other: EntityPoint) -> float:
        return abs(self.theta - other.theta)


def sort_by_angle(points: list[EntityPoint]) -> list[EntityPoint]:
    """Sort entities by angular position θ ascending — narrow-to-wide sweep."""
    return sorted(points, key=lambda p: p.theta)


def cluster_by_radius(
    points: list[EntityPoint],
    radius: float,
) -> list[list[EntityPoint]]:
    """
    Group entities within Pythagorean radius.

    Triangle inequality ensures only entities that could form a valid triangular
    boundary (non-degenerate, non-collinear) are placed in the same cluster.
    """
    clusters: list[list[EntityPoint]] = []
    assigned: set[str] = set()

    for anchor in sort_by_angle(points):
        if anchor.entity_id in assigned:
            continue
        group = [anchor]
        assigned.add(anchor.entity_id)
        for candidate in points:
            if candidate.entity_id in assigned:
                continue
            if anchor.distance_to(candidate) <= radius:
                group.append(candidate)
                assigned.add(candidate.entity_id)
        clusters.append(group)

    return clusters


def validate_triangle_boundary(
    a: EntityPoint,
    b: EntityPoint,
    c: EntityPoint,
) -> bool:
    """
    Triangle inequality — structural boundary validity check.

    Three entity-points form a valid (non-degenerate) triangle iff each side
    is strictly less than the sum of the other two. A degenerate triangle
    (collinear entities) has no interior — it cannot bound a region.

        |AB| + |BC| > |AC|
        |AB| + |AC| > |BC|
        |BC| + |AC| > |AB|
    """
    ab = a.distance_to(b)
    bc = b.distance_to(c)
    ac = a.distance_to(c)
    return (ab + bc > ac) and (ab + ac > bc) and (bc + ac > ab)


def angular_sector(
    points: list[EntityPoint],
    centre_theta: float,
    tolerance: float,
    *,
    layer: int | None = None,
) -> list[EntityPoint]:
    """
    Return entities within ± tolerance degrees of a reference angle.
    Optionally filter to a single layer's arc.
    """
    return [p for p in points if abs(p.theta - centre_theta) <= tolerance and (layer is None or p.layer == layer)]


@dataclass(frozen=True)
class ArcSlice:
    """One narrow arc — a single layer's angular window with a description tail."""

    layer: int
    label: str
    points: list[EntityPoint]
    theta_min: float
    theta_max: float
    arc_width: float
    description: str


def arcs_per_layer(points: list[EntityPoint]) -> list[ArcSlice]:
    """
    Draw multiple narrow arcs — one per occupied layer.

    Each arc is a tight angular window containing only entities at that
    atlas depth. The description tail summarises the arc concisely:
    count, angular spread, and dominant entity.

    Returns arcs sorted by layer (collective → hierarchy).
    """
    by_layer: dict[int, list[EntityPoint]] = {}
    for p in points:
        by_layer.setdefault(p.layer, []).append(p)

    arcs: list[ArcSlice] = []
    for layer_idx in sorted(by_layer):
        layer_points = sort_by_angle(by_layer[layer_idx])
        thetas = [p.theta for p in layer_points]
        theta_min = min(thetas)
        theta_max = max(thetas)
        arc_width = theta_max - theta_min

        dominant = max(layer_points, key=lambda p: p.r)
        label = LAYER_LABELS.get(layer_idx, f"layer-{layer_idx}")
        desc = (
            f"{len(layer_points)} entities, {arc_width:.1f}° arc, dominant: {dominant.entity_id} (r={dominant.r:.3f})"
        )

        arcs.append(
            ArcSlice(
                layer=layer_idx,
                label=label,
                points=layer_points,
                theta_min=theta_min,
                theta_max=theta_max,
                arc_width=arc_width,
                description=desc,
            )
        )

    return arcs


# ── Notification ───────────────────────────────────────────────────────────────

DeliveryTarget = Literal["audit", "journal", "stdout"]


@dataclass
class Notification:
    """Delivery envelope produced when a Trigger fires."""

    trigger_id: str
    entity_id: str
    event: str
    g_at_fire: float
    theta_at_fire: float  # polar angle of the entity at fire time
    r_at_fire: float  # Pythagorean distance from origin at fire time
    cluster_size: int
    snapshot: dict | None  # angular map snapshot (None if preset disables)
    delivered_to: list[DeliveryTarget] = field(default_factory=list)
    fired_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def deliver(self, targets: list[DeliveryTarget]) -> None:
        for target in targets:
            if target == "stdout":
                print(
                    f"[TRIGGER {self.trigger_id[:8]}] {self.entity_id} "
                    f"G={self.g_at_fire:.3f} θ={self.theta_at_fire:.1f}° "
                    f"r={self.r_at_fire:.3f} cluster={self.cluster_size}"
                )
            elif target == "audit":
                try:
                    import structlog

                    structlog.get_logger().info(
                        "trigger_fired",
                        trigger_id=self.trigger_id,
                        entity_id=self.entity_id,
                        g=self.g_at_fire,
                        theta=round(self.theta_at_fire, 2),
                        cluster_size=self.cluster_size,
                        fired_at=self.fired_at,
                    )
                except ImportError:
                    pass
            # "journal" → pulse-server (future integration)
        self.delivered_to = list(targets)


# ── Trigger ────────────────────────────────────────────────────────────────────


@dataclass
class Trigger:
    """
    Geometric boundary trigger.

    Watches one entity. Fires when G crosses g_threshold and is above the
    aggression floor set by the preset. On fire, sorts all sibling entities
    by angular position θ, clusters them by Pythagorean radius, and snapshots
    the map if the preset requests it.
    """

    entity_id: str
    g_threshold: float
    score_axis: float  # y-coordinate in angular space
    preset: TriggerPreset = field(
        default_factory=lambda: PRESETS["watchman"],
    )
    delivery: list[DeliveryTarget] = field(default_factory=lambda: ["stdout"])
    trigger_id: str = field(default_factory=lambda: str(uuid4()))

    def evaluate(
        self,
        current_g: float,
        sibling_points: list[EntityPoint] | None = None,
    ) -> Notification | None:
        """
        Evaluate against current G. Returns Notification or None.
        Siblings are other EntityPoints in the same graph context.
        """
        floor = _AGGRESSION_FLOOR[self.preset.aggression]
        if current_g < floor or current_g < self.g_threshold:
            return None

        self_point = EntityPoint(self.entity_id, current_g, self.score_axis)
        siblings = sibling_points or []
        all_points = [self_point, *siblings]

        sorted_points = sort_by_angle(all_points)
        clusters = cluster_by_radius(all_points, self.preset.distance_radius)
        my_cluster = next(
            (c for c in clusters if any(p.entity_id == self.entity_id for p in c)),
            [self_point],
        )

        snapshot = None
        if self.preset.snapshot_on_fire:
            arcs = arcs_per_layer(all_points)
            snapshot = {
                "sorted_angular": [
                    {
                        "id": p.entity_id,
                        "theta": round(p.theta, 2),
                        "r": round(p.r, 4),
                        "g": p.g,
                        "layer": p.layer,
                    }
                    for p in sorted_points
                ],
                "arcs": [
                    {
                        "layer": arc.layer,
                        "label": arc.label,
                        "arc_width": round(arc.arc_width, 2),
                        "description": arc.description,
                    }
                    for arc in arcs
                ],
                "my_cluster": [p.entity_id for p in my_cluster],
                "preset": self.preset.name,
                "boundary_valid": (validate_triangle_boundary(*my_cluster[:3]) if len(my_cluster) >= 3 else None),
            }

        notification = Notification(
            trigger_id=self.trigger_id,
            entity_id=self.entity_id,
            event="g_threshold_crossed",
            g_at_fire=current_g,
            theta_at_fire=self_point.theta,
            r_at_fire=self_point.r,
            cluster_size=len(my_cluster),
            snapshot=snapshot,
        )
        notification.deliver(self.delivery)
        return notification


# ── TriggerEngine ──────────────────────────────────────────────────────────────


@dataclass
class TriggerEngine:
    """
    Wire point. Register triggers, evaluate against a G map, collect notifications.

    g_map = {entity_id: (G, dimension_score)}

    Each evaluation rebuilds the full angular map from the G map snapshot,
    so the sort order and clusters reflect the current entity landscape —
    not a cached view.
    """

    triggers: list[Trigger] = field(default_factory=list)

    def register(self, trigger: Trigger) -> None:
        self.triggers.append(trigger)

    def evaluate_all(
        self,
        g_map: dict[str, tuple[float, float]],
    ) -> list[Notification]:
        """
        Evaluate all registered triggers against a G map snapshot.
        Returns all notifications that fired.
        """
        all_points = [EntityPoint(eid, g, score) for eid, (g, score) in g_map.items()]

        fired: list[Notification] = []
        for trigger in self.triggers:
            g_val, _ = g_map.get(trigger.entity_id, (0.0, 0.0))
            siblings = [p for p in all_points if p.entity_id != trigger.entity_id]
            note = trigger.evaluate(g_val, siblings)
            if note:
                fired.append(note)

        return fired

    def angular_map(
        self,
        g_map: dict[str, tuple[float, float]],
    ) -> list[EntityPoint]:
        """Return all entities sorted by θ — the current angular view of the map."""
        return sort_by_angle([EntityPoint(eid, g, score) for eid, (g, score) in g_map.items()])
