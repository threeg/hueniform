"""GET /api/taxonomy — colour family taxonomy for UI pickers and legend (FR-1–FR-5, FR-29)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import FamilyOut, TaxonomyResponse
from app.services.taxonomy_service import list_families

router = APIRouter()


@router.get(
    "/taxonomy",
    response_model=TaxonomyResponse,
    response_model_exclude_none=True,
)
def get_taxonomy() -> TaxonomyResponse:
    """Return all nineteen colour families with canonical HSL (contract §2.2)."""
    return TaxonomyResponse(
        families=[FamilyOut(**fam) for fam in list_families()]
    )
