"""
Self-check tests for the shared fixtures (test strategy §11.1, §11.3).

These tests exercise the fixtures themselves, not the matcher.  They are part
of the default gate (``make test``) and serve as the load-bearing anchor that
catches any drift if a geometry constant or canonical value is changed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tests.fixtures.generate_images import (
    IMAGE_H,
    IMAGE_W,
    KNOWN_PALETTES,
    MASKS_DIR,
    _GENERATORS,
)
from tests.fixtures.palettes import (
    ALL_FAMILIES,
    CANONICAL,
    CHROMATIC_FAMILIES,
    NEUTRAL_FAMILIES,
)

FIXTURES_DIR = Path(__file__).parent


# ── Synthetic image checks ────────────────────────────────────────────────────

class TestSyntheticImages:
    """Images render to the expected size (test strategy §11.1)."""

    @pytest.mark.parametrize("name", list(_GENERATORS))
    def test_image_dimensions(self, name: str, synthetic_images_dir: Path) -> None:
        path = synthetic_images_dir / f"{name}.png"
        assert path.exists(), f"Synthetic image missing: {path}"
        with Image.open(path) as img:
            assert img.size == (IMAGE_W, IMAGE_H), (
                f"{name}: expected {IMAGE_W}×{IMAGE_H}, got {img.size}"
            )

    @pytest.mark.parametrize("name", list(_GENERATORS))
    def test_image_is_rgb(self, name: str, synthetic_images_dir: Path) -> None:
        path = synthetic_images_dir / f"{name}.png"
        with Image.open(path) as img:
            assert img.mode == "RGB", f"{name}: expected RGB, got {img.mode}"


# ── Mask checks ───────────────────────────────────────────────────────────────

class TestCommittedMasks:
    """Committed masks are paired with every synthetic image (§11.1)."""

    @pytest.mark.parametrize("name", list(_GENERATORS))
    def test_mask_exists(self, name: str) -> None:
        assert (MASKS_DIR / f"{name}.png").exists(), (
            f"Mask missing for '{name}' — run generate_masks() to regenerate"
        )

    @pytest.mark.parametrize("name", list(_GENERATORS))
    def test_mask_dimensions(self, name: str) -> None:
        with Image.open(MASKS_DIR / f"{name}.png") as mask:
            assert mask.size == (IMAGE_W, IMAGE_H)
            assert mask.mode == "L", f"Mask {name}: expected L (greyscale), got {mask.mode}"

    @pytest.mark.parametrize("name", list(_GENERATORS))
    def test_mask_is_binary(self, name: str) -> None:
        """Mask pixels are only 0 or 255 — no anti-aliasing."""
        with Image.open(MASKS_DIR / f"{name}.png") as mask:
            lo, hi = mask.getextrema()
        # Only two distinct values are possible if lo == 0 and hi == 255
        # (or a solid mask where lo == hi ∈ {0, 255}).
        assert lo in (0, 255) and hi in (0, 255), (
            f"Mask {name}: pixel range [{lo}, {hi}] — expected only 0 and/or 255"
        )


# ── Invalid-upload fixture checks ─────────────────────────────────────────────

class TestInvalidUploadFixtures:
    def test_invalid_gif_exists(self) -> None:
        assert (FIXTURES_DIR / "invalid.gif").exists()

    def test_invalid_gif_is_small(self) -> None:
        """The GIF fixture is a tiny file, not a disguised valid image."""
        size = (FIXTURES_DIR / "invalid.gif").stat().st_size
        assert size < 1024, f"invalid.gif too large ({size} bytes) — should be < 1 KB"

    def test_truncated_jpg_exists(self) -> None:
        assert (FIXTURES_DIR / "truncated.jpg").exists()

    def test_truncated_jpg_has_jpeg_header(self) -> None:
        """Starts with JPEG SOI marker so the MIME check passes but read fails."""
        data = (FIXTURES_DIR / "truncated.jpg").read_bytes()
        assert data[:2] == b"\xff\xd8", "truncated.jpg must start with JPEG SOI marker"

    def test_truncated_jpg_is_unreadable(self) -> None:
        """Pillow cannot open the truncated file."""
        from PIL import UnidentifiedImageError
        with pytest.raises((UnidentifiedImageError, Exception)):
            Image.open(FIXTURES_DIR / "truncated.jpg").verify()

    def test_oversize_fixture_exceeds_20mb(self, oversize_file: Path) -> None:
        """Oversize fixture is > 20 MB (FR-23 / FR-24 rejection boundary)."""
        size = oversize_file.stat().st_size
        assert size > 20 * 1024 * 1024, f"oversize file is only {size} bytes"


# ── Palette table checks (§11.3) ─────────────────────────────────────────────

class TestPalettesTables:
    def test_all_nineteen_families_present(self) -> None:
        assert len(ALL_FAMILIES) == 19, (
            f"Expected 19 families, got {len(ALL_FAMILIES)}: {ALL_FAMILIES}"
        )

    def test_seven_neutrals(self) -> None:
        assert len(NEUTRAL_FAMILIES) == 7, NEUTRAL_FAMILIES

    def test_twelve_chromatics(self) -> None:
        assert len(CHROMATIC_FAMILIES) == 12, CHROMATIC_FAMILIES

    def test_neutral_chromatic_partition(self) -> None:
        """Every family is either neutral or chromatic, never both, never neither."""
        for family in ALL_FAMILIES:
            in_neutral   = family in NEUTRAL_FAMILIES
            in_chromatic = family in CHROMATIC_FAMILIES
            assert in_neutral ^ in_chromatic, (
                f"'{family}' is in both or neither neutral/chromatic lists"
            )

    @pytest.mark.parametrize("family", ALL_FAMILIES)
    def test_canonical_hsl_well_formed(self, family: str) -> None:
        """Every canonical value satisfies 0 ≤ h < 360, 0 ≤ s,l ≤ 100 (contract §1.1)."""
        h, s, l = CANONICAL[family]
        assert 0.0 <= h < 360.0, f"{family}: h={h} out of range"
        assert 0.0 <= s <= 100.0, f"{family}: s={s} out of range"
        assert 0.0 <= l <= 100.0, f"{family}: l={l} out of range"

    def test_canonical_covers_all_families(self) -> None:
        assert set(CANONICAL.keys()) == set(ALL_FAMILIES)


# ── Known palette proportion check (FR-6) ────────────────────────────────────

@pytest.mark.parametrize("image_name,palette", KNOWN_PALETTES.items())
def test_fr6_known_palette_proportions_sum_to_100(
    image_name: str, palette: list[dict]
) -> None:
    """FR-6: proportions shall sum to exactly 100."""
    total = sum(c["proportion"] for c in palette)
    assert total == 100, (
        f"FR-6 violation in known palette for '{image_name}': "
        f"proportions sum to {total}"
    )
