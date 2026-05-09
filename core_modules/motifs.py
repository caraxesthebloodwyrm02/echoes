"""Creative motivation tokens (song titles / motifs).

Safe for debug banners, logging flourishes, or docs cross-references.
Do not use these as security-sensitive identifiers or env var names.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Pink Floyd — explicit graduation catalogue (titles only; no lyrics) ---
# 1) Echoes — platform namesake / long-form continuity
TRACK_ECHOES = "Echoes"

# 2) Shine On You Crazy Diamond — persistence, return, dedication
SHINE_ON_YOU_CRAZY_DIAMOND = "shine_on_you_crazy_diamond"

# 3) Welcome to the Machine — systems, corridors, MCP/tool halls (explicit reference URL)
WELCOME_TO_THE_MACHINE = "welcome_to_the_machine"
WELCOME_TO_THE_MACHINE_VIDEO_URL = "https://www.youtube.com/watch?v=fn1R-5p_j5c&list=RDfn1R-5p_j5c&start_radio=1"

# 4) High Hopes — arc resolution; pairs with Abrasive (sound ↔ cognition bridge)
HIGH_HOPES = "high_hopes"

# Additional catalogue tokens (legacy set)
ECHOES = "echoes"  # lowercase slug; see TRACK_ECHOES for display title
TIME = "time"
US_AND_THEM = "us_and_them"
WISH_YOU_WERE_HERE = "wish_you_were_here"
COMFORTABLY_NUMB = "comfortably_numb"
BRAIN_DAMAGE = "brain_damage"
ECLIPSE = "eclipse"

PLAYGROUND_TAG = "echoes_capability_matrix"


@dataclass(frozen=True)
class Abrasive:
    """Motif anchor for 'sound meets cognition' (High Hopes).

    Not used by EchoesAssistantV2 yet — reserved for EchoesAgentsV1 layering
    (e.g. multimodal resonance vs linguistic intent edge). See
    docs/audit/ECHOES_ASSISTANT_V2_TO_AGENTS_V1_SYMBOL_MAP.md (motivation layer).
    """

    motif: str = HIGH_HOPES
