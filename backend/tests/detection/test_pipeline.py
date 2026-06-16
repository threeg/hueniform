"""
Default-gate pipeline tests (test strategy §6.2).

Drives ``detection.pipeline.detect`` with committed alpha masks replacing rembg
and a seeded KMeans replacing the non-deterministic default clusterer.  No model
file is required — these tests run in the standard ``make test`` gate.

Coverage:
  - FR-26: pipeline produces 1–4 colours with proportions summing to 100.
  - FR-27: raising segmenter and below-threshold mask both trigger fallback.
  - §6.2: injected-mask path is deterministic; expected palettes within ±5 pp.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.detection.pipeline import ColourEntry, DetectionProposal, detect
from tests.fixtures.generate_images import (
    IMAGE_H,
    IMAGE_W,
    KNOWN_PALETTES,
    MASKS_DIR,
    generate_all,
    get_synthetic_path,
)

_TOLERANCE = 5  # §6.2: ±5 percentage-point tolerance on proportions


# ── Injectable seams ──────────────────────────────────────────────────────────

def _seeded_clusterer(
    pixels: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic KMeans with a fixed random seed."""
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=k, n_init=10, random_state=0)
    labels = km.fit_predict(pixels)
    return km.cluster_centers_, labels


def _mask_segmenter(name: str):
    """
    Return a segmenter that pastes the committed alpha mask onto the image.

    The masks directory contains L-mode PNGs (255 = foreground) committed to
    the repository.  The segmenter composes them as the RGBA alpha channel.
    """
    mask_path = MASKS_DIR / f"{name}.png"

    def seg(img: Image.Image) -> Image.Image:
        mask = Image.open(mask_path).convert("L")
        rgba = img.convert("RGBA")
        rgba.putalpha(mask)
        return rgba

    return seg


def _load_bytes(name: str) -> bytes:
    """Return raw bytes for a synthetic fixture image, generating it if needed."""
    return get_synthetic_path(name).read_bytes()


def _colour_by_family(proposal: DetectionProposal, family: str) -> ColourEntry | None:
    for c in proposal.colours:
        if c.family == family:
            return c
    return None


# ── flat_red — single-colour garment ─────────────────────────────────────────

class TestFlatRed:
    def _run(self) -> DetectionProposal:
        return detect(
            _load_bytes("flat_red"),
            segmenter=_mask_segmenter("flat_red"),
            clusterer=_seeded_clusterer,
        )

    def test_returns_one_colour(self) -> None:
        assert len(self._run().colours) == 1

    def test_colour_family_is_red(self) -> None:
        assert self._run().colours[0].family == "Red"

    def test_proportion_is_100(self) -> None:
        assert self._run().colours[0].proportion == 100

    def test_fallback_not_used(self) -> None:
        assert self._run().fallback_used is False

    def test_image_dimensions(self) -> None:
        r = self._run()
        assert r.width == IMAGE_W
        assert r.height == IMAGE_H


# ── two_colour_block — 80 % Teal / 20 % Orange ───────────────────────────────

class TestTwoColourBlock:
    def _run(self) -> DetectionProposal:
        return detect(
            _load_bytes("two_colour_block"),
            segmenter=_mask_segmenter("two_colour_block"),
            clusterer=_seeded_clusterer,
        )

    def test_returns_two_colours(self) -> None:
        assert len(self._run().colours) == 2

    def test_proportions_sum_to_100(self) -> None:
        assert sum(c.proportion for c in self._run().colours) == 100

    def test_teal_is_dominant(self) -> None:
        assert self._run().colours[0].family == "Teal"

    def test_teal_proportion_within_tolerance(self) -> None:
        expected = KNOWN_PALETTES["two_colour_block"][0]["proportion"]
        c = _colour_by_family(self._run(), "Teal")
        assert c is not None
        assert abs(c.proportion - expected) <= _TOLERANCE

    def test_orange_proportion_within_tolerance(self) -> None:
        expected = KNOWN_PALETTES["two_colour_block"][1]["proportion"]
        c = _colour_by_family(self._run(), "Orange")
        assert c is not None
        assert abs(c.proportion - expected) <= _TOLERANCE

    def test_fallback_not_used(self) -> None:
        assert self._run().fallback_used is False


