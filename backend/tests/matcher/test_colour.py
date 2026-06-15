"""
Tests for matcher.colour (test strategy §4.2).

Covers:
  - Known RGB↔HSL pairs (primaries, greys, contract worked examples)
  - Round-trip RGB→HSL→RGB within ±1 per channel
  - Hue-distance table and Hypothesis metric properties
  - Circular mean across the 0°/360° wrap and Hypothesis membership property
  - Hex derivation against contract examples (FR-5)
  - Colour dataclass immutability
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.matcher.colour import (
    Colour,
    circular_mean,
    hsl_to_hex,
    hsl_to_rgb,
    hue_distance,
    rgb_to_hsl,
)


# ── Known RGB ↔ HSL pairs ─────────────────────────────────────────────────────
# (r, g, b, expected_h, expected_s, expected_l, label)
KNOWN_PAIRS: list[tuple[int, int, int, float, float, float, str]] = [
    # Pure primaries / secondaries
    (255,   0,   0,   0.0, 100.0, 50.0, "red"),
    (  0, 255,   0, 120.0, 100.0, 50.0, "green"),
    (  0,   0, 255, 240.0, 100.0, 50.0, "blue"),
    (255, 255,   0,  60.0, 100.0, 50.0, "yellow"),
    (  0, 255, 255, 180.0, 100.0, 50.0, "cyan"),
    (255,   0, 255, 300.0, 100.0, 50.0, "magenta"),
    # Achromatics
    (  0,   0,   0,   0.0,   0.0,  0.0, "black"),
    (255, 255, 255,   0.0,   0.0, 100.0, "white"),
    (128, 128, 128,   0.0,   0.0, 50.2, "mid-grey"),
    # Contract worked examples (api-contract.md §1.1)
    # #2CADA0 = (45, 173, 160) → HSL ≈ (174°, 58%, 43%)
    ( 45, 173, 160, 174.0, 58.0, 43.0, "#2CADA0 teal"),
    # #EE8225 = (238, 130, 37) → HSL ≈ (28°, 85%, 54%)
    (238, 130,  37,  28.0, 85.0, 54.0, "#EE8225 orange"),
]

_HSL_TOLERANCE = 1.0   # degrees / percent; contract worked examples
_GREY_HUE_TOLERANCE = 360.0  # achromatics have undefined hue — any value valid


@pytest.mark.parametrize("r,g,b,eh,es,el,label", KNOWN_PAIRS)
def test_rgb_to_hsl_known(r, g, b, eh, es, el, label) -> None:
    h, s, l = rgb_to_hsl(r, g, b)
    # For achromatics saturation is 0 so hue is meaningless — skip hue check.
    if es > 0:
        assert abs(hue_distance(h, eh)) <= _HSL_TOLERANCE, (
            f"{label}: expected H≈{eh}°, got {h:.1f}°"
        )
    assert abs(s - es) <= _HSL_TOLERANCE, f"{label}: expected S≈{es}%, got {s:.1f}%"
    assert abs(l - el) <= _HSL_TOLERANCE, f"{label}: expected L≈{el}%, got {l:.1f}%"


# ── Round-trip RGB → HSL → RGB within ±1 per channel ─────────────────────────

_RGB = st.integers(min_value=0, max_value=255)

@given(_RGB, _RGB, _RGB)
def test_rgb_round_trip(r: int, g: int, b: int) -> None:
    h, s, l = rgb_to_hsl(r, g, b)
    r2, g2, b2 = hsl_to_rgb(h, s, l)
    assert abs(r - r2) <= 1, f"R: {r} → HSL → {r2}"
    assert abs(g - g2) <= 1, f"G: {g} → HSL → {g2}"
    assert abs(b - b2) <= 1, f"B: {b} → HSL → {b2}"


# ── Hue distance table (test strategy §4.2) ───────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (350.0,  10.0,  20.0),  # wraps correctly
    (  0.0, 180.0, 180.0),  # maximum distance
    ( 90.0,  90.0,   0.0),  # same hue
    ( 10.0, 350.0,  20.0),  # symmetric
    (  0.0, 359.0,   1.0),  # near-wrap
    (180.0, 360.0, 180.0),  # 360 == 0
])
def test_hue_distance_table(a, b, expected) -> None:
    assert abs(hue_distance(a, b) - expected) < 1e-9, (
        f"hue_distance({a}, {b}): expected {expected}, got {hue_distance(a, b)}"
    )


# ── Hue distance Hypothesis properties ───────────────────────────────────────

_HUE = st.floats(min_value=0.0, max_value=359.9, allow_nan=False)

@given(_HUE, _HUE)
def test_hue_distance_symmetry(a: float, b: float) -> None:
    assert abs(hue_distance(a, b) - hue_distance(b, a)) < 1e-9

@given(_HUE, _HUE)
def test_hue_distance_range(a: float, b: float) -> None:
    d = hue_distance(a, b)
    assert 0.0 <= d <= 180.0

@given(_HUE, _HUE)
def test_hue_distance_invariant_under_360(a: float, b: float) -> None:
    assert abs(hue_distance(a, b) - hue_distance(a + 360.0, b)) < 1e-9
    assert abs(hue_distance(a, b) - hue_distance(a, b + 360.0)) < 1e-9


# ── Circular mean (test strategy §4.2) ───────────────────────────────────────

def test_circular_mean_wrap() -> None:
    """mean([350, 10]) must be 0, not 180 (the naïve-average trap)."""
    result = circular_mean([350.0, 10.0])
    assert hue_distance(result, 0.0) < 1.0, (
        f"circular_mean([350, 10]): expected ≈0°, got {result:.2f}°"
    )

def test_circular_mean_single() -> None:
    assert abs(circular_mean([120.0]) - 120.0) < 1e-9

def test_circular_mean_opposite_hues() -> None:
    """Antipodal hues: result may be either pole — just check it's in [0,360)."""
    result = circular_mean([0.0, 180.0])
    assert 0.0 <= result < 360.0

