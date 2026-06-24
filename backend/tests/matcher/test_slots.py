"""
Tests for matcher.slots (test strategy §4.6).

Coverage:
  - FR-16: category_to_slot — v0.2.0 mapping, v0.1.0 backward-compat, identity fallback
  - FR-16 / FR-17: slot constant correctness; GARMENT_TYPES v0.1.0 backward-compat alias
  - FR-18: dominant_layer — four-level stack (outer > mid > shirt > base), one-piece,
            error case; covered_upper_layers; get_anchor_types
  - FR-49.3 / FR-50.2: is_valid_slot_combination, minor vs statement adornment tiers
  - FR-19: build_scheme_set — dominant primaries, lower-body primaries, anchor
            secondaries, covered-layer-primary exclusion, one-piece counted once
  - FR-20: check_covered_layer — in-scheme, echo, neutral pass; out-of-scheme fail
  - FR-9:  check_anchor_secondaries — compatible and incompatible secondaries
  - FR-21 / FR-22: qualify_echo_slot — neutral, echo, minor-echo recording, fail;
            minor-adornment tier never disqualifies (FR-49.3)
  - get_anchor_chromatic_families — collects across all roles on all anchors
"""

from __future__ import annotations

import pytest

from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.matcher.slots import (
    ADORNMENT_SLOTS,
    DEFAULT_SLOTS,
    ECHO_SLOTS,
    GARMENT_TYPES,
    MINOR_ADORNMENT_SLOTS,
    REQUIRED_SLOTS,
    STATEMENT_ADORNMENT_SLOTS,
    EchoQualification,
    SchemeSet,
    build_scheme_set,
    category_to_slot,
    check_anchor_secondaries,
    check_covered_layer,
    covered_upper_layers,
    dominant_layer,
    get_anchor_chromatic_families,
    get_anchor_types,
    is_valid_slot_combination,
    qualify_echo_slot,
)
from tests.fixtures.wardrobes import (
    no_valid_outfit_constrained_by,
    neutral_fallback_only,
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


def _outfit(*garments: Garment) -> dict[str, Garment]:
    """Build an outfit dict using v0.2.0 slot keys via category_to_slot."""
    return {category_to_slot(g.garment_type): g for g in garments}


# ── FR-16: category_to_slot ───────────────────────────────────────────────────

class TestCategoryToSlot:
    def test_v2_base_categories(self) -> None:
        assert category_to_slot("t_shirt")    == "base"
        assert category_to_slot("vest")       == "base"
        assert category_to_slot("long_sleeve") == "base"

    def test_v2_shirt_categories(self) -> None:
        assert category_to_slot("shirt")  == "shirt"
        assert category_to_slot("blouse") == "shirt"
        assert category_to_slot("polo")   == "shirt"

    def test_v2_mid_categories(self) -> None:
        assert category_to_slot("jumper")    == "mid"
        assert category_to_slot("hoodie")    == "mid"
        assert category_to_slot("cardigan")  == "mid"
        assert category_to_slot("sweatshirt") == "mid"
        assert category_to_slot("track_top") == "mid"
        assert category_to_slot("waistcoat") == "mid"

    def test_v2_outer_categories(self) -> None:
        assert category_to_slot("jacket") == "outer"
        assert category_to_slot("blazer") == "outer"
        assert category_to_slot("coat")   == "outer"

    def test_v2_lower_body_categories(self) -> None:
        assert category_to_slot("trousers") == "lower_body"
        assert category_to_slot("jeans")    == "lower_body"
        assert category_to_slot("chinos")   == "lower_body"
        assert category_to_slot("shorts")   == "lower_body"
        assert category_to_slot("skirt")    == "lower_body"
        assert category_to_slot("dress")    == "lower_body"
        assert category_to_slot("jumpsuit") == "lower_body"

    def test_v2_shoe_categories(self) -> None:
        assert category_to_slot("shoes")    == "shoes"
        assert category_to_slot("boots")    == "shoes"
        assert category_to_slot("trainers") == "shoes"
        assert category_to_slot("sandals")  == "shoes"

    def test_v2_hat_categories(self) -> None:
        assert category_to_slot("hat")    == "hat"
        assert category_to_slot("cap")    == "hat"
        assert category_to_slot("beanie") == "hat"

    def test_v2_adornment_categories(self) -> None:
        assert category_to_slot("glasses")   == "glasses"
        assert category_to_slot("sunglasses") == "glasses"
        assert category_to_slot("earrings")  == "earrings"
        assert category_to_slot("tie")       == "tie"
        assert category_to_slot("scarf")     == "scarf"
        assert category_to_slot("necklace")  == "necklace"
        assert category_to_slot("watch")     == "watch"
        assert category_to_slot("ring")      == "ring"
        assert category_to_slot("bracelet")  == "bracelet"
        assert category_to_slot("belt")      == "belt"
        assert category_to_slot("socks")     == "socks"

    def test_v1_backward_compat_top(self) -> None:
        assert category_to_slot("top") == "base"

    def test_v1_backward_compat_bottom(self) -> None:
        assert category_to_slot("bottom") == "lower_body"

    def test_v1_backward_compat_jersey(self) -> None:
        assert category_to_slot("jersey") == "mid"

    def test_v1_jacket_via_category_slot(self) -> None:
        # "jacket" is a v0.2.0 category (outer) — handled by CATEGORY_SLOT, not _V1_TO_SLOT
        assert category_to_slot("jacket") == "outer"

    def test_v1_unchanged_socks_shoes_hat(self) -> None:
        # These had the same key in v0.1.0 and v0.2.0
        assert category_to_slot("socks") == "socks"
        assert category_to_slot("shoes") == "shoes"
        assert category_to_slot("hat")   == "hat"

    def test_identity_fallback_for_unknown(self) -> None:
        # Completely unknown strings pass through unchanged
        assert category_to_slot("accessory") == "accessory"
        assert category_to_slot("unknown_thing") == "unknown_thing"


# ── FR-16 / FR-17: slot constants ────────────────────────────────────────────

class TestSlotConstants:
    def test_garment_types_has_forty_members(self) -> None:
        assert len(GARMENT_TYPES) == 40

    def test_garment_types_content(self) -> None:
        from app.matcher import constants as C
        assert GARMENT_TYPES == C.ALL_CATEGORIES

    def test_required_slots_v2_content(self) -> None:
        # After HUE-065 REQUIRED_SLOTS == DEFAULT_SLOTS (v0.2.0 slot names)
        assert REQUIRED_SLOTS == frozenset({"base", "lower_body", "socks", "shoes"})

    def test_default_slots_v2_content(self) -> None:
        assert DEFAULT_SLOTS == frozenset({"base", "lower_body", "socks", "shoes"})

    def test_echo_slots_alias_equals_adornment_slots(self) -> None:
        assert ECHO_SLOTS == ADORNMENT_SLOTS

    def test_adornment_slots_includes_all_17_adornments(self) -> None:
        expected = STATEMENT_ADORNMENT_SLOTS | MINOR_ADORNMENT_SLOTS
        assert ADORNMENT_SLOTS == expected

    def test_statement_adornment_slots_content(self) -> None:
        assert STATEMENT_ADORNMENT_SLOTS == frozenset({
            "hat", "tie", "scarf", "belt", "socks", "shoes",
        })

    def test_minor_adornment_slots_content(self) -> None:
        assert MINOR_ADORNMENT_SLOTS == frozenset({
            "glasses", "earrings", "necklace", "watch", "ring", "bracelet",
        })

    def test_statement_and_minor_are_disjoint(self) -> None:
        assert not (STATEMENT_ADORNMENT_SLOTS & MINOR_ADORNMENT_SLOTS)


# ── FR-50: is_valid_slot_combination ─────────────────────────────────────────

class TestIsValidSlotCombination:
    def test_normal_outfit_is_valid(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        assert is_valid_slot_combination(outfit)

    def test_one_piece_without_base_is_valid(self) -> None:
        outfit = {
            "lower_body": Garment("dress",     (_red(100),)),
            "socks":      Garment("socks",     (_grey(100),)),
        }
        assert is_valid_slot_combination(outfit)

    def test_one_piece_with_base_is_invalid(self) -> None:
        # FR-50.2: dress occupies base slot implicitly → separate base is invalid
        outfit = {
            "lower_body": Garment("dress",    (_red(100),)),
            "base":       Garment("t_shirt",  (_teal(100),)),
        }
        assert not is_valid_slot_combination(outfit)

    def test_jumpsuit_with_base_is_invalid(self) -> None:
        outfit = {
            "lower_body": Garment("jumpsuit", (_red(100),)),
            "base":       Garment("t_shirt",  (_teal(100),)),
        }
        assert not is_valid_slot_combination(outfit)

    def test_separate_trouser_with_base_is_valid(self) -> None:
        # Trousers are not a one-piece; base + lower_body is the normal pattern
        outfit = {
            "lower_body": Garment("trousers", (_teal(100),)),
            "base":       Garment("t_shirt",  (_red(100),)),
        }
        assert is_valid_slot_combination(outfit)

    def test_no_lower_body_is_valid(self) -> None:
        # Outer layer only (e.g. jacket over base, no lower body — unusual but not excluded)
        outfit = {"outer": Garment("jacket", (_red(100),))}
        assert is_valid_slot_combination(outfit)


# ── FR-18: dominant_layer ─────────────────────────────────────────────────────

class TestDominantLayer:
    """Four-level stack: outer > mid > shirt > base; one-piece fallback."""

    def test_base_only_is_dominant(self) -> None:
        outfit = {"base": Garment("t_shirt", (_red(100),))}
        assert dominant_layer(outfit) == "base"

    def test_shirt_beats_base(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "shirt": Garment("shirt",   (_teal(100),)),
        }
        assert dominant_layer(outfit) == "shirt"

    def test_mid_beats_shirt(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "shirt": Garment("shirt",   (_teal(100),)),
            "mid":   Garment("jumper",  (_blue(100),)),
        }
        assert dominant_layer(outfit) == "mid"

    def test_outer_beats_mid(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "mid":   Garment("jumper",  (_teal(100),)),
            "outer": Garment("jacket",  (_blue(100),)),
        }
        assert dominant_layer(outfit) == "outer"

    def test_outer_beats_base_without_mid(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "outer": Garment("jacket",  (_blue(100),)),
        }
        assert dominant_layer(outfit) == "outer"

    def test_one_piece_with_no_upper_body_returns_lower_body(self) -> None:
        # Dress fills lower_body; no separate upper-body layer
        outfit = {"lower_body": Garment("dress", (_red(100),))}
        assert dominant_layer(outfit) == "lower_body"

    def test_outer_beats_one_piece(self) -> None:
        # When an outer layer IS present, it dominates even over a one-piece
        outfit = {
            "lower_body": Garment("dress",  (_red(100),)),
            "outer":      Garment("jacket", (_blue(100),)),
        }
        assert dominant_layer(outfit) == "outer"

    def test_non_one_piece_lower_body_without_upper_raises(self) -> None:
        outfit = {
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
        }
        with pytest.raises(ValueError):
            dominant_layer(outfit)

    def test_no_upper_body_at_all_raises(self) -> None:
        outfit = {"socks": Garment("socks", (_grey(100),))}
        with pytest.raises(ValueError):
            dominant_layer(outfit)


# ── FR-18: covered_upper_layers ───────────────────────────────────────────────

class TestCoveredUpperLayers:
    def test_base_only_has_no_covered_layers(self) -> None:
        outfit = {"base": Garment("t_shirt", (_red(100),))}
        assert covered_upper_layers(outfit) == []

    def test_mid_covers_base(self) -> None:
        outfit = {
            "base": Garment("t_shirt", (_red(100),)),
            "mid":  Garment("jumper",  (_teal(100),)),
        }
        assert covered_upper_layers(outfit) == ["base"]

    def test_outer_covers_mid_and_base(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "mid":   Garment("jumper",  (_teal(100),)),
            "outer": Garment("jacket",  (_blue(100),)),
        }
        assert covered_upper_layers(outfit) == ["mid", "base"]

    def test_outer_covers_only_base_when_no_mid(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "outer": Garment("jacket",  (_blue(100),)),
        }
        assert covered_upper_layers(outfit) == ["base"]

    def test_outer_alone_covers_nothing_additional(self) -> None:
        outfit = {"outer": Garment("jacket", (_blue(100),))}
        assert covered_upper_layers(outfit) == []

    def test_shirt_covers_base(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "shirt": Garment("shirt",   (_teal(100),)),
        }
        assert covered_upper_layers(outfit) == ["base"]

    def test_outer_covers_shirt_and_base(self) -> None:
        outfit = {
            "base":  Garment("t_shirt", (_red(100),)),
            "shirt": Garment("shirt",   (_teal(100),)),
            "outer": Garment("jacket",  (_blue(100),)),
        }
        assert covered_upper_layers(outfit) == ["shirt", "base"]

    def test_one_piece_returns_empty(self) -> None:
        # One-piece is the dominant; lower portion never covered (FR-50.2)
        outfit = {"lower_body": Garment("dress", (_red(100),))}
        assert covered_upper_layers(outfit) == []

    def test_echo_only_outfit_returns_empty(self) -> None:
        # No upper-body layer and no one-piece → dominant_layer raises, returns []
        outfit = {"socks": Garment("socks", (_grey(100),)), "shoes": Garment("shoes", (_black(100),))}
        assert covered_upper_layers(outfit) == []


# ── FR-18: get_anchor_types ───────────────────────────────────────────────────

class TestGetAnchorTypes:
    def test_base_and_lower_body_in_order(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        assert get_anchor_types(outfit) == ["base", "lower_body"]

    def test_all_upper_body_layers_and_lower_body_in_order(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "mid":        Garment("jumper",   (_teal(100),)),
            "outer":      Garment("jacket",   (_blue(100),)),
            "lower_body": Garment("trousers", (_grey(100),)),
        }
        assert get_anchor_types(outfit) == ["outer", "mid", "base", "lower_body"]

    def test_shirt_layer_included_in_order(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "shirt":      Garment("shirt",    (_teal(100),)),
            "lower_body": Garment("trousers", (_grey(100),)),
        }
        assert get_anchor_types(outfit) == ["shirt", "base", "lower_body"]

    def test_adornment_slots_not_included_as_anchors(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
            "hat":        Garment("hat",      (_grey(100),)),
        }
        anchors = get_anchor_types(outfit)
        assert "socks" not in anchors
        assert "shoes" not in anchors
        assert "hat"   not in anchors

    def test_no_lower_body_in_outfit(self) -> None:
        outfit = {"base": Garment("t_shirt", (_red(100),))}
        assert "lower_body" not in get_anchor_types(outfit)

    def test_one_piece_listed_once(self) -> None:
        # Dress at lower_body; no separate upper layer → listed once as lower_body
        outfit = {"lower_body": Garment("dress", (_red(100),))}
        anchors = get_anchor_types(outfit)
        assert anchors.count("lower_body") == 1


# ── FR-19: build_scheme_set ───────────────────────────────────────────────────

class TestBuildSchemeSet:
    def test_dominant_and_lower_body_primaries_included(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families
        assert "Teal" in ss.chromatic_families

    def test_neutral_primaries_excluded_from_hues(self) -> None:
        outfit = _outfit(*neutral_fallback_only())
        ss = build_scheme_set(outfit)
        assert ss.hues == ()
        assert ss.chromatic_families == frozenset()

    def test_covered_layer_primary_excluded(self) -> None:
        # outer (Red) is dominant; mid (Blue) is covered; lower_body (Teal)
        # scheme_set should include Red + Teal, but NOT Blue (from covered mid)
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_blue(100),)),
            "lower_body": Garment("trousers",(_teal(100),)),
        }
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families
        assert "Teal" in ss.chromatic_families
        assert "Blue" not in ss.chromatic_families

    def test_anchor_secondaries_included(self) -> None:
        # base: Red primary 70%, Teal secondary 20%, Blue minor 10%
        # lower_body: Grey primary 100%
        outfit = {
            "base":       Garment("t_shirt",  (_red(70), _teal(20), _blue(10))),
            "lower_body": Garment("trousers", (_grey(100),)),
        }
        ss = build_scheme_set(outfit)
        assert "Red"  in ss.chromatic_families   # dominant primary
        assert "Teal" in ss.chromatic_families   # anchor secondary (FR-19)
        # minor Blue must NOT be in the scheme set (FR-10, FR-19)
        assert "Blue" not in ss.chromatic_families

    def test_covered_layer_secondary_still_included(self) -> None:
        # FR-19: all anchors' secondaries contribute, including covered layers
        # outer (Red), mid (Blue secondary = Teal), lower_body (Grey)
        outfit = {
            "outer":      Garment("jacket",  (_red(100),)),
            "mid":        Garment("jumper",  (_blue(70), _teal(20), _grey(10))),
            "lower_body": Garment("trousers",(_grey(100),)),
        }
        ss = build_scheme_set(outfit)
        # mid secondary (Teal) should be present
        assert "Teal" in ss.chromatic_families
        # mid primary (Blue) is covered → excluded
        assert "Blue" not in ss.chromatic_families

    def test_one_piece_counted_once_not_twice(self) -> None:
        # Dress at lower_body with no upper-body layer: dominant IS lower_body
        # Primary should appear once (not doubled)
        outfit = {"lower_body": Garment("dress", (_red(100),))}
        ss = build_scheme_set(outfit)
        assert ss.hues.count(0.0) == 1   # Red hue added exactly once

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

    def test_no_lower_body_in_outfit(self) -> None:
        # outfit with only an upper-body layer — lower_body branch must not raise
        outfit = {"base": Garment("t_shirt", (_red(100),))}
        ss = build_scheme_set(outfit)
        assert "Red" in ss.chromatic_families
        assert len(ss.hues) == 1


# ── get_anchor_chromatic_families ────────────────────────────────────────────

class TestGetAnchorChromaticFamilies:
    def test_collects_all_chromatic_families_across_roles(self) -> None:
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
        outfit = _outfit(*neutral_fallback_only())
        assert get_anchor_chromatic_families(outfit) == frozenset()

    def test_adornment_slots_not_counted_as_anchors(self) -> None:
        # Blue shoes should NOT add Blue to anchor families
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_blue(100),)),
        }
        fams = get_anchor_chromatic_families(outfit)
        assert "Blue" not in fams


