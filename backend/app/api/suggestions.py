"""
Suggestions endpoint (contract §2.12, FR-17, FR-36–FR-43, NFR-5).

POST /api/suggestions — return up to three ranked outfit combinations, a
zero-result shape, or a 409 if a requested slot is empty.
"""

from __future__ import annotations

import random

from fastapi import APIRouter, Request

from app.api.converters import garment_to_summary
from app.api.errors import EMPTY_SLOTS, INVALID_REQUEST, AppError
from app.api.schemas import (
    CombinationOut,
    EchoOut,
    SlotConstraint,
    SuggestionRequest,
    SuggestionResponse,
)
from app.services.garment_service import get_garments_by_ids
from app.services.suggestion_service import (
    EmptySlotsError,
    InvalidCategoryFilterError,
    InvalidSlotError,
    suggest,
)

router = APIRouter()


@router.post("/suggestions", response_model=SuggestionResponse)
def create_suggestion(body: SuggestionRequest, request: Request) -> SuggestionResponse:
    """
    Return up to three ranked outfit combinations (contract §2.12).

    FR-51 default slots (base, lower_body, socks, shoes) are always the starting
    point.  ``slots`` adjusts the selection and adds per-category constraints (FR-52).
    Unknown slot keys or deselecting the mandatory slot → ``422 invalid_request``.
    An empty requested slot → ``409 empty_slots`` (FR-36).
    """
    engine = request.app.state.engine

    # Translate API request to service format:
    # bool values pass through; SlotConstraint becomes a list[str].
    slots_request: dict[str, bool | list[str]] = {}
    for key, value in body.slots.items():
        if isinstance(value, bool):
            slots_request[key] = value
        else:  # SlotConstraint
            slots_request[key] = value.categories

    try:
        result = suggest(slots_request, engine, random.Random())
    except (InvalidSlotError, InvalidCategoryFilterError) as exc:
        raise AppError(422, INVALID_REQUEST, str(exc))
    except EmptySlotsError as exc:
        raise AppError(
            409,
            EMPTY_SLOTS,
            str(exc),
            details={"empty_slots": exc.empty_slots},
        )

    if not result.combinations:
        return SuggestionResponse(
            combinations=[],
            explanation=result.zero_explanation,
            hint=result.hint,
        )

    # Batch-load colour data for all garments that appear in the combinations.
    garment_ids = list({
        row.id
        for combo in result.combinations
        for row in combo.slots.values()
    })
    garment_results = get_garments_by_ids(garment_ids, engine)

    combinations_out = []
    for combo in result.combinations:
        slots_out = {
            slot: garment_to_summary(garment_results[row.id])
            for slot, row in combo.slots.items()
        }
        combinations_out.append(CombinationOut(
            rank=combo.rank,
            scheme=combo.scheme,
            fallback=combo.fallback,
            slots=slots_out,
            echoes=[
                EchoOut(family=e.family, from_slot=e.from_slot, to_slot=e.to_slot)
                for e in combo.echoes
            ],
            explanation=combo.explanation,
        ))

    return SuggestionResponse(combinations=combinations_out)
