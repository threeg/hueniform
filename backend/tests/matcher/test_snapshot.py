"""
Golden-file snapshot baseline for the matcher (test strategy §4.10).

Captures the current (pre-E08-rewrite) output of classify, rank, and render
exactly, so any behavioural change during the E08 rewrite surfaces as a
reviewable diff rather than a silent regression.

Regeneration path
-----------------
  cd backend && .venv/bin/pytest tests/matcher/test_snapshot.py --snapshot-update
  # or:  make snapshot-update

After regeneration, commit the new golden files alongside the code change and
explain the delta in the ticket's ## Notes.

Three golden files (§4.10)
--------------------------
  snapshots/classifications.json  — HSL inputs → family names
  snapshots/ranking.json          — scenario wardrobes → ranked combinations
  snapshots/explanations.json     — same combinations → rendered text
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from app.matcher.explain import render
from app.matcher.ranking import EvaluationResult, rank
from app.matcher.slots import REQUIRED_SLOTS
from app.matcher.taxonomy import classify
from tests.fixtures.palettes import (
    CANONICAL,
    CHROMATIC_ARC_BOUNDARIES,
)
from tests.fixtures.wardrobes import (
    neutral_fallback_only,
    no_valid_outfit_constrained_by,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
)

# ── Constants ─────────────────────────────────────────────────────────────────

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_SEED = 42
SCORE_PRECISION = 4  # decimal places for float score fields

# S and L used for chromatic arc boundary inputs (same as test_taxonomy.py)
_ARC_S = 80.0
_ARC_L = 50.0

# Named scenario wardrobes evaluated for ranking/explanation snapshots.
# Each entry: (name, wardrobe_factory_call, requested_slots)
_SCENARIOS: list[tuple[str, object, frozenset[str]]] = [
    ("single_valid_outfit",          single_valid_outfit(),               REQUIRED_SLOTS),
    ("two_valid_outfits",            two_valid_outfits(),                 REQUIRED_SLOTS),
    ("neutral_fallback_only",        neutral_fallback_only(),             REQUIRED_SLOTS),
    ("rich_echo_wardrobe",           rich_echo_wardrobe(),                REQUIRED_SLOTS),
    ("no_valid_outfit_socks",        no_valid_outfit_constrained_by("socks"), REQUIRED_SLOTS),
]


# ── Generators — produce the live output ─────────────────────────────────────

def _classification_inputs() -> list[tuple[float, float, float]]:
    """
    Fixed HSL inputs for the classifications golden file.

    Includes every canonical family value and every chromatic arc boundary
    point (at representative S/L).  Both sets are stable between runs.
    """
    inputs: list[tuple[float, float, float]] = []
    # Canonical values — one per family (FR-1, contract §2.2)
    for h, s, l in CANONICAL.values():
        inputs.append((h, s, l))
    # Chromatic arc boundary hues — at each of the 12 30°-arc boundaries
    for boundary_h, _at, _below in CHROMATIC_ARC_BOUNDARIES:
        inputs.append((boundary_h, _ARC_S, _ARC_L))
    # Neutral edge cases that are not covered by canonicals
    inputs += [
        (0.0,  0.0, 11.9),   # just-Black (L < 12)
        (0.0,  5.0, 92.1),   # just-White (L > 92, S < 20)
        (0.0,  0.0, 50.0),   # achromatic mid-grey → Grey
        (230.0, 40.0, 24.9), # just-Navy (L < 25)
        (215.0, 30.0, 25.0), # Denim lower-L boundary (L ≥ 25)
    ]
    return inputs


def _generate_classifications() -> list[dict]:
    return [
        {"h": h, "s": s, "l": l, "family": classify(h, s, l)}
        for h, s, l in _classification_inputs()
    ]


def _fmt(v: float) -> str:
    """Serialise a float score at fixed precision so comparisons are exact."""
    return f"{v:.{SCORE_PRECISION}f}"


def _serialise_result(r: EvaluationResult) -> dict:
    return {
        "scheme":             r.scheme_result.scheme if r.scheme_result else None,
        "scheme_deviation":   _fmt(r.scheme_result.deviation) if r.scheme_result else None,
        "echo_bonus":         r.echo_bonus,
        "scheme_strength":    _fmt(r.scheme_strength),
        "score":              _fmt(r.score),
        "is_fallback":        r.is_fallback,
        "constraining_slot":  r.constraining_slot,
    }


def _generate_ranking() -> list[dict]:
    rng = random.Random(SNAPSHOT_SEED)
    rows = []
    for name, wardrobe, slots in _SCENARIOS:
        results = rank(wardrobe, slots, rng)
        rows.append({
            "scenario":    name,
            "combinations": [_serialise_result(r) for r in results],
        })
    return rows


def _generate_explanations() -> list[dict]:
    rng = random.Random(SNAPSHOT_SEED)
    rows = []
    for name, wardrobe, slots in _SCENARIOS:
        results = rank(wardrobe, slots, rng)
        rows.append({
            "scenario":    name,
            "combinations": [{"text": render(r)} for r in results],
        })
    return rows


# ── Snapshot helpers ──────────────────────────────────────────────────────────

def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def snapshot_update(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--snapshot-update")


def test_classifications(snapshot_update: bool) -> None:
    """Golden file 1: HSL inputs → family names (§4.10)."""
    path = SNAPSHOTS_DIR / "classifications.json"
    live = _generate_classifications()
    if snapshot_update:
        _dump(path, live)
        pytest.skip("Classifications golden file updated.")
    golden = _load(path)
    assert live == golden, (
        "Matcher classification output has changed. "
        "If intentional, re-run with --snapshot-update and commit the delta."
    )


def test_ranking(snapshot_update: bool) -> None:
    """Golden file 2: scenario wardrobes → ranked combinations (§4.10)."""
    path = SNAPSHOTS_DIR / "ranking.json"
    live = _generate_ranking()
    if snapshot_update:
        _dump(path, live)
        pytest.skip("Ranking golden file updated.")
    golden = _load(path)
    assert live == golden, (
        "Matcher ranking output has changed. "
        "If intentional, re-run with --snapshot-update and commit the delta."
    )


def test_explanations(snapshot_update: bool) -> None:
    """Golden file 3: ranked combinations → rendered explanation text (§4.10)."""
    path = SNAPSHOTS_DIR / "explanations.json"
    live = _generate_explanations()
    if snapshot_update:
        _dump(path, live)
        pytest.skip("Explanations golden file updated.")
    golden = _load(path)
    assert live == golden, (
        "Matcher explanation output has changed. "
        "If intentional, re-run with --snapshot-update and commit the delta."
    )
