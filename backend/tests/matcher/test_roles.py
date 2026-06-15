"""
Tests for matcher.roles (test strategy §4.4).

Coverage:
  - FR-6 validate_palette: size and sum constraints
  - FR-7 derive_roles: 30/15 thresholds; saturation tie-break; dual-primary
  - FR-8 all_primaries_qualify: one-pass / one-fail examples
  - FR-9 classify_secondary: neutral / in_scheme / echo / None branches
  - FR-10 minor harmlessness (Hypothesis property)
  - FR-11 minor_echo_families: positive echo; non-echo; neutral excluded
  - Hypothesis: totality over valid palettes
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.matcher.colour import Colour
from app.matcher.roles import (
    GarmentRoles,
    all_primaries_qualify,
    classify_secondary,
    derive_roles,
    minor_echo_families,
    validate_palette,
)
from tests.fixtures.palettes import (
    NEUTRAL_FAMILIES,
    CHROMATIC_FAMILIES,
    PRIMARY_THRESHOLD,
    SECONDARY_THRESHOLD,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _c(h: float, s: float, l: float, p: int) -> Colour:
    return Colour(h=h, s=s, l=l, proportion=p)


# A clearly chromatic colour (Red) and a clearly neutral (Grey)
_RED    = _c(  0.0, 80.0, 50.0, 0)
_GREY   = _c(  0.0,  0.0, 50.0, 0)
_BLUE   = _c(240.0, 70.0, 50.0, 0)
_GREEN  = _c(120.0, 60.0, 40.0, 0)


# ── FR-6 validate_palette ─────────────────────────────────────────────────────

class TestValidatePalette:
    def test_single_colour_full_proportion(self) -> None:
        validate_palette((_c(0, 0, 50, 100),))  # should not raise

    def test_four_colours_summing_to_100(self) -> None:
        validate_palette((
            _c(0, 80, 50, 40),
            _c(120, 60, 40, 30),
            _c(240, 70, 50, 20),
            _c(0, 0, 50, 10),
        ))

    def test_zero_colours_raises(self) -> None:
        with pytest.raises(ValueError, match="FR-6"):
            validate_palette(())

    def test_five_colours_raises(self) -> None:
        colours = tuple(_c(0, 0, 50, 20) for _ in range(5))
        with pytest.raises(ValueError, match="FR-6"):
            validate_palette(colours)

    def test_sum_not_100_raises(self) -> None:
        with pytest.raises(ValueError, match="FR-6"):
            validate_palette((_c(0, 80, 50, 50), _c(120, 60, 40, 49)))

    def test_sum_99_raises(self) -> None:
        with pytest.raises(ValueError, match="FR-6"):
            validate_palette((_c(0, 0, 50, 99),))

    def test_sum_101_raises(self) -> None:
        with pytest.raises(ValueError, match="FR-6"):
            validate_palette((_c(0, 0, 50, 100), _c(0, 0, 50, 1)))


# ── FR-7 derive_roles boundary tables ────────────────────────────────────────

class TestPrimaryThreshold:
    """Primary threshold is exactly PRIMARY_THRESHOLD (30)."""

    def test_proportion_at_threshold_is_primary(self) -> None:
        # 30% + something = 100; the 30% colour should be primary alongside the dominant
        dominant = _c(  0.0, 80.0, 50.0, 70)
        borderline = _c(120.0, 60.0, 40.0, 30)
        roles = derive_roles((dominant, borderline))
        assert borderline in roles.primaries

    def test_proportion_just_below_threshold_is_not_additional_primary(self) -> None:
        # dominant = 71, candidate = 29; 29 < 30 so candidate is secondary
        dominant = _c(  0.0, 80.0, 50.0, 71)
        candidate = _c(120.0, 60.0, 40.0, 29)
        roles = derive_roles((dominant, candidate))
        assert candidate in roles.secondaries
        assert candidate not in roles.primaries

    def test_dual_primary_when_two_colours_both_at_threshold(self) -> None:
        a = _c(  0.0, 80.0, 50.0, 50)
        b = _c(120.0, 60.0, 40.0, 50)
        roles = derive_roles((a, b))
        assert roles.is_dual_primary
        assert len(roles.primaries) == 2

    def test_single_primary_when_only_dominant_qualifies(self) -> None:
        # dominant = 25, others < 30; only dominant is primary
        dominant = _c(  0.0, 80.0, 50.0, 25)
        a = _c(120.0, 60.0, 40.0, 25)
        b = _c(240.0, 70.0, 50.0, 25)
        c = _c(  0.0,  0.0, 50.0, 25)
        roles = derive_roles((dominant, a, b, c))
        assert len(roles.primaries) == 1
        assert not roles.is_dual_primary


class TestSecondaryThreshold:
    """Secondary threshold is exactly SECONDARY_THRESHOLD (15)."""

    def test_proportion_at_threshold_is_secondary(self) -> None:
        dominant = _c(0.0, 80.0, 50.0, 85)
        borderline = _c(120.0, 60.0, 40.0, 15)
        roles = derive_roles((dominant, borderline))
        assert borderline in roles.secondaries

    def test_proportion_just_below_threshold_is_minor(self) -> None:
        dominant = _c(0.0, 80.0, 50.0, 86)
        candidate = _c(120.0, 60.0, 40.0, 14)
        roles = derive_roles((dominant, candidate))
        assert candidate in roles.minors
        assert candidate not in roles.secondaries

    def test_proportion_just_above_primary_threshold_is_primary(self) -> None:
        dominant = _c(0.0, 80.0, 50.0, 69)
        borderline = _c(120.0, 60.0, 40.0, 31)
        roles = derive_roles((dominant, borderline))
        assert borderline in roles.primaries


class TestSaturationTieBreak:
    """Ties in proportion are broken by higher saturation (FR-7)."""

    def test_higher_saturation_wins_when_proportion_equal(self) -> None:
        low_sat  = _c(0.0, 40.0, 50.0, 50)
        high_sat = _c(0.0, 80.0, 50.0, 50)
        roles = derive_roles((low_sat, high_sat))
        # Both are ≥ 30, so both are primary — but high_sat should be first
        assert roles.primaries[0] == high_sat

    def test_saturation_only_used_to_break_ties(self) -> None:
        high_prop = _c(0.0, 10.0, 50.0, 70)
        low_sat   = _c(0.0, 90.0, 50.0, 30)
        roles = derive_roles((high_prop, low_sat))
        # Both ≥ 30 → dual-primary; high_prop first (70 > 30)
        assert roles.primaries[0] == high_prop

    def test_proportions_sorted_descending_within_bucket(self) -> None:
        a = _c(0.0,   80.0, 50.0, 60)
        b = _c(120.0, 60.0, 40.0, 40)
        roles = derive_roles((b, a))  # given in reverse order
        assert roles.primaries[0].proportion >= roles.primaries[1].proportion


class TestRoleExhaustion:
    """Every colour must appear in exactly one bucket."""

    def test_all_colours_accounted_for(self) -> None:
        colours = (
            _c(  0.0, 80.0, 50.0, 40),  # primary
            _c(120.0, 60.0, 40.0, 35),  # primary (≥30)
            _c(240.0, 70.0, 50.0, 15),  # secondary
            _c(  0.0,  0.0, 50.0, 10),  # minor
        )
        roles = derive_roles(colours)
        all_in_roles = set(roles.primaries) | set(roles.secondaries) | set(roles.minors)
        assert all_in_roles == set(colours)
        total = sum(c.proportion for c in all_in_roles)
        assert total == 100


# ── FR-8 all_primaries_qualify ────────────────────────────────────────────────

class TestAllPrimariesQualify:
    """FR-8: dual-primary disqualifies when either primary fails."""

    def _qualify_if_red(self, c: Colour) -> bool:
        return c.h == 0.0

    def test_single_primary_passes(self) -> None:
        roles = derive_roles((_c(0.0, 80.0, 50.0, 100),))
        assert all_primaries_qualify(roles, self._qualify_if_red)

    def test_single_primary_fails(self) -> None:
        roles = derive_roles((_c(120.0, 60.0, 40.0, 100),))
        assert not all_primaries_qualify(roles, self._qualify_if_red)

    def test_dual_primary_both_pass(self) -> None:
        roles = derive_roles((_c(0.0, 80.0, 50.0, 50), _c(0.0, 40.0, 60.0, 50)))
        assert all_primaries_qualify(roles, self._qualify_if_red)

    def test_dual_primary_one_fails_disqualifies(self) -> None:
        roles = derive_roles((_c(0.0, 80.0, 50.0, 50), _c(120.0, 60.0, 40.0, 50)))
        assert not all_primaries_qualify(roles, self._qualify_if_red)


# ── FR-9 classify_secondary ───────────────────────────────────────────────────

class TestClassifySecondary:
    """FR-9: secondary classified as neutral / in_scheme / echo / None."""

    _SCHEME  = frozenset({"Red", "Teal"})
    _ANCHORS = frozenset({"Red", "Teal", "Blue"})

    def test_neutral_family_is_neutral(self) -> None:
        for name in NEUTRAL_FAMILIES:
            result = classify_secondary(name, self._SCHEME, self._ANCHORS)
            assert result == "neutral", f"Expected 'neutral' for {name}, got {result!r}"

    def test_in_scheme_family(self) -> None:
        assert classify_secondary("Red", self._SCHEME, self._ANCHORS) == "in_scheme"
        assert classify_secondary("Teal", self._SCHEME, self._ANCHORS) == "in_scheme"

    def test_echo_family_not_in_scheme_but_on_anchors(self) -> None:
        # Blue is on anchors but not in scheme; scheme check comes first
        assert classify_secondary("Blue", frozenset({"Red"}), self._ANCHORS) == "echo"

    def test_incompatible_returns_none(self) -> None:
        result = classify_secondary("Violet", frozenset({"Red"}), frozenset({"Red"}))
        assert result is None

    def test_scheme_checked_before_echo(self) -> None:
        # Red is both in scheme and on anchors; should return 'in_scheme', not 'echo'
        result = classify_secondary("Red", frozenset({"Red"}), frozenset({"Red"}))
        assert result == "in_scheme"

    def test_neutral_checked_before_scheme(self) -> None:
        # Grey forced into scheme and anchors — neutral check should win
        result = classify_secondary("Grey", frozenset({"Grey"}), frozenset({"Grey"}))
        assert result == "neutral"


# ── FR-10 minor harmlessness (Hypothesis) ────────────────────────────────────

_PROP = st.integers(min_value=1, max_value=97)


def _valid_palette(n: int, draw):
    """Draw n random Colour objects whose proportions sum to 100."""
    if n == 1:
        return (draw(st.builds(
            Colour,
            h=st.floats(0, 359.9, allow_nan=False, allow_infinity=False),
            s=st.floats(0, 100,   allow_nan=False, allow_infinity=False),
            l=st.floats(0, 100,   allow_nan=False, allow_infinity=False),
            proportion=st.just(100),
        )),)

    # n colours: pick n-1 proportions from [1, 100-n+1], last = 100 - sum
    parts: list[int] = []
    remaining = 100
    for i in range(n - 1):
        v = draw(st.integers(min_value=1, max_value=remaining - (n - 1 - i)))
        parts.append(v)
        remaining -= v
    parts.append(remaining)

    return tuple(
        draw(st.builds(
            Colour,
            h=st.floats(0, 359.9, allow_nan=False, allow_infinity=False),
            s=st.floats(0, 100,   allow_nan=False, allow_infinity=False),
            l=st.floats(0, 100,   allow_nan=False, allow_infinity=False),
            proportion=st.just(p),
        ))
        for p in parts
    )


@st.composite
def valid_palette(draw):
    n = draw(st.integers(min_value=1, max_value=4))
    return _valid_palette(n, draw)


@given(valid_palette())
@settings(max_examples=200)
def test_fr10_minors_never_disqualify(palette: tuple[Colour, ...]) -> None:
    """
    FR-10: removing minor colours from the palette cannot change whether a
    dummy qualifier passes — i.e. minors have no veto.

    We proxy this by asserting that role derivation always produces a
    GarmentRoles where minors is a subset of non-primaries and non-secondaries
    (i.e. minors are cleanly separated from the qualifying buckets).
    """
    roles = derive_roles(palette)
    minor_set = set(roles.minors)
    primary_set = set(roles.primaries)
    secondary_set = set(roles.secondaries)
    assert not minor_set & primary_set, "A minor colour appeared in primaries"
    assert not minor_set & secondary_set, "A minor colour appeared in secondaries"


@given(valid_palette())
@settings(max_examples=200)
def test_fr6_totality(palette: tuple[Colour, ...]) -> None:
    """derive_roles never raises on a valid FR-6 palette."""
    roles = derive_roles(palette)
    assert isinstance(roles, GarmentRoles)


@given(valid_palette())
@settings(max_examples=200)
def test_roles_partition_palette(palette: tuple[Colour, ...]) -> None:
    """Every colour in the palette appears in exactly one role bucket."""
    roles = derive_roles(palette)
    all_colours = list(roles.primaries) + list(roles.secondaries) + list(roles.minors)
    assert len(all_colours) == len(palette)
    # Proportion totals must be preserved
    assert sum(c.proportion for c in all_colours) == sum(c.proportion for c in palette)


@given(valid_palette())
@settings(max_examples=200)
def test_always_at_least_one_primary(palette: tuple[Colour, ...]) -> None:
    """Every palette has at least one primary (the dominant colour)."""
    roles = derive_roles(palette)
    assert len(roles.primaries) >= 1


# ── FR-11 minor_echo_families ─────────────────────────────────────────────────

class TestMinorEchoFamilies:
    """FR-11: minor-colour echoes accumulate the echo bonus."""

    def test_minor_chromatic_echo_found(self) -> None:
        # minor Red (h=0, s=80, l=50, p=10) echoes anchor's Red family
        colours = (
            _c(  0.0, 80.0, 50.0, 90),  # primary Red
            _c(  0.0, 80.0, 50.0, 10),  # minor Red
        )
        roles = derive_roles(colours)
        echoes = minor_echo_families(roles, frozenset({"Red"}))
        assert "Red" in echoes

    def test_minor_neutral_excluded_from_echoes(self) -> None:
        # minor Grey should never echo
        colours = (
            _c(  0.0, 80.0, 50.0, 90),  # primary
            _c(  0.0,  0.0, 50.0, 10),  # minor Grey
        )
        roles = derive_roles(colours)
        echoes = minor_echo_families(roles, frozenset({"Grey"}))
        assert not echoes

    def test_minor_chromatic_not_in_anchors_excluded(self) -> None:
        # minor Blue, anchors only have Red
        colours = (
            _c(  0.0, 80.0, 50.0, 90),  # primary Red
            _c(240.0, 70.0, 50.0, 10),  # minor Blue
        )
        roles = derive_roles(colours)
        echoes = minor_echo_families(roles, frozenset({"Red"}))
        assert "Blue" not in echoes

    def test_empty_anchors_yields_no_echoes(self) -> None:
        colours = (
            _c(  0.0, 80.0, 50.0, 90),
            _c(120.0, 60.0, 40.0, 10),
        )
        roles = derive_roles(colours)
        assert not minor_echo_families(roles, frozenset())

    def test_no_minors_yields_no_echoes(self) -> None:
        roles = derive_roles((_c(0.0, 80.0, 50.0, 100),))
        assert not minor_echo_families(roles, frozenset({"Red"}))
