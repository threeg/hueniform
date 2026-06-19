"""
Colour harmony evaluation (FR-12–FR-15, requirements §4).

Harmony is assessed over the **scheme set**: the multiset of hues from the
chromatic primary and secondary colours of an outfit's anchor garments.
Neutrals and minor colours are excluded before calling these functions
(FR-3, FR-10, FR-14).

Public API:
  ``cluster_hues(hues)``    — FR-12 grouping; returns one mean hue per cluster.
  ``evaluate_scheme(hues)`` — FR-13 ordered test; returns ``SchemeResult|None``.
  ``is_harmonious(hues)``   — FR-15(a) predicate.

Standard library only (NFR-9).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.matcher import constants as C
from app.matcher.colour import circular_mean, hue_distance

# Guard against sub-degree floating-point drift when comparing angles derived
# from circular_mean (e.g. atan2 introduces ~1e-13° error on a single hue).
_FLOAT_TOL: float = 1e-9


# ── Result value ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SchemeResult:
    """
    Outcome of an FR-13 scheme test.

    ``scheme``    — one of: 'neutral-based', 'monochromatic', 'analogous',
                    'complementary', 'triadic'.
    ``deviation`` — angular distance from the scheme's ideal geometry (degrees).
                    0.0 = perfect; used by ranking to score scheme strength
                    (FR-41.1).  Interpretation is scheme-specific:
                    neutral-based/monochromatic/analogous → arc span of hues
                    (smaller = tighter); complementary → |dist − 180°|;
                    triadic → max |pairwise-dist − 120°|.
    """
    scheme: str
    deviation: float


# ── Internal helpers ──────────────────────────────────────────────────────────

def _arc_span(hues: list[float]) -> float:
    """
    Minimum arc (degrees) containing all hues.  Handles the 0°/360° wrap.
    Calculated as 360° minus the largest gap between consecutive sorted hues.
    """
    if len(hues) <= 1:
        return 0.0
    sorted_h = sorted(hues)
    max_gap = sorted_h[0] + 360.0 - sorted_h[-1]   # wrap-around gap
    for i in range(len(sorted_h) - 1):
        gap = sorted_h[i + 1] - sorted_h[i]
        if gap > max_gap:
            max_gap = gap
    return max(0.0, 360.0 - max_gap)


# ── FR-12 hue clustering ──────────────────────────────────────────────────────

def cluster_hues(hues: list[float]) -> list[float]:
    """
    Group hues into clusters where every member lies within a 30° arc (FR-12).
    Returns one circular-mean representative hue per cluster.
    Handles the 0°/360° wrap so clusters near Red are merged correctly.
    """
    if not hues:
        return []

    sorted_h = sorted(hues)
    groups: list[list[float]] = [[sorted_h[0]]]

    for h in sorted_h[1:]:
        if h - groups[-1][0] <= C.CHROMATIC_ARC:
            groups[-1].append(h)
        else:
            groups.append([h])

    # Check whether the last cluster and first cluster span ≤ 30° through the
    # 0°/360° wrap (e.g. hues near 355° and hues near 5° belong together).
    if len(groups) > 1:
        wrap_arc = groups[0][-1] + 360.0 - groups[-1][0]
        if wrap_arc <= C.CHROMATIC_ARC:
            groups[0] = groups[-1] + groups[0]
            groups.pop()

    return [circular_mean(g) for g in groups]


# ── FR-13 ordered scheme test ─────────────────────────────────────────────────

def evaluate_scheme(hues: tuple[float, ...]) -> SchemeResult | None:
    """
    Test the scheme set against the FR-13 schemes in prescribed order.

    Returns the first matching ``SchemeResult``, or ``None`` if no scheme
    matches (outfit is not harmonious — FR-15).  The caller must have already
    excluded neutral and minor colours from *hues*.
    """
    hue_list = list(hues)

    # 1. Neutral-based — scheme set is empty (FR-13 §1)
    if not hue_list:
        return SchemeResult("neutral-based", 0.0)

    span = _arc_span(hue_list)

    # 2. Monochromatic — all hues within a single 30° arc (FR-13 §2)
    if span <= C.CHROMATIC_ARC:
        return SchemeResult("monochromatic", span)

    # 3. Analogous — all hues within a single 60° arc (FR-13 §3)
    if span <= C.ANALOGOUS_ARC:
        return SchemeResult("analogous", span)

    # Steps 4 and 5 operate on cluster representative hues (FR-12).
    reps = cluster_hues(hue_list)

    # 4. Complementary — exactly two clusters, 180° ± COMPLEMENTARY_TOLERANCE
    if len(reps) == 2:
        dist = hue_distance(reps[0], reps[1])
        dev = abs(dist - 180.0)
        if dev <= C.COMPLEMENTARY_TOLERANCE + _FLOAT_TOL:
            return SchemeResult("complementary", dev)

    # 5. Triadic — exactly three clusters, pairwise 120° ± TRIADIC_TOLERANCE
    if len(reps) == 3:
        h0, h1, h2 = reps
        dev = max(
            abs(hue_distance(h0, h1) - 120.0),
            abs(hue_distance(h1, h2) - 120.0),
            abs(hue_distance(h0, h2) - 120.0),
        )
        if dev <= C.TRIADIC_TOLERANCE + _FLOAT_TOL:
            return SchemeResult("triadic", dev)

    return None


# ── FR-15 harmony predicate ───────────────────────────────────────────────────

def is_harmonious(hues: tuple[float, ...]) -> bool:
    """FR-15(a): True iff the scheme set satisfies at least one FR-13 scheme."""
    return evaluate_scheme(hues) is not None
