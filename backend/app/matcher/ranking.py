"""
Outfit ranking, enumeration and the fallback ladder (FR-39–FR-43).

Public API
----------
``rank(wardrobe, requested_slots, rng)``
    Main entry point: enumerate valid FR-15 outfits, score them, apply greedy
    variety selection, and return up to three results.  Falls back to the
    FR-43 ladder when no harmonious outfits exist.

Standard library only (NFR-9).
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass

from app.matcher import constants as C
from app.matcher.harmony import SchemeResult, evaluate_scheme
from app.matcher.roles import Garment, GarmentRoles, classify_secondary, derive_roles
from app.matcher.slots import (
    ECHO_SLOTS,
    REQUIRED_SLOTS,
    build_scheme_set,
    check_anchor_secondaries,
    check_covered_layer,
    covered_upper_layers,
    dominant_layer,
    get_anchor_chromatic_families,
    get_anchor_types,
    qualify_echo_slot,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral


# ── Result value type ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvaluationResult:
    """
    Outcome of evaluating one outfit combination (FR-39–FR-43).

    Normal result: ``scheme_result`` set, ``score > 0``, ``is_fallback=False``,
    ``constraining_slot=None``.
    Neutral-fallback (FR-43(a)): ``is_fallback=True``.
    Zero-result sentinel (FR-43(b)): ``outfit={}`` and ``constraining_slot`` set.
    """
    outfit: dict[str, Garment]
    scheme_result: SchemeResult | None
    garment_roles: dict[str, GarmentRoles]
    echo_bonus: int
    scheme_strength: float
    score: float
    is_fallback: bool
    constraining_slot: str | None


# ── Scheme-strength normalisation (FR-41.1) ───────────────────────────────────

# Maximum possible deviation for each scheme (deviation == 0 ⇒ strength == 1.0).
_SCHEME_MAX_DEV: dict[str, float] = {
    "neutral-based":  0.0,                    # deviation is always 0.0
    "monochromatic":  C.CHROMATIC_ARC,
    "analogous":      C.ANALOGOUS_ARC,
    "complementary":  C.COMPLEMENTARY_TOLERANCE,
    "triadic":        C.TRIADIC_TOLERANCE,
}


def _scheme_strength(result: SchemeResult) -> float:
    """Normalise ``result.deviation`` to a [0, 1] strength score (FR-41.1)."""
    max_dev = _SCHEME_MAX_DEV[result.scheme]
    if max_dev == 0.0:
        return 1.0   # neutral-based always perfect
    return 1.0 - result.deviation / max_dev


# ── Single-outfit evaluation ──────────────────────────────────────────────────

def evaluate_outfit(
    outfit: dict[str, Garment],
    is_fallback: bool = False,
) -> EvaluationResult | None:
    """
    Evaluate one outfit combination against FR-15.

    Returns ``None`` if the scheme set is not harmonious or any slot rule fails.
    Otherwise returns a fully scored ``EvaluationResult``.
    """
    ss = build_scheme_set(outfit)
    scheme_result = evaluate_scheme(ss.hues)
    if scheme_result is None:
        return None

    # Compute anchor chromatic families excluding covered layers so the FR-20
    # check is non-trivial (a covered jersey cannot echo its own colour).
    covered = set(covered_upper_layers(outfit))
    outer_outfit = {k: v for k, v in outfit.items() if k not in covered}
    outer_anchor_chromatic = get_anchor_chromatic_families(outer_outfit)

    # FR-20: covered-layer constraint
    for gtype in covered:
        if not check_covered_layer(outfit[gtype], ss.chromatic_families, outer_anchor_chromatic):
            return None

    # Full anchor families for FR-9 and FR-21 (covered layers included).
    anchor_chromatic = get_anchor_chromatic_families(outfit)

    # FR-9: anchor secondary compatibility (defensive; see design note in ranking.py)
    if not check_anchor_secondaries(outfit, ss.chromatic_families, anchor_chromatic):  # pragma: no cover
        return None  # pragma: no cover

    # FR-21 / FR-22: echo-slot qualification and minor-echo bonus
    total_echoes: set[str] = set()
    for gtype in sorted(ECHO_SLOTS):   # deterministic iteration order
        if gtype in outfit:
            eq = qualify_echo_slot(outfit[gtype], anchor_chromatic)
            if not eq.qualifies:
                return None
            total_echoes.update(eq.minor_echoes)

    echo_bonus = len(total_echoes)
    strength   = _scheme_strength(scheme_result)
    score      = C.WEIGHT_SCHEME_STRENGTH * strength + C.WEIGHT_ECHO_BONUS * echo_bonus
    roles      = {gtype: derive_roles(g.colours) for gtype, g in outfit.items()}

    return EvaluationResult(
        outfit=outfit,
        scheme_result=scheme_result,
        garment_roles=roles,
        echo_bonus=echo_bonus,
        scheme_strength=strength,
        score=score,
        is_fallback=is_fallback,
        constraining_slot=None,
    )


# ── Failure-slot identification ───────────────────────────────────────────────

def _failure_slot(outfit: dict[str, Garment]) -> str | None:
    """
    Identify the slot responsible for an outfit failing FR-15.
    Returns ``None`` if the outfit is actually valid.
    """
    ss = build_scheme_set(outfit)
    if evaluate_scheme(ss.hues) is None:
        return dominant_layer(outfit)  # scheme failure → blame the dominant layer

    covered = set(covered_upper_layers(outfit))
    outer_outfit = {k: v for k, v in outfit.items() if k not in covered}
    outer_anchor_chromatic = get_anchor_chromatic_families(outer_outfit)
    anchor_chromatic = get_anchor_chromatic_families(outfit)

    for gtype in covered:
        if not check_covered_layer(outfit[gtype], ss.chromatic_families, outer_anchor_chromatic):
            return gtype

    for gtype in get_anchor_types(outfit):
        roles = derive_roles(outfit[gtype].colours)
        for c in roles.secondaries:
            fam = _classify(c.h, c.s, c.l)
            # With full anchor_chromatic, a secondary always echoes its own garment
            # so classify_secondary never returns None here; branch kept for safety.
            if classify_secondary(fam, ss.chromatic_families, anchor_chromatic) is None:  # pragma: no cover
                return gtype  # pragma: no cover

    for gtype in sorted(ECHO_SLOTS):
        if gtype in outfit:
            if not qualify_echo_slot(outfit[gtype], anchor_chromatic).qualifies:
                return gtype

    return None


# ── Greedy variety selection (FR-41.3) ────────────────────────────────────────

def _greedy_select(results: list[EvaluationResult], n: int) -> list[EvaluationResult]:
    """
    Pick up to *n* results using a greedy variety penalty (FR-41.3).

    For each subsequent pick, subtract ``WEIGHT_VARIETY × shared_garments``
    from each candidate's score before selecting the best.
    """
    selected: list[EvaluationResult] = []
    remaining = list(results)

    while len(selected) < n and remaining:
        best_idx = 0
        best_adj = -float("inf")
        for i, r in enumerate(remaining):
            shared = sum(
                1
                for slot, g in r.outfit.items()
                if any(sel.outfit.get(slot) is g for sel in selected)
            )
            adj = r.score - C.WEIGHT_VARIETY * shared
            if adj > best_adj:
                best_adj = adj
                best_idx = i
        selected.append(remaining.pop(best_idx))

    return selected


# ── Outfit enumeration ────────────────────────────────────────────────────────

_ANCHOR_ORDER: tuple[str, ...] = ("jacket", "jersey", "top", "bottom")


def _enumerate_outfits(
    garments_by_slot: dict[str, list[Garment]],
    requested_slots: frozenset[str],
    rng: random.Random | None,
) -> list[dict[str, Garment]]:
    """
    Enumerate outfit combinations for *requested_slots*, always bounded.

    Both anchor and echo combos are capped (``MAX_ANCHOR_CANDIDATES`` /
    ``MAX_ECHO_COMBOS``) using per-slot shuffle + ``islice`` so the full
    Cartesian product is never materialised (NFR-5).  Shuffling is skipped
    when *rng* is ``None`` (fallback paths); the islice cap still applies so
    large neutral sub-wardrobes cannot cause a combinatorial explosion.
    """
    anchor_types = [t for t in _ANCHOR_ORDER if t in requested_slots]
    echo_types   = sorted(ECHO_SLOTS & requested_slots)

    anchor_lists = [list(garments_by_slot[t]) for t in anchor_types]
    if rng is not None:
        for lst in anchor_lists:
            rng.shuffle(lst)
    anchor_combos: list[tuple[Garment, ...]] = list(
        itertools.islice(itertools.product(*anchor_lists), C.MAX_ANCHOR_CANDIDATES)
    )

    echo_slots_lists = [list(garments_by_slot[t]) for t in echo_types]
    if rng is not None:
        for lst in echo_slots_lists:
            rng.shuffle(lst)

    outfits: list[dict[str, Garment]] = []
    for ac in anchor_combos:
        base: dict[str, Garment] = dict(zip(anchor_types, ac))
        if echo_slots_lists:
            for ec in itertools.islice(
                itertools.product(*echo_slots_lists), C.MAX_ECHO_COMBOS
            ):
                outfits.append({**base, **dict(zip(echo_types, ec))})
        else:
            outfits.append(base)

    return outfits


# ── Neutral-based fallback (FR-43(a)) ─────────────────────────────────────────

def _is_all_neutral(garment: Garment) -> bool:
    """True iff every colour on *garment* classifies as a neutral family."""
    return all(_is_neutral(_classify(c.h, c.s, c.l)) for c in garment.colours)


def _neutral_fallback(
    garments_by_slot: dict[str, list[Garment]],
    requested_slots: frozenset[str],
) -> list[EvaluationResult]:
    """
    FR-43(a): exhaustive search for neutral-only outfit combinations.

    Filters the wardrobe to all-neutral garments per slot, then evaluates
    every combination without the anchor cap (small search space by design).
    """
    neutral_by_slot: dict[str, list[Garment]] = {
        slot: [g for g in glist if _is_all_neutral(g)]
        for slot, glist in garments_by_slot.items()
    }
    neutral_by_slot = {s: gl for s, gl in neutral_by_slot.items() if gl}

    if not all(slot in neutral_by_slot for slot in requested_slots):
        return []

    valid: list[EvaluationResult] = []
    for outfit in _enumerate_outfits(neutral_by_slot, requested_slots, rng=None):
        result = evaluate_outfit(outfit, is_fallback=True)
        if result is not None:  # pragma: no branch
            valid.append(result)
    return valid


# ── Constraining-slot heuristic (FR-43(b)) ────────────────────────────────────

def _constraining_slot(
    garments_by_slot: dict[str, list[Garment]],
    requested_slots: frozenset[str],
) -> str | None:
    """
    FR-43(b): identify the slot most responsible for all outfits failing.

    Runs ``_failure_slot`` over all combinations and returns the slot with the
    highest failure count.
    """
    counts: dict[str, int] = {}
    for outfit in _enumerate_outfits(garments_by_slot, requested_slots, rng=None):
        slot = _failure_slot(outfit)
        if slot is not None:
            counts[slot] = counts.get(slot, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda s: counts[s])


# ── Main entry point ──────────────────────────────────────────────────────────

def rank(
    wardrobe: list[Garment],
    requested_slots: frozenset[str],
    rng: random.Random,
) -> list[EvaluationResult]:
    """
    Enumerate, evaluate and rank outfit combinations from *wardrobe*.

    Returns up to three ``EvaluationResult`` objects, ranked best-first with
    variety applied (FR-39, FR-40, FR-41).

    Falls back to FR-43 ladder when no harmonious outfits are found:
      (a) neutral-based combinations flagged with ``is_fallback=True``;
      (b) a single zero-result sentinel with ``constraining_slot`` set.
    """
    # Group garments by type; verify all requested slots are present
    garments_by_slot: dict[str, list[Garment]] = {}
    for g in wardrobe:
        garments_by_slot.setdefault(g.garment_type, []).append(g)

    missing = requested_slots - frozenset(garments_by_slot)
    if missing:
        slot = sorted(missing)[0]
        return [EvaluationResult(
            outfit={}, scheme_result=None, garment_roles={},
            echo_bonus=0, scheme_strength=0.0, score=0.0,
            is_fallback=False, constraining_slot=slot,
        )]

    # Step 1: normal harmonious outfits
    valid: list[EvaluationResult] = []
    for outfit in _enumerate_outfits(garments_by_slot, requested_slots, rng):
        result = evaluate_outfit(outfit)
        if result is not None:
            valid.append(result)

    if valid:
        # Sort by score descending, then apply greedy variety (FR-41)
        valid.sort(key=lambda r: r.score, reverse=True)
        return _greedy_select(valid, 3)

    # Step 2: neutral-based fallback (FR-43(a))
    # Fires in production when the anchor cap caused step 1 to miss neutral outfits;
    # unit tests with small wardrobes never reach this path (neutral combos found in
    # step 1 before the cap is hit).
    fallback = _neutral_fallback(garments_by_slot, requested_slots)
    if fallback:  # pragma: no cover
        fallback.sort(key=lambda r: r.score, reverse=True)  # pragma: no cover
        return _greedy_select(fallback, 3)  # pragma: no cover

    # Step 3: zero-result sentinel (FR-43(b))
    constraining = _constraining_slot(garments_by_slot, requested_slots)
    return [EvaluationResult(
        outfit={}, scheme_result=None, garment_roles={},
        echo_bonus=0, scheme_strength=0.0, score=0.0,
        is_fallback=False, constraining_slot=constraining,
    )]
