"""
Slot mechanics (FR-16–FR-22, requirements §5).

Defines type-to-slot eligibility, anchor identification with layering dominance,
scheme-set assembly (covered-layer primaries excluded), covered-layer and echo-slot
qualification, and minor-echo recording.

Standard library only (NFR-9).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.matcher.roles import (
    Garment,
    classify_secondary,
    derive_roles,
    minor_echo_families,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral


# ── Slot constants (FR-16, FR-17) ─────────────────────────────────────────────

GARMENT_TYPES: frozenset[str] = frozenset({
    "top", "bottom", "jersey", "jacket", "socks", "shoes", "hat", "accessory",
})

REQUIRED_SLOTS: frozenset[str] = frozenset({"top", "bottom", "socks", "shoes"})
OPTIONAL_SLOTS: frozenset[str] = frozenset({"jersey", "jacket", "hat", "accessory"})
ECHO_SLOTS: frozenset[str] = frozenset({"socks", "shoes", "hat", "accessory"})

# Upper-body layers listed outermost-first; drives dominance and covered-layer logic
_UPPER_BODY: tuple[str, ...] = ("jacket", "jersey", "top")


# ── FR-18 anchor identification ───────────────────────────────────────────────

def dominant_layer(outfit: dict[str, Garment]) -> str:
    """
    FR-18: return the type key of the outermost upper-body layer present.
    Precedence: jacket > jersey > top.
    Raises ``ValueError`` when no upper-body layer is in the outfit.
    """
    for t in _UPPER_BODY:
        if t in outfit:
            return t
    raise ValueError("Outfit contains no upper-body layer (top, jersey or jacket)")


def covered_upper_layers(outfit: dict[str, Garment]) -> list[str]:
    """
    FR-18 / FR-20: type keys of upper-body layers that lie beneath the dominant,
    sorted outermost-first.  These layers are subject to the covered-layer constraint
    instead of contributing primaries to the scheme set.
    """
    dom_idx = _UPPER_BODY.index(dominant_layer(outfit))
    return [t for t in _UPPER_BODY[dom_idx + 1:] if t in outfit]


def get_anchor_types(outfit: dict[str, Garment]) -> list[str]:
    """
    FR-18: type keys of all anchor garments — every upper-body layer plus bottom.
    Order: jacket → jersey → top → bottom.
    """
    return [t for t in (*_UPPER_BODY, "bottom") if t in outfit]


# ── FR-19 scheme-set assembly ─────────────────────────────────────────────────

@dataclass(frozen=True)
class SchemeSet:
    """
    Colours driving scheme evaluation (FR-19).

    ``hues`` — passed directly to ``harmony.evaluate_scheme``.
    ``chromatic_families`` — used for FR-9 / FR-20 in-scheme membership tests.
    """
    hues: tuple[float, ...]
    chromatic_families: frozenset[str]


def build_scheme_set(outfit: dict[str, Garment]) -> SchemeSet:
    """
    FR-19: collect the scheme-set hues and family names.

    Contributions:
      - Dominant-layer primary colours
      - Bottom primary colours
      - All anchor secondary colours (including covered layers — FR-19)

    Covered-layer primaries are explicitly excluded (FR-20).
    Neutral colours are filtered out (FR-3, FR-14).
    """
    dom = dominant_layer(outfit)
    anchors = get_anchor_types(outfit)

    hues: list[float] = []
    families: set[str] = set()

    def _add_if_chromatic(colour) -> None:
        fam = _classify(colour.h, colour.s, colour.l)
        if not _is_neutral(fam):
            hues.append(colour.h)
            families.add(fam)

    # Dominant primaries (FR-19)
    for c in derive_roles(outfit[dom].colours).primaries:
        _add_if_chromatic(c)

    # Bottom primaries (FR-19)
    if "bottom" in outfit:
        for c in derive_roles(outfit["bottom"].colours).primaries:
            _add_if_chromatic(c)

    # All anchor secondaries — including covered layers (FR-19)
    for gtype in anchors:
        for c in derive_roles(outfit[gtype].colours).secondaries:
            _add_if_chromatic(c)

    return SchemeSet(hues=tuple(hues), chromatic_families=frozenset(families))


# ── Anchor chromatic families ─────────────────────────────────────────────────

def get_anchor_chromatic_families(outfit: dict[str, Garment]) -> frozenset[str]:
    """
    All chromatic colour families present on any anchor garment in any role
    (primary, secondary or minor).  Used for FR-21 echo qualification and the
    FR-20 covered-layer echo check.
    """
    families: set[str] = set()
    for gtype in get_anchor_types(outfit):
        for c in outfit[gtype].colours:
            fam = _classify(c.h, c.s, c.l)
            if not _is_neutral(fam):
                families.add(fam)
    return frozenset(families)


# ── FR-20 covered-layer constraint ────────────────────────────────────────────

def check_covered_layer(
    garment: Garment,
    scheme_families: frozenset[str],
    anchor_chromatic_families: frozenset[str],
) -> bool:
    """
    FR-20: True iff every chromatic primary and secondary of *garment* is either
    in-scheme or echoes a chromatic colour present on the anchors.
    All-neutral passes unconditionally.
    """
    roles = derive_roles(garment.colours)
    for c in (*roles.primaries, *roles.secondaries):
        fam = _classify(c.h, c.s, c.l)
        if _is_neutral(fam):
            continue
        if fam not in scheme_families and fam not in anchor_chromatic_families:
            return False
    return True


# ── FR-9 anchor secondary compatibility ──────────────────────────────────────

def check_anchor_secondaries(
    outfit: dict[str, Garment],
    scheme_families: frozenset[str],
    anchor_chromatic_families: frozenset[str],
) -> bool:
    """
    FR-9: True iff every secondary colour on every anchor garment is compatible —
    neutral, in-scheme, or an echo of an anchor chromatic colour.
    """
    for gtype in get_anchor_types(outfit):
        roles = derive_roles(outfit[gtype].colours)
        for c in roles.secondaries:
            fam = _classify(c.h, c.s, c.l)
            if classify_secondary(fam, scheme_families, anchor_chromatic_families) is None:
                return False
    return True


# ── FR-21 / FR-22 echo-slot qualification ────────────────────────────────────

@dataclass(frozen=True)
class EchoQualification:
    """
    FR-21 / FR-22: result of qualifying a garment for an echo slot.

    ``qualifies`` — False if any chromatic primary or secondary fails the echo test.
    ``minor_echoes`` — family names of minor colours that echo an anchor (FR-22 bonus).
    """
    qualifies: bool
    minor_echoes: frozenset[str]


def qualify_echo_slot(
    garment: Garment,
    anchor_chromatic_families: frozenset[str],
) -> EchoQualification:
    """
    FR-21 / FR-22: check whether *garment* qualifies for an echo slot.

    Qualifies iff every primary and secondary colour is either neutral or shares
    a family with a chromatic colour on any anchor garment.  Minor colours never
    disqualify (FR-10); minor echoes are recorded for the ranking bonus (FR-22).
    """
    roles = derive_roles(garment.colours)
    for c in (*roles.primaries, *roles.secondaries):
        fam = _classify(c.h, c.s, c.l)
        if _is_neutral(fam):
            continue
        if fam not in anchor_chromatic_families:
            return EchoQualification(qualifies=False, minor_echoes=frozenset())
    echoes = minor_echo_families(roles, anchor_chromatic_families)
    return EchoQualification(qualifies=True, minor_echoes=echoes)
