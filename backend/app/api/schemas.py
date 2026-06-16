"""
Shared Pydantic schemas for the Hueniform API (contract §1.1–§1.2).

``ColourIn`` / ``ColourOut`` carry a single colour entry.
``GarmentSummary`` / ``GarmentDetail`` are the two garment response shapes.
``validate_palette`` enforces the FR-6 count + sum-to-100 rule; call it from
endpoint handlers before delegating to a service.
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


def validate_palette(colours: list[ColourIn]) -> None:
    """
    Validate FR-6 palette constraints.

    Raises ``ValueError`` if:
    - The list has fewer than 1 or more than 4 entries.
    - The proportions do not sum to exactly 100.
    """
    if not (1 <= len(colours) <= 4):
        raise ValueError(
            f"A palette must have 1–4 colours (FR-6); got {len(colours)}"
        )
    total = sum(c.proportion for c in colours)
    if total != 100:
        raise ValueError(
            f"Colour proportions must sum to exactly 100 (FR-6); got {total}"
        )