# ── FR-20: check_covered_layer ────────────────────────────────────────────────

class TestCheckCoveredLayer:
    _SCHEME  = frozenset({"Red", "Teal"})
    _ANCHORS = frozenset({"Red", "Teal", "Blue"})

    def test_in_scheme_primary_passes(self) -> None:
        mid = Garment("jumper", (_red(100),))
        assert check_covered_layer(mid, self._SCHEME, self._ANCHORS)

    def test_echo_primary_passes(self) -> None:
        # Blue is not in scheme but is on anchors → echo → passes
        mid = Garment("jumper", (_blue(100),))
        assert check_covered_layer(mid, self._SCHEME, self._ANCHORS)

    def test_all_neutral_passes_unconditionally(self) -> None:
        mid = Garment("jumper", (_grey(100),))
        assert check_covered_layer(mid, self._SCHEME, frozenset())

    def test_out_of_scheme_chromatic_fails(self) -> None:
        # Chartreuse not in scheme {Red, Teal}, not in anchors {Red, Teal, Blue}
        chartreuse = Colour(h=90.0, s=70.0, l=40.0, proportion=100)
        mid = Garment("jumper", (chartreuse,))
        assert not check_covered_layer(mid, self._SCHEME, self._ANCHORS)

    def test_in_scheme_secondary_passes(self) -> None:
        # Red primary 70%, Teal secondary 20%, Blue minor 10%
        # Teal is in scheme → passes; Blue minor never disqualifies
        mid = Garment("jumper", (_red(70), _teal(20), _blue(10)))
        assert check_covered_layer(mid, self._SCHEME, self._ANCHORS)

    def test_neutral_secondary_passes(self) -> None:
        mid = Garment("jumper", (_red(85), _grey(15)))
        assert check_covered_layer(mid, self._SCHEME, self._ANCHORS)


