"""
Slot mechanics (FR-16–FR-22, FR-49–FR-51, requirements §5).

Maps garment categories to slots, provides anchor identification with
four-level upper-body dominance, one-piece spanning, scheme-set assembly,
covered-layer and adornment-tier qualification, and mutual-exclusion validation.

Standard library only (NFR-9).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.matcher import constants as C
from app.matcher.roles import (
    Garment,
    classify_secondary,
    derive_roles,
    minor_echo_families,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral


# ── Backward-compatibility slot key map (v0.1.0 → v0.2.0) ────────────────────
# Maps the eight v0.1.0 slot-as-type strings to their v0.2.0 slot keys.
# Used during the API/storage migration period (removed when complete).
_V1_TO_SLOT: dict[str, str] = {
    "top":    "base",
    "bottom": "lower_body",
    "jersey": "mid",
    # "jacket" → is a v0.2.0 category (outer slot) handled by CATEGORY_SLOT
    # "socks" / "shoes" / "hat" → same keys in v0.2.0
}


# ── Category → slot lookup ────────────────────────────────────────────────────

def category_to_slot(category: str) -> str:
    """
    Return the slot key for *category* (FR-16).

    Resolution order:
    1. v0.2.0 CATEGORY_SLOT mapping ("t_shirt" → "base", "jumper" → "mid", etc.)
    2. v0.1.0 backward-compat map  ("top" → "base", "jersey" → "mid", etc.)
    3. Identity fallback            (unknown values returned unchanged)
    """
    if category in C.CATEGORY_SLOT:
        return C.CATEGORY_SLOT[category]
    return _V1_TO_SLOT.get(category, category)


# ── Slot constants (re-exported from constants; single import point) ──────────

# v0.2.0 model
ALL_CATEGORIES: frozenset[str] = C.ALL_CATEGORIES
ALL_SLOTS: frozenset[str] = C.ALL_SLOTS
DEFAULT_SLOTS: frozenset[str] = C.DEFAULT_SLOTS
MANDATORY_SLOT: str = C.MANDATORY_SLOT
STATEMENT_ADORNMENT_SLOTS: frozenset[str] = C.STATEMENT_ADORNMENT_SLOTS
MINOR_ADORNMENT_SLOTS: frozenset[str] = C.MINOR_ADORNMENT_SLOTS
ADORNMENT_SLOTS: frozenset[str] = C.STATEMENT_ADORNMENT_SLOTS | C.MINOR_ADORNMENT_SLOTS

# v0.2.0 category and slot sets (re-exported from constants; single import point).
GARMENT_TYPES: frozenset[str] = C.ALL_CATEGORIES

# Required slots are the four default-selected slots for every request (FR-51.1).
REQUIRED_SLOTS: frozenset[str] = C.DEFAULT_SLOTS          # base, lower_body, socks, shoes
# Optional slots are every other slot the user may add to a request.
OPTIONAL_SLOTS: frozenset[str] = C.ALL_SLOTS - C.DEFAULT_SLOTS

ECHO_SLOTS: frozenset[str] = ADORNMENT_SLOTS        # adornment slots qualify as echoes

# Upper-body slots, outermost → innermost (FR-18 dominance order)
_UPPER_BODY: tuple[str, ...] = tuple(reversed(C.UPPER_BODY_LAYERS))  # outer, mid, shirt, base


# ── One-piece helper ──────────────────────────────────────────────────────────

def _is_one_piece(garment: Garment) -> bool:
    """True iff the garment category is a one-piece (dress/jumpsuit) (FR-49.2)."""
    return garment.garment_type in C.ONE_PIECE_CATEGORIES


# ── FR-50 mutual-exclusion validation ─────────────────────────────────────────

def is_valid_slot_combination(outfit: dict[str, Garment]) -> bool:
    """
    FR-50: True iff the outfit respects all mutual-exclusion groups.

    FR-50.2: a one-piece in lower_body occupies the base slot too, so a
    separate base garment is invalid when a one-piece is present.
    """
    if "lower_body" in outfit and _is_one_piece(outfit["lower_body"]):
        if "base" in outfit:
            return False
    return True


# ── FR-18 anchor identification ───────────────────────────────────────────────

def dominant_layer(outfit: dict[str, Garment]) -> str:
    """
    FR-18: return the slot key of the outermost upper-body layer present.
    Precedence: outer > mid > shirt > base.

    When no separate upper-body layer exists but a one-piece fills lower_body,
    the one-piece is the dominant (base-position) upper layer (FR-18) and
    'lower_body' is returned.

    Raises ValueError when no upper-body garment and no one-piece is present.
    """
    for slot in _UPPER_BODY:
        if slot in outfit:
            return slot
    if "lower_body" in outfit and _is_one_piece(outfit["lower_body"]):
        return "lower_body"
    raise ValueError(
        f"Outfit contains no upper-body layer and no one-piece; "
        f"slots present: {sorted(outfit)}"
    )


def covered_upper_layers(outfit: dict[str, Garment]) -> list[str]:
    """
    FR-18 / FR-20: slot keys of upper-body layers beneath the dominant layer,
    outermost-first.

    A one-piece at lower_body is never a covered layer (FR-50.2 — its lower
    portion remains visible even when outer layers are worn over it).
    """
    try:
        dom = dominant_layer(outfit)
    except ValueError:
        return []
    if dom == "lower_body":
        return []
    dom_idx = _UPPER_BODY.index(dom)
    return [t for t in _UPPER_BODY[dom_idx + 1:] if t in outfit]


def get_anchor_types(outfit: dict[str, Garment]) -> list[str]:
    """
    FR-18: slot keys of all anchor garments, outermost-first.

    Order: outer → mid → shirt → base → lower_body.
    A one-piece at lower_body is listed once; it is never duplicated for its
    implicit base-position role (FR-18).
    """
    upper = [t for t in _UPPER_BODY if t in outfit]
    lower = ["lower_body"] if "lower_body" in outfit else []
    return upper + lower


# ── FR-19 scheme-set assembly ─────────────────────────────────────────────────

@dataclass(frozen=True)
class SchemeSet:
    """
    Colours driving scheme evaluation (FR-19).

    hues — passed directly to harmony.evaluate_scheme.
    chromatic_families — used for FR-9 / FR-20 membership tests.
    """
    hues: tuple[float, ...]
    chromatic_families: frozenset[str]


def build_scheme_set(outfit: dict[str, Garment]) -> SchemeSet:
    """
    FR-19: collect the scheme-set hues and family names.

    Contributions:
      - Dominant layer's primary colours.
      - Lower-body garment's primary colours — skipped when the dominant IS
        the lower_body (one-piece with no upper layers), so it is counted once
        (FR-18, FR-19).
      - All anchors' secondary colours, including covered layers (FR-19).

    Neutral colours are excluded (FR-3, FR-14).
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

    # Dominant-layer primaries
    for c in derive_roles(outfit[dom].colours).primaries:
        _add_if_chromatic(c)

    # Lower-body primaries — omitted when lower_body IS the dominant (already counted)
    if "lower_body" in outfit and dom != "lower_body":
        for c in derive_roles(outfit["lower_body"].colours).primaries:
            _add_if_chromatic(c)

    # All anchor secondaries — including covered layers (FR-19)
    for slot in anchors:
        for c in derive_roles(outfit[slot].colours).secondaries:
            _add_if_chromatic(c)

    return SchemeSet(hues=tuple(hues), chromatic_families=frozenset(families))


