"""Trigger System Verification Suite.

Tests geometric boundary triggers with G-graded notification delivery.
All fixtures derive from the 4 planted seeds. Edge cases via seed mutation.
Deterministic — no wall-clock dependency.
"""

from __future__ import annotations

import math

import pytest

from core_modules.trigger import (
    PRESETS,
    EntityPoint,
    Trigger,
    TriggerEngine,
    angular_sector,
    arcs_per_layer,
    cluster_by_radius,
    sort_by_angle,
    validate_triangle_boundary,
)

# ── Seed fixtures ──

# (G, score, layer)
SEEDS: dict[str, tuple[float, float, int]] = {
    "grounding-gate":    (1.0, 1.0, 2),   # agentic — governance predicate
    "struggle-point":    (1.0, 0.8, 3),   # hierarchy — connective node
    "token-bridge":      (0.8, 0.7, 3),   # hierarchy — signal mapping
    "scaffold-boundary": (0.6, 0.6, 2),   # agentic — test boundary
}


def _seed_points() -> list[EntityPoint]:
    return [EntityPoint(eid, g, s, layer) for eid, (g, s, layer) in SEEDS.items()]


def _seed_point(
    name: str,
    *,
    g: float | None = None,
    score: float | None = None,
    layer: int | None = None,
) -> EntityPoint:
    """Return a seed point, optionally with mutated G, score, or layer."""
    orig_g, orig_s, orig_l = SEEDS[name]
    return EntityPoint(
        name,
        g if g is not None else orig_g,
        score if score is not None else orig_s,
        layer if layer is not None else orig_l,
    )


def _seeds_g_map() -> dict[str, tuple[float, float]]:
    """G map for TriggerEngine (entity_id → (G, score))."""
    return {eid: (g, s) for eid, (g, s, _) in SEEDS.items()}


# ── EntityPoint geometry ──

class TestEntityPointGeometry:
    def test_r_pythagorean(self):
        """grounding-gate (1.0, 1.0) → r = sqrt(2) ≈ 1.4142."""
        p = _seed_point("grounding-gate")
        assert p.r == pytest.approx(math.sqrt(2), abs=1e-4)

    def test_theta_balanced(self):
        """grounding-gate (1.0, 1.0) → θ = 45° (equal G and score)."""
        p = _seed_point("grounding-gate")
        assert p.theta == pytest.approx(45.0, abs=1e-4)

    def test_theta_pure_grounding(self):
        """scaffold-boundary mutated to score=0 → θ = 0° (pure grounding axis)."""
        p = _seed_point("scaffold-boundary", score=0.0)
        assert p.theta == pytest.approx(0.0, abs=1e-4)

    def test_theta_pure_score(self):
        """grounding-gate mutated to G=0 → θ = 90° (pure score axis)."""
        p = _seed_point("grounding-gate", g=0.0)
        assert p.theta == pytest.approx(90.0, abs=1e-4)

    def test_distance_to(self):
        """Distance between grounding-gate (1,1) and scaffold-boundary (0.6,0.6) = sqrt(0.32)."""
        a = _seed_point("grounding-gate")
        b = _seed_point("scaffold-boundary")
        expected = math.hypot(1.0 - 0.6, 1.0 - 0.6)
        assert a.distance_to(b) == pytest.approx(expected, abs=1e-4)

    def test_angular_distance(self):
        """struggle-point θ ≈ 38.66°, grounding-gate θ = 45° → angular dist ≈ 6.34°."""
        a = _seed_point("struggle-point")
        b = _seed_point("grounding-gate")
        assert a.angular_distance_to(b) == pytest.approx(45.0 - math.degrees(math.atan2(0.8, 1.0)), abs=0.1)


# ── Angular sort ──

class TestAngularSort:
    def test_sort_order(self):
        """4 seeds sorted by θ: struggle-point < token-bridge < grounding-gate = scaffold-boundary."""
        sorted_pts = sort_by_angle(_seed_points())
        ids = [p.entity_id for p in sorted_pts]
        assert ids[0] == "struggle-point"        # θ ≈ 38.66°
        assert ids[1] == "token-bridge"           # θ ≈ 41.19°
        # grounding-gate and scaffold-boundary both at θ = 45°, order is stable
        assert set(ids[2:]) == {"grounding-gate", "scaffold-boundary"}

    def test_empty_list(self):
        """Empty input → empty output."""
        assert sort_by_angle([]) == []


# ── Cluster by radius ──