# ── FR-9: check_anchor_secondaries ───────────────────────────────────────────

class TestCheckAnchorSecondaries:
    def test_no_secondaries_passes(self) -> None:
        outfit = _outfit(*single_valid_outfit())
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_in_scheme_secondary_passes(self) -> None:
        # base: Red primary 70%, Teal secondary 20%; lower_body: Teal 100%
        outfit = {
            "base":       Garment("t_shirt",  (_red(70), _teal(20), _grey(10))),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_neutral_secondary_passes(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(85), _grey(15))),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        ss = build_scheme_set(outfit)
        fams = get_anchor_chromatic_families(outfit)
        assert check_anchor_secondaries(outfit, ss.chromatic_families, fams)

    def test_incompatible_secondary_fails_with_trimmed_anchors(self) -> None:
        # Hand-craft a scheme/anchor set that excludes the secondary's family
        outfit = {
            "base":       Garment("t_shirt",  (_red(85), _blue(15))),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        partial_scheme  = frozenset({"Red", "Teal"})
        partial_anchors = frozenset({"Red", "Teal"})   # excludes Blue
        assert not check_anchor_secondaries(outfit, partial_scheme, partial_anchors)

    def test_compatible_secondary_passes_with_trimmed_anchors(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(85), _teal(15))),
            "lower_body": Garment("trousers", (_teal(100),)),
        }
        scheme  = frozenset({"Red", "Teal"})
        anchors = frozenset({"Red", "Teal"})
        assert check_anchor_secondaries(outfit, scheme, anchors)


