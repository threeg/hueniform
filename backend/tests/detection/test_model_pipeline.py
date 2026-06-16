"""
Real-model detection tests (test strategy §6.3).

Marker: ``model`` — excluded from ``make test``, run by ``make test-model``.
Skips with a clear message if the rembg U²-Net model is absent from the
directory named by the ``U2NET_HOME`` environment variable (or ``data/models/``
by default) — absence must never read as a pass (§6.3).

What is exercised here (§6.3):
  - FR-26: real rembg + KMeans over committed photographs → 1–4 colours, sum 100.
  - FR-27: the garment-free fixture triggers ``fallback_used = True`` for real.
  - NFR-4 (soft): wall-time > 5 s → pytest warning; > 10 s → assertion failure.
  - §11.1: assertions are sidecar-driven (tolerance-based, not pixel-exact).

Assertion logic per sidecar (``<name>.expected.json``):
  - ``fallback_expected = true``  → assert ``result.fallback_used is True``.
  - ``dominant_family`` (non-null) → dominant family matches and proportion is
    within ``[dominant_proportion_min, dominant_proportion_max]``.
  - All detected families must be in ``{dominant_family} ∪ allowed_extra_families``.
  - Colour count is within ``[count_min, count_max]``.
  - Proportions always sum to exactly 100 (FR-6 invariant).
"""

from __future__ import annotations

import json
import os
import time
import warnings
from pathlib import Path

import pytest

from app.detection.pipeline import detect

# ── Model availability check (skip entire module if model absent) ─────────────

_U2NET_HOME = Path(os.environ.get("U2NET_HOME", "data/models"))
_MODEL_FILE = _U2NET_HOME / "u2net.onnx"

if not _MODEL_FILE.exists():
    pytest.skip(
        f"rembg U²-Net model not found at {_MODEL_FILE}. "
        "Run 'make setup' to fetch it.",
        allow_module_level=True,
    )

# ── Fixture directory ─────────────────────────────────────────────────────────

_REAL_DIR = Path(__file__).parent.parent / "fixtures" / "images" / "real"

_NFR4_WARN_S = 5.0   # § 6.3: > 5 s emits a warning
_NFR4_FAIL_S = 10.0  # § 6.3: > 10 s fails


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_sidecar(name: str) -> dict:
    sidecar_path = _REAL_DIR / f"{name}.expected.json"
    return json.loads(sidecar_path.read_text())


def _run_detect(image_bytes: bytes) -> tuple:
    """Run detect, returning (result, elapsed_seconds)."""
    t0 = time.monotonic()
    result = detect(image_bytes)
    return result, time.monotonic() - t0


def _assert_timing(name: str, elapsed: float) -> None:
    if elapsed > _NFR4_FAIL_S:
        pytest.fail(
            f"{name}: detection took {elapsed:.2f} s (> {_NFR4_FAIL_S:.0f} s hard cap, NFR-4)"
        )
    if elapsed > _NFR4_WARN_S:
        warnings.warn(
            f"{name}: detection took {elapsed:.2f} s (> {_NFR4_WARN_S:.0f} s, NFR-4 soft bound)",
            stacklevel=2,
        )


def _assert_sidecar(name: str, result, sidecar: dict) -> None:
    """Apply all sidecar-driven assertions to a detection result."""
    # FR-6: proportions always sum to 100.
    assert sum(c.proportion for c in result.colours) == 100, (
        f"{name}: proportions sum to {sum(c.proportion for c in result.colours)}, not 100 (FR-6)"
    )

    # Colour count within expected range.
    n = len(result.colours)
    assert sidecar["count_min"] <= n <= sidecar["count_max"], (
        f"{name}: {n} colours (expected {sidecar['count_min']}–{sidecar['count_max']})"
    )

    # FR-27 fallback.
    if sidecar.get("fallback_expected") is True:
        assert result.fallback_used is True, (
            f"{name}: expected fallback_used=True (FR-27) but got False"
        )

    dominant_family = sidecar.get("dominant_family")
    if dominant_family is not None:
        # Dominant colour matches expected family.
        actual_dominant = result.colours[0].family
        assert actual_dominant == dominant_family, (
            f"{name}: dominant family {actual_dominant!r} ≠ expected {dominant_family!r}"
        )

        # Dominant proportion within tolerance.
        p = result.colours[0].proportion
        assert sidecar["dominant_proportion_min"] <= p <= sidecar["dominant_proportion_max"], (
            f"{name}: dominant proportion {p} outside "
            f"[{sidecar['dominant_proportion_min']}, {sidecar['dominant_proportion_max']}]"
        )

        # All detected families are expected.
        allowed = {dominant_family} | set(sidecar.get("allowed_extra_families", []))
        unexpected = {c.family for c in result.colours} - allowed
        assert not unexpected, (
            f"{name}: unexpected families {unexpected} (allowed: {allowed})"
        )


# ── Parametrised real-model tests ─────────────────────────────────────────────

_FIXTURES = [
    p.stem for p in sorted(_REAL_DIR.glob("*.jpg"))
]


@pytest.mark.model
@pytest.mark.parametrize("name", _FIXTURES)
def test_real_model_fixture(name: str) -> None:
    """
    Drive the genuine rembg + KMeans pipeline over each committed photograph
    and assert the sidecar's tolerance-based expectations (§6.3).
    """
    image_bytes = (_REAL_DIR / f"{name}.jpg").read_bytes()
    sidecar = _load_sidecar(name)

    result, elapsed = _run_detect(image_bytes)

    _assert_timing(name, elapsed)
    _assert_sidecar(name, result, sidecar)
