"""
Tests for storage.image_store (test strategy §7.3).

Coverage:
  - save_original writes the exact bytes supplied and returns the expected filename.
  - generate_thumbnail produces a WebP file whose longest edge is ≤ 320 px and
    whose aspect ratio is preserved.
  - Oversized and portrait images are both handled correctly.
"""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app.storage.image_store import _THUMBNAIL_MAX_PX, generate_thumbnail, save_original


# ── Helpers ───────────────────────────────────────────────────────────────────

def _png_bytes(width: int, height: int) -> bytes:
    """Return PNG-encoded bytes for a solid red image of the given dimensions."""
    img = Image.new("RGB", (width, height), color=(200, 50, 50))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ── save_original ─────────────────────────────────────────────────────────────

class TestSaveOriginal:
    def test_file_created_with_correct_name(self, tmp_path) -> None:
        data = _png_bytes(100, 100)
        name = save_original(data, "png", "abc123", tmp_path)
        assert name == "abc123.png"
        assert (tmp_path / "abc123.png").exists()

    def test_file_content_matches_input(self, tmp_path) -> None:
        data = _png_bytes(64, 64)
        save_original(data, "jpg", "g1", tmp_path)
        assert (tmp_path / "g1.jpg").read_bytes() == data

    def test_different_extensions_preserved(self, tmp_path) -> None:
        for ext in ("jpg", "jpeg", "png", "webp"):
            data = _png_bytes(32, 32)
            name = save_original(data, ext, f"g-{ext}", tmp_path)
            assert name == f"g-{ext}.{ext}"
            assert (tmp_path / name).exists()


# ── generate_thumbnail ────────────────────────────────────────────────────────

class TestGenerateThumbnail:
    def _make_source(self, tmp_path, width: int, height: int, name: str = "src.png") -> object:
        src = tmp_path / name
        src.write_bytes(_png_bytes(width, height))
        return src

    def test_thumbnail_is_webp(self, tmp_path) -> None:
        src = self._make_source(tmp_path, 200, 100)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        name = generate_thumbnail(src, thumbnails, "g1")
        assert name == "g1.webp"
        assert (thumbnails / "g1.webp").exists()

    def test_landscape_longest_edge_capped(self, tmp_path) -> None:
        src = self._make_source(tmp_path, 800, 400)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        generate_thumbnail(src, thumbnails, "g1")
        with Image.open(thumbnails / "g1.webp") as thumb:
            assert max(thumb.width, thumb.height) <= _THUMBNAIL_MAX_PX

    def test_portrait_longest_edge_capped(self, tmp_path) -> None:
        src = self._make_source(tmp_path, 300, 900)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        generate_thumbnail(src, thumbnails, "g1")
        with Image.open(thumbnails / "g1.webp") as thumb:
            assert max(thumb.width, thumb.height) <= _THUMBNAIL_MAX_PX

    def test_aspect_ratio_preserved(self, tmp_path) -> None:
        src = self._make_source(tmp_path, 640, 480)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        generate_thumbnail(src, thumbnails, "g1")
        with Image.open(thumbnails / "g1.webp") as thumb:
            original_ratio = 640 / 480
            thumb_ratio = thumb.width / thumb.height
            assert abs(thumb_ratio - original_ratio) < 0.02

    def test_small_image_not_upscaled(self, tmp_path) -> None:
        """Images smaller than 320 px must not be upscaled."""
        src = self._make_source(tmp_path, 100, 80)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        generate_thumbnail(src, thumbnails, "g1")
        with Image.open(thumbnails / "g1.webp") as thumb:
            assert thumb.width <= 100
            assert thumb.height <= 80

    def test_square_image_at_boundary(self, tmp_path) -> None:
        src = self._make_source(tmp_path, 320, 320)
        thumbnails = tmp_path / "thumbs"
        thumbnails.mkdir()
        generate_thumbnail(src, thumbnails, "g1")
        with Image.open(thumbnails / "g1.webp") as thumb:
            assert thumb.width <= _THUMBNAIL_MAX_PX
            assert thumb.height <= _THUMBNAIL_MAX_PX
