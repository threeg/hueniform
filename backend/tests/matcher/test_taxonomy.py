"""
Tests for matcher.taxonomy (test strategy §4.3).

Coverage:
  - FR-2 neutral rules, boundary value at edge ±0.1 for every comparison
  - Navy↔Denim ordering (first-match, FR-2)
  - Brown/Beige lightness gap (contractual)
  - FR-4 half-open arcs — all twelve boundaries
  - Canonical values self-classify (contract §2.2)
  - Hypothesis: totality, determinism, neutral XOR chromatic, arc membership (FR-1)
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.matcher.taxonomy import (
    FAMILIES,
    canonical_hsl,
    classify,
    family,
    is_neutral,
)
from tests.fixtures.palettes import (
    ALL_FAMILIES,
    CANONICAL,
    CHROMATIC_FAMILIES,
    NEUTRAL_FAMILIES,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

# Use clearly chromatic HSL for arc-boundary rows: high S, mid L.
_ARC_S = 80.0
_ARC_L = 50.0


# ── FR-2 Neutral boundary-value tables ───────────────────────────────────────

class TestBlackBoundary:
    """Black: L < 12 (rule 1)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # FR-2 rule 1 — L < 12
        (  0.0, 50.0, 11.9, "Black"),   # just inside
        (  0.0, 50.0, 12.0, "Red"),     # at threshold → not Black; chromatic Red
        (  0.0,  0.0, 11.9, "Black"),   # achromatic, still Black
        (180.0, 80.0,  0.0, "Black"),   # L=0 → Black regardless of H/S
    ])
    def test_fr2_black(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 1 (Black): classify({h},{s},{l}) expected {expected}"
        )


class TestWhiteBoundary:
    """White: L > 92 and S < 20 (rule 2)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # Both conditions met
        (  0.0, 19.9, 92.1, "White"),   # just inside both
        # S at boundary (S < 20 required)
        (  0.0, 20.0, 92.1, "Red"),     # S = 20 → not White; S ≥ 10 so not Grey → Red
        # L at boundary (L > 92 required)
        # S=19.9 ≥ GREY_S_MAX=10 so not Grey; no other neutral matches H=0 → Red
        (  0.0, 19.9, 92.0, "Red"),     # L = 92 not > 92 → not White; → Red
    ])
    def test_fr2_white(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 2 (White): classify({h},{s},{l}) expected {expected}"
        )

    def test_fr2_white_exact(self) -> None:
        assert classify(0.0, 5.0, 96.0) == "White"

    def test_fr2_white_l_boundary(self) -> None:
        # L=92.0 is not > 92 → not White; S=5 < 10, L=92 in [12,92] → Grey
        assert classify(0.0, 5.0, 92.0) == "Grey"

    def test_fr2_white_l_just_inside(self) -> None:
        # L=92.1 > 92, S=5 < 20 → White
        assert classify(0.0, 5.0, 92.1) == "White"


class TestGreyBoundary:
    """Grey: S < 10 and 12 ≤ L ≤ 92 (rule 3)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # S boundary
        (0.0, 9.9,  50.0, "Grey"),   # S just inside
        (0.0, 10.0, 50.0, "Red"),    # S at threshold → not Grey; chromatic Red
        # L lower boundary
        (0.0, 5.0,  12.0, "Grey"),   # L at lower bound (inclusive)
        (0.0, 5.0,  11.9, "Black"),  # L just below lower → Black (rule 1)
        # L upper boundary — S=5 < 20 so White fires first at L>92
        (0.0, 5.0,  92.0, "Grey"),   # L at upper bound (inclusive)
        (0.0, 5.0,  92.1, "White"),  # L just above upper → White (rule 2, S<20)
    ])
    def test_fr2_grey(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 3 (Grey): classify({h},{s},{l}) expected {expected}"
        )


