"""Tests for core_modules.motifs — motivation tokens and Abrasive anchor."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core_modules.motifs import (
    BRAIN_DAMAGE,
    COMFORTABLY_NUMB,
    ECHOES,
    ECLIPSE,
    HIGH_HOPES,
    PLAYGROUND_TAG,
    SHINE_ON_YOU_CRAZY_DIAMOND,
    TIME,
    TRACK_ECHOES,
    US_AND_THEM,
    WELCOME_TO_THE_MACHINE,
    WELCOME_TO_THE_MACHINE_VIDEO_URL,
    WISH_YOU_WERE_HERE,
    Abrasive,
)


def test_track_echoes_display_vs_slug() -> None:
    assert TRACK_ECHOES == "Echoes"
    assert ECHOES == "echoes"


def test_graduation_catalogue_tokens() -> None:
    assert SHINE_ON_YOU_CRAZY_DIAMOND == "shine_on_you_crazy_diamond"
    assert WELCOME_TO_THE_MACHINE == "welcome_to_the_machine"
    assert HIGH_HOPES == "high_hopes"


def test_welcome_to_the_machine_video_url_stable() -> None:
    assert "fn1R-5p_j5c" in WELCOME_TO_THE_MACHINE_VIDEO_URL
    assert WELCOME_TO_THE_MACHINE_VIDEO_URL.startswith("https://www.youtube.com/watch?v=")


def test_playground_tag() -> None:
    assert PLAYGROUND_TAG == "echoes_capability_matrix"


def test_legacy_tokens_unchanged() -> None:
    assert TIME == "time"
    assert US_AND_THEM == "us_and_them"
    assert WISH_YOU_WERE_HERE == "wish_you_were_here"
    assert COMFORTABLY_NUMB == "comfortably_numb"
    assert BRAIN_DAMAGE == "brain_damage"
    assert ECLIPSE == "eclipse"


def test_abrasive_defaults_to_high_hopes() -> None:
    assert Abrasive().motif == HIGH_HOPES


def test_abrasive_custom_motif() -> None:
    assert Abrasive(motif="custom").motif == "custom"


def test_abrasive_is_frozen() -> None:
    a = Abrasive()
    with pytest.raises(FrozenInstanceError):
        a.motif = "x"  # type: ignore[misc]
