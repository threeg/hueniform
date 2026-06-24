"""
Suggestion service: load wardrobe, enumerate and rank outfit combinations (FR-36–FR-43,
FR-49–FR-52).

Bridges the storage layer (GarmentRow / GarmentColourRow) and the pure matcher
(matcher.ranking.rank).  All ranking and harmony logic lives in the matcher;
this service is responsible for:

  1. Resolving the selected slot set from the request over FR-51 defaults.
  2. Enforcing the mandatory lower-body floor (FR-51.2).
  3. Validating and applying per-category slot constraints (FR-52).
  4. Loading and filtering the wardrobe from the database.
  5. Fail-fast on empty requested slots (FR-36).
  6. Delegating to ``matcher.ranking.rank`` with an injected RNG (FR-42, NFR-5).
  7. Rendering plain-language explanations (FR-37, FR-38).
  8. Reconstructing echo records and mapping matcher Garment objects back to
     GarmentRow objects so the API layer can build full GarmentSummary shapes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.matcher import constants as C
from app.matcher.colour import Colour
from app.matcher.explain import render
from app.matcher.ranking import EvaluationResult, rank
from app.matcher.roles import Garment, derive_roles
from app.matcher.slots import (
    ALL_SLOTS,
    DEFAULT_SLOTS,
    ECHO_SLOTS,
    MANDATORY_SLOT,
    category_to_slot,
    get_anchor_chromatic_families,
    get_anchor_types,
    qualify_echo_slot,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral
from app.storage.helpers import group_colours_by_garment
from app.storage.models import GarmentColourRow, GarmentRow


# ── Module-level slot→categories mapping (from constants, for FR-52 validation) ──

_SLOT_CATEGORIES: dict[str, frozenset[str]] = {}
for _cat, _slot in C.CATEGORY_SLOT.items():
    _SLOT_CATEGORIES.setdefault(_slot, set()).add(_cat)  # type: ignore[arg-type]
_SLOT_CATEGORIES = {k: frozenset(v) for k, v in _SLOT_CATEGORIES.items()}


# ── Errors ────────────────────────────────────────────────────────────────────

class InvalidSlotError(Exception):
    """
    One or more slot keys in the request are invalid.

    Covers unknown slot keys (not in ALL_SLOTS) and attempts to deselect the
    mandatory slot (FR-51.2).
    """

    def __init__(self, unknown: list[str]) -> None:
        self.unknown = sorted(unknown)
        super().__init__(f"Unknown slot key(s): {', '.join(self.unknown)}.")


class InvalidCategoryFilterError(Exception):
    """
    FR-52: the category filter for a slot is invalid.

    Raised when a slot filter contains an empty list or a category that does not
    belong to the requested slot.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmptySlotsError(Exception):
    """FR-36: one or more requested slots have no garments in the wardrobe."""

    def __init__(self, empty_slots: list[str]) -> None:
        self.empty_slots = sorted(empty_slots)
        slots_str = ", ".join(self.empty_slots)
        super().__init__(
            f"You have no garments for the requested slot(s): {slots_str}."
        )


# ── Value types ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EchoRecord:
    """One minor-colour echo credited in ranking (FR-22)."""
    family: str
    from_slot: str   # echo slot whose minor colour is echoing
    to_slot: str     # anchor slot that carries that chromatic family


@dataclass(frozen=True)
class SuggestionCombination:
    """One ranked outfit combination (FR-39–FR-43)."""
    rank: int
    scheme: str | None         # FR-13 scheme name; None for neutral-based
    fallback: bool             # FR-43(a) neutral fallback flag
    slots: dict[str, GarmentRow]  # slot key → DB row (API builds GarmentSummary)
    echoes: tuple[EchoRecord, ...]
    explanation: str


