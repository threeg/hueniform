"""
Storage-layer model tests (test strategy §7.1).

Coverage:
  - Both tables and all three indices are created by init_db.
  - CHECK constraint on garments.type rejects invalid values.
  - CHECK constraint on garment_colours.proportion rejects 0 and 101.
  - PRAGMA foreign_keys = ON is active on every connection.
  - PRAGMA journal_mode = WAL is active.
  - ON DELETE CASCADE removes colour rows when a garment is deleted (FR-34).
  - Storage imports nothing from matcher/detection/services/api (contract 4,
    verified by the import-linter gate in make test).
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.storage.engine import init_db, make_engine
from app.storage.models import GarmentColourRow, GarmentRow


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def engine(tmp_path):
    e = make_engine(tmp_path / "test.db")
    init_db(e)
    yield e
    e.dispose()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _garment(gid: str = "g1", gtype: str = "t_shirt") -> GarmentRow:
    return GarmentRow(
        id=gid,
        type=gtype,
        image_file=f"{gid}.jpg",
        thumbnail_file=f"{gid}.webp",
        created_at="2026-06-15T00:00:00Z",
    )


def _colour(garment_id: str = "g1", proportion: int = 100, position: int = 0) -> GarmentColourRow:
    return GarmentColourRow(
        garment_id=garment_id,
        position=position,
        h=0.0, s=80.0, l=50.0,
        family="red",
        proportion=proportion,
    )


# ── Table and index creation ──────────────────────────────────────────────────

class TestTablesCreated:
    def test_garments_table_exists(self, engine) -> None:
        with engine.connect() as conn:
            row = conn.execute(
                sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='garments'")
            ).fetchone()
        assert row is not None

    def test_garment_colours_table_exists(self, engine) -> None:
        with engine.connect() as conn:
            row = conn.execute(
                sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='garment_colours'")
            ).fetchone()
        assert row is not None

    def test_init_db_is_idempotent(self, engine) -> None:
        """Calling init_db a second time must not raise."""
        init_db(engine)


class TestIndices:
    def _index_exists(self, engine, name: str) -> bool:
        with engine.connect() as conn:
            row = conn.execute(
                sa.text("SELECT name FROM sqlite_master WHERE type='index' AND name=:n"),
                {"n": name},
            ).fetchone()
        return row is not None

    def test_idx_garments_type(self, engine) -> None:
        assert self._index_exists(engine, "idx_garments_type")

    def test_idx_colours_family(self, engine) -> None:
        assert self._index_exists(engine, "idx_colours_family")

    def test_idx_colours_garment(self, engine) -> None:
        assert self._index_exists(engine, "idx_colours_garment")


# ── garments CHECK constraint ─────────────────────────────────────────────────

class TestGarmentTypeConstraint:
    def test_all_valid_types_accepted(self, engine) -> None:
        # Spot-check a representative subset of FR-16 categories.
        valid = ("t_shirt", "trousers", "jumper", "jacket", "socks", "shoes", "hat", "glasses")
        with Session(engine) as session:
            for gtype in valid:
                session.add(_garment(gid=gtype, gtype=gtype))
            session.commit()

    def test_invalid_type_rejected(self, engine) -> None:
        with pytest.raises(IntegrityError):
            with Session(engine) as session:
                session.add(_garment(gtype="onesie"))
                session.commit()

    def test_empty_type_rejected(self, engine) -> None:
        with pytest.raises(IntegrityError):
            with Session(engine) as session:
                session.add(_garment(gtype=""))
                session.commit()


# ── garment_colours CHECK constraint ─────────────────────────────────────────

class TestProportionConstraint:
    def test_proportion_1_accepted(self, engine) -> None:
        with Session(engine) as session:
            session.add(_garment())
            session.flush()          # persist garment before colour (no FK relationship defined)
            session.add(_colour(proportion=1))
            session.commit()

    def test_proportion_100_accepted(self, engine) -> None:
        with Session(engine) as session:
            session.add(_garment(gid="g2"))
            session.flush()
            session.add(_colour(garment_id="g2", proportion=100))
            session.commit()

    def test_proportion_zero_rejected(self, engine) -> None:
        with pytest.raises(IntegrityError):
            with Session(engine) as session:
                session.add(_garment())
                session.flush()
                session.add(_colour(proportion=0))
                session.commit()

    def test_proportion_over_100_rejected(self, engine) -> None:
        with pytest.raises(IntegrityError):
            with Session(engine) as session:
                session.add(_garment())
                session.flush()
                session.add(_colour(proportion=101))
                session.commit()


# ── Foreign key and cascade delete ───────────────────────────────────────────

class TestForeignKeyAndCascade:
    def test_fk_rejects_unknown_garment_id(self, engine) -> None:
        with pytest.raises(IntegrityError):
            with Session(engine) as session:
                session.add(_colour(garment_id="no-such-garment"))
                session.commit()

    def test_cascade_delete_removes_colour_rows(self, engine) -> None:
        with Session(engine) as session:
            session.add(_garment(gid="g-del"))
            session.flush()
            session.add(_colour(garment_id="g-del"))
            session.commit()

        # Delete the garment; cascade must remove its colour rows.
        with Session(engine) as session:
            row = session.get(GarmentRow, "g-del")
            assert row is not None
            session.delete(row)
            session.commit()

        with engine.connect() as conn:
            count = conn.execute(
                sa.text("SELECT COUNT(*) FROM garment_colours WHERE garment_id='g-del'")
            ).scalar()
        assert count == 0

    def test_regenerated_at_nullable(self, engine) -> None:
        with Session(engine) as session:
            g = _garment()
            assert g.regenerated_at is None
            session.add(g)
            session.flush()
            session.commit()
        with Session(engine) as session:
            row = session.get(GarmentRow, "g1")
            assert row is not None
            assert row.regenerated_at is None


# ── PRAGMA verification ───────────────────────────────────────────────────────

class TestPragmas:
    def test_foreign_keys_on(self, engine) -> None:
        with engine.connect() as conn:
            result = conn.execute(sa.text("PRAGMA foreign_keys")).scalar()
        assert result == 1

    def test_wal_journal_mode(self, engine) -> None:
        with engine.connect() as conn:
            result = conn.execute(sa.text("PRAGMA journal_mode")).scalar()
        assert result == "wal"
