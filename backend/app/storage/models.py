"""
SQLModel table declarations for the two persistence tables (architecture §3.1).

``GarmentRow``       — the ``garments`` table (one row per saved garment).
``GarmentColourRow`` — the ``garment_colours`` table (1–4 rows per garment, FR-6).

Storage imports nothing from matcher/detection/services/api (dependency rule,
import-linter contract 4).
"""

from __future__ import annotations

import sqlalchemy as sa
import sqlmodel as sm

# ── Garment type allowlist (FR-16) ────────────────────────────────────────────

GARMENT_TYPES: tuple[str, ...] = (
    "top", "bottom", "jersey", "jacket", "socks", "shoes", "hat", "accessory"
)

_TYPE_IN = ", ".join(f"'{t}'" for t in GARMENT_TYPES)
_TYPE_CHECK_SQL = f"type IN ({_TYPE_IN})"

# ── garments ──────────────────────────────────────────────────────────────────


class GarmentRow(sm.SQLModel, table=True):
    """One row per confirmed garment (architecture §3.1)."""

    __tablename__ = "garments"
    __table_args__ = (
        sa.CheckConstraint(_TYPE_CHECK_SQL, name="ck_garment_type"),
        sa.Index("idx_garments_type", "type"),
    )

    id: str = sm.Field(primary_key=True)
    type: str = sm.Field(nullable=False)
    image_file: str = sm.Field(nullable=False)
    thumbnail_file: str = sm.Field(nullable=False)
    created_at: str = sm.Field(nullable=False)
    regenerated_at: str | None = sm.Field(default=None, nullable=True)


# ── garment_colours ───────────────────────────────────────────────────────────


class GarmentColourRow(sm.SQLModel, table=True):
    """
    1–4 colour rows per garment (FR-6), position-ordered descending proportion.

    ``family`` is stored denormalised (derived server-side on write, FR-1) so
    the FR-35 family filter resolves as an indexed query.
    """

    __tablename__ = "garment_colours"
    __table_args__ = (
        sa.CheckConstraint("proportion BETWEEN 1 AND 100", name="ck_proportion"),
        sa.Index("idx_colours_family", "family"),
        sa.Index("idx_colours_garment", "garment_id"),
    )

    id: int | None = sm.Field(default=None, primary_key=True)

    # ON DELETE CASCADE fires at the database level when PRAGMA foreign_keys = ON.
    garment_id: str = sm.Field(
        sa_column=sa.Column(
            sa.Text,
            sa.ForeignKey("garments.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    position: int = sm.Field(nullable=False)
    h: float = sm.Field(nullable=False)
    s: float = sm.Field(nullable=False)
    l: float = sm.Field(nullable=False)
    family: str = sm.Field(nullable=False)
    proportion: int = sm.Field(nullable=False)
