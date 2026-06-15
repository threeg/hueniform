"""
Self-check tests for the wardrobe scenario factories (test strategy §11.2).

These tests verify only structural validity — proportions, colour counts, garment
types.  Whether each wardrobe actually produces the claimed evaluation outcome is
the job of test_slots.py and test_ranking.py (HUE-013/HUE-014), which import
these factories.
"""

from __future__ import annotations

import pytest

from app.matcher.roles import Garment
from tests.fixtures.wardrobes import (
    GARMENT_TYPES,
    no_valid_outfit_constrained_by,
    neutral_fallback_only,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
)

_REQUIRED_SLOTS = {"top", "bottom", "socks", "shoes"}
_ECHO_SLOTS = {"socks", "shoes", "hat", "accessory"}
_ANCHOR_SLOTS = {"top", "bottom"}
_CONSTRAINED_BY_SLOTS = list(_REQUIRED_SLOTS | _ECHO_SLOTS)


def _check_garment(g: Garment) -> None:
    """Assert one garment is structurally valid (FR-6, FR-16)."""
    assert g.garment_type in GARMENT_TYPES, (
        f"Invalid garment_type '{g.garment_type}'; must be one of {sorted(GARMENT_TYPES)}"
    )
    assert 1 <= len(g.colours) <= 4, (
        f"FR-6: palette must have 1–4 colours, got {len(g.colours)} for '{g.garment_type}'"
    )
    total = sum(c.proportion for c in g.colours)
    assert total == 100, (
        f"FR-6: proportions must sum to 100, got {total} for '{g.garment_type}'"
    )
    for c in g.colours:
        assert 0 <= c.h <= 360, f"Hue {c.h} out of range for '{g.garment_type}'"
        assert 0 <= c.s <= 100, f"Saturation {c.s} out of range for '{g.garment_type}'"
        assert 0 <= c.l <= 100, f"Lightness {c.l} out of range for '{g.garment_type}'"
        assert c.proportion >= 0, f"Negative proportion for '{g.garment_type}'"


def _check_all(garments: list[Garment]) -> None:
    assert isinstance(garments, list)
    assert len(garments) >= 1
    for g in garments:
        assert isinstance(g, Garment)
        _check_garment(g)


class TestSingleValidOutfit:
    def test_structurally_valid(self) -> None:
        _check_all(single_valid_outfit())

    def test_has_all_required_slots(self) -> None:
        types = {g.garment_type for g in single_valid_outfit()}
        assert _REQUIRED_SLOTS <= types

    def test_one_garment_per_required_slot(self) -> None:
        garments = single_valid_outfit()
        for slot in _REQUIRED_SLOTS:
            count = sum(1 for g in garments if g.garment_type == slot)
            assert count == 1, f"Expected 1 garment for '{slot}', got {count}"


class TestTwoValidOutfits:
    def test_structurally_valid(self) -> None:
        _check_all(two_valid_outfits())

    def test_has_all_required_slots(self) -> None:
        types = {g.garment_type for g in two_valid_outfits()}
        assert _REQUIRED_SLOTS <= types

    def test_exactly_two_tops(self) -> None:
        tops = [g for g in two_valid_outfits() if g.garment_type == "top"]
        assert len(tops) == 2

    def test_two_tops_are_distinct(self) -> None:
        tops = [g for g in two_valid_outfits() if g.garment_type == "top"]
        assert tops[0] != tops[1]


class TestNeutralFallbackOnly:
    def test_structurally_valid(self) -> None:
        _check_all(neutral_fallback_only())

    def test_has_all_required_slots(self) -> None:
        types = {g.garment_type for g in neutral_fallback_only()}
        assert _REQUIRED_SLOTS <= types

    def test_all_colours_are_neutral(self) -> None:
        from app.matcher.taxonomy import is_neutral, classify
        for g in neutral_fallback_only():
            for c in g.colours:
                family = classify(c.h, c.s, c.l)
                assert is_neutral(family), (
                    f"Expected all neutrals; '{g.garment_type}' has chromatic '{family}'"
                )


class TestNoValidOutfitConstrainedBy:
    @pytest.mark.parametrize("slot", _CONSTRAINED_BY_SLOTS)
    def test_structurally_valid(self, slot: str) -> None:
        _check_all(no_valid_outfit_constrained_by(slot))

    @pytest.mark.parametrize("slot", _CONSTRAINED_BY_SLOTS)
    def test_has_required_slots(self, slot: str) -> None:
        garments = no_valid_outfit_constrained_by(slot)
        types = {g.garment_type for g in garments}
        required = _REQUIRED_SLOTS if slot not in {"hat", "accessory"} else _REQUIRED_SLOTS
        assert required <= types, (
            f"Wardrobe constrained by '{slot}' missing required slots"
        )

    @pytest.mark.parametrize("slot", list(_ECHO_SLOTS))
    def test_constrained_echo_slot_present(self, slot: str) -> None:
        garments = no_valid_outfit_constrained_by(slot)
        types = {g.garment_type for g in garments}
        assert slot in types, f"Constrained slot '{slot}' not present in wardrobe"


class TestRichEchoWardrobe:
    def test_structurally_valid(self) -> None:
        _check_all(rich_echo_wardrobe())

    def test_has_all_required_slots(self) -> None:
        types = {g.garment_type for g in rich_echo_wardrobe()}
        assert _REQUIRED_SLOTS <= types

    def test_top_has_minor_colour(self) -> None:
        top = next(g for g in rich_echo_wardrobe() if g.garment_type == "top")
        assert len(top.colours) == 2, "Top should have 2 colours (primary + minor)"
        minor = min(top.colours, key=lambda c: c.proportion)
        assert minor.proportion < 15, (
            f"Expected a minor colour (proportion < 15), got {minor.proportion}"
        )

    def test_top_palette_sums_to_100(self) -> None:
        top = next(g for g in rich_echo_wardrobe() if g.garment_type == "top")
        assert sum(c.proportion for c in top.colours) == 100
