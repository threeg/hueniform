"""
One-off data migration: v0.1.0 garment type values → FR-16 categories (HUE-065).

``migrate(engine)`` is idempotent and must be called before ``create_all`` in
``init_db``.  It detects whether any v0.1.0 type values remain and, if so,
performs a SQLite table-rename dance to bypass the old CHECK constraint while
applying the new one.

Storage imports nothing from matcher/detection/services/api (dependency rule).
"""

from __future__ import annotations

from sqlalchemy.engine import Engine

# v0.1.0 → FR-16 remapping (unambiguous mappings documented here; ambiguous
# defaults are also documented and remain re-editable via FR-46).
# Carry-over unchanged: jacket, socks, shoes, hat (same string in both models).
_REMAP: dict[str, str] = {
    "top":       "t_shirt",   # base-slot garment; unambiguous
    "bottom":    "trousers",  # lower_body default; re-categorisable (FR-46)
    "jersey":    "jumper",    # mid-slot garment; unambiguous
    "accessory": "glasses",   # minor-adornment default; re-categorisable (FR-46)
}

# All v0.1.0 type values that require migration.
_OLD_TYPES_SQL = ", ".join(f"'{t}'" for t in _REMAP)

# New allowlist inline (cannot import from matcher; mirrors ALL_CATEGORIES).
_NEW_TYPES: tuple[str, ...] = (
    "t_shirt", "vest", "long_sleeve",
    "shirt", "blouse", "polo",
    "jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat",
    "jacket", "blazer", "coat",
    "hat", "cap", "beanie",
    "glasses", "sunglasses",
    "earrings",
    "tie", "scarf",
    "necklace",
    "watch", "ring", "bracelet",
    "trousers", "jeans", "chinos", "shorts", "skirt",
    "dress", "jumpsuit",
    "belt",
    "socks",
    "shoes", "boots", "trainers", "sandals",
)
_NEW_TYPES_SQL = ", ".join(f"'{t}'" for t in _NEW_TYPES)

# CASE expression remapping old → new (ELSE keeps unchanged values).
_CASE_SQL = " ".join(
    f"WHEN '{old}' THEN '{new}'" for old, new in _REMAP.items()
)


def _needs_migration(cur) -> bool:
    """True iff the garments table exists and contains any v0.1.0 type values."""
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='garments'"
    )
    if cur.fetchone() is None:
        return False
    cur.execute(f"SELECT COUNT(*) FROM garments WHERE type IN ({_OLD_TYPES_SQL})")
    return cur.fetchone()[0] > 0


def migrate(engine: Engine) -> None:
    """
    Migrate v0.1.0 garment type values to FR-16 categories (idempotent).

    Uses a SQLite table-rename dance so the old CHECK constraint never fires
    on the new values:
      1. PRAGMA foreign_keys = OFF
      2. Create garments_v2 with new CHECK
      3. INSERT … SELECT with CASE remapping
      4. DROP garments; RENAME garments_v2 → garments
      5. Recreate idx_garments_type
      6. PRAGMA foreign_keys = ON

    garment_colours rows are untouched; FK integrity is preserved because
    garment_id values do not change and the table name is restored.
    """
    raw = engine.raw_connection()
    cur = raw.cursor()
    try:
        if not _needs_migration(cur):
            return

        cur.execute("PRAGMA foreign_keys = OFF")

        cur.execute("DROP TABLE IF EXISTS garments_v2")
        cur.execute(f"""
            CREATE TABLE garments_v2 (
                id TEXT NOT NULL PRIMARY KEY,
                type TEXT NOT NULL CHECK (type IN ({_NEW_TYPES_SQL})),
                image_file TEXT NOT NULL,
                thumbnail_file TEXT NOT NULL,
                created_at TEXT NOT NULL,
                regenerated_at TEXT
            )
        """)

        cur.execute(f"""
            INSERT INTO garments_v2
            SELECT
                id,
                CASE type {_CASE_SQL} ELSE type END,
                image_file, thumbnail_file, created_at, regenerated_at
            FROM garments
        """)

        cur.execute("DROP TABLE garments")
        cur.execute("ALTER TABLE garments_v2 RENAME TO garments")
        cur.execute("CREATE INDEX idx_garments_type ON garments (type)")

        raw.commit()
        cur.execute("PRAGMA foreign_keys = ON")
    finally:
        raw.close()