class TestNavyBoundary:
    """Navy: 200 ≤ H ≤ 260, S ≥ 10, L < 25 (rule 4)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # H lower boundary
        (200.0, 20.0, 18.0, "Navy"),   # H at lower bound
        (199.9, 20.0, 18.0, "Azure"),  # H just below → Azure (195–225°)
        # H upper boundary
        (260.0, 20.0, 18.0, "Navy"),   # H at upper bound
        (260.1, 20.0, 18.0, "Violet"), # H just above → Violet (255–285°)
        # L boundary (L < 25 required)
        (230.0, 20.0, 24.9, "Navy"),   # L just inside
        (230.0, 20.0, 25.0, "Denim"),  # L at threshold → Denim (rule 5, FR-2 ordering)
        # S boundary (S ≥ 10 required)
        (230.0, 10.0, 18.0, "Navy"),   # S at lower bound
        (230.0,  9.9, 18.0, "Grey"),   # S just below → Grey (S<10, L in [12,92])
    ])
    def test_fr2_navy(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 4 (Navy): classify({h},{s},{l}) expected {expected}"
        )


class TestNavyDenimOrdering:
    """FR-2 first-match ordering: Navy before Denim."""

    def test_fr2_ordering_navy_wins_at_l_below_25(self) -> None:
        # (220, 30, 24.9): Navy (L<25), even though H/S also satisfy Denim
        assert classify(220.0, 30.0, 24.9) == "Navy"

    def test_fr2_ordering_denim_at_l_25(self) -> None:
        # (220, 30, 25.0): not Navy (L≥25), falls through to Denim
        assert classify(220.0, 30.0, 25.0) == "Denim"


class TestDenimBoundary:
    """Denim: 200 ≤ H ≤ 250, 10 ≤ S < 50, 25 ≤ L ≤ 65 (rule 5)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # S upper boundary (S < 50 required)
        (220.0, 49.9, 45.0, "Denim"),  # S just inside
        (220.0, 50.0, 45.0, "Azure"),  # S at threshold → not Denim; H=220 → Azure (195–225°)
        # H upper boundary (H ≤ 250 required)
        (250.0, 30.0, 45.0, "Denim"),  # H at upper bound
        (250.1, 30.0, 45.0, "Blue"),   # H just above → Blue (225–255°)
        # L boundaries
        (220.0, 30.0, 25.0, "Denim"),  # L at lower bound (inclusive)
        (220.0, 30.0, 65.0, "Denim"),  # L at upper bound (inclusive)
        (220.0, 30.0, 65.1, "Azure"),  # L just above → H=220 → Azure (195–225°)
    ])
    def test_fr2_denim(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 5 (Denim): classify({h},{s},{l}) expected {expected}"
        )


class TestBrownBoundary:
    """Brown: 15 ≤ H ≤ 50, 10 ≤ S ≤ 70, 15 ≤ L < 45 (rule 6)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # L upper boundary (L < 45 required)
        (30.0, 40.0, 44.9, "Brown"),    # L just inside
        (30.0, 40.0, 45.0, "Orange"),   # L at threshold → not Brown; chromatic Orange
        # L lower boundary (BROWN_L_LOW=15; Black requires L<12)
        (30.0, 40.0, 15.0, "Brown"),    # L at lower bound (inclusive)
        (30.0, 40.0, 14.9, "Orange"),   # L just below Brown (14.9≥12 so not Black; → Orange)
        # H boundaries
        (15.0, 40.0, 30.0, "Brown"),    # H at lower bound
        (14.9, 40.0, 30.0, "Red"),      # H just below → Red (345–15° arc)
        (50.0, 40.0, 30.0, "Brown"),    # H at upper bound
        (50.1, 40.0, 30.0, "Yellow"),   # H just above → Yellow (45–75°)
    ])
    def test_fr2_brown(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 6 (Brown): classify({h},{s},{l}) expected {expected}"
        )

    def test_fr2_brown_beige_gap_contractual(self) -> None:
        """The 45–60 L gap between Brown and Beige/Tan is contractual behaviour."""
        # L=44.9 → Brown; L=45.0 → chromatic Orange; L=60.0 → Beige/Tan
        assert classify(30.0, 40.0, 44.9) == "Brown"
        assert classify(30.0, 40.0, 45.0) == "Orange"   # the gap
        assert classify(30.0, 30.0, 60.0) == "Beige/Tan"


class TestBeigeBoundary:
    """Beige/Tan: 20 ≤ H ≤ 60, 10 ≤ S ≤ 45, 60 ≤ L ≤ 88 (rule 7)."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # L boundaries
        (35.0, 30.0, 60.0,  "Beige/Tan"),  # L at lower bound
        (35.0, 30.0, 88.0,  "Beige/Tan"),  # L at upper bound
        (35.0, 30.0, 59.9,  "Orange"),      # L just below → chromatic Orange
        # L=88.1 exceeds Beige/Tan ceiling (L ≤ 88) and meets Cream (L > 88)
        (35.0, 15.0, 88.1,  "Cream"),       # L just above Beige upper → Cream (rule 8)
        # H boundaries
        (20.0, 30.0, 72.0,  "Beige/Tan"),  # H at lower bound
        # H=19.9 is in Orange arc [15,45) — Red arc is [345,15), not [0,15)
        (19.9, 30.0, 72.0,  "Orange"),      # H just below Beige lower → Orange arc
        (60.0, 30.0, 72.0,  "Beige/Tan"),  # H at upper bound
        (60.1, 30.0, 72.0,  "Yellow"),      # H just above → Yellow arc
        # S boundaries
        (35.0, 10.0, 72.0,  "Beige/Tan"),  # S at lower bound
        (35.0, 45.0, 72.0,  "Beige/Tan"),  # S at upper bound
        (35.0, 45.1, 72.0,  "Orange"),      # S just above → chromatic Orange
    ])
    def test_fr2_beige(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 7 (Beige/Tan): classify({h},{s},{l}) expected {expected}"
        )


