"""
Tests for matcher.slots (test strategy §4.6).

Coverage:
  - FR-16 / FR-17: slot constant correctness and partitioning
  - FR-18: dominant_layer, covered_upper_layers, get_anchor_types — all three
            layering permutations
  - FR-19: build_scheme_set — dominant primaries, bottom primaries, all
            anchor secondaries, and covered-layer-primary exclusion
  - FR-20: check_covered_layer — in-scheme, echo, neutral pass; out-of-scheme fail
  - FR-9:  check_anchor_secondaries — compatible and incompatible secondaries
  - FR-21 / FR-22: qualify_echo_slot — neutral, echo, minor-echo recording, fail
  - get_anchor_chromatic_families — collects across all roles on all anchors
"""

from __future__ import annotations

import pytest

from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.matcher.slots import (
    ECHO_SLOTS,
    GARMENT_TYPES,
    OPTIONAL_SLOTS,
    REQUIRED_SLOTS,
    EchoQualification,
    SchemeSet,
    build_scheme_set,
    check_anchor_secondaries,
    check_covered_layer,
    covered_upper_layers,
    dominant_layer,
    get_anchor_chromatic_families,
    get_anchor_types,
    qualify_echo_slot,
)
from tests.fixtures.wardrobes import (
    no_valid_outfit_constrained_by,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _c(h: float, s: float, l: float, p: int) -> Colour:
    return Colour(h=h, s=s, l=l, proportion=p)


def _red(p: int)    -> Colour: return _c(  0.0, 80.0, 50.0, p)
def _teal(p: int)   -> Colour: return _c(180.0, 70.0, 50.0, p)
def _blue(p: int)   -> Colour: return _c(240.0, 70.0, 50.0, p)
def _grey(p: int)   -> Colour: return _c(  0.0,  0.0, 50.0, p)
def _black(p: int)  -> Colour: return _c(  0.0,  0.0,  6.0, p)
def _navy(p: int)   -> Colour: return _c(230.0, 40.0, 18.0, p)

def _outfit(*garments: Garment) -> dict[str, Garment]:
    return {g.garment_type: g for g in garments}


# ── FR-16 / FR-17: slot constant structure ────────────────────────────────────

class TestSlotConstants:
    def test_garment_types_has_eight_members(self) -> None:
        assert len(GARMENT_TYPES) == 8

    def test_required_and_optional_partition_garment_types(self) -> None:
        assert REQUIRED_SLOTS | OPTIONAL_SLOTS == GARMENT_TYPES

    def test_required_and_optional_are_disjoint(self) -> None:
        assert not REQUIRED_SLOTS & OPTIONAL_SLOTS

    def test_required_slots_content(self) -> None:
        assert REQUIRED_SLOTS == frozenset({"top", "bottom", "socks", "shoes"})

    def test_optional_slots_content(self) -> None:
        assert OPTIONAL_SLOTS == frozenset({"jersey", "jacket", "hat", "accessory"})

    def test_echo_slots_are_subset_of_garment_types(self) -> None:
        assert ECHO_SLOTS.issubset(GARMENT_TYPES)

    def test_echo_slots_content(self) -> None:
        assert ECHO_SLOTS == frozenset({"socks", "shoes", "hat", "accessory"})

    def test_echo_slots_disjoint_from_anchor_upper_body(self) -> None:
        assert not ECHO_SLOTS & {"top", "jersey", "jacket"}


# ── FR-18: dominant_layer ─────────────────────────────────────────────────────

class TestDominantLayer:
    """All three layering permutations: top-only, jersey+top, jacket+jersey+top."""

    def test_top_only_is_dominant(self) -> None:
        outfit = _outfit(Garment("top", (_red(100),)))
        assert dominant_layer(outfit) == "top"

    def test_jersey_beats_top(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jersey", (_teal(100),)),
        )
        assert dominant_layer(outfit) == "jersey"

    def test_jacket_beats_jersey(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jersey", (_teal(100),)),
            Garment("jacket", (_blue(100),)),
        )
        assert dominant_layer(outfit) == "jacket"

    def test_jacket_beats_top_without_jersey(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jacket", (_blue(100),)),
        )
        assert dominant_layer(outfit) == "jacket"

    def test_no_upper_body_raises_value_error(self) -> None:
        outfit = _outfit(
            Garment("bottom", (_teal(100),)),
            Garment("socks",  (_grey(100),)),
        )
        with pytest.raises(ValueError):
            dominant_layer(outfit)


# ── FR-18: covered_upper_layers ───────────────────────────────────────────────

class TestCoveredUpperLayers:
    def test_top_only_has_no_covered_layers(self) -> None:
        outfit = _outfit(Garment("top", (_red(100),)))
        assert covered_upper_layers(outfit) == []

    def test_jersey_covers_top(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jersey", (_teal(100),)),
        )
        assert covered_upper_layers(outfit) == ["top"]

    def test_jacket_covers_jersey_and_top(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jersey", (_teal(100),)),
            Garment("jacket", (_blue(100),)),
        )
        assert covered_upper_layers(outfit) == ["jersey", "top"]

    def test_jacket_covers_only_top_when_no_jersey(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jacket", (_blue(100),)),
        )
        assert covered_upper_layers(outfit) == ["top"]

    def test_jacket_alone_covers_nothing_additional(self) -> None:
        outfit = _outfit(Garment("jacket", (_blue(100),)))
        assert covered_upper_layers(outfit) == []


# ── FR-18: get_anchor_types ───────────────────────────────────────────────────

class TestGetAnchorTypes:
    def test_top_and_bottom_in_order(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("bottom", (_teal(100),)),
        )
        assert get_anchor_types(outfit) == ["top", "bottom"]

    def test_all_upper_body_layers_and_bottom_in_order(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(100),)),
            Garment("jersey", (_teal(100),)),
            Garment("jacket", (_blue(100),)),
            Garment("bottom", (_grey(100),)),
        )
        assert get_anchor_types(outfit) == ["jacket", "jersey", "top", "bottom"]

    def test_echo_slots_not_included_as_anchors(self) -> None:
        outfit = _outfit(
            Garment("top",       (_red(100),)),
            Garment("bottom",    (_teal(100),)),
            Garment("socks",     (_grey(100),)),
            Garment("shoes",     (_black(100),)),
            Garment("hat",       (_grey(100),)),
            Garment("accessory", (_grey(100),)),
        )
        anchors = get_anchor_types(outfit)
        assert "socks"     not in anchors
        assert "shoes"     not in anchors
        assert "hat"       not in anchors
        assert "accessory" not in anchors

    def test_no_bottom_in_outfit(self) -> None:
        outfit = _outfit(Garment("top", (_red(100),)))
        assert "bottom" not in get_anchor_types(outfit)


