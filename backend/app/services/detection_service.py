"""
Detection service: stage upload → run pipeline → return proposal (architecture §2.4, §4.1).

Orchestrates the upload-and-detect step (FR-24, FR-26, FR-27, FR-28):
  1. Run the pipeline on the supplied image bytes.
  2. Convert each ``ColourEntry`` to a ``ColourProposal`` (adds ``hex`` and ``neutral``).
  3. Stage the image + proposal sidecar via ``storage.staging``.
  4. Return a ``DetectionResult`` containing token, expiry, colours and image dimensions.

Nothing is written to the database at this stage (FR-24).  The confirm step
(HUE-022) moves the staged image and writes to the DB.

The ``segmenter`` and ``clusterer`` parameters are injectable seams (§6.2) that
allow the default gate to drive the pipeline deterministically without the real
rembg model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from app.detection.pipeline import DetectionProposal, detect
from app.matcher.colour import hsl_to_hex
from app.matcher.taxonomy import is_neutral
from app.storage import staging

_EXT_TO_CONTENT_TYPE: dict[str, str] = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


# ── Value types ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ColourProposal:
    """Single-colour entry in the detection result, matching API contract §2.3."""
    h: float
    s: float
    l: float
    family: str
    neutral: bool
    hex: str     # CSS hex string, e.g. "#2CADA0"
    proportion: int


@dataclass(frozen=True)
class DetectionResult:
    """Return value of the detection service (both upload and regeneration flows)."""
    token: str
    expires_at: str   # ISO 8601 UTC, copied from the sidecar
    fallback_used: bool
    image_width: int
    image_height: int
    colours: tuple[ColourProposal, ...]
    garment_id: str | None = None


# ── Internal helpers ───────────────────────────────────────────────────────────

def _build_colour_proposal(entry: Any) -> ColourProposal:
    return ColourProposal(
        h=entry.h,
        s=entry.s,
        l=entry.l,
        family=entry.family,
        neutral=is_neutral(entry.family),
        hex=hsl_to_hex(entry.h, entry.s, entry.l),
        proportion=entry.proportion,
    )


def _colours_to_proposal_dict(colours: tuple[ColourProposal, ...]) -> list[dict[str, Any]]:
    return [
        {
            "h": c.h,
            "s": c.s,
            "l": c.l,
            "family": c.family,
            "neutral": c.neutral,
            "hex": c.hex,
            "proportion": c.proportion,
        }
        for c in colours
    ]


# ── Public API ─────────────────────────────────────────────────────────────────

def run_detection(
    image_data: bytes,
    ext: str,
    content_type: str,
    staging_dir: Path,
    *,
    garment_id: str | None = None,
    segmenter: Callable | None = None,
    clusterer: Callable | None = None,
) -> DetectionResult:
    """
    Run the detection pipeline on *image_data* and stage the result.

    Returns a ``DetectionResult`` with the token, expiry (copied from the
    sidecar), colours, and image dimensions.  Nothing is written to the DB
    (FR-24).
    """
    raw: DetectionProposal = detect(
        image_data, segmenter=segmenter, clusterer=clusterer
    )
    colours = tuple(_build_colour_proposal(c) for c in raw.colours)

    token = staging.stage(
        data=image_data,
        ext=ext,
        content_type=content_type,
        fallback_used=raw.fallback_used,
        proposal={"colours": _colours_to_proposal_dict(colours)},
        staging_dir=staging_dir,
        garment_id=garment_id,
    )

    sidecar_path = staging_dir / f"{token}.json"
    expires_at: str = json.loads(sidecar_path.read_text(encoding="utf-8"))["expires_at"]

    return DetectionResult(
        token=token,
        expires_at=expires_at,
        fallback_used=raw.fallback_used,
        image_width=raw.width,
        image_height=raw.height,
        colours=colours,
        garment_id=garment_id,
    )


def run_regeneration(
    garment_id: str,
    image_file: str,
    images_dir: Path,
    staging_dir: Path,
    *,
    segmenter: Callable | None = None,
    clusterer: Callable | None = None,
) -> DetectionResult:
    """
    Re-run detection on a stored garment photograph and return a bound token.

    Loads the image from ``images_dir / image_file``, derives the extension and
    content type, and delegates to ``run_detection`` with the supplied
    ``garment_id`` so the staging sidecar is bound to that garment.
    """
    ext = image_file.rsplit(".", 1)[-1].lower()
    content_type = _EXT_TO_CONTENT_TYPE.get(ext, "image/jpeg")
    image_data = (images_dir / image_file).read_bytes()
    return run_detection(
        image_data,
        ext,
        content_type,
        staging_dir,
        garment_id=garment_id,
        segmenter=segmenter,
        clusterer=clusterer,
    )
