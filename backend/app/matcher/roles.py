"""
Colour role derivation (FR-6–FR-11, requirements §3).

``derive_roles(colours)`` maps a validated palette to primary/secondary/minor
buckets (FR-7).  The frozen ``GarmentRoles`` value is passed unchanged to
harmony and slot evaluation; roles are never persisted (architecture §2.2).

Standard library only (NFR-9).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.matcher import constants as C
from app.matcher.colour import Colour
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral


# ── Value types ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Garment:
    """
    Matcher-layer value type: a garment's type tag and ordered palette.

    ``garment_type`` is one of the eight FR-16 values.
    ``colours`` is the validated palette produced by detection (FR-6).
    """
    garment_type: str
    colours: tuple[Colour, ...]


@dataclass(frozen=True)
class GarmentRoles:
    """
    Derived colour roles for one garment (FR-7).

    ``primaries`` has length 1 normally, or 2+ when the garment is dual-primary
    (FR-8).  Each bucket is sorted by proportion descending.
    """
    primaries: tuple[Colour, ...]
    secondaries: tuple[Colour, ...]
    minors: tuple[Colour, ...]
    is_dual_primary: bool


# ── FR-6 palette validation ───────────────────────────────────────────────────

def validate_palette(colours: tuple[Colour, ...]) -> None:
    """Raise ``ValueError`` if the palette violates FR-6 (1–4 colours, sum = 100)."""
    if not 1 <= len(colours) <= 4:
        raise ValueError(
            f"FR-6: palette must have 1–4 colours, got {len(colours)}"
        )
    total = sum(c.proportion for c in colours)
    if total != 100:
        raise ValueError(
            f"FR-6: proportions must sum to exactly 100, got {total}"
        )


# ── FR-7 role derivation ──────────────────────────────────────────────────────

def derive_roles(colours: tuple[Colour, ...]) -> GarmentRoles:
    """
    Derive primary/secondary/minor roles from a palette (FR-7).

    Primary: the highest-proportion colour (saturation as tie-break), plus any
    other colour with proportion ≥ PRIMARY_THRESHOLD.  Two or more primaries
    → is_dual_primary = True (FR-8).
    Secondary: proportion in [SECONDARY_THRESHOLD, PRIMARY_THRESHOLD).
    Minor: proportion < SECONDARY_THRESHOLD.
    """
    dominant_idx = max(
        range(len(colours)),
        key=lambda i: (colours[i].proportion, colours[i].s),
    )

    primaries: list[Colour] = []
    secondaries: list[Colour] = []
    minors: list[Colour] = []

    for i, c in enumerate(colours):
        if i == dominant_idx or c.proportion >= C.PRIMARY_THRESHOLD:
            primaries.append(c)
        elif c.proportion >= C.SECONDARY_THRESHOLD:
            secondaries.append(c)
        else:
            minors.append(c)

    primaries.sort(key=lambda c: (c.proportion, c.s), reverse=True)
    secondaries.sort(key=lambda c: (c.proportion, c.s), reverse=True)
    minors.sort(key=lambda c: (c.proportion, c.s), reverse=True)

    return GarmentRoles(
        primaries=tuple(primaries),
        secondaries=tuple(secondaries),
        minors=tuple(minors),
        is_dual_primary=len(primaries) >= 2,
    )


# ── FR-8 primary qualification ────────────────────────────────────────────────

def all_primaries_qualify(
    roles: GarmentRoles,
    predicate: Callable[[Colour], bool],
) -> bool:
    """FR-8: True iff every primary in *roles* satisfies *predicate*."""
    return all(predicate(c) for c in roles.primaries)


# ── FR-9 secondary compatibility ──────────────────────────────────────────────

def classify_secondary(
    family_name: str,
    scheme_families: frozenset[str],
    anchor_chromatic_families: frozenset[str],
) -> str | None:
    """
    FR-9: classify a secondary colour family as ``'neutral'``, ``'in_scheme'``,
    ``'echo'``, or ``None`` (incompatible — disqualifies the anchor).

    *scheme_families*: the chromatic families present in the active harmony scheme.
    *anchor_chromatic_families*: all chromatic families on the outfit's anchors.
    """
    if _is_neutral(family_name):
        return "neutral"
    if family_name in scheme_families:
        return "in_scheme"
    if family_name in anchor_chromatic_families:
        return "echo"
    return None


# ── FR-11 minor echoes ────────────────────────────────────────────────────────

def minor_echo_families(
    roles: GarmentRoles,
    anchor_chromatic_families: frozenset[str],
) -> frozenset[str]:
    """
    FR-11: return the set of minor-colour families that echo any family in
    *anchor_chromatic_families*.  Used to accumulate the echo bonus in ranking.
    """
    result: set[str] = set()
    for c in roles.minors:
        fam = _classify(c.h, c.s, c.l)
        if not _is_neutral(fam) and fam in anchor_chromatic_families:
            result.add(fam)
    return frozenset(result)