class TestClusterByRadius:
    def test_tight_radius_isolates(self):
        """radius=0.05 → each seed is its own cluster (all pairwise distances > 0.05)."""
        clusters = cluster_by_radius(_seed_points(), radius=0.05)
        assert len(clusters) == 4
        for cluster in clusters:
            assert len(cluster) == 1

    def test_wide_radius_merges(self):
        """radius=1.0 → all seeds in one cluster (max distance < 1.0)."""
        clusters = cluster_by_radius(_seed_points(), radius=1.0)
        assert len(clusters) == 1
        assert len(clusters[0]) == 4

    def test_medium_radius_partial(self):
        """radius=0.25 → some merge, some don't. Total entities still = 4."""
        clusters = cluster_by_radius(_seed_points(), radius=0.25)
        total = sum(len(c) for c in clusters)
        assert total == 4
        assert 1 < len(clusters) < 4  # neither all isolated nor all merged


# ── Triangle boundary ──

class TestTriangleBoundary:
    def test_valid_triangle(self):
        """grounding-gate + struggle-point + token-bridge form a valid triangle."""
        a = _seed_point("grounding-gate")
        b = _seed_point("struggle-point")
        c = _seed_point("token-bridge")
        assert validate_triangle_boundary(a, b, c) is True

    def test_degenerate_collinear(self):
        """Three seeds mutated to same G → collinear on G=0.5 line → degenerate."""
        a = EntityPoint("a", 0.5, 0.0)
        b = EntityPoint("b", 0.5, 0.5)
        c = EntityPoint("c", 0.5, 1.0)
        assert validate_triangle_boundary(a, b, c) is False

    def test_collinear_seeds_rejected(self):
        """scaffold-boundary + struggle-point + token-bridge are collinear (slope=0.5) → invalid."""
        a = _seed_point("scaffold-boundary")
        b = _seed_point("struggle-point")
        c = _seed_point("token-bridge")
        assert validate_triangle_boundary(a, b, c) is False

    def test_non_collinear_seeds_accepted(self):
        """grounding-gate + struggle-point + token-bridge break collinearity → valid triangle."""
        a = _seed_point("grounding-gate")
        b = _seed_point("struggle-point")
        c = _seed_point("token-bridge")
        assert validate_triangle_boundary(a, b, c) is True


# ── Angular sector ──

class TestAngularSector:
    def test_sector_captures_nearby(self):
        """centre=45°, tolerance=5° → captures grounding-gate (45°) and scaffold-boundary (45°)."""
        captured = angular_sector(_seed_points(), centre_theta=45.0, tolerance=5.0)
        ids = {p.entity_id for p in captured}
        assert "grounding-gate" in ids
        assert "scaffold-boundary" in ids

    def test_sector_excludes_far(self):
        """centre=0°, tolerance=3° → no seeds near 0° (all are ≥ 38°)."""
        captured = angular_sector(_seed_points(), centre_theta=0.0, tolerance=3.0)
        assert len(captured) == 0

    def test_sector_filters_by_layer(self):
        """centre=45°, tolerance=10°, layer=2 → only agentic seeds."""
        captured = angular_sector(_seed_points(), centre_theta=45.0, tolerance=10.0, layer=2)
        ids = {p.entity_id for p in captured}
        assert ids == {"grounding-gate", "scaffold-boundary"}


# ── Arcs per layer ──

class TestArcsPerLayer:
    def test_two_arcs_from_seeds(self):
        """4 seeds across 2 layers → 2 arcs (agentic + hierarchy)."""
        arcs = arcs_per_layer(_seed_points())
        assert len(arcs) == 2
        labels = [a.label for a in arcs]
        assert "agentic" in labels
        assert "hierarchy" in labels

    def test_arc_width_narrow(self):
        """Each arc is narrow — agentic arc ≈ 6.3°, hierarchy arc ≈ 2.5°."""
        arcs = arcs_per_layer(_seed_points())
        for arc in arcs:
            assert arc.arc_width < 10.0  # all arcs are narrow

    def test_arc_description_tail(self):
        """Each arc carries a concise description with count, width, and dominant entity."""
        arcs = arcs_per_layer(_seed_points())
        for arc in arcs:
            assert "entities" in arc.description
            assert "arc" in arc.description
            assert "dominant" in arc.description

    def test_agentic_arc_entities(self):
        """Agentic arc (layer 2) contains grounding-gate and scaffold-boundary."""
        arcs = arcs_per_layer(_seed_points())
        agentic = next(a for a in arcs if a.layer == 2)
        ids = {p.entity_id for p in agentic.points}
        assert ids == {"grounding-gate", "scaffold-boundary"}

    def test_hierarchy_arc_entities(self):
        """Hierarchy arc (layer 3) contains struggle-point and token-bridge."""
        arcs = arcs_per_layer(_seed_points())
        hierarchy = next(a for a in arcs if a.layer == 3)
        ids = {p.entity_id for p in hierarchy.points}
        assert ids == {"struggle-point", "token-bridge"}

    def test_single_entity_arc_zero_width(self):
        """A layer with one entity produces a 0° arc."""
        single = [EntityPoint("solo", 0.5, 0.5, layer=1)]
        arcs = arcs_per_layer(single)
        assert len(arcs) == 1
        assert arcs[0].arc_width == 0.0


