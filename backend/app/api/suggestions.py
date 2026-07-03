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
    InvalidAnchorError,
    InvalidCategoryFilterError,
    InvalidPinError,
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

    # Validate count range (FR-48; §2.12 error: 422 with details.count)
    if not (1 <= body.count <= 25):
        raise AppError(
            422,
            INVALID_REQUEST,
            f"count must be between 1 and 25, got {body.count}.",
            details={"count": body.count},
        )

    # Translate API request to service format:
    # bool values pass through; SlotConstraint becomes a list[str].
    slots_request: dict[str, bool | list[str]] = {}
    for key, value in body.slots.items():
        if isinstance(value, bool):
            slots_request[key] = value
        else:  # SlotConstraint
            slots_request[key] = value.categories

    anchor_family = body.anchor.family if body.anchor else None
    anchor_scheme = body.anchor.scheme if body.anchor else None

    try:
        result = suggest(
            slots_request,
            engine,
            random.Random(),
            count=body.count,
            pins=body.pins if body.pins else None,
            anchor_family=anchor_family,
            anchor_scheme=anchor_scheme,
        )
    except (InvalidSlotError, InvalidCategoryFilterError) as exc:
        raise AppError(422, INVALID_REQUEST, str(exc))
    except InvalidPinError as exc:
        raise AppError(
            422, INVALID_REQUEST, str(exc),
            details={"slot": exc.slot, "garment_id": exc.garment_id},
        )
    except InvalidAnchorError as exc:
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
            requested_count=body.count,
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

    return SuggestionResponse(requested_count=body.count, combinations=combinations_out)
