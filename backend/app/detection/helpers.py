"""
Pure detection helpers (FR-6, FR-27, architecture §2.3).

All functions are stateless and importable without the web framework or the
rembg / scikit-learn models.  Detection may only import matcher.taxonomy,
matcher.colour and matcher.constants (import-linter contract 3).

Public API
----------
``to_proportions(weights)``
    Largest-remainder integerisation: cluster weights → integer percentages
    summing to exactly 100, every entry ≥ 1, index order preserved (FR-6).

``merge_clusters(clusters)``
    Merge clusters whose HSL centroids classify into the same family.

``select_k(inertias)``
    Choose k from a sequence of KMeans inertias via the elbow heuristic.

``is_foreground_sufficient(coverage)``
    Return True iff mask coverage meets the minimum-foreground threshold (FR-27).
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from app.matcher import constants as C
from app.matcher.taxonomy import classify as _classify


# ── Proportion integerisation (FR-6) ─────────────────────────────────────────

def to_proportions(weights: Sequence[float]) -> list[int]:
    """
    Convert *weights* to integer percentages summing to exactly 100 (FR-6).

    Uses the largest-remainder method so rounding error is minimised.  Every
    output value is at least 1 (any weight that would round to 0 is bumped up,
    with the excess taken from the largest entry).
    """
    n = len(weights)
    total = sum(weights)
    exact = [w / total * 100.0 for w in weights]
    floors = [int(w) for w in exact]
    remainder = 100 - sum(floors)

    # Distribute the remainder to entries with the largest fractional parts.
    order = sorted(range(n), key=lambda i: -(exact[i] - floors[i]))
    for i in range(remainder):
        floors[order[i]] += 1

    # Guarantee every entry ≥ 1 (take from the largest when needed).
    for i in range(n):
        if floors[i] == 0:
            max_idx = max(range(n), key=lambda j: floors[j])
            floors[i] = 1
            floors[max_idx] -= 1

    return floors


# ── Same-family cluster merging (architecture §2.3) ──────────────────────────

def _weighted_circular_mean(pairs: list[tuple[float, float]]) -> float:
    """Weighted circular mean of (hue, weight) pairs; result in [0, 360)."""
    sin_sum = sum(w * math.sin(math.radians(h)) for h, w in pairs)
    cos_sum = sum(w * math.cos(math.radians(h)) for h, w in pairs)
    return math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0


def merge_clusters(
    clusters: list[tuple[float, float, float, float]],
) -> list[tuple[float, float, float, float]]:
    """
    Merge clusters whose centroids classify into the same family.

    Input:  list of ``(h, s, l, weight)`` tuples.
    Output: deduplicated list in first-appearance order; merged centroid is the
            weight-averaged (h, s, l) of the input clusters in that family.
    """
    groups: dict[str, list[tuple[float, float, float, float]]] = {}
    order: list[str] = []

    for h, s, l, w in clusters:
        fam = _classify(h, s, l)
        if fam not in groups:
            groups[fam] = []
            order.append(fam)
        groups[fam].append((h, s, l, w))

    result: list[tuple[float, float, float, float]] = []
    for fam in order:
        group = groups[fam]
        total_w = sum(w for _, _, _, w in group)
        merged_h = _weighted_circular_mean([(h, w) for h, _, _, w in group])
        merged_s = sum(s * w for _, s, _, w in group) / total_w
        merged_l = sum(l * w for _, _, l, w in group) / total_w
        result.append((merged_h, merged_s, merged_l, total_w))

    return result


# ── k-selection heuristic (architecture §2.3) ────────────────────────────────

def select_k(inertias: Sequence[float]) -> int:
    """
    Select k from a sequence of KMeans inertias (one per k, starting at k=1).

    Uses the elbow heuristic: stop adding clusters once the marginal inertia
    improvement drops below ``K_ELBOW_FACTOR`` times the first improvement.
    Returns 1 when there is only one option, or when the first improvement is
    zero or negative (all k give the same inertia).
    """
    n = len(inertias)
    if n == 1:
        return 1
    diffs = [inertias[i] - inertias[i + 1] for i in range(n - 1)]
    if diffs[0] <= 0:
        return 1
    for k_idx, d in enumerate(diffs):
        if d / diffs[0] < C.K_ELBOW_FACTOR:
            return k_idx + 1   # first k where the marginal gain is insufficient
    return n


# ── Minimum-foreground fallback predicate (FR-27) ────────────────────────────

def is_foreground_sufficient(coverage: float) -> bool:
    """
    Return ``True`` iff mask coverage meets the minimum-foreground threshold.

    *coverage* is the fraction of image pixels that belong to the segmented
    foreground (0.0–1.0).  Values below ``MINIMUM_FOREGROUND`` indicate that
    rembg failed to isolate the garment; the pipeline should fall back to
    whole-image clustering and set ``fallback_used = True`` (FR-27).
    """
    return coverage >= C.MINIMUM_FOREGROUND