# ── thin_stripe — 97 % Teal / 3 % Orange (minor-colour fixture) ──────────────

class TestThinStripe:
    def _run(self) -> DetectionProposal:
        return detect(
            _load_bytes("thin_stripe"),
            segmenter=_mask_segmenter("thin_stripe"),
            clusterer=_seeded_clusterer,
        )

    def test_teal_is_present_and_dominant(self) -> None:
        r = self._run()
        assert r.colours[0].family == "Teal"

    def test_teal_proportion_within_tolerance(self) -> None:
        expected = KNOWN_PALETTES["thin_stripe"][0]["proportion"]
        c = _colour_by_family(self._run(), "Teal")
        assert c is not None
        assert abs(c.proportion - expected) <= _TOLERANCE

    def test_proportions_sum_to_100(self) -> None:
        assert sum(c.proportion for c in self._run().colours) == 100

    def test_fallback_not_used(self) -> None:
        assert self._run().fallback_used is False


# ── Fallback path — raising segmenter (FR-27) ─────────────────────────────────

class TestFallbackOnRaisingSegmenter:
    def _run(self) -> DetectionProposal:
        def raising_seg(img: Image.Image) -> Image.Image:
            raise RuntimeError("segmentation failed")

        return detect(
            _load_bytes("flat_red"),
            segmenter=raising_seg,
            clusterer=_seeded_clusterer,
        )

    def test_fallback_used_is_true(self) -> None:
        assert self._run().fallback_used is True

    def test_still_returns_at_least_one_colour(self) -> None:
        assert len(self._run().colours) >= 1

    def test_proportions_still_sum_to_100(self) -> None:
        assert sum(c.proportion for c in self._run().colours) == 100


# ── Fallback path — below-threshold coverage (FR-27) ─────────────────────────

class TestFallbackOnLowCoverage:
    def _run(self) -> DetectionProposal:
        def empty_mask_seg(img: Image.Image) -> Image.Image:
            rgba = img.convert("RGBA")
            zero_alpha = Image.new("L", rgba.size, 0)
            rgba.putalpha(zero_alpha)
            return rgba

        return detect(
            _load_bytes("flat_red"),
            segmenter=empty_mask_seg,
            clusterer=_seeded_clusterer,
        )

    def test_fallback_used_is_true(self) -> None:
        assert self._run().fallback_used is True

    def test_still_returns_at_least_one_colour(self) -> None:
        assert len(self._run().colours) >= 1

    def test_proportions_still_sum_to_100(self) -> None:
        assert sum(c.proportion for c in self._run().colours) == 100


# ── Structural invariants (FR-26, FR-6) ──────────────────────────────────────

class TestInvariants:
    _NAMES = ("flat_red", "two_colour_block", "thin_stripe")

    @pytest.mark.parametrize("name", _NAMES)
    def test_proportions_sum_to_100(self, name: str) -> None:
        r = detect(
            _load_bytes(name),
            segmenter=_mask_segmenter(name),
            clusterer=_seeded_clusterer,
        )
        assert sum(c.proportion for c in r.colours) == 100

    @pytest.mark.parametrize("name", _NAMES)
    def test_colour_count_between_1_and_4(self, name: str) -> None:
        r = detect(
            _load_bytes(name),
            segmenter=_mask_segmenter(name),
            clusterer=_seeded_clusterer,
        )
        assert 1 <= len(r.colours) <= 4

    @pytest.mark.parametrize("name", _NAMES)
    def test_all_proportions_at_least_1(self, name: str) -> None:
        r = detect(
            _load_bytes(name),
            segmenter=_mask_segmenter(name),
            clusterer=_seeded_clusterer,
        )
        assert all(c.proportion >= 1 for c in r.colours)

    @pytest.mark.parametrize("name", _NAMES)
    def test_sorted_descending_by_proportion(self, name: str) -> None:
        r = detect(
            _load_bytes(name),
            segmenter=_mask_segmenter(name),
            clusterer=_seeded_clusterer,
        )
        props = [c.proportion for c in r.colours]
        assert props == sorted(props, reverse=True)
