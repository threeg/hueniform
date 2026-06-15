"""
Tests for storage.staging (test strategy §7.3).

Coverage:
  - stage() writes image file and sidecar; returns a UUID4 token.
  - load() returns a live entry; returns None for unknown token.
  - load() lazily removes and returns None for an expired entry (sidecar edit).
  - load() handles malformed sidecar gracefully.
  - move() relocates the image, deletes the sidecar, returns the destination.
  - sweep() removes expired entries and returns count; leaves live entries.
  - sweep() removes malformed sidecars.
"""

from __future__ import annotations

import io
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from PIL import Image

from app.storage.staging import StagingEntry, load, move, stage, sweep


# ── Helpers ───────────────────────────────────────────────────────────────────

_PROPOSAL: dict = {"colours": [{"h": 0.0, "s": 80.0, "l": 50.0, "proportion": 100}]}


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color=(200, 50, 50)).save(buf, "PNG")
    return buf.getvalue()


def _expire_sidecar(staging_dir: Path, token: str) -> None:
    """Edit the sidecar so the entry appears expired."""
    sc = staging_dir / f"{token}.json"
    data = json.loads(sc.read_text(encoding="utf-8"))
    data["expires_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()
    sc.write_text(json.dumps(data), encoding="utf-8")


# ── stage() ───────────────────────────────────────────────────────────────────

class TestStage:
    def test_returns_uuid4_token(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        uuid.UUID(token, version=4)   # raises if invalid

    def test_image_file_written(self, tmp_path) -> None:
        data = _png_bytes()
        token = stage(data, "png", "image/png", False, _PROPOSAL, tmp_path)
        assert (tmp_path / f"{token}.png").read_bytes() == data

    def test_sidecar_written(self, tmp_path) -> None:
        token = stage(_png_bytes(), "jpg", "image/jpeg", True, _PROPOSAL, tmp_path)
        sc = tmp_path / f"{token}.json"
        assert sc.exists()
        data = json.loads(sc.read_text(encoding="utf-8"))
        assert data["token"] == token
        assert data["ext"] == "jpg"
        assert data["content_type"] == "image/jpeg"
        assert data["fallback_used"] is True
        assert data["proposal"] == _PROPOSAL
        assert data["garment_id"] is None
        assert "expires_at" in data

    def test_garment_id_stored_for_regeneration(self, tmp_path) -> None:
        gid = str(uuid.uuid4())
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path, garment_id=gid)
        sc = json.loads((tmp_path / f"{token}.json").read_text(encoding="utf-8"))
        assert sc["garment_id"] == gid

    def test_tokens_are_unique(self, tmp_path) -> None:
        tokens = {stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path) for _ in range(10)}
        assert len(tokens) == 10


# ── load() ────────────────────────────────────────────────────────────────────

class TestLoad:
    def test_live_entry_returned(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        entry = load(token, tmp_path)
        assert isinstance(entry, StagingEntry)
        assert entry.token == token
        assert entry.ext == "png"
        assert entry.content_type == "image/png"
        assert entry.fallback_used is False
        assert entry.proposal == _PROPOSAL
        assert entry.garment_id is None

    def test_unknown_token_returns_none(self, tmp_path) -> None:
        assert load(str(uuid.uuid4()), tmp_path) is None

    def test_expired_entry_returns_none(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        _expire_sidecar(tmp_path, token)
        assert load(token, tmp_path) is None

    def test_expired_entry_files_deleted_on_load(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        _expire_sidecar(tmp_path, token)
        load(token, tmp_path)
        assert not (tmp_path / f"{token}.png").exists()
        assert not (tmp_path / f"{token}.json").exists()

    def test_malformed_sidecar_returns_none(self, tmp_path) -> None:
        token = str(uuid.uuid4())
        (tmp_path / f"{token}.json").write_text("not json", encoding="utf-8")
        assert load(token, tmp_path) is None

    def test_malformed_sidecar_deleted_on_load(self, tmp_path) -> None:
        token = str(uuid.uuid4())
        sc = tmp_path / f"{token}.json"
        sc.write_text("{}", encoding="utf-8")   # valid JSON but missing keys
        load(token, tmp_path)
        assert not sc.exists()


# ── move() ────────────────────────────────────────────────────────────────────

class TestMove:
    def test_image_relocated_to_images_dir(self, tmp_path) -> None:
        staging = tmp_path / "staging"
        images = tmp_path / "images"
        staging.mkdir()
        images.mkdir()
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, staging)
        gid = str(uuid.uuid4())
        dst = move(token, "png", gid, staging, images)
        assert dst == images / f"{gid}.png"
        assert dst.exists()

    def test_original_staging_file_gone(self, tmp_path) -> None:
        staging = tmp_path / "staging"
        images = tmp_path / "images"
        staging.mkdir()
        images.mkdir()
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, staging)
        gid = str(uuid.uuid4())
        move(token, "png", gid, staging, images)
        assert not (staging / f"{token}.png").exists()

    def test_sidecar_deleted_after_move(self, tmp_path) -> None:
        staging = tmp_path / "staging"
        images = tmp_path / "images"
        staging.mkdir()
        images.mkdir()
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, staging)
        gid = str(uuid.uuid4())
        move(token, "png", gid, staging, images)
        assert not (staging / f"{token}.json").exists()

    def test_image_content_preserved_after_move(self, tmp_path) -> None:
        staging = tmp_path / "staging"
        images = tmp_path / "images"
        staging.mkdir()
        images.mkdir()
        data = _png_bytes()
        token = stage(data, "png", "image/png", False, _PROPOSAL, staging)
        gid = str(uuid.uuid4())
        dst = move(token, "png", gid, staging, images)
        assert dst.read_bytes() == data


# ── sweep() ───────────────────────────────────────────────────────────────────

class TestSweep:
    def test_sweep_removes_expired_entries(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        _expire_sidecar(tmp_path, token)
        removed = sweep(tmp_path)
        assert removed == 1
        assert not (tmp_path / f"{token}.png").exists()
        assert not (tmp_path / f"{token}.json").exists()

    def test_sweep_preserves_live_entries(self, tmp_path) -> None:
        token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        removed = sweep(tmp_path)
        assert removed == 0
        assert (tmp_path / f"{token}.png").exists()
        assert (tmp_path / f"{token}.json").exists()

    def test_sweep_returns_correct_count(self, tmp_path) -> None:
        live_token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
        for _ in range(3):
            token = stage(_png_bytes(), "png", "image/png", False, _PROPOSAL, tmp_path)
            _expire_sidecar(tmp_path, token)
        removed = sweep(tmp_path)
        assert removed == 3
        assert (tmp_path / f"{live_token}.json").exists()

    def test_sweep_removes_malformed_sidecar(self, tmp_path) -> None:
        bad_sc = tmp_path / "garbage.json"
        bad_sc.write_text("not json", encoding="utf-8")
        removed = sweep(tmp_path)
        assert removed == 1
        assert not bad_sc.exists()

    def test_empty_staging_dir_returns_zero(self, tmp_path) -> None:
        assert sweep(tmp_path) == 0
