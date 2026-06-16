"""
Garment service: confirm-save (FR-1, FR-25, FR-29, FR-30), delete (FR-34) and
regeneration confirmation (FR-32, FR-33).

``confirm`` consumes the detection token, re-derives every family server-side
from submitted HSL (FR-1 — never trust a client family), validates the palette,
atomically moves the staged image, generates the thumbnail and inserts both
database tables.  A mid-save failure leaves no rows and no files (FR-30).

``confirm_regeneration`` accepts a garment-bound regeneration token, validates
it, and replaces the palette and type in place — same id, same image (FR-33).
The token requirement is the FR-32 enforcement: there is no field-edit path.

``delete`` removes the garment record (cascade to colour rows) and both files.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.matcher.colour import hsl_to_hex
from app.matcher.taxonomy import FAMILIES, classify, is_neutral
from app.storage import staging
from app.storage.image_store import generate_thumbnail
from app.storage.models import GARMENT_TYPES, GarmentColourRow, GarmentRow

_VALID_FAMILIES: frozenset[str] = frozenset(f.name for f in FAMILIES)


# ── Errors ────────────────────────────────────────────────────────────────────

class TokenNotFoundError(Exception):
    """Staging token absent, expired or already consumed."""


class InvalidPaletteError(Exception):
    """Colour palette failed validation (count, sum or value ranges)."""


class InvalidTypeError(Exception):
    """Garment type is not in the FR-16 allowlist."""


class GarmentNotFoundError(Exception):
    """No garment with this id exists in the database."""


class InvalidFilterError(Exception):
    """Unknown type or family value used as a list filter."""


class RegenerationTokenError(Exception):
    """Token absent, expired, consumed, or bound to a different garment (§2.10 → 409)."""


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


@dataclass(frozen=True)
class GarmentPage:
    """Paginated result from ``list_garments``."""
    garments: tuple[GarmentResult, ...]
    total: int


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


# ── Internal helpers ──────────────────────────────────────────────────────────

def _row_to_result(row: GarmentRow, colour_rows: list[GarmentColourRow]) -> GarmentResult:
    """Convert DB rows to a ``GarmentResult``, computing hex and neutral flag."""
    saved_colours = tuple(
        SavedColour(
            h=c.h,
            s=c.s,
            l=c.l,
            family=c.family,
            neutral=is_neutral(c.family),
            hex=hsl_to_hex(c.h, c.s, c.l),
            proportion=c.proportion,
        )
        for c in colour_rows
    )
    return GarmentResult(
        id=row.id,
        type=row.type,
        created_at=row.created_at,
        regenerated_at=row.regenerated_at,
        image_file=row.image_file,
        thumbnail_file=row.thumbnail_file,
        colours=saved_colours,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def list_garments(
    engine: Engine,
    *,
    type_filter: str | None = None,
    family_filter: str | None = None,
    limit: int = 500,
    offset: int = 0,
) -> GarmentPage:
    """
    Return a paginated list of garments matching the optional filters.

    Raises ``InvalidFilterError`` for unknown type or family values.
    ``total`` reflects the full match count before pagination.
    """
    if type_filter is not None and type_filter not in _GARMENT_TYPES:
        raise InvalidFilterError(f"Unknown garment type: '{type_filter}'.")
    if family_filter is not None and family_filter not in _VALID_FAMILIES:
        raise InvalidFilterError(f"Unknown colour family: '{family_filter}'.")

    with Session(engine) as session:
        # Build the family subquery: IDs of garments that have at least one
        # colour row with the requested family (matches any role — FR-35).
        family_subq = None
        if family_filter is not None:
            family_subq = (
                select(GarmentColourRow.garment_id)
                .where(GarmentColourRow.family == family_filter)
                .distinct()
            )

        # Fetch all matching garment rows ordered by creation time.
        all_stmt = select(GarmentRow).order_by(GarmentRow.created_at)
        if type_filter is not None:
            all_stmt = all_stmt.where(GarmentRow.type == type_filter)
        if family_subq is not None:
            all_stmt = all_stmt.where(GarmentRow.id.in_(family_subq))

        all_rows = session.exec(all_stmt).all()
        total = len(all_rows)

        # Apply pagination in Python — avoids a second round-trip for count.
        paged = all_rows[offset : offset + limit]
        if not paged:
            return GarmentPage(garments=(), total=total)

        # Bulk-load colours for the page only (not the full match set).
        page_ids = [r.id for r in paged]
        colour_rows = session.exec(
            select(GarmentColourRow)
            .where(GarmentColourRow.garment_id.in_(page_ids))
            .order_by(GarmentColourRow.garment_id, GarmentColourRow.position)
        ).all()

    colours_by_id: dict[str, list[GarmentColourRow]] = {}
    for c in colour_rows:
        colours_by_id.setdefault(c.garment_id, []).append(c)

    garments = tuple(
        _row_to_result(row, colours_by_id.get(row.id, []))
        for row in paged
    )
    return GarmentPage(garments=garments, total=total)


def get_garment(garment_id: str, engine: Engine) -> GarmentResult:
    """
    Return the full ``GarmentResult`` for *garment_id*.

    Raises ``GarmentNotFoundError`` if no such garment exists.
    """
    with Session(engine) as session:
        row = session.get(GarmentRow, garment_id)
        if row is None:
            raise GarmentNotFoundError(f"Garment '{garment_id}' not found.")
        colour_rows = session.exec(
            select(GarmentColourRow)
            .where(GarmentColourRow.garment_id == garment_id)
            .order_by(GarmentColourRow.position)
        ).all()
    return _row_to_result(row, colour_rows)


def get_garments_by_ids(
    garment_ids: list[str],
    engine: Engine,
) -> dict[str, GarmentResult]:
    """
    Batch-load ``GarmentResult`` objects for the given IDs in two queries.

    Returns a dict keyed by garment id.  IDs not found in the database are
    silently omitted (the caller must handle missing entries if needed).
    """
    if not garment_ids:
        return {}
    with Session(engine) as session:
        rows = session.exec(
            select(GarmentRow).where(GarmentRow.id.in_(garment_ids))
        ).all()
        colour_rows = session.exec(
            select(GarmentColourRow)
            .where(GarmentColourRow.garment_id.in_(garment_ids))
            .order_by(GarmentColourRow.garment_id, GarmentColourRow.position)
        ).all()

    colours_by_garment: dict[str, list[GarmentColourRow]] = {}
    for c in colour_rows:
        colours_by_garment.setdefault(c.garment_id, []).append(c)

    return {
        row.id: _row_to_result(row, colours_by_garment.get(row.id, []))
        for row in rows
    }


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


def confirm_regeneration(
    garment_id: str,
    token: str,
    garment_type: str,
    colours: list[ColourIn],
    staging_dir: Path,
    images_dir: Path,
    engine: Engine,
) -> GarmentResult:
    """
    Confirm a regeneration: validate the token, replace palette + type in place (FR-33).

    The token must be bound to *garment_id*; absent / expired / consumed / foreign
    tokens all raise ``RegenerationTokenError`` (FR-32 — no field-edit path).

    Raises
    ------
    RegenerationTokenError
        Token absent, expired, consumed, or bound to a different garment (→ 409).
    GarmentNotFoundError
        No garment with *garment_id* exists (→ 404).
    InvalidTypeError
        *garment_type* not in the FR-16 allowlist.
    InvalidPaletteError
        Colour count, ranges or sum failed validation.
    """
    entry = staging.load(token, staging_dir)
    if entry is None or entry.garment_id != garment_id:
        raise RegenerationTokenError(
            "Regeneration token is absent, expired, consumed, or bound to a different garment."
        )

    if garment_type not in _GARMENT_TYPES:
        raise InvalidTypeError(
            f"'{garment_type}' is not a valid garment type. "
            f"Allowed: {', '.join(sorted(_GARMENT_TYPES))}."
        )

    _validate_palette(colours)

    families = [classify(c.h, c.s, c.l) for c in colours]
    regenerated_at = datetime.now(timezone.utc).isoformat()

    # Consume the token: move the staged copy over the stored image (same content).
    staging.move(token, entry.ext, garment_id, staging_dir, images_dir)

    return _update_garment_in_place(
        engine, garment_id, garment_type, colours, families, regenerated_at
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


def _update_garment_in_place(
    engine: Engine,
    garment_id: str,
    garment_type: str,
    colours: list[ColourIn],
    families: list[str],
    regenerated_at: str,
) -> GarmentResult:
    with Session(engine) as session:
        row = session.get(GarmentRow, garment_id)
        if row is None:
            raise GarmentNotFoundError(f"Garment '{garment_id}' not found.")

        # Capture immutable fields before any modifications.
        created_at = row.created_at
        image_file = row.image_file
        thumbnail_file = row.thumbnail_file

        # Update in place — same id, same image (FR-33).
        row.type = garment_type
        row.regenerated_at = regenerated_at
        session.add(row)

        # Replace colour rows: delete old, flush, insert new.
        old = session.exec(
            select(GarmentColourRow).where(GarmentColourRow.garment_id == garment_id)
        ).all()
        for oc in old:
            session.delete(oc)
        session.flush()

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
        regenerated_at=regenerated_at,
        image_file=image_file,
        thumbnail_file=thumbnail_file,
        colours=saved_colours,
    )