# ── FR-21 / FR-22: qualify_echo_slot — statement adornments ───────────────────

class TestQualifyEchoSlotStatement:
    """Statement adornments (hat, tie, scarf, belt, socks, shoes) are echo-constrained."""

    def test_neutral_primary_qualifies(self) -> None:
        socks = Garment("socks", (_grey(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies
        assert result.minor_echoes == frozenset()

    def test_echo_primary_qualifies(self) -> None:
        socks = Garment("socks", (_red(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies

    def test_chromatic_non_echo_primary_fails(self) -> None:
        socks = Garment("socks", (_blue(100),))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert not result.qualifies
        assert result.minor_echoes == frozenset()

    def test_chromatic_non_echo_secondary_fails(self) -> None:
        socks = Garment("socks", (_grey(85), _blue(15)))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert not result.qualifies

    def test_minor_does_not_disqualify(self) -> None:
        socks = Garment("socks", (_red(90), _blue(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies

    def test_minor_echo_recorded_when_qualifying(self) -> None:
        socks = Garment("socks", (_red(90), _teal(10)))
        result = qualify_echo_slot(socks, frozenset({"Red", "Teal"}))
        assert result.qualifies
        assert "Teal" in result.minor_echoes

    def test_minor_non_echo_not_recorded(self) -> None:
        socks = Garment("socks", (_red(90), _blue(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies
        assert "Blue" not in result.minor_echoes

    def test_neutral_minor_not_recorded(self) -> None:
        socks = Garment("socks", (_red(90), _grey(10)))
        result = qualify_echo_slot(socks, frozenset({"Red"}))
        assert result.qualifies
        assert not result.minor_echoes

    def test_hat_is_statement_adornment(self) -> None:
        # Hat is a statement adornment; chromatic non-echo primary must fail
        hat = Garment("hat", (_blue(100),))
        result = qualify_echo_slot(hat, frozenset({"Red", "Teal"}))
        assert not result.qualifies

    def test_returns_echo_qualification_type(self) -> None:
        socks = Garment("socks", (_grey(100),))
        result = qualify_echo_slot(socks, frozenset())
        assert isinstance(result, EchoQualification)


# ── FR-21 / FR-22: qualify_echo_slot — minor adornments (FR-49.3) ────────────

class TestQualifyEchoSlotMinor:
    """Minor adornments (glasses, earrings, necklace, watch, ring, bracelet) never disqualify."""

    @pytest.mark.parametrize("category", [
        "glasses", "sunglasses", "earrings", "necklace", "watch", "ring", "bracelet",
    ])
    def test_chromatic_non_echo_never_disqualifies(self, category: str) -> None:
        # Even though the colour is not in the anchor families, minor adornments qualify
        garment = Garment(category, (_blue(100),))
        result = qualify_echo_slot(garment, frozenset({"Red", "Teal"}))
        assert result.qualifies

    @pytest.mark.parametrize("category", [
        "glasses", "earrings", "necklace", "watch", "ring", "bracelet",
    ])
    def test_minor_echo_is_still_recorded(self, category: str) -> None:
        # Even though it never disqualifies, echoing minor colours are recorded (FR-22).
        # Red is primary (90%), Teal is minor (10%); anchor has Teal → "Teal" in minor_echoes
        garment = Garment(category, (_red(90), _teal(10)))
        result = qualify_echo_slot(garment, frozenset({"Red", "Teal"}))
        assert result.qualifies
        assert "Teal" in result.minor_echoes

    def test_non_echo_minor_not_in_minor_echoes(self) -> None:
        garment = Garment("ring", (_blue(90), _teal(10)))
        result = qualify_echo_slot(garment, frozenset({"Red"}))
        # qualifies (minor adornment)
        assert result.qualifies
        # Teal echoes Red? No — Teal not in {"Red"} → not recorded
        # Blue not in {"Red"} → not recorded either
        assert result.minor_echoes == frozenset()


# ── Wardrobe integration: single_valid_outfit ─────────────────────────────────

class TestSingleValidOutfitSlots:
    """Slots pipeline over the single_valid_outfit fixture (FR-13, FR-15)."""

    def setup_method(self) -> None:
        self.outfit  = _outfit(*single_valid_outfit())
        self.ss      = build_scheme_set(self.outfit)
        self.anchors = get_anchor_chromatic_families(self.outfit)

    def test_dominant_is_base(self) -> None:
        assert dominant_layer(self.outfit) == "base"

    def test_no_covered_layers(self) -> None:
        assert covered_upper_layers(self.outfit) == []

    def test_anchor_types_are_base_and_lower_body(self) -> None:
        assert get_anchor_types(self.outfit) == ["base", "lower_body"]

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

    def test_valid_slot_combination(self) -> None:
        assert is_valid_slot_combination(self.outfit)


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
        result = qualify_echo_slot(self.outfit["socks"], self.anchors)
        assert result.minor_echoes == frozenset()


# ── Wardrobe integration: no_valid_outfit echo-slot failure ───────────────────

class TestNoValidOutfitEchoFails:
    """Blue statement-adornment slot cannot satisfy FR-21 against Red+Teal anchors."""

    @pytest.mark.parametrize("slot", ["socks", "shoes", "hat"])
    def test_blue_echo_slot_fails_qualification(self, slot: str) -> None:
        garments = no_valid_outfit_constrained_by(slot)
        outfit   = _outfit(*garments)
        anchors  = get_anchor_chromatic_families(outfit)
        # The constrained slot carries Blue; Blue is not Red or Teal
        constrained = outfit[slot]
        result = qualify_echo_slot(constrained, anchors)
        assert not result.qualifies


# ── Wardrobe integration: two_valid_outfits ───────────────────────────────────

class TestTwoValidOutfitsSlots:
    """Both distinct tops form the same Red+Teal complementary scheme (FR-40)."""

    def test_both_tops_yield_same_scheme_family(self) -> None:
        garments = two_valid_outfits()
        tops = [g for g in garments if g.garment_type == "t_shirt"]
        assert len(tops) == 2
        for top in tops:
            outfit = {
                "base":       top,
                "lower_body": next(g for g in garments if g.garment_type == "trousers"),
                "socks":      next(g for g in garments if g.garment_type == "socks"),
                "shoes":      next(g for g in garments if g.garment_type == "shoes"),
            }
            ss = build_scheme_set(outfit)
            assert "Red"  in ss.chromatic_families
            assert "Teal" in ss.chromatic_families