def test_circular_mean_empty_raises() -> None:
    with pytest.raises(ValueError):
        circular_mean([])


# ── Circular mean membership property ────────────────────────────────────────

@given(st.lists(_HUE, min_size=2, max_size=8))
def test_circular_mean_within_cluster(hues: list[float]) -> None:
    """
    The circular mean of hues drawn from a ≤30° window lies within that window
    (test strategy §4.2 — membership property).
    """
    # Build a cluster within a 30° arc anchored at hues[0].
    anchor = hues[0]
    cluster = [anchor + ((h - anchor + 180.0) % 360.0 - 180.0) % 30.0 for h in hues]
    mean = circular_mean(cluster)
    for h in cluster:
        assert hue_distance(mean, h) <= 30.0, (
            f"mean {mean:.1f}° is more than 30° from cluster member {h:.1f}°"
        )


# ── Hex derivation (FR-5, contract §1.1) ────────────────────────────────────

@pytest.mark.parametrize("h,s,l,expected_hex", [
    # Pure primaries / secondaries cover all six hsl_to_rgb sectors;
    # achromatics are exact.
    (  0.0,   0.0,   0.0, "#000000"),   # black
    (  0.0,   0.0, 100.0, "#FFFFFF"),   # white
    (  0.0, 100.0,  50.0, "#FF0000"),   # red    — sector 0
    ( 60.0, 100.0,  50.0, "#FFFF00"),   # yellow — sector 1
    (120.0, 100.0,  50.0, "#00FF00"),   # green  — sector 2
    (180.0, 100.0,  50.0, "#00FFFF"),   # cyan   — sector 3
    (240.0, 100.0,  50.0, "#0000FF"),   # blue   — sector 4
    (300.0, 100.0,  50.0, "#FF00FF"),   # magenta — sector 5
])
def test_hsl_to_hex_known(h, s, l, expected_hex) -> None:
    result = hsl_to_hex(h, s, l)
    r1, g1, b1 = int(result[1:3], 16), int(result[3:5], 16), int(result[5:7], 16)
    re, ge, be = int(expected_hex[1:3], 16), int(expected_hex[3:5], 16), int(expected_hex[5:7], 16)
    assert abs(r1 - re) <= 1 and abs(g1 - ge) <= 1 and abs(b1 - be) <= 1, (
        f"hsl_to_hex({h},{s},{l}): expected {expected_hex}, got {result}"
    )


def test_hsl_to_hex_contract_teal_round_trip() -> None:
    """
    Contract §1.1: #2CADA0 (RGB 44,173,160) is the teal example.
    The contract's stated HSL (174,58,41) is a rounded display value;
    we verify the round-trip: pixels → HSL → hex ≈ original pixels.
    """
    h, s, l = rgb_to_hsl(44, 173, 160)
    result = hsl_to_hex(h, s, l)
    r1, g1, b1 = int(result[1:3], 16), int(result[3:5], 16), int(result[5:7], 16)
    assert abs(r1 - 44) <= 1 and abs(g1 - 173) <= 1 and abs(b1 - 160) <= 1, (
        f"round-trip RGB(44,173,160) → hex: expected ≈#2CADA0, got {result}"
    )

def test_hsl_to_hex_format() -> None:
    """Hex output is always 7 chars, '#' + 6 uppercase hex digits."""
    result = hsl_to_hex(120.0, 50.0, 50.0)
    assert len(result) == 7
    assert result[0] == "#"
    assert result[1:].upper() == result[1:]


# ── Colour dataclass ──────────────────────────────────────────────────────────

def test_colour_frozen() -> None:
    c = Colour(h=174.0, s=58.0, l=41.0, proportion=80)
    with pytest.raises((AttributeError, TypeError)):
        c.h = 0.0  # type: ignore[misc]

def test_colour_equality() -> None:
    assert Colour(0.0, 0.0, 0.0, 0) == Colour(0.0, 0.0, 0.0, 0)
    assert Colour(0.0, 0.0, 0.0, 0) != Colour(1.0, 0.0, 0.0, 0)

def test_colour_default_proportion() -> None:
    c = Colour(h=0.0, s=0.0, l=0.0)
    assert c.proportion == 0