@dataclass(frozen=True)
class SuggestionResult:
    """
    Return value of ``suggest``.

    Normal (at least one combination): ``combinations`` is non-empty;
    ``zero_explanation`` and ``hint`` are None.

    Zero-result (FR-43(b)): ``combinations`` is empty; ``zero_explanation`` and
    ``hint`` are set.
    """
    combinations: tuple[SuggestionCombination, ...]
    zero_explanation: str | None
    hint: str | None


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_wardrobe(engine: Engine) -> tuple[list[Garment], dict[int, GarmentRow]]:
    """
    Load all garments from the database in exactly two queries.

    Returns the ``Garment`` list for the matcher and an identity mapping
    ``id(garment) → GarmentRow`` used to reconstruct DB rows from matcher output.
    """
    garments: list[Garment] = []
    index: dict[int, GarmentRow] = {}

    with Session(engine) as s:
        rows = s.exec(select(GarmentRow)).all()

        all_colour_rows = s.exec(
            select(GarmentColourRow).order_by(
                GarmentColourRow.garment_id,
                GarmentColourRow.position,
            )
        ).all()

    colours_by_garment = group_colours_by_garment(list(all_colour_rows))

    for row in rows:
        colours = tuple(
            Colour(h=c.h, s=c.s, l=c.l, proportion=c.proportion)
            for c in colours_by_garment.get(row.id, [])
        )
        g = Garment(garment_type=row.type, colours=colours)
        index[id(g)] = row
        garments.append(g)

    return garments, index


def _apply_category_filters(
    wardrobe: list[Garment],
    category_filters: dict[str, list[str]],
) -> list[Garment]:
    """
    FR-52: retain only garments whose category is in the requested subset for
    their slot.  Garments in slots without a filter are kept unchanged.
    """
    if not category_filters:
        return wardrobe
    filtered: list[Garment] = []
    for g in wardrobe:
        slot = category_to_slot(g.garment_type)
        if slot in category_filters:
            if g.garment_type in category_filters[slot]:
                filtered.append(g)
        else:
            filtered.append(g)
    return filtered


def _anchor_family_map(outfit: dict[str, Garment]) -> dict[str, str]:
    """
    Map each chromatic family present on any anchor garment to the first anchor
    slot that carries it.  Used to populate ``EchoRecord.to_slot``.
    """
    mapping: dict[str, str] = {}
    for slot in get_anchor_types(outfit):
        for c in outfit[slot].colours:
            fam = _classify(c.h, c.s, c.l)
            if not _is_neutral(fam) and fam not in mapping:
                mapping[fam] = slot
    return mapping


def _compute_echoes(result: EvaluationResult) -> tuple[EchoRecord, ...]:
    """Derive EchoRecord objects from a successful EvaluationResult (FR-22)."""
    anchor_chromatic = get_anchor_chromatic_families(result.outfit)
    family_to_anchor = _anchor_family_map(result.outfit)

    echoes: list[EchoRecord] = []
    for slot in sorted(ECHO_SLOTS):
        if slot not in result.outfit:
            continue
        eq = qualify_echo_slot(result.outfit[slot], anchor_chromatic)
        for family in sorted(eq.minor_echoes):
            to_slot = family_to_anchor.get(family)
            if to_slot is not None:
                echoes.append(EchoRecord(family=family, from_slot=slot, to_slot=to_slot))

    return tuple(echoes)


def _build_combination(
    i: int,
    result: EvaluationResult,
    garment_index: dict[int, GarmentRow],
) -> SuggestionCombination:
    scheme = result.scheme_result.scheme if result.scheme_result else None
    slot_rows = {slot: garment_index[id(g)] for slot, g in result.outfit.items()}
    return SuggestionCombination(
        rank=i,
        scheme=scheme,
        fallback=result.is_fallback,
        slots=slot_rows,
        echoes=_compute_echoes(result),
        explanation=render(result),
    )


# ── Public API ────────────────────────────────────────────────────────────────

