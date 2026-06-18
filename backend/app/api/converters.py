"""
Shared API response conversion helpers.

These helpers centralise the mapping from service layer objects to API
schema objects so that each transformation lives in exactly one place.
"""

from __future__ import annotations

from sqlalchemy.engine import Engine

from app.api.errors import GARMENT_NOT_FOUND, AppError
from app.api.schemas import ColourOut, GarmentSummary
from app.services.garment_service import (
    GarmentMetadata,
    GarmentNotFoundError,
    GarmentResult,
    get_garment,
    get_garment_metadata,
)


def colour_out(c: object) -> ColourOut:
    """Convert any colour-like object (SavedColour, ColourProposal) to ColourOut."""
    return ColourOut(
        h=c.h, s=c.s, l=c.l,  # type: ignore[attr-defined]
        family=c.family, neutral=c.neutral,  # type: ignore[attr-defined]
        hex=c.hex, proportion=c.proportion,  # type: ignore[attr-defined]
    )


def garment_to_summary(result: GarmentResult) -> GarmentSummary:
    """Convert a GarmentResult to a GarmentSummary (list / suggestion-slot shape)."""
    return GarmentSummary(
        id=result.id,
        type=result.type,
        colours=[colour_out(c) for c in result.colours],
        thumbnail_url=f"/api/garments/{result.id}/thumbnail",
    )


def require_garment(garment_id: str, engine: Engine) -> GarmentResult:
    """Fetch a garment or raise AppError 404 if absent."""
    try:
        return get_garment(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, GARMENT_NOT_FOUND, "Garment not found.")


def require_garment_metadata(garment_id: str, engine: Engine) -> GarmentMetadata:
    """Fetch lightweight garment metadata (file paths only) or raise AppError 404."""
    try:
        return get_garment_metadata(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, GARMENT_NOT_FOUND, "Garment not found.")
