"""
Tests for app.services.garment_service (HUE-022).

Strategy: §7.3 lifecycle tests with real staging/storage I/O and an in-memory
SQLite engine (no mocking of storage layers, per the CLAUDE.md pattern).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from sqlmodel import Session, select

from app.matcher.taxonomy import classify
from app.services.garment_service import (
    ColourIn,
    GarmentNotFoundError,
    GarmentResult,
    InvalidPaletteError,
    InvalidTypeError,
    TokenNotFoundError,
    confirm,
    delete,
)
from app.storage import staging
from app.storage.engine import init_db, make_engine
from app.storage.models import GarmentColourRow, GarmentRow


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def engine(tmp_path):
    e = make_engine(tmp_path / "test.db")
    init_db(e)
    yield e
    e.dispose()


@pytest.fixture()
def dirs(tmp_path):
    d = {
        "staging": tmp_path / "staging",
        "images": tmp_path / "images",
        "thumbnails": tmp_path / "thumbnails",
    }
    for p in d.values():
        p.mkdir()
    return d


def _make_jpeg_bytes(colour: tuple[int, int, int] = (200, 30, 30)) -> bytes:
    from io import BytesIO
    img = Image.new("RGB", (200, 200), colour)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _stage_image(staging_dir: Path, data: bytes | None = None) -> str:
    """Stage a JPEG and return the token."""
    return staging.stage(
        data=data or _make_jpeg_bytes(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={},
        staging_dir=staging_dir,
    )


_DEFAULT_COLOURS = [ColourIn(h=0.0, s=80.0, l=40.0, proportion=100)]
_TWO_COLOURS = [
    ColourIn(h=0.0, s=80.0, l=40.0, proportion=80),
    ColourIn(h=180.0, s=60.0, l=40.0, proportion=20),
]


# ── Confirm — happy-path ──────────────────────────────────────────────────────

class TestConfirmHappyPath:
    def test_garment_row_inserted(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with Session(engine) as s:
            row = s.get(GarmentRow, result.id)
        assert row is not None
        assert row.type == "top"

    def test_colour_rows_inserted(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _TWO_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow).where(GarmentColourRow.garment_id == result.id)
            ).all()
        assert len(rows) == 2

    def test_image_file_in_images_dir(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert (dirs["images"] / result.image_file).exists()

    def test_thumbnail_file_created(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert (dirs["thumbnails"] / result.thumbnail_file).exists()

    def test_staged_image_removed_from_staging(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert list(dirs["staging"].iterdir()) == [], "staging dir should be empty after confirm"

    def test_returns_garment_result(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert isinstance(result, GarmentResult)
        assert result.type == "top"
        assert result.regenerated_at is None

    def test_proportions_preserved(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _TWO_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        props = {c.proportion for c in result.colours}
        assert props == {80, 20}


# ── Confirm — family re-derivation (FR-1) ────────────────────────────────────

class TestFamilyRederivation:
    def test_family_derived_from_hsl_not_client(self, engine, dirs):
        """The service always classifies family from HSL; client cannot override (FR-1)."""
        token = _stage_image(dirs["staging"])
        # h=0°, s=80%, l=40% should be Red.
        result = confirm(
            token, "top", [ColourIn(h=0.0, s=80.0, l=40.0, proportion=100)],
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        expected_family = classify(0.0, 80.0, 40.0)
        assert result.colours[0].family == expected_family

    def test_family_stored_in_db(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", [ColourIn(h=180.0, s=70.0, l=50.0, proportion=100)],
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow).where(GarmentColourRow.garment_id == result.id)
            ).all()
        expected = classify(180.0, 70.0, 50.0)
        assert rows[0].family == expected

    def test_hex_field_populated(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert result.colours[0].hex.startswith("#")
        assert len(result.colours[0].hex) == 7

    def test_neutral_flag_correct(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        # Black (h=0, s=0, l=5) is neutral.
        result = confirm(
            token, "top", [ColourIn(h=0.0, s=0.0, l=5.0, proportion=100)],
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert result.colours[0].neutral is True


# ── Confirm — token lifecycle ─────────────────────────────────────────────────

class TestTokenLifecycle:
    def test_expired_token_raises(self, engine, dirs):
        import json
        from datetime import timedelta

        token = _stage_image(dirs["staging"])
        # Force-expire the sidecar.
        sidecar = dirs["staging"] / f"{token}.json"
        data = json.loads(sidecar.read_text())
        from datetime import datetime, timezone
        data["expires_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        sidecar.write_text(json.dumps(data))

        with pytest.raises(TokenNotFoundError):
            confirm(
                token, "top", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_second_confirm_with_same_token_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with pytest.raises(TokenNotFoundError):
            _stage_second = _stage_image(dirs["staging"])  # noqa: F841
            confirm(
                token, "top", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_missing_token_raises(self, engine, dirs):
        with pytest.raises(TokenNotFoundError):
            confirm(
                "00000000-0000-0000-0000-000000000000",
                "top", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )


# ── Confirm — validation errors ───────────────────────────────────────────────

class TestConfirmValidation:
    def test_invalid_garment_type_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with pytest.raises(InvalidTypeError):
            confirm(
                token, "trousers", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_zero_colours_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with pytest.raises(InvalidPaletteError):
            confirm(token, "top", [], dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_five_colours_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=float(i * 60), s=80.0, l=40.0, proportion=20) for i in range(5)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "top", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_proportions_not_summing_to_100_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=0.0, s=80.0, l=40.0, proportion=90)]
        with pytest.raises(InvalidPaletteError, match="100"):
            confirm(token, "top", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_h_out_of_range_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=360.0, s=80.0, l=40.0, proportion=100)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "top", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_s_out_of_range_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=0.0, s=101.0, l=40.0, proportion=100)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "top", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_proportion_zero_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [
            ColourIn(h=0.0, s=80.0, l=40.0, proportion=0),
            ColourIn(h=60.0, s=80.0, l=40.0, proportion=100),
        ]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "top", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)


# ── Confirm — atomicity (FR-30) ───────────────────────────────────────────────

class TestConfirmAtomicity:
    def test_thumbnail_failure_leaves_no_image_in_images_dir(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with patch(
            "app.services.garment_service.generate_thumbnail",
            side_effect=RuntimeError("disk full"),
        ):
            with pytest.raises(RuntimeError):
                confirm(
                    token, "top", _DEFAULT_COLOURS,
                    dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
                )
        assert list(dirs["images"].iterdir()) == []

    def test_thumbnail_failure_leaves_no_db_rows(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with patch(
            "app.services.garment_service.generate_thumbnail",
            side_effect=RuntimeError("disk full"),
        ):
            with pytest.raises(RuntimeError):
                confirm(
                    token, "top", _DEFAULT_COLOURS,
                    dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
                )
        with Session(engine) as s:
            rows = s.exec(select(GarmentRow)).all()
        assert rows == []

    def test_db_failure_cleans_up_files(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with patch(
            "app.services.garment_service.Session",
            side_effect=RuntimeError("db error"),
        ):
            with pytest.raises(RuntimeError):
                confirm(
                    token, "top", _DEFAULT_COLOURS,
                    dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
                )
        assert list(dirs["images"].iterdir()) == []
        assert list(dirs["thumbnails"].iterdir()) == []


# ── Delete ────────────────────────────────────────────────────────────────────

class TestDelete:
    @pytest.fixture()
    def saved_garment(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        return confirm(
            token, "top", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )

    def test_garment_row_removed(self, engine, dirs, saved_garment):
        delete(saved_garment.id, dirs["images"], dirs["thumbnails"], engine)
        with Session(engine) as s:
            assert s.get(GarmentRow, saved_garment.id) is None

    def test_colour_rows_cascade_deleted(self, engine, dirs, saved_garment):
        delete(saved_garment.id, dirs["images"], dirs["thumbnails"], engine)
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow).where(GarmentColourRow.garment_id == saved_garment.id)
            ).all()
        assert rows == []

    def test_image_file_removed(self, engine, dirs, saved_garment):
        image_path = dirs["images"] / saved_garment.image_file
        assert image_path.exists()
        delete(saved_garment.id, dirs["images"], dirs["thumbnails"], engine)
        assert not image_path.exists()

    def test_thumbnail_file_removed(self, engine, dirs, saved_garment):
        thumb_path = dirs["thumbnails"] / saved_garment.thumbnail_file
        assert thumb_path.exists()
        delete(saved_garment.id, dirs["images"], dirs["thumbnails"], engine)
        assert not thumb_path.exists()

    def test_missing_garment_raises(self, engine, dirs):
        with pytest.raises(GarmentNotFoundError):
            delete("00000000-0000-0000-0000-000000000000", dirs["images"], dirs["thumbnails"], engine)

    def test_delete_tolerates_missing_files(self, engine, dirs, saved_garment):
        """Deleting when files are already absent must not raise (missing_ok)."""
        (dirs["images"] / saved_garment.image_file).unlink()
        (dirs["thumbnails"] / saved_garment.thumbnail_file).unlink()
        delete(saved_garment.id, dirs["images"], dirs["thumbnails"], engine)
        with Session(engine) as s:
            assert s.get(GarmentRow, saved_garment.id) is None
