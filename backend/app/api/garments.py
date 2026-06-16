"""
Garments endpoints (contract §2.5–§2.11, FR-6, FR-25, FR-29, FR-30, FR-31).

POST /api/garments — confirm a detection and save the garment.

Further endpoints (read, regenerate, delete) are added by later tickets.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.errors import AppError
from app.api.schemas import ColourOut, GarmentCreateRequest, GarmentDetail
from app.services.garment_service import (
    ColourIn as ServiceColourIn,
    GarmentResult,
    InvalidPaletteError,
    InvalidTypeError,
    TokenNotFoundError,
    confirm,
)

router = APIRouter()


def _to_detail(result: GarmentResult) -> GarmentDetail:
    """Convert a service GarmentResult to the API GarmentDetail response shape."""
    return GarmentDetail(
        id=result.id,
        type=result.type,
        colours=[
            ColourOut(
                h=c.h,
                s=c.s,
                l=c.l,
                family=c.family,
                neutral=c.neutral,
                hex=c.hex,
                proportion=c.proportion,
            )
            for c in result.colours
        ],
        thumbnail_url=f"/api/garments/{result.id}/thumbnail",
        image_url=f"/api/garments/{result.id}/image",
        created_at=result.created_at,
        regenerated_at=result.regenerated_at,
    )


@router.post("/garments", status_code=201, response_model=GarmentDetail)
def create_garment(body: GarmentCreateRequest, request: Request) -> GarmentDetail:
    """
    Consume a detection token and save the garment (contract §2.5).

    Validates the palette and type, atomically moves the staged image and
    creates the garment record.  The detection token is consumed on success.
    """
    settings = request.app.state.settings
    engine = request.app.state.engine

    service_colours = [
        ServiceColourIn(h=c.h, s=c.s, l=c.l, proportion=c.proportion)
        for c in body.colours
    ]

    try:
        result = confirm(
            token=body.detection_token,
            garment_type=body.type,
            colours=service_colours,
            staging_dir=settings.data_dir / "staging",
            images_dir=settings.data_dir / "images",
            thumbnails_dir=settings.data_dir / "thumbnails",
            engine=engine,
        )
    except TokenNotFoundError:
        raise AppError(
            404,
            "detection_not_found",
            "Detection token not found, expired or already consumed.",
        )
    except InvalidTypeError as e:
        raise AppError(422, "invalid_type", str(e))
    except InvalidPaletteError as e:
        raise AppError(422, "invalid_palette", str(e))

    return _to_detail(result)