# ── FR-19: build_scheme_set ───────────────────────────────────────────────────

class TestBuildSchemeSet:
    def test_dominant_and_bottom_primaries_included(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families
        assert "Teal" in ss.chromatic_families

    def test_neutral_primaries_excluded_from_hues(self) -> None:
        # all-neutral outfit: no chromatic hues expected
        from tests.fixtures.wardrobes import neutral_fallback_only
        outfit = _outfit(*neutral_fallback_only())
        ss = build_scheme_set(outfit)
        assert ss.hues == ()
        assert ss.chromatic_families == frozenset()

    def test_covered_layer_primary_excluded(self) -> None:
        # jacket (Red) is dominant; jersey (Blue) is covered; bottom (Teal)
        # scheme_set should include Red + Teal, but NOT Blue (from covered jersey)
        outfit = _outfit(
            Garment("jacket", (_red(100),)),
            Garment("jersey", (_blue(100),)),
            Garment("bottom", (_teal(100),)),
        )
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families
        assert "Teal" in ss.chromatic_families
        assert "Blue" not in ss.chromatic_families

    def test_anchor_secondaries_included(self) -> None:
        # top: Red primary 70%, Teal secondary 20%, Blue minor 10%
        # bottom: Grey primary 100%
        # secondary Teal from top should appear in scheme set
        outfit = _outfit(
            Garment("top",    (_red(70), _teal(20), _blue(10))),
            Garment("bottom", (_grey(100),)),
        )
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families   # dominant primary
        assert "Teal" in ss.chromatic_families   # anchor secondary (FR-19)
        # minor Blue must NOT be in the scheme set (FR-10, FR-19)
        assert "Blue" not in ss.chromatic_families

    def test_covered_layer_secondary_still_included(self) -> None:
        # FR-19: all anchors' secondaries contribute, including covered layers
        # jacket (Red dominant), jersey (Blue secondary = Teal), bottom (Grey)
        outfit = _outfit(
            Garment("jacket", (_red(100),)),
            Garment("jersey", (_blue(70), _teal(20), _grey(10))),
            Garment("bottom", (_grey(100),)),
        )
        ss = build_scheme_set(outfit)
        # jersey secondary (Teal) should be present
        assert "Teal" in ss.chromatic_families
        # jersey primary (Blue) is covered → excluded
        assert "Blue" not in ss.chromatic_families

    def test_scheme_set_result_type(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        assert isinstance(ss, SchemeSet)
        assert isinstance(ss.hues, tuple)
        assert isinstance(ss.chromatic_families, frozenset)

    def test_hues_match_families(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        # exactly the two primary hues: Red (0.0) and Teal (180.0)
        assert 0.0   in ss.hues
        assert 180.0 in ss.hues
        assert len(ss.hues) == 2

    def test_no_bottom_in_outfit(self) -> None:
        # outfit with only an upper-body layer — bottom branch must not raise
        outfit = _outfit(Garment("top", (_red(100),)))
        ss = build_scheme_set(outfit)
        assert "Red" in ss.chromatic_families
        assert len(ss.hues) == 1


# ── get_anchor_chromatic_families ────────────────────────────────────────────

class TestGetAnchorChromaticFamilies:
    def test_collects_all_chromatic_families_across_roles(self) -> None:
        # top: Red primary (87%) + Teal minor (13%); bottom: Teal primary (100%)
        outfit = _outfit(*rich_echo_wardrobe())
        fams = get_anchor_chromatic_families(outfit)
        assert "Red"  in fams
        assert "Teal" in fams

    def test_excludes_neutrals(self) -> None:
        outfit = _outfit(*rich_echo_wardrobe())
        fams = get_anchor_chromatic_families(outfit)
        for name in ("Grey", "Black", "White", "Navy"):
            assert name not in fams

    def test_all_neutral_outfit_returns_empty(self) -> None:
        from tests.fixtures.wardrobes import neutral_fallback_only
        outfit = _outfit(*neutral_fallback_only())
        assert get_anchor_chromatic_families(outfit) == frozenset()

    def test_echo_slots_not_counted_as_anchors(self) -> None:
        # Blue shoes should NOT add Blue to anchor families
        outfit = _outfit(
            Garment("top",   (_red(100),)),
            Garment("bottom",(_teal(100),)),
            Garment("socks", (_grey(100),)),
            Garment("shoes", (_blue(100),)),
        )
        fams = get_anchor_chromatic_families(outfit)
        assert "Blue" not in fams


# ── FR-20: check_covered_layer ────────────────────────────────────────────────

class TestCheckCoveredLayer:
    _SCHEME  = frozenset({"Red", "Teal"})
    _ANCHORS = frozenset({"Red", "Teal", "Blue"})

    def test_in_scheme_primary_passes(self) -> None:
        jersey = Garment("jersey", (_red(100),))
        assert check_covered_layer(jersey, self._SCHEME, self._ANCHORS)

    def test_echo_primary_passes(self) -> None:
        # Blue is not in scheme but is on anchors → echo → passes
        jersey = Garment("jersey", (_blue(100),))
        assert check_covered_layer(jersey, self._SCHEME, self._ANCHORS)

    def test_all_neutral_passes_unconditionally(self) -> None:
        jersey = Garment("jersey", (_grey(100),))
        assert check_covered_layer(jersey, self._SCHEME, frozenset())

    def test_out_of_scheme_chromatic_fails(self) -> None:
        # Chartreuse not in scheme {Red, Teal}, not in anchors {Red, Teal, Blue}
        chartreuse = Colour(h=90.0, s=70.0, l=40.0, proportion=100)
        jersey = Garment("jersey", (chartreuse,))
        assert not check_covered_layer(jersey, self._SCHEME, self._ANCHORS)

    def test_in_scheme_secondary_passes(self) -> None:
        # Red primary 70%, Teal secondary 20%, Blue minor 10%
        # Teal is in scheme → passes; Blue minor never disqualifies
        jersey = Garment("jersey", (_red(70), _teal(20), _blue(10)))
        assert check_covered_layer(jersey, self._SCHEME, self._ANCHORS)

    def test_neutral_secondary_passes(self) -> None:
        jersey = Garment("jersey", (_red(85), _grey(15)))
        assert check_covered_layer(jersey, self._SCHEME, self._ANCHORS)


# ── FR-9: check_anchor_secondaries ───────────────────────────────────────────

class TestCheckAnchorSecondaries:
    def test_no_secondaries_passes(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_in_scheme_secondary_passes(self) -> None:
        # top: Red primary 70%, Teal secondary 20%; bottom: Teal 100%
        # Teal secondary is in scheme → passes
        outfit = _outfit(
            Garment("top",    (_red(70), _teal(20), _grey(10))),
            Garment("bottom", (_teal(100),)),
        )
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_neutral_secondary_passes(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(85), _grey(15))),
            Garment("bottom", (_teal(100),)),
        )
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_incompatible_secondary_fails(self) -> None:
        # scheme is Red+Teal; top has Blue secondary — not in scheme, not on anchors
        # (anchors here are top+bottom; top secondary Blue IS on anchors if counted,
        #  but classify_secondary checks anchor_chromatic_families which comes from
        #  get_anchor_chromatic_families — Blue *would* appear via top's secondary)
        # Use a truly isolated colour: Chartreuse, not on any anchor
        chartreuse = Colour(h=90.0, s=70.0, l=40.0, proportion=15)
        red_dom    = _red(85)
        outfit = _outfit(
            Garment("top",    (red_dom, chartreuse)),
            Garment("bottom", (_teal(100),)),
        )
        # Scheme = {Red, Teal}; anchors have Red + Chartreuse + Teal;
        # Chartreuse is in anchors so it echoes → actually passes!
        # We need anchors that genuinely don't contain the secondary's family.
        # Build a case: top secondary = Blue, but no blue on any anchor
        blue_secondary = _blue(15)
        outfit2 = _outfit(
            Garment("top",    (_red(85), blue_secondary)),
            Garment("bottom", (_teal(100),)),
        )
        # Now: anchor families include Red, Blue (from top secondary itself), Teal
        # → Blue is in anchor families → echo → passes.
        # The only guaranteed failure: a colour family truly absent from all anchors.
        # Create an outfit where the scheme and anchors cover Red+Teal, but the
        # secondary is Chartreuse and Chartreuse has no garment in any anchor slot.
        chartreuse_secondary = Colour(h=90.0, s=70.0, l=40.0, proportion=20)
        red_primary = _red(80)
        outfit3 = _outfit(
            Garment("top",    (red_primary, chartreuse_secondary)),
            Garment("bottom", (_teal(100),)),
        )
        # anchors: top (Red 80%, Chartreuse 20%), bottom (Teal 100%)
        # → anchor_chromatic_families includes Red, Chartreuse, Teal
        # So Chartreuse on top's secondary IS in anchor families → echo → passes
        # This demonstrates that FR-9 only fails when a secondary is from a family
        # completely absent from all anchor garments.
        #
        # To force failure: use an outfit where we call the function directly with
        # a hand-crafted scheme and anchor set that excludes the secondary.
        from app.matcher.slots import check_anchor_secondaries
        partial_scheme  = frozenset({"Red", "Teal"})
        partial_anchors = frozenset({"Red", "Teal"})  # excludes Blue
        # top has Blue secondary
        outfit4 = _outfit(
            Garment("top",    (_red(85), _blue(15))),
            Garment("bottom", (_teal(100),)),
        )
        assert not check_anchor_secondaries(outfit4, partial_scheme, partial_anchors)

    def test_compatible_secondary_passes_with_trimmed_anchors(self) -> None:
        outfit = _outfit(
            Garment("top",    (_red(85), _teal(15))),
            Garment("bottom", (_teal(100),)),
        )
        scheme  = frozenset({"Red", "Teal"})
        anchors = frozenset({"Red", "Teal"})
        from app.matcher.slots import check_anchor_secondaries
        assert check_anchor_secondaries(outfit, scheme, anchors)


# ── FR-21 / FR-22: qualify_echo_slot ─────────────────────────────────────────

class TestQualifyEchoSlot:
    def test_neutral_primary_qualifies(self) -> None:
        socks = Garment("socks", (_grey(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies
        assert result.minor_echoes == frozenset()

    def test_echo_primary_qualifies(self) -> None:
        # Red socks, anchors have Red
        socks = Garment("socks", (_red(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies

    def test_chromatic_non_echo_primary_fails(self) -> None:
        # Blue socks, anchors have Red + Teal only
        socks = Garment("socks", (_blue(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert not result.qualifies
        assert result.minor_echoes == frozenset()

    def test_chromatic_non_echo_secondary_fails(self) -> None:
        # Grey primary (neutral), Blue secondary; anchors have Red+Teal
        socks = Garment("socks", (_grey(85), _blue(15)))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert not result.qualifies

    def test_minor_does_not_disqualify(self) -> None:
        # Red primary (90%), Blue minor (10%); anchors have Red
        socks = Garment("socks", (_red(90), _blue(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies

    def test_minor_echo_recorded_when_qualifying(self) -> None:
        # Red primary (90%), Teal minor (10%); anchors have Red + Teal
        # socks qualifies; Teal minor echoes anchor → recorded in minor_echoes
        socks = Garment("socks", (_red(90), _teal(10)))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies
        assert "Teal" in result.minor_echoes

    def test_minor_non_echo_not_recorded(self) -> None:
        # Red primary (90%), Blue minor (10%); anchors have Red only (no Blue)
        socks = Garment("socks", (_red(90), _blue(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies
        assert "Blue" not in result.minor_echoes

    def test_neutral_minor_not_recorded(self) -> None:
        socks = Garment("socks", (_red(90), _grey(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies
        assert not result.minor_echoes

    def test_returns_echo_qualification_type(self) -> None:
        socks = Garment("socks", (_grey(100),))
        result = qualify_echo_slot(socks, frozenset())
        assert isinstance(result, EchoQualification)


# ── Wardrobe integration: single_valid_outfit ─────────────────────────────────

class TestSingleValidOutfitSlots:
    """Slots pipeline over the single_valid_outfit fixture (FR-13, FR-15)."""

    def setup_method(self) -> None:
        self.outfit = _outfit(*single_valid_outfit())
        self.ss     = build_scheme_set(self.outfit)
        self.anchors = get_anchor_chromatic_families(self.outfit)

    def test_dominant_is_top(self) -> None:
        assert dominant_layer(self.outfit) == "top"

    def test_no_covered_layers(self) -> None:
        assert covered_upper_layers(self.outfit) == []

    def test_anchor_types_are_top_and_bottom(self) -> None:
        assert get_anchor_types(self.outfit) == ["top", "bottom"]

    def test_scheme_set_has_red_and_teal(self) -> None:
        assert self.ss.chromatic_families == frozenset({"Red", "Teal"})

    def test_socks_grey_qualify_echo(self) -> None:
        result = qualify_echo_slot(self.outfit["socks"], self.anchors)
        assert result.qualifies

    def test_shoes_black_qualify_echo(self) -> None:
        result = qualify_echo_slot(self.outfit["shoes"], self.anchors)
        assert result.qualifies

    def test_anchor_secondaries_pass(self) -> None:
        assert check_anchor_secondaries(
            self.outfit, self.ss.chromatic_families, self.anchors
        )


# ── Wardrobe integration: rich_echo_wardrobe ─────────────────────────────────

class TestRichEchoWardrobeSlots:
    """Minor-echo recording via the rich_echo_wardrobe fixture (FR-11, FR-22)."""

    def setup_method(self) -> None:
        self.outfit  = _outfit(*rich_echo_wardrobe())
        self.anchors = get_anchor_chromatic_families(self.outfit)

    def test_anchor_families_include_teal_minor(self) -> None:
        # top carries Teal as minor (13%); it should still appear in anchor families
        assert "Teal" in self.anchors

    def test_red_socks_qualify(self) -> None:
        result = qualify_echo_slot(self.outfit["socks"], self.anchors)
        assert result.qualifies

    def test_grey_shoes_qualify_as_neutral(self) -> None:
        result = qualify_echo_slot(self.outfit["shoes"], self.anchors)
        assert result.qualifies

    def test_no_minor_echoes_on_single_colour_socks(self) -> None:
        # socks is Red only; no minor colours on socks
        result = qualify_echo_slot(self.outfit["socks"], self.anchors)
        assert result.minor_echoes == frozenset()


# ── Wardrobe integration: no_valid_outfit echo-slot failure ───────────────────

class TestNoValidOutfitEchoFails:
    """Blue echo slot cannot satisfy FR-21 against Red+Teal anchors."""

    @pytest.mark.parametrize("slot", ["socks", "shoes", "hat", "accessory"])
    def test_blue_echo_slot_fails_qualification(self, slot: str) -> None:
        garments = no_valid_outfit_constrained_by(slot)
        outfit   = _outfit(*garments)
        # Build anchor families from the top+bottom (Red and Teal)
        anchors = get_anchor_chromatic_families(outfit)
        # The constrained slot carries Blue; Blue is not Red or Teal
        constrained = outfit[slot]
        result = qualify_echo_slot(constrained, anchors)
        assert not result.qualifies


# ── Wardrobe integration: two_valid_outfits ───────────────────────────────────

class TestTwoValidOutfitsSlots:
    """Both distinct tops form the same Red+Teal complementary scheme (FR-40)."""

    def test_both_tops_yield_same_scheme_family(self) -> None:
        garments = two_valid_outfits()
        tops = [g for g in garments if g.garment_type == "top"]
        assert len(tops) == 2
        for top in tops:
            outfit = {
                "top":    top,
                "bottom": next(g for g in garments if g.garment_type == "bottom"),
                "socks":  next(g for g in garments if g.garment_type == "socks"),
                "shoes":  next(g for g in garments if g.garment_type == "shoes"),
            }
            ss = build_scheme_set(outfit)
            assert "Red"  in ss.chromatic_families
            assert "Teal" in ss.chromatic_families
