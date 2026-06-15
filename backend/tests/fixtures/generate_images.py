"""
Deterministic synthetic image generator for the Hueniform test suite (§11.1).

Three garment images are produced on first use and cached in
``backend/tests/fixtures/synthetic/`` (gitignored).  They are regenerated if
the cache directory is missing; the pixel content is fully determined by the
constants below — no randomness.

Image inventory
---------------
flat_red        — solid red (#CC2020) rectangle on a white background;
                  palette: Red 100%.
two_colour_block — upper teal (#2CADA0) / lower orange (#EE8225) split block
                  on a dark-grey background; palette: Teal 80%, Orange 20%.
thin_stripe      — teal body (#2CADA0) with a single thin orange (#EE8225)
                  stripe near the bottom; palette: Teal 88%, Orange 12%.
                  Orange is a *minor* colour (< 15%) — the FR-11 echo-bonus
                  fixture.

Each image is ``IMAGE_W × IMAGE_H`` pixels.  The garment occupies the centre
``GARMENT_W × GARMENT_H`` region; background fills the rest.

Paired masks
------------
The corresponding ``masks/<name>.png`` files are committed alpha-channel images
(mode ``L``): 255 inside the garment rectangle, 0 outside — ready for the
§6.2 injected-segmenter tests.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# ── Layout ────────────────────────────────────────────────────────────────────
IMAGE_W, IMAGE_H = 400, 500
GARMENT_W, GARMENT_H = 280, 380
GARMENT_X = (IMAGE_W - GARMENT_W) // 2   # 60
GARMENT_Y = (IMAGE_H - GARMENT_H) // 2   # 60
GARMENT_BOX = (GARMENT_X, GARMENT_Y, GARMENT_X + GARMENT_W, GARMENT_Y + GARMENT_H)

# ── Colours (RGB) ─────────────────────────────────────────────────────────────
BG_WHITE     = (255, 255, 255)
BG_DARKGREY  = (30,  30,  30)
RED          = (204, 32,  32)    # HSL ≈ (0°, 73%, 46%) → Red
TEAL         = (45,  173, 160)   # HSL ≈ (174°, 58%, 43%) → Teal  (#2CADA0)
ORANGE       = (238, 130, 37)    # HSL ≈ (28°, 85%, 54%) → Orange (#EE8225)

# ── Known palettes (for test assertions — FR-6: proportions sum to 100) ───────
# Proportions are pixel-exact for the geometry above.
_TOTAL_GARMENT_PX = GARMENT_W * GARMENT_H  # 280 * 380 = 106 400

def _split_proportions(top_fraction: float) -> tuple[int, int]:
    """Return (top_pct, bottom_pct) as integers summing to 100."""
    top = round(top_fraction * 100)
    return top, 100 - top

_STRIPE_H = 12   # thin-stripe image: orange stripe height in pixels

def _stripe_proportions() -> tuple[int, int]:
    """Return (teal_pct, orange_pct) summing to 100 for the stripe image."""
    orange_px = GARMENT_W * _STRIPE_H
    orange = round(orange_px / _TOTAL_GARMENT_PX * 100)
    return 100 - orange, orange

TWO_COLOUR_SPLIT = 0.80     # 80% teal, 20% orange (top fraction)

KNOWN_PALETTES: dict[str, list[dict]] = {
    "flat_red": [
        {"family": "Red", "proportion": 100},
    ],
    "two_colour_block": [
        {"family": "Teal",   "proportion": _split_proportions(TWO_COLOUR_SPLIT)[0]},
        {"family": "Orange", "proportion": _split_proportions(TWO_COLOUR_SPLIT)[1]},
    ],
    "thin_stripe": [
        {"family": "Teal",   "proportion": _stripe_proportions()[0]},
        {"family": "Orange", "proportion": _stripe_proportions()[1]},
    ],
}

# Validate at import time — FR-6: proportions must sum to 100.
for _name, _palette in KNOWN_PALETTES.items():
    _total = sum(c["proportion"] for c in _palette)
    assert _total == 100, f"{_name}: proportions sum to {_total}, not 100 (FR-6)"


# ── Generator ─────────────────────────────────────────────────────────────────

def _draw_garment_box(img: Image.Image, colour: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(img)
    draw.rectangle(GARMENT_BOX, fill=colour)


def _make_flat_red() -> Image.Image:
    img = Image.new("RGB", (IMAGE_W, IMAGE_H), BG_WHITE)
    _draw_garment_box(img, RED)
    return img


def _make_two_colour_block() -> Image.Image:
    img = Image.new("RGB", (IMAGE_W, IMAGE_H), BG_DARKGREY)
    teal_h = round(GARMENT_H * TWO_COLOUR_SPLIT)
    draw = ImageDraw.Draw(img)
    # Top portion — Teal
    draw.rectangle(
        (GARMENT_X, GARMENT_Y, GARMENT_X + GARMENT_W, GARMENT_Y + teal_h),
        fill=TEAL,
    )
    # Bottom portion — Orange
    draw.rectangle(
        (GARMENT_X, GARMENT_Y + teal_h, GARMENT_X + GARMENT_W, GARMENT_Y + GARMENT_H),
        fill=ORANGE,
    )
    return img


def _make_thin_stripe() -> Image.Image:
    img = Image.new("RGB", (IMAGE_W, IMAGE_H), BG_DARKGREY)
    draw = ImageDraw.Draw(img)
    # Teal body
    draw.rectangle(GARMENT_BOX, fill=TEAL)
    # Thin orange stripe near the bottom
    stripe_y = GARMENT_Y + GARMENT_H - _STRIPE_H - 20
    draw.rectangle(
        (GARMENT_X, stripe_y, GARMENT_X + GARMENT_W, stripe_y + _STRIPE_H),
        fill=ORANGE,
    )
    return img


def _make_mask() -> Image.Image:
    """Alpha mask: 255 inside the garment box, 0 outside."""
    mask = Image.new("L", (IMAGE_W, IMAGE_H), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(GARMENT_BOX, fill=255)
    return mask


_GENERATORS: dict[str, callable] = {
    "flat_red":         _make_flat_red,
    "two_colour_block": _make_two_colour_block,
    "thin_stripe":      _make_thin_stripe,
}

SYNTHETIC_DIR = Path(__file__).parent / "synthetic"
MASKS_DIR     = Path(__file__).parent / "masks"


def generate_all(output_dir: Path | None = None) -> Path:
    """
    Render all synthetic images into *output_dir* (defaults to
    ``fixtures/synthetic/``).  Idempotent — skips files that exist.
    Returns the output directory path.
    """
    out = output_dir or SYNTHETIC_DIR
    out.mkdir(parents=True, exist_ok=True)
    for name, gen in _GENERATORS.items():
        dest = out / f"{name}.png"
        if not dest.exists():
            gen().save(dest, format="PNG")
    return out


def get_synthetic_path(name: str, output_dir: Path | None = None) -> Path:
    """Return the path to a named synthetic image, generating it if needed."""
    out = generate_all(output_dir)
    path = out / f"{name}.png"
    if not path.exists():
        raise FileNotFoundError(f"Unknown synthetic image '{name}'")
    return path


def generate_masks(masks_dir: Path | None = None) -> None:
    """
    Render the alpha masks into *masks_dir* (defaults to ``fixtures/masks/``).
    The masks are the same for all three images (same garment box geometry).
    Idempotent.
    """
    out = masks_dir or MASKS_DIR
    out.mkdir(parents=True, exist_ok=True)
    mask = _make_mask()
    for name in _GENERATORS:
        dest = out / f"{name}.png"
        if not dest.exists():
            mask.save(dest, format="PNG")
