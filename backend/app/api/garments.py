"""
Garments endpoints (contract §2.5–§2.11, FR-6, FR-25, FR-29–FR-35).

POST  /api/garments                    — confirm a detection and save the garment.
GET   /api/garments                    — list with optional type/family/limit/offset filters.
GET   /api/garments/{id}               — full Garment detail.
GET   /api/garments/{id}/image
GET   /api/garments/{id}/thumbnail
POST  /api/garments/{id}/regenerate    — re-detect; returns a garment-bound proposal.
PUT   /api/garments/{id}               — confirm regeneration token; replace in place.
DELETE /api/garments/{id}              — remove record and files.
"""

from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse

from app.api.errors import AppError
from app.api.schemas import (
    ColourOut,
    DetectionImageInfo,
    GarmentCreateRequest,
    GarmentDetail,
    GarmentSummary,
    GarmentUpdateRequest,
    InventoryResponse,
    RegenerationProposalResponse,
)
from app.services.detection_service import run_regeneration
from app.services.garment_service import (
    ColourIn as ServiceColourIn,
    GarmentNotFoundError,
    GarmentResult,
    InvalidFilterError,
    InvalidPaletteError,
    InvalidTypeError,
    RegenerationTokenError,
    TokenNotFoundError,
    confirm,
    confirm_regeneration,
    delete as garment_delete,
    get_garment,
    list_garments,
)

router = APIRouter()


# ── Response conversion helpers ───────────────────────────────────────────────

def _colours_out(result: GarmentResult) -> list[ColourOut]:
    return [
        ColourOut(
            h=c.h, s=c.s, l=c.l,
            family=c.family, neutral=c.neutral,
            hex=c.hex, proportion=c.proportion,
        )
        for c in result.colours
    ]


def _to_summary(result: GarmentResult) -> GarmentSummary:
    return GarmentSummary(
        id=result.id,
        type=result.type,
        colours=_colours_out(result),
        thumbnail_url=f"/api/garments/{result.id}/thumbnail",
    )


def _to_detail(result: GarmentResult) -> GarmentDetail:
    return GarmentDetail(
        id=result.id,
        type=result.type,
        colours=_colours_out(result),
        thumbnail_url=f"/api/garments/{result.id}/thumbnail",
        image_url=f"/api/garments/{result.id}/image",
        created_at=result.created_at,
        regenerated_at=result.regenerated_at,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

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


@router.get("/garments", response_model=InventoryResponse)
def list_garments_endpoint(
    request: Request,
    type: str | None = Query(default=None),
    family: str | None = Query(default=None),
    limit: int = Query(default=500, ge=0),
    offset: int = Query(default=0, ge=0),
) -> InventoryResponse:
    """
    Return a paginated inventory list with optional AND filters (contract §2.6, FR-35).

    ``family`` matches a garment if **any** of its colours belongs to that family.
    Unknown ``type`` or ``family`` values → ``422 invalid_filter``.
    """
    engine = request.app.state.engine

    try:
        page = list_garments(
            engine,
            type_filter=type,
            family_filter=family,
            limit=limit,
            offset=offset,
        )
    except InvalidFilterError as e:
        raise AppError(422, "invalid_filter", str(e))

    return InventoryResponse(
        garments=[_to_summary(g) for g in page.garments],
        total=page.total,
    )


@router.get("/garments/{garment_id}", response_model=GarmentDetail)
def get_garment_endpoint(garment_id: str, request: Request) -> GarmentDetail:
    """Return the full Garment detail (contract §2.7)."""
    engine = request.app.state.engine

    try:
        result = get_garment(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")

    return _to_detail(result)


@router.get("/garments/{garment_id}/image", include_in_schema=False)
def get_garment_image(garment_id: str, request: Request) -> FileResponse:
    """Serve the stored garment photograph (contract §2.8)."""
    engine = request.app.state.engine
    settings = request.app.state.settings

    try:
        result = get_garment(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")

    return FileResponse(settings.data_dir / "images" / result.image_file)


@router.get("/garments/{garment_id}/thumbnail", include_in_schema=False)
def get_garment_thumbnail(garment_id: str, request: Request) -> FileResponse:
    """Serve the garment thumbnail (contract §2.8)."""
    engine = request.app.state.engine
    settings = request.app.state.settings

    try:
        result = get_garment(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")

    return FileResponse(settings.data_dir / "thumbnails" / result.thumbnail_file)


@router.post("/garments/{garment_id}/regenerate", response_model=RegenerationProposalResponse)
def regenerate_garment(garment_id: str, request: Request) -> RegenerationProposalResponse:
    """
    Re-run detection on the stored photograph and return a garment-bound proposal
    (contract §2.9, FR-26, FR-33).

    The stored record and image are not modified until the client confirms with
    PUT /api/garments/{id}.
    """
    settings = request.app.state.settings
    engine = request.app.state.engine

    try:
        garment = get_garment(garment_id, engine)
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")

    result = run_regeneration(
        garment_id=garment_id,
        image_file=garment.image_file,
        images_dir=settings.data_dir / "images",
        staging_dir=settings.data_dir / "staging",
    )

    return RegenerationProposalResponse(
        garment_id=garment_id,
        token=result.token,
        expires_at=result.expires_at,
        fallback_used=result.fallback_used,
        image=DetectionImageInfo(
            url=f"/api/detections/{result.token}/image",
            width=result.image_width,
            height=result.image_height,
        ),
        colours=[
            ColourOut(
                h=c.h, s=c.s, l=c.l,
                family=c.family, neutral=c.neutral,
                hex=c.hex, proportion=c.proportion,
            )
            for c in result.colours
        ],
    )


@router.put("/garments/{garment_id}", response_model=GarmentDetail)
def update_garment(
    garment_id: str,
    body: GarmentUpdateRequest,
    request: Request,
) -> GarmentDetail:
    """
    Confirm a regeneration token and replace palette + type in place
    (contract §2.10, FR-32, FR-33).

    This is the only mutation path — there is no field-edit endpoint (FR-32).
    The garment keeps the same id and photograph; only palette and type change.
    """
    settings = request.app.state.settings
    engine = request.app.state.engine

    service_colours = [
        ServiceColourIn(h=c.h, s=c.s, l=c.l, proportion=c.proportion)
        for c in body.colours
    ]

    try:
        result = confirm_regeneration(
            garment_id=garment_id,
            token=body.regeneration_token,
            garment_type=body.type,
            colours=service_colours,
            staging_dir=settings.data_dir / "staging",
            images_dir=settings.data_dir / "images",
            engine=engine,
        )
    except RegenerationTokenError:
        raise AppError(
            409,
            "invalid_regeneration_token",
            "Regeneration token is absent, expired, consumed, or bound to a different garment.",
        )
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")
    except InvalidTypeError as e:
        raise AppError(422, "invalid_type", str(e))
    except InvalidPaletteError as e:
        raise AppError(422, "invalid_palette", str(e))

    return _to_detail(result)


@router.delete("/garments/{garment_id}", status_code=204)
def delete_garment(garment_id: str, request: Request) -> None:
    """Remove the garment record, photograph and thumbnail (contract §2.11, FR-34)."""
    settings = request.app.state.settings
    engine = request.app.state.engine

    try:
        garment_delete(
            garment_id=garment_id,
            images_dir=settings.data_dir / "images",
            thumbnails_dir=settings.data_dir / "thumbnails",
            engine=engine,
        )
    except GarmentNotFoundError:
        raise AppError(404, "garment_not_found", "Garment not found.")
