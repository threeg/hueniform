"""
Garment service: confirm-save (FR-1, FR-25, FR-29, FR-30) and delete (FR-34).

``confirm`` consumes the detection token, re-derives every family server-side
from submitted HSL (FR-1 — never trust a client family), validates the palette,
atomically moves the staged image, generates the thumbnail and inserts both
database tables.  A mid-save failure leaves no rows and no files (FR-30).

``delete`` removes the garment record (cascade to colour rows) and both files.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session

from app.matcher.colour import hsl_to_hex
from app.matcher.taxonomy import classify, is_neutral
from app.storage import staging
from app.storage.image_store import generate_thumbnail
from app.storage.models import GARMENT_TYPES, GarmentColourRow, GarmentRow


# ── Errors ────────────────────────────────────────────────────────────────────

class TokenNotFoundError(Exception):
    """Staging token absent, expired or already consumed."""


class InvalidPaletteError(Exception):
    """Colour palette failed validation (count, sum or value ranges)."""


class InvalidTypeError(Exception):
    """Garment type is not in the FR-16 allowlist."""


class GarmentNotFoundError(Exception):
    """No garment with this id exists in the database."""


# ── Value types ───────────────────────────────────────────────────────────────

@dataclass
class ColourIn:
    """Submitted colour from the confirm request (h, s, l + proportion only)."""
    h: float
    s: float
    l: float
    proportion: int


@dataclass(frozen=True)
class SavedColour:
    """Stored colour with server-derived family (FR-1) and computed hex."""
    h: float
    s: float
    l: float
    family: str
    neutral: bool
    hex: str
    proportion: int


@dataclass(frozen=True)
class GarmentResult:
    """Return value of ``confirm``; matches the API §1.2 Garment shape."""
    id: str
    type: str
    created_at: str
    regenerated_at: str | None
    image_file: str
    thumbnail_file: str
    colours: tuple[SavedColour, ...]


# ── Validation ────────────────────────────────────────────────────────────────

_GARMENT_TYPES = frozenset(GARMENT_TYPES)


def _validate_palette(colours: list[ColourIn]) -> None:
    if not (1 <= len(colours) <= 4):
        raise InvalidPaletteError(
            f"A palette must have 1–4 colours; got {len(colours)}."
        )
    for i, c in enumerate(colours):
        if not (0.0 <= c.h < 360.0):
            raise InvalidPaletteError(f"colours[{i}].h = {c.h} out of range [0, 360).")
        if not (0.0 <= c.s <= 100.0):
            raise InvalidPaletteError(f"colours[{i}].s = {c.s} out of range [0, 100].")
        if not (0.0 <= c.l <= 100.0):
            raise InvalidPaletteError(f"colours[{i}].l = {c.l} out of range [0, 100].")
        if not isinstance(c.proportion, int) or not (1 <= c.proportion <= 100):
            raise InvalidPaletteError(
                f"colours[{i}].proportion = {c.proportion} must be an integer 1–100."
            )
    total = sum(c.proportion for c in colours)
    if total != 100:
        raise InvalidPaletteError(
            f"Proportions must sum to exactly 100; got {total}."
        )


# ── Public API ────────────────────────────────────────────────────────────────

def confirm(
    token: str,
    garment_type: str,
    colours: list[ColourIn],
    staging_dir: Path,
    images_dir: Path,
    thumbnails_dir: Path,
    engine: Engine,
) -> GarmentResult:
    """
    Consume *token*, validate the palette and save the garment.

    Raises
    ------
    TokenNotFoundError
        Token absent, expired or already consumed.
    InvalidTypeError
        *garment_type* not in the FR-16 allowlist.
    InvalidPaletteError
        Colour count, ranges or sum failed validation.
    """
    entry = staging.load(token, staging_dir)
    if entry is None:
        raise TokenNotFoundError(f"Detection token '{token}' not found or expired.")

    if garment_type not in _GARMENT_TYPES:
        raise InvalidTypeError(
            f"'{garment_type}' is not a valid garment type. "
            f"Allowed: {', '.join(sorted(_GARMENT_TYPES))}."
        )

    _validate_palette(colours)

    # Derive families once — used in both the DB insert and the return value (FR-1).
    families = [classify(c.h, c.s, c.l) for c in colours]

    garment_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    # Move staged image → images_dir (deletes sidecar; token is consumed from here).
    dst = staging.move(token, entry.ext, garment_id, staging_dir, images_dir)
    image_file = dst.name

    try:
        thumbnail_file = generate_thumbnail(dst, thumbnails_dir, garment_id)
    except Exception:
        dst.unlink(missing_ok=True)
        raise

    try:
        _insert_garment(
            engine, garment_id, garment_type, image_file, thumbnail_file,
            created_at, colours, families,
        )
    except Exception:
        dst.unlink(missing_ok=True)
        (thumbnails_dir / thumbnail_file).unlink(missing_ok=True)
        raise

    saved_colours = tuple(
        SavedColour(
            h=c.h,
            s=c.s,
            l=c.l,
            family=f,
            neutral=is_neutral(f),
            hex=hsl_to_hex(c.h, c.s, c.l),
            proportion=c.proportion,
        )
        for c, f in zip(colours, families)
    )

    return GarmentResult(
        id=garment_id,
        type=garment_type,
        created_at=created_at,
        regenerated_at=None,
        image_file=image_file,
        thumbnail_file=thumbnail_file,
        colours=saved_colours,
    )


def delete(
    garment_id: str,
    images_dir: Path,
    thumbnails_dir: Path,
    engine: Engine,
) -> None:
    """
    Remove the garment record (cascade to colour rows) and both files (FR-34).

    Raises ``GarmentNotFoundError`` if no such garment exists.
    """
    with Session(engine) as session:
        row = session.get(GarmentRow, garment_id)
        if row is None:
            raise GarmentNotFoundError(f"Garment '{garment_id}' not found.")

        image_file = row.image_file
        thumbnail_file = row.thumbnail_file

        session.delete(row)
        session.commit()

    (images_dir / image_file).unlink(missing_ok=True)
    (thumbnails_dir / thumbnail_file).unlink(missing_ok=True)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _insert_garment(
    engine: Engine,
    garment_id: str,
    garment_type: str,
    image_file: str,
    thumbnail_file: str,
    created_at: str,
    colours: list[ColourIn],
    families: list[str],
) -> None:
    with Session(engine) as session:
        garment = GarmentRow(
            id=garment_id,
            type=garment_type,
            image_file=image_file,
            thumbnail_file=thumbnail_file,
            created_at=created_at,
        )
        session.add(garment)
        session.flush()  # make garment row visible before FK child rows

        for i, (c, f) in enumerate(zip(colours, families)):
            session.add(
                GarmentColourRow(
                    garment_id=garment_id,
                    position=i,
                    h=c.h,
                    s=c.s,
                    l=c.l,
                    family=f,
                    proportion=c.proportion,
                )
            )

        session.commit()
