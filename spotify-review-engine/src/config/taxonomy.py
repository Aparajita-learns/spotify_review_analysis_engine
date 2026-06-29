"""
src/config/taxonomy.py
----------------------
Full taxonomy of themes and user segments used for classification.

Structure:
  THEMES        — dict[theme_code → ThemeDefinition]
  USER_SEGMENTS — dict[segment_code → SegmentDefinition]
  KEYWORD_MAP   — dict[theme_code → list[keywords]] for rule-based classification
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ThemeDefinition:
    code: str
    name: str
    group: str          # discovery_frictions | behavioral_intent | repetition_triggers | unmet_needs
    description: str
    keywords: List[str] = field(default_factory=list)


@dataclass
class SegmentDefinition:
    code: str
    name: str
    description: str
    signal_phrases: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# THEMES
# ──────────────────────────────────────────────────────────────────────────────

THEMES: Dict[str, ThemeDefinition] = {

    # ── Discovery Frictions ──────────────────────────────────────────────────

    "repetitive_recommendations": ThemeDefinition(
        code="repetitive_recommendations",
        name="Repetitive Recommendations",
        group="discovery_frictions",
        description="Algorithm keeps recommending the same artists or tracks the user already knows.",
        keywords=[
            "same songs", "same music", "same artists", "always recommends",
            "keeps playing", "only plays", "repetitive", "repeat recommendations",
            "same playlist", "nothing new", "same tracks", "always the same",
        ],
    ),

    "weak_novelty": ThemeDefinition(
        code="weak_novelty",
        name="Weak Novelty",
        group="discovery_frictions",
        description="Recommendations do not introduce genuinely new or unfamiliar content.",
        keywords=[
            "no new music", "nothing new", "already know", "already heard",
            "familiar", "known songs", "not discovering", "same old",
        ],
    ),

    "playlist_overdependence": ThemeDefinition(
        code="playlist_overdependence",
        name="Playlist Overdependence",
        group="discovery_frictions",
        description="User relies entirely on curated playlists rather than organic discovery.",
        keywords=[
            "rely on playlist", "only playlists", "playlist dependent", "discover weekly",
            "release radar", "daily mixes", "editorial playlist",
        ],
    ),

    # ── Behavioral Intent ────────────────────────────────────────────────────

    "passive_discovery": ThemeDefinition(
        code="passive_discovery",
        name="Passive Discovery",
        group="behavioral_intent",
        description="User wants music discovered for them without active effort.",
        keywords=[
            "just plays", "let it play", "autoplay", "shuffle", "radio",
            "without effort", "automatically", "background",
        ],
    ),

    "active_exploration": ThemeDefinition(
        code="active_exploration",
        name="Active Exploration",
        group="behavioral_intent",
        description="User actively seeks out new genres, artists, or sounds.",
        keywords=[
            "looking for", "searching for new", "exploring", "want to find",
            "trying new", "want to discover", "browsing",
        ],
    ),

    "social_discovery": ThemeDefinition(
        code="social_discovery",
        name="Social Discovery",
        group="behavioral_intent",
        description="User discovers music through friends, social sharing, or community.",
        keywords=[
            "friend recommended", "friend shared", "saw on instagram", "tiktok",
            "friend's playlist", "concert", "someone told me", "social",
        ],
    ),

    "genre_expansion": ThemeDefinition(
        code="genre_expansion",
        name="Genre Expansion",
        group="behavioral_intent",
        description="User wants to branch out into adjacent or unfamiliar genres.",
        keywords=[
            "new genre", "different genre", "expand taste", "genre exploration",
            "try different", "outside my comfort zone", "diverse music",
        ],
    ),

    # ── Repetition Triggers ──────────────────────────────────────────────────

    "comfort_listening": ThemeDefinition(
        code="comfort_listening",
        name="Comfort Listening",
        group="repetition_triggers",
        description="User deliberately returns to familiar music for comfort.",
        keywords=[
            "comfort", "familiar", "safe", "go-to", "always go back",
            "soothing", "reassuring", "old favorites",
        ],
    ),

    "habit_loop": ThemeDefinition(
        code="habit_loop",
        name="Habit Loop",
        group="repetition_triggers",
        description="Listening to the same content has become an unconscious habit.",
        keywords=[
            "habit", "automatically", "without thinking", "muscle memory",
            "default", "always open", "every day same",
        ],
    ),

    # ── Unmet Needs ──────────────────────────────────────────────────────────

    "novelty_control": ThemeDefinition(
        code="novelty_control",
        name="Novelty Control",
        group="unmet_needs",
        description="User wants a dial or setting to control how adventurous recommendations are.",
        keywords=[
            "control", "slider", "setting", "how adventurous", "novelty",
            "dial up", "more new music", "less familiar", "customize",
        ],
    ),

    "reset_recommendations": ThemeDefinition(
        code="reset_recommendations",
        name="Reset Recommendations",
        group="unmet_needs",
        description="User wants to clear or reset their listening history and algorithm state.",
        keywords=[
            "reset", "fresh start", "clear history", "start over",
            "erase listening", "algorithm reset", "clean slate",
        ],
    ),
}


# ──────────────────────────────────────────────────────────────────────────────
# USER SEGMENTS
# ──────────────────────────────────────────────────────────────────────────────

USER_SEGMENTS: Dict[str, SegmentDefinition] = {

    "passive_familiar_listener": SegmentDefinition(
        code="passive_familiar_listener",
        name="Passive Familiar Listener",
        description="Listens passively to familiar music. Low motivation to actively discover.",
        signal_phrases=[
            "just let it play", "don't care what plays", "shuffle my liked",
            "comfortable with", "don't want to search", "play anything",
        ],
    ),

    "playlist_reliant_listener": SegmentDefinition(
        code="playlist_reliant_listener",
        name="Playlist-Reliant Listener",
        description="Relies almost exclusively on curated playlists. Does not actively search.",
        signal_phrases=[
            "discover weekly", "daily mix", "release radar", "always use playlists",
            "spotify made playlist", "editorial", "curated for me",
        ],
    ),

    "active_explorer": SegmentDefinition(
        code="active_explorer",
        name="Active Explorer",
        description="Actively seeks new music, genres, and artists using search and radio.",
        signal_phrases=[
            "love finding new", "always looking for", "exploring genres",
            "follow new artists", "want to discover", "try new music",
        ],
    ),

    "mood_context_listener": SegmentDefinition(
        code="mood_context_listener",
        name="Mood / Context Listener",
        description="Selects music based on mood, activity, or context.",
        signal_phrases=[
            "for working out", "study music", "when i'm sad", "chill playlist",
            "focus mode", "workout songs", "morning music", "driving",
        ],
    ),

    "social_discovery_listener": SegmentDefinition(
        code="social_discovery_listener",
        name="Social Discovery Listener",
        description="Discovers music primarily through friends, social sharing, or social media.",
        signal_phrases=[
            "friend told me", "saw on tiktok", "instagram reel", "friend shared",
            "concert discovery", "someone showed me", "group chat",
        ],
    ),
}


# ──────────────────────────────────────────────────────────────────────────────
# Convenience helpers
# ──────────────────────────────────────────────────────────────────────────────

THEME_GROUPS = list({t.group for t in THEMES.values()})
THEME_CODES = list(THEMES.keys())
SEGMENT_CODES = list(USER_SEGMENTS.keys())


def get_theme(code: str) -> ThemeDefinition:
    """Return a ThemeDefinition by theme_code, or raise KeyError."""
    return THEMES[code]


def get_segment(code: str) -> SegmentDefinition:
    """Return a SegmentDefinition by segment_code, or raise KeyError."""
    return USER_SEGMENTS[code]


def themes_by_group(group: str) -> List[ThemeDefinition]:
    """Return all themes belonging to a given group."""
    return [t for t in THEMES.values() if t.group == group]
