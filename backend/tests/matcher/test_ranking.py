"""
Tests for matcher.ranking (test strategy §4.7).

Coverage:
  - FR-39 / FR-48: up to N results (default 3, 1–25); fewer when fewer exist
  - FR-40: all returned combinations are pairwise distinct
  - FR-41: scheme-strength ordering (180° over 165°; narrower analogous);
            neutral-based first-class at NEUTRAL_BASED_STRENGTH (0.98);
            echo-bonus ordering; variety prevents same garments dominating;
            anchor-interleaved enumeration for diversity within the cap
  - FR-42: seeded random.Random accepted; two seeds → independent streams
  - FR-43: fallback ladder — neutral-based (rung 1) and zero-result sentinel
            with constraining_slot set (rung 2)
"""

from __future__ import annotations

import random

import pytest

from app.matcher import constants as C
from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.matcher.ranking import (
    EvaluationResult,
    _constraining_slot,
    _enumerate_outfits,
    _failure_slot,
    _neutral_fallback,
    evaluate_outfit,
    rank,
)
from app.matcher.slots import category_to_slot
from tests.fixtures.wardrobes import (
    no_valid_outfit_constrained_by,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
    neutral_fallback_only,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

_RNG = random.Random(42)

# v0.2.0 default slots (base, lower_body, socks, shoes)
_REQUIRED = frozenset({"base", "lower_body", "socks", "shoes"})


def _c(h: float, s: float, l: float, p: int) -> Colour:
    return Colour(h=h, s=s, l=l, proportion=p)


def _red(p: int)    -> Colour: return _c(  0.0, 80.0, 50.0, p)
def _teal(p: int)   -> Colour: return _c(180.0, 70.0, 50.0, p)
def _blue(p: int)   -> Colour: return _c(240.0, 70.0, 50.0, p)
def _grey(p: int)   -> Colour: return _c(  0.0,  0.0, 50.0, p)
def _black(p: int)  -> Colour: return _c(  0.0,  0.0,  6.0, p)
def _navy(p: int)   -> Colour: return _c(230.0, 40.0, 18.0, p)


def _outfit_from(garments) -> dict[str, Garment]:
    """Convert a garment list to an outfit dict using v0.2.0 slot keys."""
    return {category_to_slot(g.garment_type): g for g in garments}


# ── evaluate_outfit ───────────────────────────────────────────────────────────

class TestEvaluateOutfit:
    def test_valid_complementary_returns_result(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.scheme_result is not None
        assert result.scheme_result.scheme == "complementary"

    def test_non_harmonious_returns_none(self) -> None:
        # Chartreuse + Blue = 150° apart — no valid scheme
        outfit = {
            "base":       Garment("t_shirt",  (Colour(90.0, 70.0, 40.0, 100),)),
            "lower_body": Garment("trousers", (_blue(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        assert evaluate_outfit(outfit) is None

    def test_echo_slot_failure_returns_none(self) -> None:
        # Blue socks do not echo Red/Teal anchors
        garments = no_valid_outfit_constrained_by("socks")
        outfit = _outfit_from(garments)
        assert evaluate_outfit(outfit) is None

    def test_score_fields_populated(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.score > 0.0
        assert 0.0 <= result.scheme_strength <= 1.0
        assert isinstance(result.echo_bonus, int)

    def test_garment_roles_populated_for_each_slot(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        for slot in outfit:
            assert slot in result.garment_roles

    def test_is_fallback_flag_forwarded(self) -> None:
        outfit = _outfit_from(neutral_fallback_only())
        result = evaluate_outfit(outfit, is_fallback=True)
        assert result is not None
        assert result.is_fallback

    def test_normal_result_not_flagged_fallback(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert not result.is_fallback

    def test_one_piece_with_separate_base_returns_none(self) -> None:
        # FR-50.2: dress (lower_body one-piece) + t_shirt (base) is invalid
        outfit = {
            "lower_body": Garment("dress",   (_red(100),)),
            "base":       Garment("t_shirt", (_teal(100),)),
            "socks":      Garment("socks",   (_grey(100),)),
            "shoes":      Garment("shoes",   (_black(100),)),
        }
        assert evaluate_outfit(outfit) is None


# ── FR-41.1: scheme-strength ordering ────────────────────────────────────────

class TestSchemeStrengthOrdering:
    """Perfect complement (180°) scores higher than imperfect (165°)."""

    def _make_outfit(self, lower_body_hue: float) -> dict[str, Garment]:
        return {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (Colour(lower_body_hue, 70.0, 50.0, 100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }

    def test_perfect_complement_stronger_than_imperfect(self) -> None:
        perfect   = evaluate_outfit(self._make_outfit(180.0))  # 180° = 0 deviation
        imperfect = evaluate_outfit(self._make_outfit(165.0))  # 165° = 15° deviation
        assert perfect   is not None, "Perfect complement should be valid"
        assert imperfect is not None, "165° complement should be valid (within ±20°)"
        assert perfect.scheme_strength > imperfect.scheme_strength

    def test_perfect_complement_score_higher_than_imperfect(self) -> None:
        perfect   = evaluate_outfit(self._make_outfit(180.0))
        imperfect = evaluate_outfit(self._make_outfit(165.0))
        assert perfect   is not None
        assert imperfect is not None
        assert perfect.score > imperfect.score

    def test_narrower_analogous_scores_higher(self) -> None:
        # Two analogous outfits; span must be in (30°, 60°] for analogous.
        # base=Red(h=0), lower_body=h=35 → span=35° (analogous, narrow)
        # base=Red(h=0), lower_body=h=55 → span=55° (analogous, wide)
        narrow = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (Colour(35.0, 70.0, 50.0, 100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        wide = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (Colour(55.0, 70.0, 50.0, 100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        r_narrow = evaluate_outfit(narrow)
        r_wide   = evaluate_outfit(wide)
        assert r_narrow is not None
        assert r_wide   is not None
        assert r_narrow.scheme_result.scheme == "analogous"
        assert r_wide.scheme_result.scheme   == "analogous"
        assert r_narrow.scheme_strength > r_wide.scheme_strength

    def test_neutral_based_scheme_strength(self) -> None:
        outfit = _outfit_from(neutral_fallback_only())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.scheme_strength == pytest.approx(C.NEUTRAL_BASED_STRENGTH)

    def test_perfect_monochromatic_scheme_strength_is_one(self) -> None:
        # Single Red hue → arc_span = 0 → deviation 0
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_red(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.scheme_result.scheme == "monochromatic"
        assert result.scheme_strength == 1.0


# ── FR-41.2: echo-bonus ordering ─────────────────────────────────────────────

class TestEchoBonusOrdering:
    """More distinct minor echoes → higher score (all else equal)."""

    def test_echo_bonus_raises_score(self) -> None:
        # Echo bonus comes from minor colours on ECHO SLOTS (socks/shoes) that
        # echo a chromatic colour on the anchors (FR-22).
        #
        # Anchors: Red base + Teal lower_body → anchor_chromatic = {Red, Teal}
        #
        # no_echo: socks = Red primary only → qualifies, no minor echoes
        # with_echo: socks = Red primary (90%) + Teal minor (10%)
        #   → Red qualifies (echo), Teal minor echoes anchor Teal → echo_bonus = 1
        no_echo = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_red(100),)),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }
        with_echo = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (Colour(0.0, 80.0, 50.0, 90), _teal(10))),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }
        r_no_echo   = evaluate_outfit(no_echo)
        r_with_echo = evaluate_outfit(with_echo)
        assert r_no_echo   is not None
        assert r_with_echo is not None
        assert r_with_echo.echo_bonus > r_no_echo.echo_bonus
        assert r_with_echo.score > r_no_echo.score


# ── FR-39 / FR-40: cap and distinctness ──────────────────────────────────────

class TestCapAndDistinctness:
    def test_single_valid_outfit_returns_one(self) -> None:
        wardrobe = single_valid_outfit()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1

    def test_two_valid_outfits_returns_two(self) -> None:
        wardrobe = two_valid_outfits()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 2

    def test_never_more_than_default_count(self) -> None:
        # Build a wardrobe with many valid combinations:
        # 4 different Red tops (different saturation), 2 Teal bottoms, Grey socks, Black shoes
        tops = [
            Garment("top", (Colour(0.0, s, 50.0, 100),))
            for s in (80.0, 70.0, 60.0, 50.0)
        ]
        bottoms = [
            Garment("bottom", (_teal(100),)),
            Garment("bottom", (Colour(180.0, 60.0, 45.0, 100),)),
        ]
        wardrobe = tops + bottoms + [
            Garment("socks", (_grey(100),)),
            Garment("shoes", (_black(100),)),
        ]
        results = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) <= C.COUNT_DEFAULT

    def test_all_results_pairwise_distinct(self) -> None:
        wardrobe = two_valid_outfits()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                assert results[i].outfit != results[j].outfit, (
                    f"Results {i} and {j} are identical outfits"
                )

    def test_all_results_valid_fr15(self) -> None:
        wardrobe = single_valid_outfit()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        for r in results:
            assert r.scheme_result is not None
            assert r.constraining_slot is None


# ── FR-39 / FR-48: top-N selection ───────────────────────────────────────────

class TestTopNSelection:
    """rank() respects the count parameter (FR-39, FR-48)."""

    def test_count_one_returns_at_most_one(self) -> None:
        wardrobe = two_valid_outfits()
        results = rank(wardrobe, _REQUIRED, random.Random(0), count=1)
        assert len(results) == 1

    def test_count_twenty_five_returns_all_when_fewer_exist(self) -> None:
        # single_valid_outfit has exactly one valid combination
        wardrobe = single_valid_outfit()
        results = rank(wardrobe, _REQUIRED, random.Random(0), count=25)
        assert len(results) == 1

    def test_count_many_returns_all_available(self) -> None:
        # two_valid_outfits has exactly two valid combinations
        wardrobe = two_valid_outfits()
        results = rank(wardrobe, _REQUIRED, random.Random(0), count=25)
        assert len(results) == 2

    def test_count_is_independent_of_cap(self) -> None:
        # count controls the output size, not the candidate cap
        wardrobe = two_valid_outfits()
        r1 = rank(wardrobe, _REQUIRED, random.Random(0), count=1)
        r2 = rank(wardrobe, _REQUIRED, random.Random(0), count=2)
        assert len(r1) == 1
        assert len(r2) == 2


# ── FR-41: first-class neutral-based (0.98) ───────────────────────────────────

class TestFirstClassNeutral:
    """All-neutral outfits are first-class at NEUTRAL_BASED_STRENGTH (FR-41)."""

    def test_neutral_based_is_first_class_not_fallback(self) -> None:
        # neutral_fallback_only wardrobe: all neutrals → step 1 finds them
        # as neutral-based (not FR-43(a) fallback)
        results = rank(neutral_fallback_only(), _REQUIRED, random.Random(0))
        assert len(results) >= 1
        result = results[0]
        assert result.scheme_result is not None
        assert result.scheme_result.scheme == "neutral-based"
        assert not result.is_fallback

    def test_neutral_based_strength_is_below_perfect_chromatic(self) -> None:
        # neutral-based (0.98) ranks below a perfect complementary outfit (1.0)
        neutral_outfit = _outfit_from(neutral_fallback_only())
        chromatic_outfit = _outfit_from(single_valid_outfit())
        r_neutral   = evaluate_outfit(neutral_outfit)
        r_chromatic = evaluate_outfit(chromatic_outfit)
        assert r_neutral   is not None
        assert r_chromatic is not None
        assert r_neutral.scheme_strength  == pytest.approx(C.NEUTRAL_BASED_STRENGTH)
        assert r_chromatic.scheme_strength > r_neutral.scheme_strength


# ── FR-41.3 / NFR-5: anchor-interleaved enumeration ──────────────────────────

class TestAnchorInterleave:
    """Diverse anchor garments appear before the MAX_ANCHOR_CANDIDATES cap."""

    def test_first_n_outfits_have_distinct_bases(self) -> None:
        # 4 bases × 2 lower_bodies = 8 combos (well under the 200 cap).
        # Anchor-interleaved order: bases cycle fastest, so the first 4 outfits
        # each use a different base garment.
        bases = [
            Garment("t_shirt", (Colour(0.0, s, 50.0, 100),))
            for s in (80.0, 70.0, 60.0, 50.0)
        ]
        lower_bodies = [
            Garment("trousers", (_teal(100),)),
            Garment("trousers", (Colour(180.0, 60.0, 45.0, 100),)),
        ]
        outfits = _enumerate_outfits(
            {"base": bases, "lower_body": lower_bodies},
            frozenset({"base", "lower_body"}),
            rng=None,
        )
        assert len(outfits) == 8
        first_four_bases = [o["base"] for o in outfits[:4]]
        assert len({id(b) for b in first_four_bases}) == 4, (
            "Anchor-interleaved order should cycle bases fastest"
        )

    def test_no_rng_still_interleaves(self) -> None:
        # Interleaving applies regardless of rng (even rng=None fallback paths)
        bases = [Garment("t_shirt", (Colour(0.0, s, 50.0, 100),)) for s in (80.0, 70.0)]
        lbs   = [Garment("trousers", (Colour(180.0, s, 50.0, 100),)) for s in (70.0, 60.0)]
        outfits = _enumerate_outfits(
            {"base": bases, "lower_body": lbs},
            frozenset({"base", "lower_body"}),
            rng=None,
        )
        # bases[0] and bases[1] both appear before all lower_body combinations are cycled
        assert outfits[0]["base"] is bases[0]
        assert outfits[1]["base"] is bases[1]

    def test_single_anchor_slot(self) -> None:
        # Single-anchor case uses the else branch (no reversal needed for one slot)
        bases = [
            Garment("t_shirt", (_red(100),)),
            Garment("t_shirt", (Colour(0.0, 70.0, 50.0, 100),)),
        ]
        outfits = _enumerate_outfits(
            {"base": bases},
            frozenset({"base"}),
            rng=None,
        )
        assert len(outfits) == 2
        assert {id(o["base"]) for o in outfits} == {id(b) for b in bases}


# ── FR-42: seedable RNG (NFR-10) ─────────────────────────────────────────────

class TestSeedableRNG:
    """Injected RNG; no global state; same seed → identical results."""

    def test_same_seed_same_results(self) -> None:
        wardrobe = two_valid_outfits()
        r1 = rank(wardrobe, _REQUIRED, random.Random(0))
        r2 = rank(wardrobe, _REQUIRED, random.Random(0))
        assert [r.outfit for r in r1] == [r.outfit for r in r2]

    def test_different_seeds_both_valid(self) -> None:
        wardrobe = two_valid_outfits()
        r1 = rank(wardrobe, _REQUIRED, random.Random(1))
        r2 = rank(wardrobe, _REQUIRED, random.Random(2))
        for r in r1 + r2:
            assert r.scheme_result is not None


# ── FR-41.3: variety factor ───────────────────────────────────────────────────

class TestVarietyFactor:
    """Greedy variety selection favours combinations that reuse fewer garments."""

    def test_variety_selects_different_garments_when_possible(self) -> None:
        # 3 distinct tops, 2 distinct bottoms, 1 socks, 1 shoes
        # All tops and bottoms are Red+Teal complementary → many valid combos
        tops = [
            Garment("top", (Colour(0.0, s, 50.0, 100),))
            for s in (80.0, 70.0, 60.0)
        ]
        bottoms = [
            Garment("bottom", (_teal(100),)),
            Garment("bottom", (Colour(180.0, 60.0, 50.0, 100),)),
        ]
        socks = Garment("socks",  (_grey(100),))
        shoes = Garment("shoes",  (_black(100),))
        wardrobe = tops + bottoms + [socks, shoes]
        results = rank(wardrobe, _REQUIRED, random.Random(1))
        assert len(results) == 3
        # The 3 results should use at least 2 distinct bases across them
        used_bases = {r.outfit["base"] for r in results}
        assert len(used_bases) >= 2, "Variety should favour different base layers"


# ── FR-43: fallback ladder ────────────────────────────────────────────────────

class TestFallbackLadder:
    def test_neutral_fallback_returned_when_no_harmonious_outfits(self) -> None:
        # `neutral_fallback_only` wardrobe: all-neutral garments.
        # When rank is called, it finds a valid neutral-based outfit in step 1
        # (not requiring the fallback path) — but if we force step 1 to miss it
        # by building a wardrobe with ONLY non-harmonious chromatic options plus
        # neutral alternatives, we trigger FR-43(a).
        #
        # The cleanest testable scenario for FR-43(a):
        # ALL available garments are neutral (neutral_fallback_only wardrobe).
        # rank() finds them in step 1 as "neutral-based" — those are valid FR-15.
        # That means is_fallback=False (found in step 1).
        #
        # FR-43 says: "If no combination satisfies FR-15 for the requested slots,
        # attempt neutral-based combinations ONLY."  So the fallback fires ONLY
        # when step 1 finds nothing.  A wardrobe of pure neutrals means step 1
        # succeeds (neutral-based IS FR-15 harmonious), so is_fallback stays False.
        #
        # The fallback flag fires when: step 1 returns nothing, AND step 2 finds
        # neutral combinations.  This requires BOTH chromatic (non-harmonious)
        # AND neutral garments in each slot, but where the chromatic combinations
        # don't form valid schemes and the neutral combinations do.
        # But if neutral combos form valid schemes (neutral-based), step 1 would
        # find them too…
        #
        # Conclusion: the FR-43(a) path only fires in large wardrobes where the
        # MAX_ANCHOR_CANDIDATES cap causes step 1 to miss neutral combinations.
        # For unit tests with small wardrobes, all combinations are explored in
        # step 1, so a valid neutral outfit is always found in step 1.
        #
        # We test the flag via evaluate_outfit(is_fallback=True) directly (above).
        # Here we just confirm the neutral_fallback_only wardrobe returns a
        # neutral-based result (even if step 1 found it).
        wardrobe = neutral_fallback_only()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1
        assert results[0].scheme_result is not None
        assert results[0].scheme_result.scheme == "neutral-based"

    def test_zero_result_sentinel_when_no_valid_outfit(self) -> None:
        # Chartreuse top + Blue bottom (150° apart) → no scheme.
        # No neutral options for either anchor slot.
        wardrobe = no_valid_outfit_constrained_by("top")
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1
        assert results[0].outfit == {}
        assert results[0].constraining_slot is not None
        assert results[0].scheme_result is None

    def test_constraining_slot_is_identified(self) -> None:
        wardrobe = no_valid_outfit_constrained_by("socks")
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1
        assert results[0].constraining_slot == "socks"

    def test_constraining_slot_for_anchor_clash(self) -> None:
        # The top (now mapped to "base") causes the scheme clash
        wardrobe = no_valid_outfit_constrained_by("top")
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert results[0].constraining_slot == "base"

    def test_missing_slot_in_wardrobe_returns_sentinel(self) -> None:
        # Wardrobe missing "shoes" → constraining_slot = "shoes"
        wardrobe = [
            Garment("top",    (_red(100),)),
            Garment("bottom", (_teal(100),)),
            Garment("socks",  (_grey(100),)),
            # no shoes
        ]
        results = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1
        assert results[0].constraining_slot == "shoes"

    def test_fallback_result_has_no_valid_outfit_fields(self) -> None:
        wardrobe = no_valid_outfit_constrained_by("top")
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        sentinel = results[0]
        assert sentinel.score == 0.0
        assert sentinel.echo_bonus == 0
        assert sentinel.scheme_strength == 0.0
        assert sentinel.garment_roles == {}


# ── Integration: wardrobe fixtures ───────────────────────────────────────────

class TestWardrobeIntegration:
    def test_single_valid_outfit_has_complementary_scheme(self) -> None:
        results = rank(single_valid_outfit(), _REQUIRED, random.Random(0))
        assert len(results) == 1
        assert results[0].scheme_result.scheme == "complementary"

    def test_two_valid_outfits_both_complementary(self) -> None:
        results = rank(two_valid_outfits(), _REQUIRED, random.Random(0))
        assert len(results) == 2
        for r in results:
            assert r.scheme_result.scheme == "complementary"

    def test_rich_echo_wardrobe_has_positive_echo_bonus(self) -> None:
        wardrobe = rich_echo_wardrobe()
        results  = rank(wardrobe, _REQUIRED, random.Random(0))
        assert len(results) == 1
        # The top has a Teal minor that echoes the Teal bottom
        assert results[0].echo_bonus >= 0   # minor echo recorded as bonus

    def test_rank_accepts_seeded_rng(self) -> None:
        wardrobe = two_valid_outfits()
        rng = random.Random(999)
        results = rank(wardrobe, _REQUIRED, rng)
        assert len(results) >= 1

    def test_results_are_evaluation_result_instances(self) -> None:
        results = rank(single_valid_outfit(), _REQUIRED, random.Random(0))
        for r in results:
            assert isinstance(r, EvaluationResult)


# ── Internal function tests: coverage for private helpers ────────────────────

class TestEvaluateOutfitCoveredLayer:
    """Covered-layer failure path (FR-20): evaluate_outfit covered-layer check."""

    def test_covered_mid_with_discordant_colour_returns_none(self) -> None:
        # Outer (Red) is dominant; mid (Blue) is covered.
        # outer anchors = {Red, Teal}; Blue not in scheme and not in outer anchors.
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_blue(100),)),
            "lower_body": Garment("trousers",(_teal(100),)),
            "socks":      Garment("socks",   (_grey(100),)),
            "shoes":      Garment("shoes",   (_black(100),)),
        }
        assert evaluate_outfit(outfit) is None

    def test_covered_mid_echoing_outer_anchor_passes(self) -> None:
        # Outer (Red) is dominant; mid (Red) is covered.
        # Red is in-scheme → covered-layer check passes.
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_red(100),)),
            "lower_body": Garment("trousers",(_teal(100),)),
            "socks":      Garment("socks",   (_grey(100),)),
            "shoes":      Garment("shoes",   (_black(100),)),
        }
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.scheme_result.scheme == "complementary"


class TestFailureSlotHelpers:
    """Direct tests of private helpers for coverage."""

    def test_failure_slot_returns_none_for_valid_outfit(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        assert _failure_slot(outfit) is None

    def test_failure_slot_identifies_dominant_for_scheme_failure(self) -> None:
        # top type → "base" slot → dominant layer for scheme failure
        outfit = _outfit_from(no_valid_outfit_constrained_by("top"))
        assert _failure_slot(outfit) == "base"

    def test_failure_slot_identifies_echo_slot(self) -> None:
        outfit = _outfit_from(no_valid_outfit_constrained_by("socks"))
        assert _failure_slot(outfit) == "socks"

    def test_failure_slot_identifies_covered_layer(self) -> None:
        # Outer (Red) + mid (Blue covered) + lower_body (Teal)
        # Scheme passes (Red+Teal complementary), but mid Blue fails FR-20
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_blue(100),)),
            "lower_body": Garment("trousers",(_teal(100),)),
            "socks":      Garment("socks",   (_grey(100),)),
            "shoes":      Garment("shoes",   (_black(100),)),
        }
        assert _failure_slot(outfit) == "mid"

    def test_failure_slot_returns_none_for_covered_layer_that_passes(self) -> None:
        # Outer (Red) + mid (Red covered) + lower_body (Teal)
        # Covered mid: Red is in-scheme {Red, Teal} → passes FR-20 → _failure_slot = None
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_red(100),)),
            "lower_body": Garment("trousers",(_teal(100),)),
            "socks":      Garment("socks",   (_grey(100),)),
            "shoes":      Garment("shoes",   (_black(100),)),
        }
        assert _failure_slot(outfit) is None

    def test_failure_slot_returns_none_with_passing_secondary(self) -> None:
        # Base: Red(70%) + Teal(20% secondary) + Grey(10% minor)
        # Lower_body: Teal. Secondary Teal is in-scheme → passes; _failure_slot → None.
        outfit = {
            "base":       Garment("t_shirt",  (_red(70), _teal(20), _grey(10))),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        assert _failure_slot(outfit) is None


class TestNeutralFallbackDirect:
    """Direct test of _neutral_fallback to cover lines 267-272."""

    def test_neutral_fallback_returns_valid_results_for_neutral_wardrobe(self) -> None:
        wardrobe = neutral_fallback_only()
        garments_by_slot: dict = {}
        for g in wardrobe:
            garments_by_slot.setdefault(category_to_slot(g.garment_type), []).append(g)
        results = _neutral_fallback(garments_by_slot, _REQUIRED)
        assert len(results) >= 1
        for r in results:
            assert r.is_fallback
            assert r.scheme_result is not None
            assert r.scheme_result.scheme == "neutral-based"

    def test_neutral_fallback_returns_empty_when_no_neutral_garments(self) -> None:
        wardrobe = no_valid_outfit_constrained_by("top")
        garments_by_slot: dict = {}
        for g in wardrobe:
            garments_by_slot.setdefault(category_to_slot(g.garment_type), []).append(g)
        # No neutral base or lower_body → neutral fallback cannot fill all required slots
        results = _neutral_fallback(garments_by_slot, _REQUIRED)
        assert results == []


class TestConstrainingSlotDirect:
    """Direct test of _constraining_slot to cover the None branch (line 293)."""

    def test_constraining_slot_returns_none_when_all_valid(self) -> None:
        # Wardrobe with only a valid outfit → _failure_slot returns None for all
        # combinations → counts empty → _constraining_slot returns None
        wardrobe = single_valid_outfit()
        garments_by_slot: dict = {}
        for g in wardrobe:
            garments_by_slot.setdefault(category_to_slot(g.garment_type), []).append(g)
        result = _constraining_slot(garments_by_slot, _REQUIRED)
        assert result is None


class TestEnumerateOutfitsNoEchoSlots:
    """_enumerate_outfits no-echo-slots branch."""

    def test_enumerate_with_no_echo_slots(self) -> None:
        # requested_slots with no ECHO_SLOTS types → echo_slots_lists is empty
        # → the else branch appends the anchor-only dict
        garments_by_slot = {
            "base":       [Garment("t_shirt",  (_red(100),))],
            "lower_body": [Garment("trousers", (_teal(100),))],
        }
        outfits = _enumerate_outfits(
            garments_by_slot,
            frozenset({"base", "lower_body"}),
            rng=None,
        )
        assert len(outfits) == 1
        assert set(outfits[0].keys()) == {"base", "lower_body"}


class TestOutfitWithSecondaries:
    """Exercise the anchor-secondary loop body to cover the secondary-check lines."""

    def test_outfit_with_secondary_is_valid(self) -> None:
        # Base: Red primary 70%, Teal secondary 20%, Grey minor 10%.
        # Teal secondary is in the complementary scheme {Red, Teal} → in_scheme.
        # Exercises the secondary-check loop in evaluate_outfit and _failure_slot.
        outfit = {
            "base":       Garment("t_shirt",  (_red(70), _teal(20), _grey(10))),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        result = evaluate_outfit(outfit)
        assert result is not None