class TestCreamBoundary:
    """Cream: 20 ≤ H ≤ 70, 10 ≤ S ≤ 45, L > 88 (rule 8); White takes priority at L > 92, S < 20."""

    @pytest.mark.parametrize("h,s,l,expected", [
        # canonical and worked example (ticket)
        (45.0, 25.0, 90.0,  "Cream"),       # canonical
        (52.0, 28.0, 90.0,  "Cream"),       # ecru/white-jeans example (≈ H52, S28, L90)
        # L boundary — Beige/Tan hands off at L=88
        (45.0, 25.0, 88.1,  "Cream"),       # L just above threshold
        (45.0, 25.0, 88.0,  "Beige/Tan"),   # L at threshold → Beige/Tan (L ≤ 88)
        # H lower boundary (Cream shares H_LOW=20 with Beige/Tan)
        (20.0, 25.0, 90.0,  "Cream"),       # H at lower bound
        (19.9, 25.0, 90.0,  "Orange"),      # H just below → Orange arc [15, 45)
        # H upper boundary — Cream extends to 70°, Beige/Tan only to 60°
        (70.0, 25.0, 90.0,  "Cream"),       # H at upper bound
        (70.1, 25.0, 90.0,  "Yellow"),      # H just above → Yellow arc [45, 75)
        (65.0, 25.0, 90.0,  "Cream"),       # H in (60, 70] — above Beige/Tan ceiling
        # S boundaries
        (45.0, 10.0, 90.0,  "Cream"),       # S at lower bound
        (45.0, 45.0, 90.0,  "Cream"),       # S at upper bound
        (45.0, 45.1, 90.0,  "Yellow"),      # S just above → chromatic Yellow
        (45.0,  9.9, 90.0,  "Grey"),        # S just below 10 → Grey (S < 10, 12 ≤ L ≤ 92)
        # White takes priority when L > 92 and S < 20 (rule 2 before rule 8)
        (45.0, 15.0, 93.0,  "White"),       # White before Cream
    ])
    def test_fr2_cream(self, h, s, l, expected) -> None:
        assert classify(h, s, l) == expected, (
            f"FR-2 rule 8 (Cream): classify({h},{s},{l}) expected {expected}"
        )


# ── FR-4 chromatic arc boundaries (all twelve) ───────────────────────────────

class TestChromaticArcBoundaries:
    """
    Every boundary between adjacent chromatic families.
    FR-4: boundary value belongs to the arc that starts at it.
    Uses S=80, L=50 to avoid neutral rules.
    """

    @pytest.mark.parametrize("h,expected", [
        # H=15° boundary — Orange starts here
        (15.0, "Orange"),
        (14.9, "Red"),
        # H=45° — Yellow starts here
        (45.0, "Yellow"),
        (44.9, "Orange"),
        # H=75° — Chartreuse starts here
        (75.0, "Chartreuse"),
        (74.9, "Yellow"),
        # H=105° — Green starts here
        (105.0, "Green"),
        (104.9, "Chartreuse"),
        # H=135° — Mint starts here
        (135.0, "Mint"),
        (134.9, "Green"),
        # H=165° — Teal starts here
        (165.0, "Teal"),
        (164.9, "Mint"),
        # H=195° — Azure starts here
        (195.0, "Azure"),
        (194.9, "Teal"),
        # H=225° — Blue starts here
        (225.0, "Blue"),
        (224.9, "Azure"),
        # H=255° — Violet starts here
        (255.0, "Violet"),
        (254.9, "Blue"),
        # H=285° — Magenta starts here
        (285.0, "Magenta"),
        (284.9, "Violet"),
        # H=315° — Pink starts here
        (315.0, "Pink"),
        (314.9, "Magenta"),
        # H=345° — Red starts here (wraps)
        (345.0, "Red"),
        (344.9, "Pink"),
        # H=0° is inside Red arc
        (  0.0, "Red"),
    ])
    def test_fr4_arc_boundary(self, h: float, expected: str) -> None:
        result = classify(h, _ARC_S, _ARC_L)
        assert result == expected, (
            f"FR-4 arc boundary: classify({h},{_ARC_S},{_ARC_L}) "
            f"expected {expected}, got {result}"
        )


