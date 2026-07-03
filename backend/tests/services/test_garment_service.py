"""
Tests for app.services.garment_service (HUE-022).

Strategy: §7.3 lifecycle tests with real staging/storage I/O and an in-memory
SQLite engine (no mocking of storage layers, per the CLAUDE.md pattern).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlmodel import Session, select

from app.matcher.taxonomy import classify
from app.services.garment_service import (
    ColourIn,
    GarmentNotFoundError,
    GarmentResult,
    InvalidFilterError,
    InvalidPaletteError,
    InvalidTypeError,
    TokenNotFoundError,
    confirm,
    delete,
    edit_category,
    list_garments,
)
from app.storage.models import GarmentColourRow, GarmentRow
from tests.conftest import make_test_jpeg as _make_jpeg_bytes, stage_test_image as _stage_image


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
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with Session(engine) as s:
            row = s.get(GarmentRow, result.id)
        assert row is not None
        assert row.type == "t_shirt"

    def test_colour_rows_inserted(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "t_shirt", _TWO_COLOURS,
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
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert (dirs["images"] / result.image_file).exists()

    def test_thumbnail_file_created(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert (dirs["thumbnails"] / result.thumbnail_file).exists()

    def test_staged_image_removed_from_staging(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        confirm(
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert list(dirs["staging"].iterdir()) == [], "staging dir should be empty after confirm"

    def test_returns_garment_result(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert isinstance(result, GarmentResult)
        assert result.type == "t_shirt"
        assert result.regenerated_at is None

    def test_proportions_preserved(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "t_shirt", _TWO_COLOURS,
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
            token, "t_shirt", [ColourIn(h=0.0, s=80.0, l=40.0, proportion=100)],
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        expected_family = classify(0.0, 80.0, 40.0)
        assert result.colours[0].family == expected_family

    def test_family_stored_in_db(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        result = confirm(
            token, "t_shirt", [ColourIn(h=180.0, s=70.0, l=50.0, proportion=100)],
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
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        assert result.colours[0].hex.startswith("#")
        assert len(result.colours[0].hex) == 7

    def test_neutral_flag_correct(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        # Black (h=0, s=0, l=5) is neutral.
        result = confirm(
            token, "t_shirt", [ColourIn(h=0.0, s=0.0, l=5.0, proportion=100)],
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
                token, "t_shirt", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_second_confirm_with_same_token_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        confirm(
            token, "t_shirt", _DEFAULT_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )
        with pytest.raises(TokenNotFoundError):
            _stage_second = _stage_image(dirs["staging"])  # noqa: F841
            confirm(
                token, "t_shirt", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_missing_token_raises(self, engine, dirs):
        with pytest.raises(TokenNotFoundError):
            confirm(
                "00000000-0000-0000-0000-000000000000",
                "t_shirt", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )


# ── Confirm — validation errors ───────────────────────────────────────────────

class TestConfirmValidation:
    def test_invalid_garment_type_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with pytest.raises(InvalidTypeError):
            confirm(
                token, "onesie", _DEFAULT_COLOURS,
                dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
            )

    def test_zero_colours_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        with pytest.raises(InvalidPaletteError):
            confirm(token, "t_shirt", [], dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_five_colours_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=float(i * 60), s=80.0, l=40.0, proportion=20) for i in range(5)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "t_shirt", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_proportions_not_summing_to_100_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=0.0, s=80.0, l=40.0, proportion=90)]
        with pytest.raises(InvalidPaletteError, match="100"):
            confirm(token, "t_shirt", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_h_out_of_range_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=360.0, s=80.0, l=40.0, proportion=100)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "t_shirt", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_s_out_of_range_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [ColourIn(h=0.0, s=101.0, l=40.0, proportion=100)]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "t_shirt", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)

    def test_proportion_zero_raises(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        colours = [
            ColourIn(h=0.0, s=80.0, l=40.0, proportion=0),
            ColourIn(h=60.0, s=80.0, l=40.0, proportion=100),
        ]
        with pytest.raises(InvalidPaletteError):
            confirm(token, "t_shirt", colours, dirs["staging"], dirs["images"], dirs["thumbnails"], engine)


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
                    token, "t_shirt", _DEFAULT_COLOURS,
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
                    token, "t_shirt", _DEFAULT_COLOURS,
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
                    token, "t_shirt", _DEFAULT_COLOURS,
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
            token, "t_shirt", _DEFAULT_COLOURS,
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


# ── Edit category (FR-32, FR-46) ──────────────────────────────────────────────

class TestEditCategory:
    @pytest.fixture()
    def saved_garment(self, engine, dirs):
        token = _stage_image(dirs["staging"])
        return confirm(
            token, "t_shirt", _TWO_COLOURS,
            dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
        )

    def test_category_updated_in_db(self, engine, dirs, saved_garment):
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.type == "trousers"

    def test_returns_result_with_new_category(self, engine, dirs, saved_garment):
        result = edit_category(saved_garment.id, "trousers", engine)
        assert isinstance(result, GarmentResult)
        assert result.type == "trousers"
        assert result.id == saved_garment.id

    def test_image_file_unchanged(self, engine, dirs, saved_garment):
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.image_file == saved_garment.image_file

    def test_thumbnail_file_unchanged(self, engine, dirs, saved_garment):
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.thumbnail_file == saved_garment.thumbnail_file

    def test_colour_rows_unchanged(self, engine, dirs, saved_garment):
        before = saved_garment.colours
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow)
                .where(GarmentColourRow.garment_id == saved_garment.id)
                .order_by(GarmentColourRow.position)
            ).all()
        assert len(rows) == len(before)
        for row, colour in zip(rows, before):
            assert row.h == colour.h
            assert row.s == colour.s
            assert row.l == colour.l
            assert row.proportion == colour.proportion

    def test_regenerated_at_unchanged(self, engine, dirs, saved_garment):
        """edit_category must not modify regenerated_at (FR-46)."""
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.regenerated_at == saved_garment.regenerated_at

    def test_created_at_unchanged(self, engine, dirs, saved_garment):
        edit_category(saved_garment.id, "trousers", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.created_at == saved_garment.created_at

    def test_invalid_category_raises(self, engine, dirs, saved_garment):
        with pytest.raises(InvalidTypeError):
            edit_category(saved_garment.id, "onesie", engine)

    def test_invalid_category_does_not_mutate_db(self, engine, dirs, saved_garment):
        with pytest.raises(InvalidTypeError):
            edit_category(saved_garment.id, "onesie", engine)
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.type == "t_shirt"

    def test_not_found_raises(self, engine, dirs):
        with pytest.raises(GarmentNotFoundError):
            edit_category("00000000-0000-0000-0000-000000000000", "trousers", engine)


# ── Inventory ordering (FR-47) ────────────────────────────────────────────────

class TestInventoryOrdering:
    """FR-47: hue-spectrum (default) and date ordering in list_garments."""

    # Known-hue single-colour palettes; families derived by classify().
    _RED    = [ColourIn(h=10.0,  s=80.0, l=40.0, proportion=100)]  # classify → Red
    _YELLOW = [ColourIn(h=60.0,  s=80.0, l=40.0, proportion=100)]  # classify → Yellow
    _BLUE   = [ColourIn(h=240.0, s=80.0, l=40.0, proportion=100)]  # classify → Blue
    _GREY   = [ColourIn(h=0.0,   s=0.0,  l=50.0, proportion=100)]  # classify → Grey (neutral)

    def _save(self, engine, dirs, garment_type: str, colours: list[ColourIn]) -> GarmentResult:
        token = _stage_image(dirs["staging"])
        return confirm(
            token=token,
            garment_type=garment_type,
            colours=colours,
            staging_dir=dirs["staging"],
            images_dir=dirs["images"],
            thumbnails_dir=dirs["thumbnails"],
            engine=engine,
        )

    def _set_created_at(self, engine, garment_id: str, dt: str) -> None:
        with Session(engine) as s:
            row = s.get(GarmentRow, garment_id)
            row.created_at = dt
            s.add(row)
            s.commit()

    def test_hue_is_default(self, engine, dirs):
        """list_garments without order= defaults to hue ordering."""
        r_low  = self._save(engine, dirs, "t_shirt", self._RED)    # h=10, created first
        r_high = self._save(engine, dirs, "t_shirt", self._BLUE)   # h=240, created second
        # date order would put r_high first (newest); hue order puts r_low first (lower h).
        date_page = list_garments(engine, order="date")
        assert [g.id for g in date_page.garments][0] == r_high.id  # confirm date differs
        hue_page = list_garments(engine)  # default
        assert [g.id for g in hue_page.garments][0] == r_low.id

    def test_hue_chromatic_ordered_by_raw_hue(self, engine, dirs):
        """Chromatic garments within a category are ordered by primary hue, low to high."""
        r_blue   = self._save(engine, dirs, "t_shirt", self._BLUE)   # h=240
        r_red    = self._save(engine, dirs, "t_shirt", self._RED)    # h=10
        r_yellow = self._save(engine, dirs, "t_shirt", self._YELLOW) # h=60
        page = list_garments(engine, order="hue")
        ids = [g.id for g in page.garments]
        assert ids == [r_red.id, r_yellow.id, r_blue.id]

    def test_hue_neutral_trails_chromatic(self, engine, dirs):
        """Neutral-primary garments appear after all chromatic garments in their category."""
        r_grey = self._save(engine, dirs, "t_shirt", self._GREY)  # neutral
        r_blue = self._save(engine, dirs, "t_shirt", self._BLUE)  # chromatic, h=240
        page = list_garments(engine, order="hue")
        ids = [g.id for g in page.garments]
        assert ids.index(r_blue.id) < ids.index(r_grey.id)

    def test_hue_groups_by_type_first(self, engine, dirs):
        """Results are grouped by garment type before applying hue ordering."""
        r_jumper = self._save(engine, dirs, "jumper",  self._BLUE)  # h=240
        r_shirt  = self._save(engine, dirs, "t_shirt", self._RED)   # h=10
        page = list_garments(engine, order="hue")
        types = [g.type for g in page.garments]
        # 'jumper' < 't_shirt' alphabetically → jumper group first
        assert types == ["jumper", "t_shirt"]

    def test_date_newest_first(self, engine, dirs):
        """date order: newest garment first within each category."""
        r_first  = self._save(engine, dirs, "t_shirt", self._RED)
        r_second = self._save(engine, dirs, "t_shirt", self._YELLOW)
        r_third  = self._save(engine, dirs, "t_shirt", self._BLUE)
        self._set_created_at(engine, r_first.id,  "2026-06-01T10:00:00+00:00")
        self._set_created_at(engine, r_second.id, "2026-06-02T10:00:00+00:00")
        self._set_created_at(engine, r_third.id,  "2026-06-03T10:00:00+00:00")
        page = list_garments(engine, order="date")
        ids = [g.id for g in page.garments]
        assert ids == [r_third.id, r_second.id, r_first.id]

    def test_date_groups_by_type_first(self, engine, dirs):
        """date order: grouped by type; within each group, newest first."""
        r_jumper = self._save(engine, dirs, "jumper",  self._BLUE)
        r_shirt  = self._save(engine, dirs, "t_shirt", self._RED)
        page = list_garments(engine, order="date")
        types = [g.type for g in page.garments]
        assert types == ["jumper", "t_shirt"]

    def test_unknown_order_raises(self, engine):
        """Unknown order value raises InvalidFilterError."""
        with pytest.raises(InvalidFilterError, match="Unknown order"):
            list_garments(engine, order="random")

    def test_total_unaffected_by_order(self, engine, dirs):
        """Total count is the same regardless of the order parameter."""
        for _ in range(3):
            self._save(engine, dirs, "t_shirt", self._RED)
        assert list_garments(engine, order="hue").total == 3
        assert list_garments(engine, order="date").total == 3
