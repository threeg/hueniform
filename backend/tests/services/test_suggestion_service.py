"""
Tests for app.services.suggestion_service (HUE-068).

Strategy: §7.3 service tests over the HUE-012 engineered wardrobe fixtures,
with a seeded RNG for deterministic results, plus the §4.9.4 oracle pattern
(re-evaluate the returned combination, assert it matches).
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import Session, select

from app.matcher.colour import Colour
from app.matcher.ranking import evaluate_outfit
from app.matcher.roles import Garment
from app.services.suggestion_service import (
    EmptySlotsError,
    InvalidAnchorError,
    InvalidCategoryFilterError,
    InvalidPinError,
    InvalidSlotError,
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
            suggest({}, engine, _rng())
        assert "lower_body" in exc_info.value.empty_slots

    def test_empty_optional_slot_raises(self, engine):
        _materialise(engine, single_valid_outfit())
        # Request mid but wardrobe has no mid-layer garments.
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest({"mid": True}, engine, _rng())
        assert "mid" in exc_info.value.empty_slots

    def test_empty_slots_error_lists_all_missing(self, engine):
        # Completely empty wardrobe.
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest({}, engine, _rng())
        missing = exc_info.value.empty_slots
        assert "base" in missing and "lower_body" in missing

    def test_no_error_when_all_slots_populated(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert isinstance(result, SuggestionResult)


# ── Normal combinations ───────────────────────────────────────────────────────

class TestNormalCombinations:
    def test_single_valid_outfit_returns_one_combination(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert len(result.combinations) == 1

    def test_combination_rank_starts_at_one(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert result.combinations[0].rank == 1

    def test_combination_is_not_fallback(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert result.combinations[0].fallback is False

    def test_combination_has_scheme(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert result.combinations[0].scheme is not None
        # Red + Teal → complementary
        assert result.combinations[0].scheme == "complementary"

    def test_combination_slots_match_requested(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        combo = result.combinations[0]
        assert set(combo.slots.keys()) == {"base", "lower_body", "socks", "shoes"}

    def test_combination_slots_are_garment_rows(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        for row in result.combinations[0].slots.values():
            assert isinstance(row, GarmentRow)

    def test_combination_explanation_nonempty(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert len(result.combinations[0].explanation) > 0

    def test_zero_explanation_none_for_normal(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng())
        assert result.zero_explanation is None
        assert result.hint is None

    def test_two_valid_outfits_returns_up_to_two(self, engine):
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng())
        assert 1 <= len(result.combinations) <= 3

    def test_ranks_are_sequential(self, engine):
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng())
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
        result = suggest({}, engine, _rng())
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
        result = suggest({}, engine, _rng())
        combo = result.combinations[0]
        # Oracle: scheme should be complementary for Red+Teal
        assert combo.scheme == "complementary"


# ── Neutral-based scheme ──────────────────────────────────────────────────────

class TestNeutralBasedScheme:
    def test_neutral_wardrobe_returns_combination(self, engine):
        _materialise(engine, neutral_fallback_only())
        result = suggest({}, engine, _rng())
        assert len(result.combinations) >= 1

    def test_neutral_scheme_name(self, engine):
        _materialise(engine, neutral_fallback_only())
        result = suggest({}, engine, _rng())
        assert result.combinations[0].scheme == "neutral-based"


# ── Zero-result sentinel (FR-43(b)) ──────────────────────────────────────────

class TestZeroResultSentinel:
    def test_no_valid_outfit_returns_empty_combinations(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest({}, engine, _rng())
        assert result.combinations == ()

    def test_zero_result_has_explanation(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest({}, engine, _rng())
        assert result.zero_explanation is not None
        assert len(result.zero_explanation) > 0

    def test_zero_result_has_hint(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest({}, engine, _rng())
        assert result.hint is not None

    def test_constraining_slot_named_in_hint(self, engine):
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest({}, engine, _rng())
        # The constraining slot maps to "base" (v0.2.0) — must appear in the hint.
        assert "base" in result.hint

    def test_echo_slot_constraint(self, engine):
        """An incompatible echo slot triggers the zero-result path."""
        _materialise(engine, no_valid_outfit_constrained_by("socks"))
        result = suggest({}, engine, _rng())
        assert result.combinations == ()
        assert result.zero_explanation is not None


# ── Slot deselection (FR-51) — beach example ─────────────────────────────────

class TestSlotDeselection:
    def test_deselect_shoes_removes_shoes_from_outfit(self, engine):
        """
        FR-51: deselecting a default slot removes it from the requested set.
        A wardrobe with no shoes but shoes=False succeeds; the outfit lacks shoes.
        """
        # Insert base+lower_body+socks only (no shoes).
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
        ])
        result = suggest({"shoes": False}, engine, _rng())
        assert isinstance(result, SuggestionResult)
        assert len(result.combinations) >= 1
        assert "shoes" not in result.combinations[0].slots

    def test_deselect_shoes_default_request_fails(self, engine):
        """
        Same wardrobe (no shoes) with a default request (shoes included) raises
        EmptySlotsError because shoes is in DEFAULT_SLOTS.
        """
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
        ])
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest({}, engine, _rng())
        assert "shoes" in exc_info.value.empty_slots

    def test_deselect_socks_removes_socks(self, engine):
        _materialise(engine, single_valid_outfit())
        result = suggest({"socks": False}, engine, _rng())
        # socks deselected → outfit has only base, lower_body, shoes
        assert isinstance(result, SuggestionResult)
        assert "socks" not in result.combinations[0].slots
        assert set(result.combinations[0].slots.keys()) == {"base", "lower_body", "shoes"}


# ── Mandatory floor (FR-51.2) ─────────────────────────────────────────────────

class TestMandatoryFloor:
    def test_deselect_lower_body_raises(self, engine):
        """FR-51.2: lower_body cannot be deselected."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidSlotError) as exc_info:
            suggest({"lower_body": False}, engine, _rng())
        assert "lower_body" in exc_info.value.unknown

    def test_unknown_slot_key_raises(self, engine):
        with pytest.raises(InvalidSlotError):
            suggest({"dungarees": True}, engine, _rng())