# ── Anchor chromatic families ─────────────────────────────────────────────────

def get_anchor_chromatic_families(outfit: dict[str, Garment]) -> frozenset[str]:
    """
    All chromatic colour families on any anchor garment in any role.
    Used for FR-21 echo qualification and the FR-20 covered-layer echo check.
    """
    families: set[str] = set()
    for slot in get_anchor_types(outfit):
        for c in outfit[slot].colours:
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
    FR-20: True iff every chromatic primary and secondary of *garment* is
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
    FR-9: True iff every secondary on every anchor garment is neutral,
    in-scheme, or echoes an anchor chromatic colour.
    """
    for slot in get_anchor_types(outfit):
        roles = derive_roles(outfit[slot].colours)
        for c in roles.secondaries:
            fam = _classify(c.h, c.s, c.l)
            if classify_secondary(fam, scheme_families, anchor_chromatic_families) is None:
                return False
    return True


# ── FR-21 / FR-22 adornment-slot qualification ────────────────────────────────

@dataclass(frozen=True)
class EchoQualification:
    """
    FR-21 / FR-22: result of qualifying a garment for an adornment slot.

    qualifies — False only for statement-adornment slots where a primary or
                secondary is chromatic and does not echo the anchors.
    minor_echoes — family names of minor colours that echo an anchor (FR-22 bonus).
    """
    qualifies: bool
    minor_echoes: frozenset[str]


def qualify_echo_slot(
    garment: Garment,
    anchor_chromatic_families: frozenset[str],
) -> EchoQualification:
    """
    FR-21 / FR-22: check whether *garment* qualifies for its adornment slot.

    Minor adornments (glasses, earrings, necklace, watch, ring, bracelet)
    never disqualify (FR-49.3); their minor echoes are still recorded (FR-22).

    Statement adornments (hat, tie, scarf, belt, socks, shoes) qualify iff
    every primary and secondary colour is neutral or echoes an anchor family.
    Minor colours never disqualify (FR-10); minor echoes are recorded (FR-22).

    Unknown/legacy slot keys fall through to statement-adornment logic (safe
    default during the v0.1.0→v0.2.0 migration period).
    """
    slot = category_to_slot(garment.garment_type)
    roles = derive_roles(garment.colours)

    if slot in C.MINOR_ADORNMENT_SLOTS:
        # Minor adornment: never disqualifies (FR-49.3)
        echoes = minor_echo_families(roles, anchor_chromatic_families)
        return EchoQualification(qualifies=True, minor_echoes=echoes)

    # Statement adornment (or unknown): echo-constrained
    for c in (*roles.primaries, *roles.secondaries):
        fam = _classify(c.h, c.s, c.l)
        if _is_neutral(fam):
            continue
        if fam not in anchor_chromatic_families:
            return EchoQualification(qualifies=False, minor_echoes=frozenset())
    echoes = minor_echo_families(roles, anchor_chromatic_families)
    return EchoQualification(qualifies=True, minor_echoes=echoes)
