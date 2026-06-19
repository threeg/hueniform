"""
Tests for the v0.1.0 → FR-16 storage migration (HUE-065, §7.5).

A helper builds a v0.1.0-schema SQLite database in a tmp_path, then
``migrate()`` is called and its effects are verified: type remapping,
pass-through values, unchanged IDs / image / colour rows, new CHECK
constraint, and idempotency.  The fresh-DB (no garments table) path is
also exercised.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.storage.engine import make_engine
from app.storage.migration import migrate
from app.storage.models import GarmentRow


# ── v0.1.0 fixture helper ─────────────────────────────────────────────────────

_V010_ROWS: list[tuple[str, str]] = [
    ("g-top",       "top"),
    ("g-bottom",    "bottom"),
    ("g-jersey",    "jersey"),
    ("g-accessory", "accessory"),
    ("g-jacket",    "jacket"),
    ("g-socks",     "socks"),
    ("g-shoes",     "shoes"),
    ("g-hat",       "hat"),
]


def _v010_engine(db_path: Path):
    """Create a v0.1.0-schema engine with one garment per old type."""
    engine = make_engine(db_path)
    raw = engine.raw_connection()
    cur = raw.cursor()

    cur.execute("PRAGMA foreign_keys = OFF")
    cur.execute("""
        CREATE TABLE garments (
            id TEXT NOT NULL PRIMARY KEY,
            type TEXT NOT NULL
                CHECK (type IN ('top','bottom','jersey','jacket','socks','shoes','hat','accessory')),
            image_file TEXT NOT NULL,
            thumbnail_file TEXT NOT NULL,
            created_at TEXT NOT NULL,
            regenerated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE garment_colours (
            id INTEGER PRIMARY KEY,
            garment_id TEXT NOT NULL REFERENCES garments(id) ON DELETE CASCADE,
            position INTEGER NOT NULL,
            h REAL NOT NULL,
            s REAL NOT NULL,
            l REAL NOT NULL,
            family TEXT NOT NULL,
            proportion INTEGER NOT NULL CHECK (proportion BETWEEN 1 AND 100)
        )
    """)
    cur.execute("CREATE INDEX idx_garments_type ON garments (type)")
    cur.execute("CREATE INDEX idx_colours_family ON garment_colours (family)")
    cur.execute("CREATE INDEX idx_colours_garment ON garment_colours (garment_id)")

    for gid, gtype in _V010_ROWS:
        cur.execute(
            "INSERT INTO garments VALUES (?, ?, ?, ?, ?, ?)",
            (gid, gtype, f"{gid}.jpg", f"{gid}.webp", "2026-01-01T00:00:00Z", None),
        )
        cur.execute(
            "INSERT INTO garment_colours (garment_id, position, h, s, l, family, proportion)"
            " VALUES (?, 0, 0.0, 80.0, 50.0, 'red', 100)",
            (gid,),
        )

    raw.commit()
    cur.execute("PRAGMA foreign_keys = ON")
    raw.close()
    return engine


# ── Migration tests ───────────────────────────────────────────────────────────

class TestMigrateUnambiguousMappings:
    def _migrated(self, tmp_path: Path) -> dict[str, str]:
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            rows = conn.execute(sa.text("SELECT id, type FROM garments")).fetchall()
        engine.dispose()
        return {row[0]: row[1] for row in rows}

    def test_top_becomes_t_shirt(self, tmp_path):
        assert self._migrated(tmp_path)["g-top"] == "t_shirt"

    def test_jersey_becomes_jumper(self, tmp_path):
        assert self._migrated(tmp_path)["g-jersey"] == "jumper"

    def test_jacket_passes_through(self, tmp_path):
        assert self._migrated(tmp_path)["g-jacket"] == "jacket"

    def test_socks_passes_through(self, tmp_path):
        assert self._migrated(tmp_path)["g-socks"] == "socks"

    def test_shoes_passes_through(self, tmp_path):
        assert self._migrated(tmp_path)["g-shoes"] == "shoes"

    def test_hat_passes_through(self, tmp_path):
        assert self._migrated(tmp_path)["g-hat"] == "hat"


class TestMigrateAmbiguousDefaults:
    """FR-46: bottom→trousers and accessory→glasses are documented defaults,
    editable after migration."""

    def _migrated(self, tmp_path: Path) -> dict[str, str]:
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            rows = conn.execute(sa.text("SELECT id, type FROM garments")).fetchall()
        engine.dispose()
        return {row[0]: row[1] for row in rows}

    def test_bottom_maps_to_trousers(self, tmp_path):
        assert self._migrated(tmp_path)["g-bottom"] == "trousers"

    def test_accessory_maps_to_glasses(self, tmp_path):
        assert self._migrated(tmp_path)["g-accessory"] == "glasses"

    def test_trousers_re_editable_as_skirt(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, "g-bottom")
            assert row is not None
            row.type = "skirt"
            s.commit()
        with engine.connect() as conn:
            result = conn.execute(
                sa.text("SELECT type FROM garments WHERE id='g-bottom'")
            ).scalar()
        assert result == "skirt"
        engine.dispose()


class TestMigrateIntegrity:
    def test_row_count_unchanged(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            count = conn.execute(sa.text("SELECT COUNT(*) FROM garments")).scalar()
        engine.dispose()
        assert count == len(_V010_ROWS)

    def test_ids_unchanged(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            ids = {r[0] for r in conn.execute(sa.text("SELECT id FROM garments")).fetchall()}
        engine.dispose()
        assert ids == {row[0] for row in _V010_ROWS}

    def test_colour_rows_intact(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            count = conn.execute(sa.text("SELECT COUNT(*) FROM garment_colours")).scalar()
        engine.dispose()
        assert count == len(_V010_ROWS)

    def test_image_files_unchanged(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with engine.connect() as conn:
            rows = conn.execute(
                sa.text("SELECT id, image_file FROM garments")
            ).fetchall()
        engine.dispose()
        for gid, img in rows:
            assert img == f"{gid}.jpg"


class TestMigrateNewCheck:
    def test_old_value_rejected_after_migration(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with pytest.raises(IntegrityError):
            with Session(engine) as s:
                s.add(GarmentRow(
                    id="x", type="top",
                    image_file="x.jpg", thumbnail_file="x.webp",
                    created_at="2026-01-01T00:00:00Z",
                ))
                s.commit()
        engine.dispose()

    def test_new_value_accepted_after_migration(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        with Session(engine) as s:
            s.add(GarmentRow(
                id="new", type="hoodie",
                image_file="new.jpg", thumbnail_file="new.webp",
                created_at="2026-01-01T00:00:00Z",
            ))
            s.commit()
        engine.dispose()


class TestMigrateIdempotency:
    def test_double_migrate_no_error(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        migrate(engine)  # must not raise
        engine.dispose()

    def test_double_migrate_data_unchanged(self, tmp_path):
        engine = _v010_engine(tmp_path / "test.db")
        migrate(engine)
        migrate(engine)
        with engine.connect() as conn:
            count = conn.execute(sa.text("SELECT COUNT(*) FROM garments")).scalar()
        engine.dispose()
        assert count == len(_V010_ROWS)


class TestMigrateFreshDb:
    def test_fresh_db_no_error(self, tmp_path):
        """migrate() on a DB with no garments table must be a no-op."""
        engine = make_engine(tmp_path / "fresh.db")
        migrate(engine)  # must not raise
        engine.dispose()