# ── FR-52 per-category slot constraint ───────────────────────────────────────

class TestCategoryFilter:
    def test_category_filter_narrows_lower_body_candidates(self, engine):
        """
        FR-52: when lower_body is filtered to ["jeans"], the outfit only uses
        jeans and not the other lower_body garment (trousers).
        """
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("jeans",    (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
            Garment("shoes",    (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),
        ])
        result = suggest({"lower_body": ["jeans"]}, engine, _rng())
        assert len(result.combinations) >= 1
        for combo in result.combinations:
            assert combo.slots["lower_body"].type == "jeans"

    def test_category_filter_empty_list_raises(self, engine):
        """FR-52: an empty category list is invalid."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidCategoryFilterError):
            suggest({"lower_body": []}, engine, _rng())

    def test_category_not_in_slot_raises(self, engine):
        """FR-52: a category that does not belong to the slot is invalid."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidCategoryFilterError):
            # t_shirt belongs to 'base', not 'lower_body'
            suggest({"lower_body": ["t_shirt"]}, engine, _rng())

    def test_category_filter_causes_empty_slot_error(self, engine):
        """
        FR-52 + FR-36: if the category filter leaves no matching garments in the
        slot, EmptySlotsError is raised (not a silent empty result).
        """
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
            Garment("shoes",    (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),
        ])
        # Wardrobe has trousers but filter requests jeans — no jeans → empty slot
        with pytest.raises(EmptySlotsError) as exc_info:
            suggest({"lower_body": ["jeans"]}, engine, _rng())
        assert "lower_body" in exc_info.value.empty_slots


