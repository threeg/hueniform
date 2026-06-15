"""
Colour family taxonomy (FR-1–FR-5, requirements §2).

``classify(h, s, l)`` maps any valid HSL value to exactly one of the nineteen
family names, deterministically (FR-1).  Rules are evaluated in this order:

  1. Neutral rules in the FR-2 table order (first match wins).
  2. Chromatic arc whose half-open boundary contains the hue (FR-4).

Neutral families carry no hue for harmony evaluation (FR-3); the
``is_neutral`` helper exposes this distinction.

Standard library only (NFR-9).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.matcher import constants as C


# ── Family data type ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Family:
    """
    Descriptor for one colour family.

    ``representative_hue`` and ``hue_arc`` are present only on chromatic
    families (contract §2.2).  ``canonical`` is the HSL used as the stored
    value when the user adds a colour by family alone (FR-29, contract §2.2).
    """
    name: str
    is_neutral: bool
    canonical: tuple[float, float, float]          # (h, s, l)
    representative_hue: float | None = None        # chromatics only
    hue_arc: tuple[float, float] | None = None     # chromatics only; [start, end)


# ── Family registry ───────────────────────────────────────────────────────────
# Neutrals are listed in FR-2 evaluation order; chromatics in hue order.

FAMILIES: list[Family] = [
    # ── Neutrals (FR-2 order) ────────────────────────────────────────────────
    Family("Black",     True,  (  0.0,   0.0,  6.0)),
    Family("White",     True,  (  0.0,   0.0, 96.0)),
    Family("Grey",      True,  (  0.0,   0.0, 50.0)),
    Family("Navy",      True,  (230.0,  40.0, 18.0)),
    Family("Denim",     True,  (215.0,  30.0, 45.0)),
    Family("Brown",     True,  ( 25.0,  40.0, 30.0)),
    Family("Beige/Tan", True,  ( 35.0,  30.0, 72.0)),
    # ── Chromatics (hue order) ───────────────────────────────────────────────
    Family("Red",        False, (  0.0, 80.0, 50.0), representative_hue=  0.0, hue_arc=(345.0,  15.0)),
    Family("Orange",     False, ( 30.0, 90.0, 55.0), representative_hue= 30.0, hue_arc=( 15.0,  45.0)),
    Family("Yellow",     False, ( 60.0, 90.0, 50.0), representative_hue= 60.0, hue_arc=( 45.0,  75.0)),
    Family("Chartreuse", False, ( 90.0, 70.0, 40.0), representative_hue= 90.0, hue_arc=( 75.0, 105.0)),
    Family("Green",      False, (120.0, 60.0, 40.0), representative_hue=120.0, hue_arc=(105.0, 135.0)),
    Family("Mint",       False, (150.0, 60.0, 45.0), representative_hue=150.0, hue_arc=(135.0, 165.0)),
    Family("Teal",       False, (180.0, 70.0, 50.0), representative_hue=180.0, hue_arc=(165.0, 195.0)),
    Family("Azure",      False, (210.0, 70.0, 50.0), representative_hue=210.0, hue_arc=(195.0, 225.0)),
    Family("Blue",       False, (240.0, 70.0, 50.0), representative_hue=240.0, hue_arc=(225.0, 255.0)),
    Family("Violet",     False, (270.0, 60.0, 45.0), representative_hue=270.0, hue_arc=(255.0, 285.0)),
    Family("Magenta",    False, (300.0, 70.0, 45.0), representative_hue=300.0, hue_arc=(285.0, 315.0)),
    Family("Pink",       False, (330.0, 70.0, 65.0), representative_hue=330.0, hue_arc=(315.0, 345.0)),
]

_FAMILY_MAP: dict[str, Family] = {f.name: f for f in FAMILIES}
_ALL_NAMES: frozenset[str] = frozenset(_FAMILY_MAP)


# ── Public helpers ────────────────────────────────────────────────────────────

def family(name: str) -> Family:
    """Return the ``Family`` descriptor for *name*; raises ``KeyError`` if unknown."""
    return _FAMILY_MAP[name]


def is_neutral(name: str) -> bool:
    """Return True if *name* is a neutral family (FR-3)."""
    return _FAMILY_MAP[name].is_neutral


def canonical_hsl(name: str) -> tuple[float, float, float]:
    """Return the canonical (h, s, l) for the named family (contract §2.2)."""
    return _FAMILY_MAP[name].canonical


# ── Classification (FR-1, FR-2, FR-4) ────────────────────────────────────────

# Chromatic family names indexed by arc position.
# Arc index 0 = Red [345°, 15°); each step is 30° clockwise.
# Formula: arc_idx = int((h - 345) % 360 / 30) — derived from Red's arc start.
_CHROMATIC_NAMES: list[str] = [
    "Red", "Orange", "Yellow", "Chartreuse",
    "Green", "Mint", "Teal", "Azure",
    "Blue", "Violet", "Magenta", "Pink",
]


def classify(h: float, s: float, l: float) -> str:
    """
    Return the family name for the given HSL colour (FR-1).

    Neutral rules are evaluated first in FR-2 order; the chromatic arc
    containing the hue is the fallback.  Every valid HSL input matches
    exactly one family.
    """
    # 1. Black — L < BLACK_L_MAX (FR-2 rule 1)
    if l < C.BLACK_L_MAX:
        return "Black"

    # 2. White — L > WHITE_L_MIN and S < WHITE_S_MAX (FR-2 rule 2)
    if l > C.WHITE_L_MIN and s < C.WHITE_S_MAX:
        return "White"

    # 3. Grey — S < GREY_S_MAX and GREY_L_MIN ≤ L ≤ GREY_L_MAX (FR-2 rule 3)
    if s < C.GREY_S_MAX and C.GREY_L_MIN <= l <= C.GREY_L_MAX:
        return "Grey"

    # 4. Navy — NAVY_H_LOW ≤ H ≤ NAVY_H_HIGH, S ≥ NAVY_S_MIN, L < NAVY_L_MAX
    if C.NAVY_H_LOW <= h <= C.NAVY_H_HIGH and s >= C.NAVY_S_MIN and l < C.NAVY_L_MAX:
        return "Navy"

    # 5. Denim — DENIM_H_LOW ≤ H ≤ DENIM_H_HIGH, DENIM_S_LOW ≤ S < DENIM_S_HIGH,
    #            DENIM_L_LOW ≤ L ≤ DENIM_L_HIGH
    if (C.DENIM_H_LOW <= h <= C.DENIM_H_HIGH
            and C.DENIM_S_LOW <= s < C.DENIM_S_HIGH
            and C.DENIM_L_LOW <= l <= C.DENIM_L_HIGH):
        return "Denim"

    # 6. Brown — BROWN_H_LOW ≤ H ≤ BROWN_H_HIGH, BROWN_S_LOW ≤ S ≤ BROWN_S_HIGH,
    #            BROWN_L_LOW ≤ L < BROWN_L_HIGH
    if (C.BROWN_H_LOW <= h <= C.BROWN_H_HIGH
            and C.BROWN_S_LOW <= s <= C.BROWN_S_HIGH
            and C.BROWN_L_LOW <= l < C.BROWN_L_HIGH):
        return "Brown"

    # 7. Beige/Tan — BEIGE_H_LOW ≤ H ≤ BEIGE_H_HIGH, BEIGE_S_LOW ≤ S ≤ BEIGE_S_HIGH,
    #               BEIGE_L_LOW ≤ L ≤ BEIGE_L_HIGH
    if (C.BEIGE_H_LOW <= h <= C.BEIGE_H_HIGH
            and C.BEIGE_S_LOW <= s <= C.BEIGE_S_HIGH
            and C.BEIGE_L_LOW <= l <= C.BEIGE_L_HIGH):
        return "Beige/Tan"

    # 8. Chromatic arc (FR-4: half-open boundaries; boundary belongs to starting arc).
    # Red's arc starts at 345°; offset by that, then every 30° is one arc index.
    return _CHROMATIC_NAMES[int((h - 345.0) % 360.0 // C.CHROMATIC_ARC) % 12]
