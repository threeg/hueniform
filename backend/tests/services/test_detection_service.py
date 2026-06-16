"""
Tests for app.services.detection_service (HUE-021).

Strategy: §7.3 service/integration tests with injected detection seams so
the default gate runs without the real rembg model.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.services.detection_service import (
    ColourProposal,
    DetectionResult,
    run_detection,
    run_regeneration,
)


# ── Shared seams ───────────────────────────────────────────────────────────────

def _passthrough_segmenter(img: Image.Image) -> Image.Image:
    """Return the image as RGBA with a fully-opaque alpha (no pixels removed)."""
    rgba = img.convert("RGBA")
    r, g, b, _a = rgba.split()
    opaque = Image.new("L", img.size, 255)
    return Image.merge("RGBA", (r, g, b, opaque))


def _seeded_clusterer(pixels: np.ndarray, k: int):
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=k, n_init=10, random_state=0)
    labels = km.fit_predict(pixels)
    return km.cluster_centers_, labels


def _make_red_jpeg(tmp_path: Path, filename: str = "red.jpg") -> tuple[Path, bytes]:
    """200×200 solid red JPEG."""
    img = Image.new("RGB", (200, 200), (200, 30, 30))
    p = tmp_path / filename
    img.save(str(p), format="JPEG")
    return p, p.read_bytes()


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestRunDetectionStagingIO:
    """Staging stores file + sidecar and nothing touches the DB (FR-24)."""

    def test_image_file_created(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        image_file = staging_dir / f"{result.token}.jpg"
        assert image_file.exists(), "staged image file missing"
        assert image_file.read_bytes() == data

    def test_sidecar_created(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        sidecar = staging_dir / f"{result.token}.json"
        assert sidecar.exists(), "sidecar missing"
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        assert payload["token"] == result.token
        assert "expires_at" in payload
        assert "colours" in payload["proposal"]

    def test_no_db_files_created(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        db_files = list(tmp_path.rglob("*.db")) + list(tmp_path.rglob("*.sqlite"))
        assert db_files == [], f"unexpected DB files created: {db_files}"

    def test_sidecar_garment_id_none_for_new_upload(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        payload = json.loads(
            (staging_dir / f"{result.token}.json").read_text(encoding="utf-8")
        )
        assert payload["garment_id"] is None


class TestRunDetectionResultShape:
    """DetectionResult matches the API contract §2.3 shape."""

    @pytest.fixture()
    def result(self, tmp_path) -> DetectionResult:
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        return run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )

    def test_token_is_nonempty_string(self, result):
        assert isinstance(result.token, str) and result.token

    def test_expires_at_is_iso8601(self, result):
        dt = datetime.fromisoformat(result.expires_at)
        assert dt.tzinfo is not None, "expires_at must be timezone-aware"

    def test_expires_at_is_in_future(self, result):
        dt = datetime.fromisoformat(result.expires_at)
        assert dt > datetime.now(timezone.utc), "expires_at must be in the future"

    def test_fallback_used_is_bool(self, result):
        assert isinstance(result.fallback_used, bool)

    def test_image_dimensions_positive(self, result):
        assert result.image_width > 0
        assert result.image_height > 0

    def test_colours_nonempty(self, result):
        assert len(result.colours) >= 1

    def test_proportions_sum_to_100(self, result):
        total = sum(c.proportion for c in result.colours)
        assert total == 100, f"proportions sum to {total}, expected 100"

    def test_each_colour_has_hex(self, result):
        for c in result.colours:
            assert isinstance(c.hex, str)
            assert c.hex.startswith("#") and len(c.hex) == 7

    def test_each_colour_has_neutral_bool(self, result):
        for c in result.colours:
            assert isinstance(c.neutral, bool)

    def test_each_colour_has_family_string(self, result):
        for c in result.colours:
            assert isinstance(c.family, str) and c.family

    def test_dominant_colour_is_red_family(self, result):
        dominant = max(result.colours, key=lambda c: c.proportion)
        assert dominant.family in {"Red", "Orange", "Pink"}, (
            f"expected dominant Red family, got {dominant.family}"
        )

    def test_garment_id_none_for_new_upload(self, result):
        assert result.garment_id is None


class TestProposalSidecarShape:
    """Sidecar proposal matches the API contract §2.3 ColourOut fields."""

    def test_sidecar_colours_have_all_fields(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        payload = json.loads(
            (staging_dir / f"{result.token}.json").read_text(encoding="utf-8")
        )
        for entry in payload["proposal"]["colours"]:
            for field in ("h", "s", "l", "family", "neutral", "hex", "proportion"):
                assert field in entry, f"missing field '{field}' in sidecar colour"


class TestRunDetectionFallbackSurface:
    """fallback_used is surfaced when the segmenter raises (FR-27, FR-28)."""

    def test_fallback_used_false_on_success(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)
        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_passthrough_segmenter, clusterer=_seeded_clusterer,
        )
        assert result.fallback_used is False

    def test_fallback_used_true_on_raising_segmenter(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)

        def _raising_segmenter(img):
            raise RuntimeError("segmentation failed")

        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_raising_segmenter, clusterer=_seeded_clusterer,
        )
        assert result.fallback_used is True

    def test_fallback_used_stored_in_sidecar(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        _, data = _make_red_jpeg(tmp_path)

        def _raising_segmenter(img):
            raise RuntimeError("segmentation failed")

        result = run_detection(
            data, "jpg", "image/jpeg", staging_dir,
            segmenter=_raising_segmenter, clusterer=_seeded_clusterer,
        )
        payload = json.loads(
            (staging_dir / f"{result.token}.json").read_text(encoding="utf-8")
        )
        assert payload["fallback_used"] is True


class TestRunRegeneration:
    """Regeneration binds the token to a garment_id (§2.9, FR-32)."""

    @pytest.fixture()
    def images_dir(self, tmp_path) -> Path:
        d = tmp_path / "images"
        d.mkdir()
        img = Image.new("RGB", (200, 200), (30, 100, 200))
        img.save(str(d / "garment-abc123.jpg"), format="JPEG")
        return d

    def test_result_has_garment_id(self, tmp_path, images_dir):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        result = run_regeneration(
            garment_id="garment-abc123",
            image_file="garment-abc123.jpg",
            images_dir=images_dir,
            staging_dir=staging_dir,
            segmenter=_passthrough_segmenter,
            clusterer=_seeded_clusterer,
        )
        assert result.garment_id == "garment-abc123"

    def test_sidecar_binds_garment_id(self, tmp_path, images_dir):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        result = run_regeneration(
            garment_id="garment-abc123",
            image_file="garment-abc123.jpg",
            images_dir=images_dir,
            staging_dir=staging_dir,
            segmenter=_passthrough_segmenter,
            clusterer=_seeded_clusterer,
        )
        payload = json.loads(
            (staging_dir / f"{result.token}.json").read_text(encoding="utf-8")
        )
        assert payload["garment_id"] == "garment-abc123"

    def test_proportions_sum_to_100(self, tmp_path, images_dir):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        result = run_regeneration(
            garment_id="garment-abc123",
            image_file="garment-abc123.jpg",
            images_dir=images_dir,
            staging_dir=staging_dir,
            segmenter=_passthrough_segmenter,
            clusterer=_seeded_clusterer,
        )
        assert sum(c.proportion for c in result.colours) == 100

    def test_ttl_sweep_removes_expired_entry(self, tmp_path, images_dir):
        """Sweep removes expired sidecar — staging sweep contract honoured."""
        from datetime import timedelta
        from app.storage import staging as _staging

        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        result = run_regeneration(
            garment_id="garment-abc123",
            image_file="garment-abc123.jpg",
            images_dir=images_dir,
            staging_dir=staging_dir,
            segmenter=_passthrough_segmenter,
            clusterer=_seeded_clusterer,
        )
        # Force-expire the sidecar
        sidecar = staging_dir / f"{result.token}.json"
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        past = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        data["expires_at"] = past
        sidecar.write_text(json.dumps(data), encoding="utf-8")

        removed = _staging.sweep(staging_dir)
        assert removed == 1
        assert not sidecar.exists()
