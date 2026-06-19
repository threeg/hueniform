"""
Tests for app.services.suggestion_service (HUE-024).

Strategy: §7.3 service tests over the HUE-012 engineered wardrobe fixtures,
with a seeded RNG for deterministic results, plus the §4.9.4 oracle pattern
(re-evaluate the returned combination, assert it matches).
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import Session

from app.matcher.ranking import evaluate_outfit
from app.matcher.roles import Garment
from app.services.suggestion_service import (
    EmptySlotsError,
    SuggestionCombination,
    SuggestionResult,
    suggest,
)
from app.storage.models import GarmentColourRow, GarmentRow
from tests.fixtures.wardrobes import (
    neutral_fallback_only,
    no_valid_outfit_constrained_by,
    single_valid_outfit,
    two_valid_outfits,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _materialise(engine, garments: list[Garment]) -> None:
    """Insert a list of matcher Garment objects into the DB as GarmentRow records."""
    now = datetime.now(timezone.utc).isoformat()
    with Session(engine) as s:
        for g in garments:
            gid = str(uuid.uuid4())
            row = GarmentRow(
                id=gid,
                type=g.garment_type,
                image_file=f"{gid}.jpg",
                thumbnail_file=f"{gid}.webp",
                created_at=now,
            )
            s.add(row)
            s.flush()
            for i, c in enumerate(g.colours):
                s.add(GarmentColourRow(
                    garment_id=gid,
                    position=i,
                    h=c.h,
                    s=c.s,
                    l=c.l,
                    family="Red",  # placeholder; service re-derives via classifier
                    proportion=c.proportion,
                ))
        s.commit()


def _rng() -> random.Random:
    return random.Random(42)


# ── FR-36 fail-fast on empty slots ────────────────────────────────────────────

class TestEmptySlotsFailFast:
    def test_empty_required_slot_raises(self, engine):
        # Only insert t_shirt + socks + shoes; lower_body is missing.
        _materialise(engine, [
            Garment("t_shirt", (pytest.importorskip("app.matcher.colour").Colour(h=0.0, s=80.0, l=50.0, proportion=100),)),
            Garment("socks",   (pytest.importorskip("app.matcher.colour").Colour(h=0.0, s=0.0, l=50.0, proportion=100),)),
            Garment("shoes",   (pytest.importorskip("app.matcher.colour").Colour(h=0.0, s=0.0, l=6.0, proportion=100),)),
        ])
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest(frozenset(), engine, _rng())
        assert "lower_body" in exc_info.value.empty_slots

    def test_empty_optional_slot_raises(self, engine):
        _materialise(engine, single_valid_outfit())
        # Request mid but wardrobe has no mid-layer garments.
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest(frozenset({"mid"}), engine, _rng())
        assert "mid" in exc_info.value.empty_slots

    def test_empty_slots_error_lists_all_missing(self, engine):
        # Completely empty wardrobe.
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest(frozenset(), engine, _rng())
        missing = exc_info.value.empty_slots
        assert "base" in missing and "lower_body" in missing

    def test_no_error_when_all_slots_populated(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert isinstance(result, SuggestionResult)


# ── Normal combinations ───────────────────────────────────────────────────────

class TestNormalCombinations:
    def test_single_valid_outfit_returns_one_combination(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert len(result.combinations) == 1

    def test_combination_rank_starts_at_one(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations[0].rank == 1

    def test_combination_is_not_fallback(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations[0].fallback is False

    def test_combination_has_scheme(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations[0].scheme is not None
        # Red + Teal → complementary
        assert result.combinations[0].scheme == "complementary"

    def test_combination_slots_match_requested(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        combo = result.combinations[0]
        assert set(combo.slots.keys()) == {"base", "lower_body", "socks", "shoes"}

    def test_combination_slots_are_garment_rows(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        for row in result.combinations[0].slots.values():
            assert isinstance(row, GarmentRow)

    def test_combination_explanation_nonempty(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert len(result.combinations[0].explanation) > 0

    def test_zero_explanation_none_for_normal(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        assert result.zero_explanation is None
        assert result.hint is None

    def test_two_valid_outfits_returns_up_to_two(self, engine):
        _materialise(engine, two_valid_outfits())
        result = suggest(frozenset(), engine, _rng())
        assert 1 <= len(result.combinations) <= 3

    def test_ranks_are_sequential(self, engine):
        _materialise(engine, two_valid_outfits())
        result = suggest(frozenset(), engine, _rng())
        ranks = [c.rank for c in result.combinations]
        assert ranks == list(range(1, len(ranks) + 1))


# ── Oracle (§4.9.4): re-evaluate returned combinations ───────────────────────

class TestOracleRevalidation:
    def test_returned_combination_is_valid_outfit(self, engine):
        """
        Re-evaluate each returned outfit combination using evaluate_outfit;
        assert it produces a non-None EvaluationResult (§4.9.4 oracle).
        """
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        for combo in result.combinations:
            # Reconstruct matcher Garment from returned GarmentRow.
            from app.matcher.colour import Colour
            outfit_garments: dict[str, Garment] = {}
            for slot, row in combo.slots.items():
                from sqlmodel import Session as S
                from app.storage.models import GarmentColourRow
                from sqlmodel import select
                with S(engine) as s:
                    colour_rows = s.exec(
                        select(GarmentColourRow).where(GarmentColourRow.garment_id == row.id)
                        .order_by(GarmentColourRow.position)
                    ).all()
                colours = tuple(
                    Colour(h=c.h, s=c.s, l=c.l, proportion=c.proportion)
                    for c in colour_rows
                )
                outfit_garments[slot] = Garment(garment_type=slot, colours=colours)

            eval_result = evaluate_outfit(outfit_garments)
            assert eval_result is not None, (
                f"Returned combination at rank {combo.rank} fails evaluate_outfit"
            )

    def test_scheme_matches_oracle(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest(frozenset(), engine, _rng())
        combo = result.combinations[0]
        # Oracle: scheme should be complementary for Red+Teal
        assert combo.scheme == "complementary"


# ── Neutral-based scheme ──────────────────────────────────────────────────────

class TestNeutralBasedScheme:
    def test_neutral_wardrobe_returns_combination(self, engine):
        _materialise(engine, neutral_fallback_only())
        result = suggest(frozenset(), engine, _rng())
        assert len(result.combinations) >= 1

    def test_neutral_scheme_name(self, engine):
        _materialise(engine, neutral_fallback_only())
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations[0].scheme == "neutral-based"


# ── Zero-result sentinel (FR-43(b)) ──────────────────────────────────────────

class TestZeroResultSentinel:
    def test_no_valid_outfit_returns_empty_combinations(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations == ()

    def test_zero_result_has_explanation(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest(frozenset(), engine, _rng())
        assert result.zero_explanation is not None
        assert len(result.zero_explanation) > 0

    def test_zero_result_has_hint(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest(frozenset(), engine, _rng())
        assert result.hint is not None

    def test_constraining_slot_named_in_hint(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest(frozenset(), engine, _rng())
        # The constraining slot maps to "base" (v0.2.0) — must appear in the hint.
        assert "base" in result.hint

    def test_echo_slot_constraint(self, engine):
        """An incompatible echo slot triggers the zero-result path."""
        _materialise(engine, no_valid_outfit_constrained_by("socks"))
        result = suggest(frozenset(), engine, _rng())
        assert result.combinations == ()
        assert result.zero_explanation is not None
