"""
Tests for the regeneration path in app.services.garment_service (HUE-023).

Strategy: §7.3 lifecycle tests.  A garment is confirmed first (via the
existing ``confirm`` function), then the regeneration flow is exercised
against it.  Staging tokens are created directly via ``staging.stage`` to
avoid running the full detection pipeline.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlmodel import Session, select

from app.services.garment_service import (
    ColourIn,
    GarmentNotFoundError,
    InvalidPaletteError,
    InvalidTypeError,
    RegenerationTokenError,
    confirm,
    confirm_regeneration,
)
from app.storage import staging
from app.storage.models import GarmentColourRow, GarmentRow
from tests.services.conftest import _make_jpeg_bytes, _stage_image


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _stage_regen_token(staging_dir: Path, garment_id: str, data: bytes | None = None) -> str:
    """Stage a token bound to *garment_id* (simulating run_regeneration)."""
    return staging.stage(
        data=data or _make_jpeg_bytes(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={},
        staging_dir=staging_dir,
        garment_id=garment_id,
    )


_ORIGINAL_COLOURS = [ColourIn(h=0.0, s=80.0, l=40.0, proportion=100)]
_NEW_COLOURS = [
    ColourIn(h=180.0, s=60.0, l=40.0, proportion=70),
    ColourIn(h=60.0, s=70.0, l=50.0, proportion=30),
]


@pytest.fixture()
def saved_garment(engine, dirs):
    """A confirmed garment to regenerate against."""
    token = _stage_image(dirs["staging"])
    return confirm(
        token, "t_shirt", _ORIGINAL_COLOURS,
        dirs["staging"], dirs["images"], dirs["thumbnails"], engine,
    )


# ── Happy-path ────────────────────────────────────────────────────────────────

class TestConfirmRegenerationHappyPath:
    def test_palette_replaced_in_db(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow).where(GarmentColourRow.garment_id == saved_garment.id)
            ).all()
        assert len(rows) == 2
        stored_hs = {(r.h, r.proportion) for r in rows}
        assert (180.0, 70) in stored_hs
        assert (60.0, 30) in stored_hs

    def test_old_colour_rows_removed(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        with Session(engine) as s:
            rows = s.exec(
                select(GarmentColourRow).where(GarmentColourRow.garment_id == saved_garment.id)
            ).all()
        original_hs = {r.h for r in rows}
        assert 0.0 not in original_hs, "original Red colour should be replaced"

    def test_same_garment_id(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        assert result.id == saved_garment.id

    def test_same_image_file(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        assert result.image_file == saved_garment.image_file

    def test_type_updated(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        assert result.type == "jumper"
        with Session(engine) as s:
            row = s.get(GarmentRow, saved_garment.id)
        assert row.type == "jumper"

    def test_regenerated_at_set(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        assert result.regenerated_at is not None
        dt = datetime.fromisoformat(result.regenerated_at)
        assert dt.tzinfo is not None

    def test_token_consumed(self, engine, dirs, saved_garment):
        """Second confirm with the same token → RegenerationTokenError (token consumed)."""
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        # Re-stage a new token so the garment is re-patchable; old token should be gone.
        second_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        with pytest.raises(RegenerationTokenError):
            confirm_regeneration(
                saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )

    def test_family_rederived_server_side(self, engine, dirs, saved_garment):
        from app.matcher.taxonomy import classify
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper",
            [ColourIn(h=180.0, s=70.0, l=50.0, proportion=100)],
            dirs["staging"], dirs["images"], engine,
        )
        expected = classify(180.0, 70.0, 50.0)
        assert result.colours[0].family == expected

    def test_proportions_sum_to_100(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        result = confirm_regeneration(
            saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
            dirs["staging"], dirs["images"], engine,
        )
        assert sum(c.proportion for c in result.colours) == 100


# ── Token validation (FR-32) ──────────────────────────────────────────────────

class TestRegenerationTokenValidation:
    def test_missing_token_raises(self, engine, dirs, saved_garment):
        with pytest.raises(RegenerationTokenError):
            confirm_regeneration(
                saved_garment.id,
                "00000000-0000-0000-0000-000000000000",
                "jumper", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )

    def test_expired_token_raises(self, engine, dirs, saved_garment):
        from datetime import timedelta
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        sidecar = dirs["staging"] / f"{regen_token}.json"
        data = json.loads(sidecar.read_text())
        data["expires_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        sidecar.write_text(json.dumps(data))
        with pytest.raises(RegenerationTokenError):
            confirm_regeneration(
                saved_garment.id, regen_token, "jumper", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )

    def test_foreign_token_raises(self, engine, dirs, saved_garment):
        """Token bound to a different garment_id → rejected."""
        foreign_token = _stage_regen_token(dirs["staging"], "other-garment-id")
        with pytest.raises(RegenerationTokenError):
            confirm_regeneration(
                saved_garment.id, foreign_token, "jumper", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )

    def test_unbound_token_raises(self, engine, dirs, saved_garment):
        """A new-upload token (garment_id=None) is not a valid regeneration token."""
        upload_token = _stage_image(dirs["staging"])
        with pytest.raises(RegenerationTokenError):
            confirm_regeneration(
                saved_garment.id, upload_token, "jumper", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )


# ── Validation errors apply ───────────────────────────────────────────────────

class TestRegenerationValidation:
    def test_invalid_type_raises(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        with pytest.raises(InvalidTypeError):
            confirm_regeneration(
                saved_garment.id, regen_token, "onesie", _NEW_COLOURS,
                dirs["staging"], dirs["images"], engine,
            )

    def test_invalid_palette_raises(self, engine, dirs, saved_garment):
        regen_token = _stage_regen_token(dirs["staging"], saved_garment.id)
        bad_colours = [ColourIn(h=0.0, s=80.0, l=40.0, proportion=90)]
        with pytest.raises(InvalidPaletteError):
            confirm_regeneration(
                saved_garment.id, regen_token, "jumper", bad_colours,
                dirs["staging"], dirs["images"], engine,
            )