# ── Trigger firing ──

class TestTriggerFiring:
    def test_fires_above_threshold(self):
        """G=1.0, threshold=0.9, watchman preset → fires."""
        trigger = Trigger(
            entity_id="grounding-gate",
            g_threshold=0.9,
            score_axis=1.0,
            preset=PRESETS["watchman"],
            delivery=[],  # suppress stdout
        )
        note = trigger.evaluate(1.0)
        assert note is not None
        assert note.g_at_fire == 1.0
        assert note.event == "g_threshold_crossed"

    def test_silent_below_threshold(self):
        """G=0.3, threshold=0.5 → None."""
        trigger = Trigger(
            entity_id="scaffold-boundary",
            g_threshold=0.5,
            score_axis=0.6,
            preset=PRESETS["explorer"],
            delivery=[],
        )
        note = trigger.evaluate(0.3)
        assert note is None

    def test_aggression_floor_blocks(self):
        """TRACE preset floor is 1.0 → G=0.9 doesn't fire even if threshold=0.5."""
        trigger = Trigger(
            entity_id="token-bridge",
            g_threshold=0.5,
            score_axis=0.7,
            preset=PRESETS["sentinel"],
            delivery=[],
        )
        note = trigger.evaluate(0.9)
        assert note is None


# ── Trigger snapshot ──

class TestTriggerSnapshot:
    def test_snapshot_present_when_enabled(self):
        """watchman preset → snapshot dict with sorted_angular, my_cluster, preset, boundary_valid."""
        trigger = Trigger(
            entity_id="grounding-gate",
            g_threshold=0.5,
            score_axis=1.0,
            preset=PRESETS["watchman"],
            delivery=[],
        )
        siblings = [_seed_point("struggle-point"), _seed_point("token-bridge")]
        note = trigger.evaluate(1.0, siblings)
        assert note is not None
        assert note.snapshot is not None
        assert "sorted_angular" in note.snapshot
        assert "my_cluster" in note.snapshot
        assert note.snapshot["preset"] == "watchman"

    def test_snapshot_absent_when_disabled(self):
        """explorer preset → snapshot is None."""
        trigger = Trigger(
            entity_id="scaffold-boundary",
            g_threshold=0.4,
            score_axis=0.6,
            preset=PRESETS["explorer"],
            delivery=[],
        )
        note = trigger.evaluate(0.6)
        assert note is not None
        assert note.snapshot is None


# ── TriggerEngine ──

class TestTriggerEngine:
    def test_evaluate_all_with_seeds(self):
        """4 registered triggers, G map = 4 seeds → all 4 fire."""
        engine = TriggerEngine()
        engine.register(Trigger("grounding-gate",    g_threshold=0.9, score_axis=1.0, preset=PRESETS["watchman"], delivery=[]))
        engine.register(Trigger("struggle-point",    g_threshold=0.9, score_axis=0.8, preset=PRESETS["watchman"], delivery=[]))
        engine.register(Trigger("token-bridge",      g_threshold=0.7, score_axis=0.7, preset=PRESETS["watchman"], delivery=[]))
        engine.register(Trigger("scaffold-boundary", g_threshold=0.5, score_axis=0.6, preset=PRESETS["explorer"], delivery=[]))
        fired = engine.evaluate_all(_seeds_g_map())
        assert len(fired) == 4

    def test_angular_map_sorted(self):
        """engine.angular_map() returns entities sorted by θ ascending."""
        engine = TriggerEngine()
        angular = engine.angular_map(_seeds_g_map())
        thetas = [p.theta for p in angular]
        assert thetas == sorted(thetas)
        assert angular[0].entity_id == "struggle-point"

    def test_missing_entity_not_fired(self):
        """Entity not in g_map → G defaults to 0.0 → trigger doesn't fire."""
        engine = TriggerEngine()
        engine.register(Trigger("phantom", g_threshold=0.5, score_axis=0.5, preset=PRESETS["watchman"], delivery=[]))
        fired = engine.evaluate_all(_seeds_g_map())  # "phantom" not in SEEDS
        assert len(fired) == 0
