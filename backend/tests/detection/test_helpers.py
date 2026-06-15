"""
Tests for detection.helpers (test strategy §6.1).

Coverage:
  - FR-6: to_proportions sums to 100, every entry ≥ 1, ordering preserved
    (including Hypothesis property over arbitrary valid weight vectors).
  - merge_clusters: same-family centroids merge; distinct families preserved.
  - select_k: known elbow curves map to expected k; edge cases.
  - is_foreground_sufficient: boundary rows at/below/above MINIMUM_FOREGROUND.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.matcher.constants import K_ELBOW_FACTOR, MINIMUM_FOREGROUND
from app.detection.helpers import (
    is_foreground_sufficient,
    merge_clusters,
    select_k,
    to_proportions,
)


# ── to_proportions ────────────────────────────────────────────────────────────

class TestToProportions:
    def test_single_weight_gives_100(self) -> None:
        assert to_proportions([1.0]) == [100]

    def test_equal_weights_sum_to_100(self) -> None:
        result = to_proportions([1.0, 1.0])
        assert sum(result) == 100
        assert len(result) == 2

    def test_three_equal_weights(self) -> None:
        result = to_proportions([1.0, 1.0, 1.0])
        assert sum(result) == 100
        assert all(v >= 1 for v in result)

    def test_four_equal_weights(self) -> None:
        result = to_proportions([25.0, 25.0, 25.0, 25.0])
        assert sum(result) == 100
        assert all(v == 25 for v in result)

    def test_known_proportions(self) -> None:
        result = to_proportions([60.0, 25.0, 15.0])
        assert sum(result) == 100
        assert result == [60, 25, 15]

    def test_very_small_weight_gets_minimum_one(self) -> None:
        # One near-zero weight that would floor to 0
        result = to_proportions([99.0, 0.5, 0.5])
        assert sum(result) == 100
        assert all(v >= 1 for v in result)

    def test_index_order_preserved(self) -> None:
        # Largest weight stays in index 0
        result = to_proportions([70.0, 20.0, 10.0])
        assert result[0] > result[1] > result[2]

    def test_non_normalised_weights_accepted(self) -> None:
        # Weights that don't sum to 1 or 100 are valid
        result = to_proportions([0.7, 0.2, 0.1])
        assert sum(result) == 100
        assert all(v >= 1 for v in result)


@given(
    weights=st.lists(
        st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=4,
    )
)
@settings(max_examples=500)
def test_to_proportions_property(weights: list[float]) -> None:
    """FR-6: output sums to 100, every entry ≥ 1, same length as input."""
    result = to_proportions(weights)
    assert sum(result) == 100
    assert all(v >= 1 for v in result)
    assert len(result) == len(weights)


# ── merge_clusters ────────────────────────────────────────────────────────────

class TestMergeClusters:
    def test_distinct_families_unchanged_count(self) -> None:
        # Red (h=0) and Teal (h=180) are different families
        clusters = [
            (0.0, 80.0, 50.0, 60.0),    # red
            (180.0, 70.0, 50.0, 40.0),  # teal
        ]
        result = merge_clusters(clusters)
        assert len(result) == 2

    def test_same_family_merges_to_one(self) -> None:
        # Two red hues (h=355 and h=5) both classify as red
        clusters = [
            (355.0, 80.0, 50.0, 30.0),
            (5.0, 80.0, 50.0, 30.0),
        ]
        result = merge_clusters(clusters)
        assert len(result) == 1

    def test_merged_weight_is_sum(self) -> None:
        clusters = [
            (355.0, 80.0, 50.0, 30.0),
            (5.0, 80.0, 50.0, 20.0),
        ]
        result = merge_clusters(clusters)
        assert len(result) == 1
        assert result[0][3] == pytest.approx(50.0)

    def test_single_cluster_unchanged(self) -> None:
        clusters = [(0.0, 80.0, 50.0, 100.0)]
        result = merge_clusters(clusters)
        assert len(result) == 1
        h, s, l, w = result[0]
        assert h == pytest.approx(0.0, abs=1.0)
        assert s == pytest.approx(80.0)
        assert l == pytest.approx(50.0)
        assert w == pytest.approx(100.0)

    def test_first_appearance_order_preserved(self) -> None:
        # teal first, then red
        clusters = [
            (180.0, 70.0, 50.0, 40.0),  # teal
            (0.0, 80.0, 50.0, 60.0),    # red
        ]
        result = merge_clusters(clusters)
        assert len(result) == 2
        # teal should still be first
        from app.matcher.taxonomy import classify
        assert classify(result[0][0], result[0][1], result[0][2]) == "Teal"
        assert classify(result[1][0], result[1][1], result[1][2]) == "Red"

    def test_merged_hue_is_weighted_mean(self) -> None:
        # Two red-family hues with equal weight → mean should be between them
        clusters = [
            (350.0, 80.0, 50.0, 50.0),
            (10.0, 80.0, 50.0, 50.0),
        ]
        result = merge_clusters(clusters)
        assert len(result) == 1
        merged_h = result[0][0]
        # Weighted circular mean of 350 and 10 (equal weights) = 0° ≡ 360°
        assert merged_h == pytest.approx(0.0, abs=1.0) or merged_h == pytest.approx(360.0, abs=1.0)

    def test_three_clusters_two_merge(self) -> None:
        clusters = [
            (0.0, 80.0, 50.0, 40.0),    # red
            (5.0, 80.0, 50.0, 20.0),    # red (merges with first)
            (180.0, 70.0, 50.0, 40.0),  # teal
        ]
        result = merge_clusters(clusters)
        assert len(result) == 2
        assert result[0][3] == pytest.approx(60.0)  # merged red weight
        assert result[1][3] == pytest.approx(40.0)  # teal weight


# ── select_k ─────────────────────────────────────────────────────────────────

class TestSelectK:
    def test_single_inertia_returns_1(self) -> None:
        assert select_k([100.0]) == 1

    def test_zero_first_improvement_returns_1(self) -> None:
        # No improvement at all → k=1
        assert select_k([100.0, 100.0, 100.0, 100.0]) == 1

    def test_sharp_elbow_at_k2(self) -> None:
        # Big drop 1→2, tiny drops after
        assert select_k([100.0, 10.0, 9.5, 9.0]) == 2

    def test_sharp_elbow_at_k3(self) -> None:
        # Big drops 1→2 and 2→3, tiny drop 3→4
        assert select_k([100.0, 50.0, 10.0, 9.5]) == 3

    def test_no_elbow_returns_max_k(self) -> None:
        # Equal drops → all improvements are large → use all k
        assert select_k([100.0, 75.0, 50.0, 25.0]) == 4

    def test_two_k_options(self) -> None:
        # Only two options; big drop → k=2
        assert select_k([100.0, 10.0]) == 2

    def test_two_k_no_improvement(self) -> None:
        assert select_k([100.0, 100.0]) == 1

    def test_elbow_factor_boundary(self) -> None:
        # Marginal improvement exactly at threshold: d[1]/d[0] = K_ELBOW_FACTOR
        # → NOT < factor → does not stop at k=2, continues to k=3
        d0 = 100.0
        d1 = K_ELBOW_FACTOR * d0  # exactly at threshold
        inertias = [200.0, 200.0 - d0, 200.0 - d0 - d1, 200.0 - d0 - d1 - 1.0]
        k = select_k(inertias)
        assert k >= 3  # boundary: not stopped at k=2


# ── is_foreground_sufficient ──────────────────────────────────────────────────

class TestIsForegroundSufficient:
    def test_above_threshold_is_sufficient(self) -> None:
        assert is_foreground_sufficient(MINIMUM_FOREGROUND + 0.01) is True

    def test_at_threshold_is_sufficient(self) -> None:
        # At the boundary: coverage == MINIMUM_FOREGROUND → sufficient
        assert is_foreground_sufficient(MINIMUM_FOREGROUND) is True

    def test_below_threshold_is_insufficient(self) -> None:
        assert is_foreground_sufficient(MINIMUM_FOREGROUND - 0.01) is False

    def test_full_coverage_is_sufficient(self) -> None:
        assert is_foreground_sufficient(1.0) is True

    def test_zero_coverage_is_insufficient(self) -> None:
        assert is_foreground_sufficient(0.0) is False
