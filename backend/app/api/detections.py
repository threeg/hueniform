"""
Detections endpoints (contract §2.3–§2.4, FR-23, FR-24, FR-26, FR-27, FR-28).

POST /api/detections  — validate upload, run detection, return the proposal.
GET  /api/detections/{token}/image — serve the staged image for preview.

Nothing is written to the database at this stage (FR-24).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse

from app.api.errors import AppError
from app.api.schemas import ColourOut, DetectionImageInfo, DetectionResponse
from app.services.detection_service import (
    UnreadableImageError,
    get_staged_image_path,
    run_detection,
)

router = APIRouter()

_MAX_UPLOAD_BYTES: int = 20 * 1024 * 1024  # 20 MB (FR-23)

_ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)

_CONTENT_TYPE_TO_EXT: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


@router.post("/detections", status_code=201, response_model=DetectionResponse)
async def upload_and_detect(
    request: Request,
    file: UploadFile = File(...),
) -> DetectionResponse:
    """
    Accept a photograph, run colour detection, and return the proposal.

    The upload is validated for format (JPEG, PNG, WebP) and size (≤ 20 MB)
    before the pipeline runs.  Nothing is persisted to the database (FR-24).
    """
    content_type: str | None = file.content_type
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise AppError(
            400,
            "unsupported_format",
            "Only JPEG, PNG and WebP photographs are accepted (FR-23).",
        )

    ext: str = _CONTENT_TYPE_TO_EXT[content_type]

    # Read at most MAX + 1 bytes; any more means the upload exceeds the limit.
    data: bytes = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(data) > _MAX_UPLOAD_BYTES:
        raise AppError(413, "file_too_large", "Upload exceeds the 20 MB limit (FR-23).")

    settings = request.app.state.settings
    staging_dir: Path = settings.data_dir / "staging"

    try:
        result = run_detection(data, ext, content_type, staging_dir)
    except UnreadableImageError:
        raise AppError(
            400,
            "unreadable_image",
            "The uploaded image could not be read. Check that the file is not corrupt.",
        )

    return DetectionResponse(
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
    )


@router.get("/detections/{token}/image", include_in_schema=False)
async def get_detection_image(token: str, request: Request) -> FileResponse:
    """
    Serve the staged image bytes for preview (contract §2.4).

    Returns 404 if the token is unknown or the entry has expired.
    """
    settings = request.app.state.settings
    staging_dir: Path = settings.data_dir / "staging"

    found = get_staged_image_path(token, staging_dir)
    if found is None:
        raise AppError(404, "detection_not_found", "Detection not found or has expired.")

    image_path, media_type = found
    return FileResponse(image_path, media_type=media_type)