def suggest(
    slots_request: dict[str, bool | list[str]],
    engine: Engine,
    rng: random.Random,
) -> SuggestionResult:
    """
    Build ranked outfit suggestions from the wardrobe.

    Parameters
    ----------
    slots_request:
        Per-slot selection dict from the v0.2.0 request body.  Each key is a
        slot name; values are:
        - ``True``  — include this slot (adds to default selection if optional).
        - ``False`` — exclude this slot (removes from default selection).
        - ``list[str]`` — include with FR-52 per-category constraint.

        FR-51 defaults (``base``, ``lower_body``, ``socks``, ``shoes``) are the
        starting point; ``slots_request`` adjusts that set.
    engine:
        SQLAlchemy engine bound to the application database.
    rng:
        Injected random.Random for deterministic shuffling of anchor candidates
        (FR-42, NFR-5).

    Raises
    ------
    InvalidSlotError
        Any key in *slots_request* is not a valid slot name, or the mandatory
        slot (``lower_body``) is deselected (FR-51.2).
    InvalidCategoryFilterError
        A list value is empty, or contains a category that does not belong to
        the named slot (FR-52).
    EmptySlotsError
        Any selected slot — after applying category filters — has no garments
        in the wardrobe (FR-36).
    """
    # 1. Validate slot keys
    unknown = [k for k in slots_request if k not in ALL_SLOTS]
    if unknown:
        raise InvalidSlotError(unknown)

    # 2. Resolve selected slots over FR-51 defaults
    selected: set[str] = set(DEFAULT_SLOTS)
    category_filters: dict[str, list[str]] = {}

    for slot, value in slots_request.items():
        if value is False:
            selected.discard(slot)
        elif value is True:
            selected.add(slot)
        else:
            # FR-52: per-category constraint (value is list[str])
            cats: list[str] = value  # type: ignore[assignment]
            if not cats:
                raise InvalidCategoryFilterError(
                    f"Category filter for slot '{slot}' must not be empty."
                )
            slot_cats = _SLOT_CATEGORIES.get(slot, frozenset())
            bad = [c for c in cats if c not in slot_cats]
            if bad:
                raise InvalidCategoryFilterError(
                    f"Categories not valid for slot '{slot}': {', '.join(sorted(bad))}."
                )
            selected.add(slot)
            category_filters[slot] = cats

    # 3. Enforce mandatory lower-body floor (FR-51.2)
    if MANDATORY_SLOT not in selected:
        raise InvalidSlotError([MANDATORY_SLOT])

    # 4. One-piece / base auto-exclusion (FR-50.2)
    # When lower_body is constrained to one-piece categories only, a separately
    # selected base is implicitly occupied by the one-piece and must be removed.
    if "lower_body" in category_filters:
        if all(c in C.ONE_PIECE_CATEGORIES for c in category_filters["lower_body"]):
            selected.discard("base")

    requested_slots = frozenset(selected)

    # 5. Load wardrobe and apply category filters
    wardrobe, garment_index = _load_wardrobe(engine)
    wardrobe = _apply_category_filters(wardrobe, category_filters)

    # 6. Fail-fast on empty requested slots (FR-36)
    by_slot: dict[str, int] = {}
    for g in wardrobe:
        slot = category_to_slot(g.garment_type)
        by_slot[slot] = by_slot.get(slot, 0) + 1

    empty = [s for s in requested_slots if by_slot.get(s, 0) == 0]
    if empty:
        raise EmptySlotsError(empty)

    results: list[EvaluationResult] = rank(wardrobe, requested_slots, rng)

    # Zero-result sentinel: rank always returns at least one element (FR-43(b)).
    if len(results) == 1 and not results[0].outfit:
        sentinel = results[0]
        constraining = sentinel.constraining_slot
        hint = (
            f"The {constraining} slot most constrained the search — "
            f"try the request without it, or add a neutral {constraining}."
            if constraining else None
        )
        return SuggestionResult(
            combinations=(),
            zero_explanation=render(sentinel),
            hint=hint,
        )

    combinations = tuple(
        _build_combination(i, result, garment_index)
        for i, result in enumerate(results, 1)
    )

    return SuggestionResult(combinations=combinations, zero_explanation=None, hint=None)