# ── One-piece / base auto-exclusion (FR-50.2) ─────────────────────────────────

class TestOnePieceExclusion:
    def test_one_piece_filter_excludes_base_slot(self, engine):
        """
        FR-50.2: when lower_body is filtered to one-piece categories only, the
        service removes base from the selected slots automatically so the one-piece
        can span both lower_body and base without a mutual-exclusion violation.
        """
        _materialise(engine, [
            Garment("dress",   (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("t_shirt", (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("socks",   (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
            Garment("shoes",   (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),
        ])
        result = suggest({"lower_body": ["dress"]}, engine, _rng())
        assert isinstance(result, SuggestionResult)
        # Combinations must not include a separately selected base garment
        for combo in result.combinations:
            assert "base" not in combo.slots
            assert combo.slots["lower_body"].type == "dress"


# ── Count parameter (FR-39, FR-48) ───────────────────────────────────────────

class TestCountParameter:
    def test_count_one_returns_exactly_one(self, engine):
        """FR-48: count=1 returns exactly 1 combination even when more exist."""
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng(), count=1)
        assert len(result.combinations) == 1

    def test_count_two_returns_two(self, engine):
        """FR-39: count=2 returns 2 combinations when 2 are available."""
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng(), count=2)
        assert len(result.combinations) == 2

    def test_count_default_three(self, engine):
        """FR-48: default count is COUNT_DEFAULT (3); returns up to 3."""
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng())
        # two_valid_outfits has 2 distinct combos; default=3 caps at available
        assert len(result.combinations) <= 3

    def test_count_large_caps_at_available(self, engine):
        """FR-39: count=25 with only 2 available outfits returns 2."""
        _materialise(engine, two_valid_outfits())
        result = suggest({}, engine, _rng(), count=25)
        assert len(result.combinations) == 2


# ── Fallback flag distinction (FR-41, FR-43) ─────────────────────────────────

class TestFallbackFlag:
    def test_first_class_neutral_is_not_fallback(self, engine):
        """FR-43: neutral-based found in step 1 sets fallback=False."""
        _materialise(engine, neutral_fallback_only())
        result = suggest({}, engine, _rng())
        assert len(result.combinations) >= 1
        assert result.combinations[0].fallback is False

    def test_first_class_neutral_scheme_name(self, engine):
        """FR-41: first-class neutral-based scheme name is 'neutral-based'."""
        _materialise(engine, neutral_fallback_only())
        result = suggest({}, engine, _rng())
        assert result.combinations[0].scheme == "neutral-based"

    def test_zero_result_has_no_fallback_combinations(self, engine):
        """FR-43(b): zero-result returns empty combinations tuple."""
        _materialise(engine, no_valid_outfit_constrained_by("top"))
        result = suggest({}, engine, _rng())
        assert result.combinations == ()


# ── Pins (FR-44) ──────────────────────────────────────────────────────────────

class TestPins:
    def test_pin_forces_garment_into_all_combinations(self, engine):
        """FR-44: a pin forces the pinned garment into every returned combination."""
        _materialise(engine, two_valid_outfits())
        with Session(engine) as s:
            row = s.exec(select(GarmentRow).where(GarmentRow.type == "t_shirt")).first()
        pinned_id = row.id
        result = suggest({}, engine, _rng(), pins={"base": pinned_id})
        assert len(result.combinations) >= 1
        for combo in result.combinations:
            assert combo.slots["base"].id == pinned_id

    def test_pin_unknown_slot_raises(self, engine):
        """FR-44: unknown slot key in pins raises InvalidPinError."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidPinError):
            suggest({}, engine, _rng(), pins={"nonexistent_slot": "some-id"})

    def test_pin_garment_not_found_raises(self, engine):
        """FR-44: a garment ID that does not exist raises InvalidPinError."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidPinError):
            suggest({}, engine, _rng(), pins={"base": "00000000-0000-0000-0000-000000000000"})

    def test_pin_category_wrong_slot_raises(self, engine):
        """FR-44: garment category does not map to pinned slot → InvalidPinError."""
        _materialise(engine, single_valid_outfit())
        with Session(engine) as s:
            row = s.exec(select(GarmentRow).where(GarmentRow.type == "trousers")).first()
        with pytest.raises(InvalidPinError):
            # trousers maps to lower_body, not base
            suggest({}, engine, _rng(), pins={"base": row.id})

    def test_pin_conflicts_with_constraint_raises(self, engine):
        """FR-44+FR-52: pin's category not in constraint → InvalidPinError."""
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("jeans",    (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
            Garment("shoes",    (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),
        ])
        with Session(engine) as s:
            row = s.exec(select(GarmentRow).where(GarmentRow.type == "trousers")).first()
        with pytest.raises(InvalidPinError):
            # Constraint is jeans; trousers is not in that set
            suggest({"lower_body": ["jeans"]}, engine, _rng(), pins={"lower_body": row.id})

    def test_multiple_pins_all_honoured(self, engine):
        """FR-44: multiple simultaneous pins all appear in every combination."""
        _materialise(engine, single_valid_outfit())
        with Session(engine) as s:
            base_row = s.exec(select(GarmentRow).where(GarmentRow.type == "t_shirt")).first()
            lb_row   = s.exec(select(GarmentRow).where(GarmentRow.type == "trousers")).first()
        result = suggest({}, engine, _rng(), pins={"base": base_row.id, "lower_body": lb_row.id})
        assert len(result.combinations) >= 1
        for combo in result.combinations:
            assert combo.slots["base"].id == base_row.id
            assert combo.slots["lower_body"].id == lb_row.id

    def test_one_piece_pin_excludes_base(self, engine):
        """FR-44+FR-50.2: pinning a one-piece to lower_body auto-excludes base."""
        _materialise(engine, [
            Garment("dress",   (Colour(h=230.0, s=40.0, l=18.0, proportion=100),)),  # Navy
            Garment("t_shirt", (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("socks",   (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),  # Grey
            Garment("shoes",   (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),  # Black
        ])
        with Session(engine) as s:
            dress_row = s.exec(select(GarmentRow).where(GarmentRow.type == "dress")).first()
        result = suggest({}, engine, _rng(), pins={"lower_body": dress_row.id})
        assert isinstance(result, SuggestionResult)
        for combo in result.combinations:
            assert "base" not in combo.slots
            assert combo.slots["lower_body"].id == dress_row.id


# ── Anchor (FR-45) ────────────────────────────────────────────────────────────

class TestAnchor:
    def test_anchor_family_keeps_matching_combinations(self, engine):
        """FR-45: pre-filter keeps anchor garments that carry the family."""
        # All anchor garments (base + lower_body) are Red; pre-filter keeps them.
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=  0.0, s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("trousers", (Colour(h=  0.0, s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("socks",    (Colour(h=  0.0, s= 0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=  0.0, s= 0.0, l= 6.0, proportion=100),)),  # Black
        ])
        result = suggest({}, engine, _rng(), anchor_family="Red")
        assert len(result.combinations) >= 1

    def test_anchor_family_no_match_raises_empty_slots(self, engine):
        """FR-45: pre-filter removes all anchor garments → EmptySlotsError."""
        _materialise(engine, single_valid_outfit())  # Red t_shirt + Teal trousers
        with pytest.raises(EmptySlotsError):
            suggest({}, engine, _rng(), anchor_family="Blue")

    def test_anchor_scheme_keeps_matching_combinations(self, engine):
        """FR-45: anchor_scheme keeps combos whose matched scheme equals it."""
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng(), anchor_scheme="complementary")
        assert len(result.combinations) >= 1
        for combo in result.combinations:
            assert combo.scheme == "complementary"

    def test_anchor_scheme_no_match_returns_zero(self, engine):
        """FR-45: anchor_scheme that matches no result → zero result."""
        _materialise(engine, single_valid_outfit())
        result = suggest({}, engine, _rng(), anchor_scheme="monochromatic")
        assert result.combinations == ()
        assert result.zero_explanation is not None

    def test_anchor_family_and_scheme_compose(self, engine):
        """FR-45: family pre-filter + scheme post-filter both apply."""
        # All-Teal anchor garments → monochromatic scheme; complementary won't match.
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("socks",    (Colour(h=  0.0, s= 0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=  0.0, s= 0.0, l= 6.0, proportion=100),)),  # Black
        ])
        result = suggest({}, engine, _rng(), anchor_family="Teal", anchor_scheme="monochromatic")
        assert len(result.combinations) >= 1
        result2 = suggest({}, engine, _rng(), anchor_family="Teal", anchor_scheme="complementary")
        assert result2.combinations == ()

    def test_anchor_unknown_family_raises(self, engine):
        """FR-45: unknown family name → InvalidAnchorError."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidAnchorError):
            suggest({}, engine, _rng(), anchor_family="Ultraviolet")

    def test_anchor_unknown_scheme_raises(self, engine):
        """FR-45: unknown scheme name → InvalidAnchorError."""
        _materialise(engine, single_valid_outfit())
        with pytest.raises(InvalidAnchorError):
            suggest({}, engine, _rng(), anchor_scheme="tetrachromatic")

    def test_anchor_family_is_deterministic(self, engine):
        """HUE-087: same wardrobe + family + different RNG seeds always return results."""
        # All anchor garments are Black; family pre-filter keeps them on every seed.
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
            Garment("trousers", (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
            Garment("socks",    (Colour(h=0.0, s=0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
        ])
        seeds = [0, 1, 7, 42, 99]
        results = [
            suggest({}, engine, random.Random(s), anchor_family="Black")
            for s in seeds
        ]
        # Every seed must return combinations (pre-filter guarantees this).
        for r in results:
            assert len(r.combinations) >= 1, "anchor_family pre-filter must be deterministic"

    def test_anchor_family_surfaces_matching_garment(self, engine):
        """HUE-087: pre-filter ensures the anchor-family garment always appears."""
        # One Black shirt (shirt slot); all required anchor slots also Black.
        # Request shirt slot so it appears in the combination.
        _materialise(engine, [
            Garment("t_shirt",  (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
            Garment("trousers", (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
            Garment("shirt",    (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black (only shirt)
            Garment("socks",    (Colour(h=0.0, s=0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=0.0, s=0.0, l= 6.0, proportion=100),)),  # Black
        ])
        seeds = [0, 1, 7, 42, 99]
        for s in seeds:
            result = suggest({"shirt": True}, engine, random.Random(s), anchor_family="Black")
            assert len(result.combinations) >= 1
            for combo in result.combinations:
                assert "shirt" in combo.slots

    def test_anchor_scheme_is_deterministic(self, engine):
        """HUE-087: oversampling makes scheme anchor consistent across seeds."""
        _materialise(engine, single_valid_outfit())  # Red+Teal → complementary
        seeds = [0, 1, 7, 42, 99]
        # All seeds must agree: either all return combinations or all return zero.
        outcomes = [
            len(suggest({}, engine, random.Random(s), anchor_scheme="complementary").combinations) > 0
            for s in seeds
        ]
        assert all(outcomes) or not any(outcomes), (
            "anchor_scheme must give consistent results across seeds"
        )

    def test_empty_slots_when_no_anchor_family_garments(self, engine):
        """HUE-087: pre-filter removes all anchor garments → EmptySlotsError."""
        # All anchor garments are Red/Teal; no Black garments in any anchor slot.
        _materialise(engine, single_valid_outfit())  # Red t_shirt + Teal trousers
        with pytest.raises(EmptySlotsError):
            suggest({}, engine, _rng(), anchor_family="Black")
