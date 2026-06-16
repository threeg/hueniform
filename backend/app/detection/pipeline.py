"""
Detection pipeline: photograph → proposed palette (FR-26, FR-27, architecture §2.3).

Steps:
  1. Decode image bytes with Pillow.
  2. Segment with an injectable segmenter (default: rembg).
  3. Fallback check (FR-27): if segmentation raises or mask coverage is below
     MINIMUM_FOREGROUND, use whole-image pixels and set ``fallback_used = True``.
  4. Sample masked (or whole-image) pixels; cluster with KMeans for k = 1…4;
     select k by the inertia-elbow heuristic.
  5. Merge same-family clusters; convert centroids to HSL; classify families;
     compute integer proportions (FR-6).
  6. Return a ``DetectionProposal`` — no persistence here.

The *segmenter* and *clusterer* parameters are injectable seams (test strategy
§6.2) so the default gate can drive the pipeline deterministically with committed
masks and a seeded KMeans, without requiring the rembg model or scikit-learn's
non-deterministic initialisation.
"""

from __future__ import annotations

import io
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from PIL import Image

from app.matcher import constants as C
from app.matcher.colour import rgb_to_hsl
from app.matcher.taxonomy import classify as _classify
from app.detection.helpers import (
    is_foreground_sufficient,
    merge_clusters,
    select_k,
    to_proportions,
)

# Maximum number of pixels to sample for clustering (NFR-4 performance bound).
_PIXEL_SAMPLE: int = 2000
# Maximum k to try (FR-6: 1–4 colours per garment).
_K_MAX: int = 4

# Callable signatures for the injectable seams.
Segmenter = Callable[[Image.Image], Image.Image]
Clusterer = Callable[[np.ndarray, int], tuple[np.ndarray, np.ndarray]]


# ── Value types returned by the pipeline ─────────────────────────────────────

@dataclass(frozen=True)
class ColourEntry:
    """One detected colour with its HSL centroid, family and proportion."""
    h: float          # hue in [0, 360)
    s: float          # saturation in [0, 100]
    l: float          # lightness in [0, 100]
    family: str       # taxonomy family name (FR-1)
    proportion: int   # integer percentage [1, 100]; all entries sum to 100 (FR-6)


@dataclass(frozen=True)
class DetectionProposal:
    """Proposed palette produced by the pipeline. Never persisted directly."""
    colours: tuple[ColourEntry, ...]
    fallback_used: bool   # True when rembg failed or mask was below threshold (FR-27)
    width: int            # original image width in pixels
    height: int           # original image height in pixels


# ── Default segmenter (lazy rembg import — not loaded in the default test gate)

def _default_segmenter(img: Image.Image) -> Image.Image:
    import rembg  # noqa: PLC0415
    result = rembg.remove(img)
    if isinstance(result, Image.Image):
        return result
    # Older rembg versions return bytes.
    return Image.open(io.BytesIO(result))


# ── Default clusterer (lazy sklearn import, non-deterministic) ────────────────

