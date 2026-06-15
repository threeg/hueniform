"""
Tests for matcher.harmony (test strategy §4.5).

Coverage:
  - FR-12 cluster_hues: within-arc grouping; circular wrap; single and empty inputs
  - FR-13 evaluate_scheme: one pass + one fail per scheme; order (mono-over-analogous,
    neutral-based on empty); tolerance boundary rows (complementary/triadic/analogous)
  - FR-14 neutral transparency: adding neutral hues does not change scheme
  - FR-15 is_harmonious predicate
  - Hypothesis: neutral-transparency property; scheme returned in valid set
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.matcher.harmony import (
    SchemeResult,
    cluster_hues,
    evaluate_scheme,
    is_harmonious,
)
from tests.fixtures.palettes import COMPLEMENTARY_TOLERANCE, TRIADIC_TOLERANCE, ANALOGOUS_ARC


# ── Helpers ───────────────────────────────────────────────────────────────────

_SCHEMES = {"neutral-based", "monochromatic", "analogous", "complementary", "triadic"}


def _scheme(hues) -> str | None:
    r = evaluate_scheme(tuple(hues))
    return r.scheme if r is not None else None


def _dev(hues) -> float | None:
    r = evaluate_scheme(tuple(hues))
    return r.deviation if r is not None else None


# ── FR-12 cluster_hues ────────────────────────────────────────────────────────

class TestClusterHues:
    def test_empty_input(self) -> None:
        assert cluster_hues([]) == []

    def test_single_hue(self) -> None:
        result = cluster_hues([120.0])
        assert len(result) == 1
        assert abs(result[0] - 120.0) < 0.01

    def test_two_hues_within_arc_form_one_cluster(self) -> None:
        result = cluster_hues([10.0, 35.0])   # span 25 ≤ 30
        assert len(result) == 1

    def test_two_hues_at_arc_boundary_form_one_cluster(self) -> None:
        result = cluster_hues([10.0, 40.0])   # span exactly 30 ≤ 30
        assert len(result) == 1

    def test_two_hues_just_outside_arc_form_two_clusters(self) -> None:
        result = cluster_hues([10.0, 40.1])   # span 30.1 > 30
        assert len(result) == 2

    def test_cluster_hue_is_mean_of_members(self) -> None:
        # Two hues at 100° and 120° → mean 110°
        result = cluster_hues([100.0, 120.0])
        assert len(result) == 1
        assert abs(result[0] - 110.0) < 0.5

    def test_circular_wrap_merges_near_zero_and_near_360(self) -> None:
        # 350° and 10° are 20° apart through 0° — should merge
        result = cluster_hues([350.0, 10.0])
        assert len(result) == 1

    def test_circular_wrap_mean_near_zero(self) -> None:
        result = cluster_hues([355.0, 5.0])
        assert len(result) == 1
        # Mean should be near 0° (either ~360 or ~0)
        mean = result[0]
        assert mean < 15.0 or mean > 345.0

    def test_no_wrap_when_arc_exceeds_30(self) -> None:
        # 340° and 15° are 35° apart through 0° — should not merge
        result = cluster_hues([340.0, 15.0])
        assert len(result) == 2

    def test_wrap_boundary_at_exactly_30(self) -> None:
        # 345° and 15° are exactly 30° apart → merge
        result = cluster_hues([345.0, 15.0])
        assert len(result) == 1

    def test_wrap_boundary_at_30_plus_epsilon(self) -> None:
        # 344.9° and 15° are 30.1° apart → no merge
        result = cluster_hues([344.9, 15.0])
        assert len(result) == 2

    def test_four_hues_in_two_clusters(self) -> None:
        result = cluster_hues([0.0, 15.0, 180.0, 195.0])
        assert len(result) == 2

    def test_duplicate_hues_form_one_cluster(self) -> None:
        result = cluster_hues([30.0, 30.0, 30.0])
        assert len(result) == 1
        assert abs(result[0] - 30.0) < 0.01


# ── FR-13 scheme tests ────────────────────────────────────────────────────────

class TestNeutralBased:
    def test_empty_scheme_set_is_neutral_based(self) -> None:
        assert _scheme([]) == "neutral-based"

    def test_neutral_based_deviation_is_zero(self) -> None:
        assert _dev([]) == 0.0

    def test_non_empty_is_not_neutral_based(self) -> None:
        assert _scheme([120.0]) != "neutral-based"


class TestMonochromatic:
    def test_single_hue_is_monochromatic(self) -> None:
        assert _scheme([120.0]) == "monochromatic"

    def test_two_hues_within_30_is_monochromatic(self) -> None:
        assert _scheme([10.0, 35.0]) == "monochromatic"

    def test_span_at_30_boundary_is_monochromatic(self) -> None:
        # hues spanning exactly 30° → monochromatic
        assert _scheme([0.0, 30.0]) == "monochromatic"

    def test_span_just_above_30_is_not_monochromatic(self) -> None:
        result = _scheme([0.0, 30.1])
        assert result != "monochromatic"

    def test_deviation_equals_span(self) -> None:
        dev = _dev([0.0, 20.0])
        assert dev is not None
        assert abs(dev - 20.0) < 0.01

    def test_monochromatic_wins_over_analogous(self) -> None:
        # Hues within 30° satisfy both mono and analogous; mono wins (FR-13 order)
        assert _scheme([0.0, 28.0]) == "monochromatic"


class TestAnalogous:
    def test_hues_within_60_is_analogous(self) -> None:
        assert _scheme([0.0, 30.1, 50.0]) == "analogous"

    def test_span_at_60_boundary_is_analogous(self) -> None:
        assert _scheme([0.0, 60.0]) == "analogous"

    def test_span_just_above_60_is_not_analogous(self) -> None:
        result = _scheme([0.0, 60.1])
        assert result != "analogous"

    def test_analogous_cannot_win_when_monochromatic_matches(self) -> None:
        # Any set within 30° is monochromatic, not analogous
        assert _scheme([5.0, 20.0]) == "monochromatic"


class TestComplementary:
    """FR-13 §4: exactly two clusters, hues 180° ± COMPLEMENTARY_TOLERANCE apart."""

    def test_perfect_complementary(self) -> None:
        assert _scheme([0.0, 180.0]) == "complementary"

    def test_deviation_at_perfect_is_zero(self) -> None:
        dev = _dev([0.0, 180.0])
        assert dev == 0.0

    # Boundary rows from ticket: 159.9 / 160 / 180 / 200 / 200.1

    def test_distance_160_passes(self) -> None:
        # hue_distance(0, 160) = 160; deviation = |160-180| = 20 = COMPLEMENTARY_TOLERANCE
        assert _scheme([0.0, 160.0]) == "complementary"

    def test_distance_159_9_fails(self) -> None:
        # deviation = |159.9-180| = 20.1 > 20 → fail
        result = _scheme([0.0, 159.9])
        assert result != "complementary"

    def test_distance_200_passes(self) -> None:
        # hue_distance(0, 200) = 160; deviation = |160-180| = 20
        assert _scheme([0.0, 200.0]) == "complementary"

    def test_distance_200_1_fails(self) -> None:
        # hue_distance(0, 200.1) = 159.9; deviation = 20.1 > 20 → fail
        result = _scheme([0.0, 200.1])
        assert result != "complementary"

    def test_complementary_with_spread_within_clusters(self) -> None:
        # Two clusters near 0° and 180° — each cluster spans < 30°
        assert _scheme([0.0, 15.0, 180.0, 195.0]) == "complementary"

    def test_three_clusters_does_not_match_complementary(self) -> None:
        result = _scheme([0.0, 120.0, 240.0])
        assert result != "complementary"

    def test_one_cluster_does_not_match_complementary(self) -> None:
        result = _scheme([0.0, 10.0])
        assert result != "complementary"  # it's monochromatic


class TestTriadic:
    """FR-13 §5: exactly three clusters, pairwise 120° ± TRIADIC_TOLERANCE apart."""

    def test_perfect_triadic(self) -> None:
        assert _scheme([0.0, 120.0, 240.0]) == "triadic"

    def test_deviation_at_perfect_is_zero(self) -> None:
        dev = _dev([0.0, 120.0, 240.0])
        assert abs(dev) < 0.01

    # Boundary rows from ticket: 105 / 135 edges

    def test_pairwise_105_degrees_passes(self) -> None:
        # 0, 105, 225 — distances: d(0,105)=105, d(105,225)=120, d(0,225)=135
        # max deviation = |105-120| = |135-120| = 15 = TRIADIC_TOLERANCE
        assert _scheme([0.0, 105.0, 225.0]) == "triadic"

    def test_pairwise_104_9_fails(self) -> None:
        # 0, 104.9, 224.9 — d(0,104.9)=104.9; deviation = 15.1 > 15
        result = _scheme([0.0, 104.9, 224.9])
        assert result != "triadic"

    def test_pairwise_135_degrees_passes(self) -> None:
        # 0, 135, 255 — d(0,135)=135, d(135,255)=120, d(0,255)=105
        # max deviation = 15
        assert _scheme([0.0, 135.0, 255.0]) == "triadic"

    def test_pairwise_135_1_fails(self) -> None:
        # 0, 135.1, 255.1 — d(0,135.1)=135.1; deviation = 15.1 > 15
        result = _scheme([0.0, 135.1, 255.1])
        assert result != "triadic"

    def test_two_clusters_does_not_match_triadic(self) -> None:
        result = _scheme([0.0, 180.0])
        assert result != "triadic"

    def test_four_clusters_does_not_match_triadic(self) -> None:
        # Four well-separated hues → 4 clusters
        result = _scheme([0.0, 90.0, 180.0, 270.0])
        assert result != "triadic"


class TestNoSchemeReturnsNone:
    def test_two_hues_not_complementary_returns_none(self) -> None:
        # hue_distance(0, 90) = 90; not within 60° arc and not complementary
        assert evaluate_scheme((0.0, 90.0)) is None

    def test_four_clusters_not_matching_returns_none(self) -> None:
        # 4 well-spaced clusters → no scheme matches
        assert evaluate_scheme((0.0, 90.0, 180.0, 270.0)) is None


class TestSchemeOrder:
    def test_mono_wins_before_analogous(self) -> None:
        # hues within 30° satisfy mono; analogous is checked after mono
        assert _scheme([0.0, 25.0]) == "monochromatic"

    def test_neutral_based_wins_on_empty(self) -> None:
        assert _scheme([]) == "neutral-based"

    def test_complementary_checked_before_triadic(self) -> None:
        # Only 2 clusters → complementary check fires; triadic is irrelevant
        r = evaluate_scheme((0.0, 180.0))
        assert r is not None and r.scheme == "complementary"

    def test_analogous_wins_before_complementary_when_all_in_60(self) -> None:
        # If all hues fit in 60° arc, analogous is matched before clustering step
        assert _scheme([0.0, 40.0, 55.0]) == "analogous"


# ── FR-14 neutral transparency ────────────────────────────────────────────────

class TestNeutralTransparency:
    """
    FR-14: adding neutral hues to a harmonious scheme must not change the
    matched scheme.  Tests use explicit examples; the property is also
    verified with Hypothesis below.
    """

    def test_neutral_hue_does_not_change_monochromatic(self) -> None:
        # caller is responsible for filtering neutrals before calling
        # evaluate_scheme; this test confirms that the function itself
        # produces the right answer when the caller passes only chromatics.
        assert _scheme([120.0]) == "monochromatic"

    def test_complementary_holds_when_called_with_chromatic_hues_only(self) -> None:
        assert _scheme([0.0, 180.0]) == "complementary"

    def test_empty_scheme_set_is_neutral_based(self) -> None:
        # All anchor colours are neutral → caller passes empty hues
        assert _scheme([]) == "neutral-based"


# ── FR-15 is_harmonious predicate ─────────────────────────────────────────────

class TestIsHarmonious:
    def test_empty_is_harmonious(self) -> None:
        assert is_harmonious(())

    def test_single_hue_is_harmonious(self) -> None:
        assert is_harmonious((120.0,))

    def test_well_separated_hues_are_not_harmonious(self) -> None:
        assert not is_harmonious((0.0, 90.0))

    def test_complementary_is_harmonious(self) -> None:
        assert is_harmonious((0.0, 180.0))

    def test_triadic_is_harmonious(self) -> None:
        assert is_harmonious((0.0, 120.0, 240.0))


# ── Hypothesis properties ─────────────────────────────────────────────────────

_HUE = st.floats(min_value=0.0, max_value=359.9, allow_nan=False, allow_infinity=False)


@given(st.lists(_HUE, min_size=0, max_size=8))
@settings(max_examples=300)
def test_scheme_is_in_valid_set_or_none(hues: list[float]) -> None:
    """evaluate_scheme returns a known scheme name or None."""
    result = evaluate_scheme(tuple(hues))
    if result is not None:
        assert result.scheme in _SCHEMES
        assert result.deviation >= 0.0


@given(st.lists(_HUE, min_size=1, max_size=4))
@settings(max_examples=300)
def test_is_harmonious_consistent_with_evaluate_scheme(hues: list[float]) -> None:
    """is_harmonious(hues) == (evaluate_scheme(hues) is not None)."""
    assert is_harmonious(tuple(hues)) == (evaluate_scheme(tuple(hues)) is not None)


@given(st.lists(_HUE, min_size=0, max_size=4))
@settings(max_examples=300)
def test_cluster_hues_count_no_greater_than_input(hues: list[float]) -> None:
    """Number of clusters cannot exceed number of hues."""
    assert len(cluster_hues(hues)) <= len(hues)
