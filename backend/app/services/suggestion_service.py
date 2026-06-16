"""
Suggestion service: load wardrobe, enumerate and rank outfit combinations (FR-36–FR-43).

Bridges the storage layer (GarmentRow / GarmentColourRow) and the pure matcher
(matcher.ranking.rank).  All ranking and harmony logic lives in the matcher;
this service is responsible for:

  1. Loading and grouping the wardrobe from the database.
  2. Fail-fast on empty requested slots (FR-36).
  3. Delegating to ``matcher.ranking.rank`` with an injected RNG (FR-42, NFR-5).
  4. Rendering plain-language explanations (FR-37, FR-38).
  5. Reconstructing echo records and mapping matcher Garment objects back to
     GarmentRow objects so the API layer can build full GarmentSummary shapes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.matcher.colour import Colour
from app.matcher.explain import render
from app.matcher.ranking import EvaluationResult, rank
from app.matcher.roles import Garment, derive_roles
from app.matcher.slots import (
    ECHO_SLOTS,
    OPTIONAL_SLOTS,
    REQUIRED_SLOTS,
    get_anchor_chromatic_families,
    get_anchor_types,
    qualify_echo_slot,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral
from app.storage.models import GarmentColourRow, GarmentRow


# ── Errors ────────────────────────────────────────────────────────────────────

class InvalidSlotError(Exception):
    """One or more keys in ``include_optional`` are not valid optional slot names."""

    def __init__(self, unknown: list[str]) -> None:
        self.unknown = sorted(unknown)
        super().__init__(f"Unknown slot key(s): {', '.join(self.unknown)}.")


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

        # One bulk query for all colour rows; group by garment_id in Python.
        all_colour_rows = s.exec(
            select(GarmentColourRow).order_by(
                GarmentColourRow.garment_id,
                GarmentColourRow.position,
            )
        ).all()

    colours_by_garment: dict[str, list[GarmentColourRow]] = {}
    for c in all_colour_rows:
        colours_by_garment.setdefault(c.garment_id, []).append(c)

    for row in rows:
        colours = tuple(
            Colour(h=c.h, s=c.s, l=c.l, proportion=c.proportion)
            for c in colours_by_garment.get(row.id, [])
        )
        g = Garment(garment_type=row.type, colours=colours)
        index[id(g)] = row
        garments.append(g)

    return garments, index


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
    include_optional: frozenset[str],
    engine: Engine,
    rng: random.Random,
) -> SuggestionResult:
    """
    Build ranked outfit suggestions from the wardrobe.

    Parameters
    ----------
    include_optional:
        Optional slot keys (jersey, jacket, hat, accessory) the user wants
        included.  Required slots (top, bottom, socks, shoes) are always added.
    engine:
        SQLAlchemy engine bound to the application database.
    rng:
        Injected random.Random for deterministic shuffling of anchor candidates
        (FR-42, NFR-5).

    Raises
    ------
    InvalidSlotError
        Any key in *include_optional* is not a valid optional slot name.
    EmptySlotsError
        Any requested slot — required or chosen optional — has no garments
        in the wardrobe (FR-36).
    """
    unknown = [k for k in include_optional if k not in OPTIONAL_SLOTS]
    if unknown:
        raise InvalidSlotError(unknown)

    requested_slots = REQUIRED_SLOTS | frozenset(include_optional)

    wardrobe, garment_index = _load_wardrobe(engine)

    # Group by type to detect empty slots (FR-36).
    by_type: dict[str, int] = {}
    for g in wardrobe:
        by_type[g.garment_type] = by_type.get(g.garment_type, 0) + 1

    empty = [s for s in requested_slots if by_type.get(s, 0) == 0]
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
