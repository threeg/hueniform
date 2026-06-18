"""
Shared Pydantic schemas for the Hueniform API (contract §1.1–§1.2).

``ColourIn`` / ``ColourOut`` carry a single colour entry.
``GarmentSummary`` / ``GarmentDetail`` are the two garment response shapes.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator

# FR-16 garment types (contract §1.3).
GARMENT_TYPES: frozenset[str] = frozenset(
    {"top", "bottom", "jersey", "jacket", "socks", "shoes", "hat", "accessory"}
)


class ColourIn(BaseModel):
    """Colour values submitted by the client (contract §1.1)."""

    h: float
    s: float
    l: float
    proportion: int

    @field_validator("h")
    @classmethod
    def _h_range(cls, v: float) -> float:
        if not (0.0 <= v < 360.0):
            raise ValueError("h must satisfy 0 ≤ h < 360")
        return v

    @field_validator("s", "l")
    @classmethod
    def _sl_range(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("must satisfy 0 ≤ value ≤ 100")
        return v

    @field_validator("proportion")
    @classmethod
    def _proportion_range(cls, v: int) -> int:
        if not (1 <= v <= 100):
            raise ValueError("proportion must be in [1, 100]")
        return v


class ColourOut(BaseModel):
    """Colour values returned by the server (contract §1.1)."""

    h: float
    s: float
    l: float
    family: str
    neutral: bool
    hex: str
    proportion: int


class GarmentSummary(BaseModel):
    """Garment representation for lists and suggestion slots (contract §1.2)."""

    id: str
    type: str
    colours: list[ColourOut]
    thumbnail_url: str


class GarmentDetail(BaseModel):
    """Full garment representation for detail endpoints (contract §1.2)."""

    id: str
    type: str
    colours: list[ColourOut]
    thumbnail_url: str
    image_url: str
    created_at: str
    regenerated_at: str | None


class CanonicalHSL(BaseModel):
    """Canonical HSL stored when the user adds a colour by family alone (FR-29)."""

    h: float
    s: float
    l: float


class FamilyOut(BaseModel):
    """One colour family entry in the taxonomy response (contract §2.2)."""

    name: str
    neutral: bool
    canonical: CanonicalHSL
    # Present only on chromatic families; absent (not null) for neutrals via
    # response_model_exclude_none=True on the endpoint.
    representative_hue: float | None = None
    hue_arc: tuple[float, float] | None = None


class TaxonomyResponse(BaseModel):
    """Response body for GET /api/taxonomy (contract §2.2)."""

    families: list[FamilyOut]


class GarmentUpdateRequest(BaseModel):
    """Request body for PUT /api/garments/{id} (contract §2.10)."""

    regeneration_token: str
    type: str
    colours: list[ColourIn]


class RegenerationProposalResponse(BaseModel):
    """Response body for POST /api/garments/{id}/regenerate (contract §2.9).

    Same shape as DetectionResponse (§2.3) plus garment_id.
    """

    garment_id: str
    token: str
    expires_at: str
    fallback_used: bool
    image: DetectionImageInfo
    colours: list[ColourOut]


class InventoryResponse(BaseModel):
    """Response body for GET /api/garments (contract §2.6)."""

    garments: list[GarmentSummary]
    total: int


class GarmentCreateRequest(BaseModel):
    """Request body for POST /api/garments (contract §2.5)."""

    detection_token: str
    type: str
    colours: list[ColourIn]


class DetectionImageInfo(BaseModel):
    """Image metadata returned in the detection proposal (contract §2.3)."""

    url: str
    width: int
    height: int


class DetectionResponse(BaseModel):
    """Response body for POST /api/detections (contract §2.3)."""

    token: str
    expires_at: str
    fallback_used: bool
    image: DetectionImageInfo
    colours: list[ColourOut]


class SuggestionRequest(BaseModel):
    """Request body for POST /api/suggestions (contract §2.12)."""

    include: dict[str, bool] = {}


class EchoOut(BaseModel):
    """One minor-colour echo credited in ranking (FR-22, contract §2.12)."""

    family: str
    from_slot: str
    to_slot: str


class CombinationOut(BaseModel):
    """One ranked outfit combination in the suggestions response (contract §2.12)."""

    rank: int
    scheme: str | None
    fallback: bool
    slots: dict[str, GarmentSummary]
    echoes: list[EchoOut]
    explanation: str


class SuggestionResponse(BaseModel):
    """
    Response body for POST /api/suggestions (contract §2.12).

    On success: ``combinations`` is non-empty, ``explanation`` and ``hint`` absent.
    Zero-result: ``combinations`` is empty, ``explanation`` and ``hint`` are set.
    """

    combinations: list[CombinationOut]
    explanation: str | None = None
    hint: str | None = None