# ── Canonical self-classification (contract §2.2) ────────────────────────────

@pytest.mark.parametrize("family_name", ALL_FAMILIES)
def test_canonical_classifies_into_own_family(family_name: str) -> None:
    """Each family's canonical HSL must classify into its own family (FR-1, contract §2.2)."""
    h, s, l = CANONICAL[family_name]
    result = classify(h, s, l)
    assert result == family_name, (
        f"Canonical for '{family_name}' ({h},{s},{l}) classified as '{result}'"
    )


# ── FAMILIES registry checks ──────────────────────────────────────────────────

def test_families_count() -> None:
    assert len(FAMILIES) == 20

def test_neutral_chromatic_distinction() -> None:
    neutral_names = {f.name for f in FAMILIES if f.is_neutral}
    chromatic_names = {f.name for f in FAMILIES if not f.is_neutral}
    assert neutral_names == set(NEUTRAL_FAMILIES)
    assert chromatic_names == set(CHROMATIC_FAMILIES)

def test_chromatics_have_arc_data() -> None:
    for f in FAMILIES:
        if not f.is_neutral:
            assert f.representative_hue is not None, f"{f.name} missing representative_hue"
            assert f.hue_arc is not None, f"{f.name} missing hue_arc"

def test_neutrals_have_no_arc_data() -> None:
    for f in FAMILIES:
        if f.is_neutral:
            assert f.representative_hue is None, f"{f.name} should have no representative_hue"
            assert f.hue_arc is None, f"{f.name} should have no hue_arc"


# ── is_neutral / canonical_hsl helpers ───────────────────────────────────────

@pytest.mark.parametrize("name", NEUTRAL_FAMILIES)
def test_is_neutral_returns_true_for_neutrals(name: str) -> None:
    assert is_neutral(name) is True

@pytest.mark.parametrize("name", CHROMATIC_FAMILIES)
def test_is_neutral_returns_false_for_chromatics(name: str) -> None:
    assert is_neutral(name) is False

@pytest.mark.parametrize("name", ALL_FAMILIES)
def test_canonical_hsl_matches_registry(name: str) -> None:
    """canonical_hsl() must agree with the FAMILIES registry (contract §2.2)."""
    h, s, l = canonical_hsl(name)
    expected = family(name).canonical
    assert (h, s, l) == expected, (
        f"canonical_hsl('{name}') returned {(h,s,l)}, registry has {expected}"
    )


# ── Hypothesis properties (FR-1) ─────────────────────────────────────────────

_H = st.floats(min_value=0.0, max_value=359.9, allow_nan=False, allow_infinity=False)
_S = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
_L = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)


@given(_H, _S, _L)
def test_fr1_totality(h: float, s: float, l: float) -> None:
    """FR-1: classification always returns exactly one of the twenty families."""
    result = classify(h, s, l)
    assert result in ALL_FAMILIES, f"classify({h},{s},{l}) returned unknown family '{result}'"


@given(_H, _S, _L)
def test_fr1_determinism(h: float, s: float, l: float) -> None:
    """FR-1: same input always yields same family."""
    assert classify(h, s, l) == classify(h, s, l)


@given(_H, _S, _L)
def test_fr1_neutral_xor_chromatic(h: float, s: float, l: float) -> None:
    """FR-1 / FR-3: result is neutral XOR chromatic, never both, never neither."""
    name = classify(h, s, l)
    in_neutral = name in set(NEUTRAL_FAMILIES)
    in_chromatic = name in set(CHROMATIC_FAMILIES)
    assert in_neutral ^ in_chromatic, (
        f"'{name}' is in both or neither neutral/chromatic lists"
    )


@given(_H, _S, _L)
def test_fr1_chromatic_arc_membership(h: float, s: float, l: float) -> None:
    """
    FR-1 / FR-4: if the result is chromatic, the input hue must lie within
    that family's declared hue_arc.
    """
    name = classify(h, s, l)
    f = family(name)
    if f.is_neutral:
        return  # neutrals have no arc to check
    assert f.hue_arc is not None
    start, end = f.hue_arc
    if start > end:
        # Wrapping arc (Red)
        assert h >= start or h < end, (
            f"classify({h},{s},{l})='{name}' but {h}° not in [{start},{end})"
        )
    else:
        assert start <= h < end, (
            f"classify({h},{s},{l})='{name}' but {h}° not in [{start},{end})"
        )