def _default_clusterer(pixels: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    from sklearn.cluster import KMeans  # noqa: PLC0415
    km = KMeans(n_clusters=k, n_init=10)
    labels = km.fit_predict(pixels)
    return km.cluster_centers_, labels


# ── Internal helpers ──────────────────────────────────────────────────────────

def _compute_inertia(
    pixels: np.ndarray,
    centres: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Sum of squared distances from each pixel to its cluster centre."""
    total = 0.0
    for i in range(len(centres)):
        mask = labels == i
        if mask.any():
            diff = pixels[mask] - centres[i]
            total += float(np.sum(diff ** 2))
    return total


def _sample_pixels(img: Image.Image, alpha: np.ndarray | None) -> np.ndarray:
    """
    Return up to ``_PIXEL_SAMPLE`` RGB pixel rows from *img*.

    If *alpha* is provided, only pixels where alpha > 128 are eligible
    (masked-area sampling).  Downsamples linearly when the eligible count
    exceeds the cap.
    """
    arr = np.array(img.convert("RGB"), dtype=float)
    flat = arr.reshape(-1, 3)
    if alpha is not None:
        flat = flat[alpha.flatten() > 128]
    n = len(flat)
    if n > _PIXEL_SAMPLE:
        idx = np.linspace(0, n - 1, _PIXEL_SAMPLE, dtype=int)
        flat = flat[idx]
    return flat


# ── Public entry point ────────────────────────────────────────────────────────

def detect(
    image_data: bytes,
    *,
    segmenter: Segmenter | None = None,
    clusterer: Clusterer | None = None,
) -> DetectionProposal:
    """
    Run the detection pipeline and return a ``DetectionProposal``.

    Parameters
    ----------
    image_data:
        Raw image bytes (JPEG, PNG, WebP, …).
    segmenter:
        Callable ``(img: Image) → Image`` that returns an RGBA image whose
        alpha channel is the foreground mask.  Defaults to rembg.  In tests,
        inject a function that pastes a committed mask onto the image.
    clusterer:
        Callable ``(pixels: np.ndarray, k: int) → (centres, labels)`` where
        *centres* is shape ``(k, 3)`` and *labels* is shape ``(n,)``.
        Defaults to KMeans with ``n_init=10``.  In tests, inject a seeded
        KMeans to get deterministic results.
    """
    _seg = segmenter if segmenter is not None else _default_segmenter
    _clus = clusterer if clusterer is not None else _default_clusterer

    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    width, height = img.size

    # ── Step 1: segment and check foreground coverage ─────────────────────────
    alpha: np.ndarray | None = None
    fallback_used = False
    try:
        segmented = _seg(img)
        # Accept either RGBA (standard rembg output) or L-mode alpha mask.
        if segmented.mode == "RGBA":
            alpha_channel = np.array(segmented.split()[3])
        else:
            alpha_channel = np.array(segmented.convert("L"))
        coverage = float(np.mean(alpha_channel > 128))
        if is_foreground_sufficient(coverage):
            alpha = alpha_channel
        else:
            fallback_used = True
    except Exception:  # noqa: BLE001 — any segmentation failure triggers fallback
        fallback_used = True

    # ── Step 2: sample pixels ─────────────────────────────────────────────────
    pixels = _sample_pixels(img, alpha)
    if len(pixels) == 0:
        # Edge case: mask returned no foreground pixels — fall back to whole image.
        pixels = _sample_pixels(img, None)
        fallback_used = True

    # ── Step 3: cluster for k = 1…min(K_MAX, pixel_count, distinct_colours) ───
    # Capping by the number of distinct pixel values prevents sklearn from
    # emitting ConvergenceWarning on images with fewer distinct colours than k.
    n_distinct = len(np.unique(pixels.astype(int), axis=0))
    max_k = min(_K_MAX, len(pixels), n_distinct)
    inertias: list[float] = []
    results: list[tuple[np.ndarray, np.ndarray]] = []
    for k in range(1, max_k + 1):
        centres, labels = _clus(pixels, k)
        inertias.append(_compute_inertia(pixels, centres, labels))
        results.append((centres, labels))

    # ── Step 4: select k, merge same-family clusters ──────────────────────────
    best_k = select_k(inertias)
    centres, labels = results[best_k - 1]

    counts = np.bincount(labels, minlength=best_k).astype(float)

    raw_clusters: list[tuple[float, float, float, float]] = []
    for i in range(best_k):
        r, g, b = centres[i]
        h, s, l = rgb_to_hsl(round(float(r)), round(float(g)), round(float(b)))
        raw_clusters.append((h, s, l, float(counts[i])))

    merged = merge_clusters(raw_clusters)

    # ── Step 5: proportions, sort, classify ───────────────────────────────────
    merged_weights = [w for _, _, _, w in merged]
    proportions = to_proportions(merged_weights)

    order = sorted(range(len(merged)), key=lambda i: -proportions[i])
    colours: list[ColourEntry] = []
    for i in order:
        h, s, l, _ = merged[i]
        colours.append(
            ColourEntry(
                h=h,
                s=s,
                l=l,
                family=_classify(h, s, l),
                proportion=proportions[i],
            )
        )

    return DetectionProposal(
        colours=tuple(colours),
        fallback_used=fallback_used,
        width=width,
        height=height,
    )
