"""
Tests for matcher.explain (test strategy §4.9).

Coverage:
  - FR-37: scheme name, per-slot garment colour and role, echo families
  - FR-38: covariance — changing any result field changes the rendered text
  - Determinism: same input → same output
  - Sentinel (zero-result) and fallback label cases
"""

from __future__ import annotations

import pytest

from app.matcher.colour import Colour
from app.matcher.roles import Garment, GarmentRoles, derive_roles
from app.matcher.ranking import evaluate_outfit, EvaluationResult
from app.matcher.harmony import SchemeResult
from app.matcher.explain import render
from app.matcher.slots import category_to_slot
from tests.fixtures.wardrobes import (
    neutral_fallback_only,
    no_valid_outfit_constrained_by,
    single_valid_outfit,
)


def _outfit_from(garments) -> dict[str, Garment]:
    """Convert a garment list to an outfit dict using v0.2.0 slot keys."""
    return {category_to_slot(g.garment_type): g for g in garments}


# ── Colour helpers ────────────────────────────────────────────────────────────

def _c(h: float, s: float, l: float, p: int) -> Colour:
    return Colour(h=h, s=s, l=l, proportion=p)

def _red(p: int)   -> Colour: return _c(  0.0, 80.0, 50.0, p)
def _teal(p: int)  -> Colour: return _c(180.0, 70.0, 50.0, p)
def _grey(p: int)  -> Colour: return _c(  0.0,  0.0, 50.0, p)
def _black(p: int) -> Colour: return _c(  0.0,  0.0,  6.0, p)
def _navy(p: int)  -> Colour: return _c(230.0, 40.0, 18.0, p)
def _white(p: int) -> Colour: return _c(  0.0,  0.0, 96.0, p)


# ── Construction tests: scheme name appears in output ─────────────────────────

class TestSchemeInOutput:
    def test_complementary_scheme_named(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        assert "complementary" in text.lower()

    def test_neutral_based_scheme_named(self) -> None:
        outfit = _outfit_from(neutral_fallback_only())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        assert "neutral" in text.lower()

    def test_analogous_scheme_named(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_c(0.0, 80.0, 50.0, 100),)),   # red
            "lower_body": Garment("trousers", (_c(35.0, 70.0, 50.0, 100),)),  # orange (35° span)
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.scheme_result is not None
        assert result.scheme_result.scheme == "analogous"
        text = render(result)
        assert "analogous" in text.lower()


# ── Construction tests: slot colours appear in output ─────────────────────────

class TestSlotColoursInOutput:
    def test_anchor_slot_colour_families_appear(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result).lower()
        # Red base and teal lower_body are anchors; their family names must appear
        assert "red" in text
        assert "teal" in text

    def test_neutral_echo_slot_families_appear(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        # Grey socks and black shoes appear in the output
        assert "socks" in text
        assert "shoes" in text

    def test_all_requested_slots_appear(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        for slot in outfit:
            assert slot in text

    def test_anchor_role_label_present(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        assert "anchor" in text

    def test_neutral_role_label_present(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        assert "neutral" in text


# ── Construction tests: echo families appear when present ─────────────────────

class TestEchoFamiliesInOutput:
    def _echo_outfit(self) -> dict[str, Garment]:
        """Red+Teal complementary anchors; socks has Teal minor → echo_bonus=1."""
        return {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            # Red(87%) primary echoes anchor Red; Teal(13%) minor echoes anchor Teal
            "socks":      Garment("socks",    (Colour(0.0, 80.0, 50.0, 87), Colour(180.0, 70.0, 50.0, 13))),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }

    def test_echo_family_appears_when_echo_bonus_positive(self) -> None:
        outfit = self._echo_outfit()
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.echo_bonus == 1
        text = render(result)
        assert "teal" in text.lower()

    def test_minor_echoes_label_appears(self) -> None:
        outfit = self._echo_outfit()
        result = evaluate_outfit(outfit)
        assert result is not None
        text = render(result)
        assert "echo" in text.lower()

    def test_no_echo_text_when_echo_bonus_zero(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.echo_bonus == 0
        text = render(result)
        # "Minor echoes:" section must not appear
        assert "minor echoes" not in text.lower()


# ── No-primary garment ────────────────────────────────────────────────────────

class TestNoPrimaryGarment:
    def test_garment_with_no_primary_renders_without_crash(self) -> None:
        """A garment where every colour is < 30% (no primary) renders gracefully."""
        # Four equal-proportion colours (25% each) → none reaches the 30% threshold
        colours_no_primary = (
            Colour(h=0.0, s=80.0, l=50.0, proportion=25),
            Colour(h=180.0, s=70.0, l=50.0, proportion=25),
            Colour(h=240.0, s=70.0, l=50.0, proportion=25),
            Colour(h=0.0, s=0.0, l=50.0, proportion=25),
        )
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        # Build EvaluationResult directly with a no-primary garment_roles for socks
        garment_roles = {
            "base":       derive_roles(outfit["base"].colours),
            "lower_body": derive_roles(outfit["lower_body"].colours),
            "socks":      GarmentRoles(primaries=(), secondaries=(), minors=colours_no_primary, is_dual_primary=False),
            "shoes":      derive_roles(outfit["shoes"].colours),
        }
        result = EvaluationResult(
            outfit=outfit,
            scheme_result=SchemeResult("complementary", 0.0),
            garment_roles=garment_roles,
            echo_bonus=0,
            scheme_strength=1.0,
            score=100.0,
            is_fallback=False,
            constraining_slot=None,
        )
        text = render(result)
        assert "socks" in text
        assert "no primary colour" in text


# ── Sentinel case ─────────────────────────────────────────────────────────────

class TestSentinelOutput:
    def _sentinel(self, slot: str | None) -> EvaluationResult:
        return EvaluationResult(
            outfit={},
            scheme_result=None,
            garment_roles={},
            echo_bonus=0,
            scheme_strength=0.0,
            score=0.0,
            is_fallback=False,
            constraining_slot=slot,
        )

    def test_constraining_slot_named_in_output(self) -> None:
        text = render(self._sentinel("socks"))
        assert "socks" in text

    def test_different_constraining_slot_named(self) -> None:
        text = render(self._sentinel("top"))
        assert "top" in text

    def test_none_constraining_slot_renders_without_crash(self) -> None:
        text = render(self._sentinel(None))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_sentinel_does_not_contain_scheme_name(self) -> None:
        text = render(self._sentinel("socks"))
        assert "scheme" not in text.lower()


# ── Fallback label ────────────────────────────────────────────────────────────

class TestFallbackLabel:
    def test_fallback_result_labelled(self) -> None:
        outfit = _outfit_from(neutral_fallback_only())
        result = evaluate_outfit(outfit, is_fallback=True)
        assert result is not None
        assert result.is_fallback is True
        text = render(result)
        assert "fallback" in text.lower()

    def test_non_fallback_not_labelled_as_fallback(self) -> None:
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert result.is_fallback is False
        text = render(result)
        assert "fallback" not in text.lower()


# ── Covariance tests: changing a field changes the text ───────────────────────

class TestCovariance:
    def test_scheme_change_changes_text(self) -> None:
        """Different matched schemes must produce different output."""
        outfit_comp    = _outfit_from(single_valid_outfit())
        outfit_neutral = _outfit_from(neutral_fallback_only())
        result_comp = evaluate_outfit(outfit_comp)
        result_neutral = evaluate_outfit(outfit_neutral)
        assert result_comp is not None
        assert result_neutral is not None
        text_comp = render(result_comp)
        text_neutral = render(result_neutral)
        assert text_comp != text_neutral

    def test_top_colour_change_changes_text(self) -> None:
        """Changing the base's primary colour changes the output text."""
        # Red base → complementary with Teal lower_body
        outfit_red = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        # Base replaced by Teal (monochromatic with Teal lower_body)
        outfit_teal = {
            "base":       Garment("t_shirt",  (_teal(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_grey(100),)),
            "shoes":      Garment("shoes",    (_black(100),)),
        }
        result_red = evaluate_outfit(outfit_red)
        result_teal = evaluate_outfit(outfit_teal)
        assert result_red is not None
        assert result_teal is not None
        text_red = render(result_red)
        text_teal = render(result_teal)
        assert text_red != text_teal

    def test_echo_bonus_change_changes_text(self) -> None:
        """Adding a minor echo changes the output text."""
        # Without minor echo: socks 100% Red (primary, no minor)
        outfit_no_echo = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (_red(100),)),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }
        # With minor echo: socks Red(87%) + Teal(13% minor) → echo_bonus=1
        outfit_with_echo = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (Colour(0.0, 80.0, 50.0, 87), Colour(180.0, 70.0, 50.0, 13))),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }
        result_no_echo = evaluate_outfit(outfit_no_echo)
        result_with_echo = evaluate_outfit(outfit_with_echo)
        assert result_no_echo is not None
        assert result_with_echo is not None
        assert result_no_echo.echo_bonus == 0
        assert result_with_echo.echo_bonus == 1
        text_no_echo = render(result_no_echo)
        text_with_echo = render(result_with_echo)
        assert text_no_echo != text_with_echo

    def test_constraining_slot_change_changes_sentinel_text(self) -> None:
        """Different constraining slots produce different sentinel text."""
        sentinel_socks = EvaluationResult(
            outfit={}, scheme_result=None, garment_roles={},
            echo_bonus=0, scheme_strength=0.0, score=0.0,
            is_fallback=False, constraining_slot="socks",
        )
        sentinel_top = EvaluationResult(
            outfit={}, scheme_result=None, garment_roles={},
            echo_bonus=0, scheme_strength=0.0, score=0.0,
            is_fallback=False, constraining_slot="top",
        )
        assert render(sentinel_socks) != render(sentinel_top)

    def test_is_fallback_change_changes_text(self) -> None:
        """Setting is_fallback changes the output."""
        outfit = _outfit_from(neutral_fallback_only())
        result_normal = evaluate_outfit(outfit, is_fallback=False)
        result_fallback = evaluate_outfit(outfit, is_fallback=True)
        assert result_normal is not None
        assert result_fallback is not None
        assert render(result_normal) != render(result_fallback)


# ── Determinism ───────────────────────────────────────────────────────────────

class TestDeterminism:
    def test_same_result_same_text(self) -> None:
        """render is deterministic: calling twice returns identical text."""
        outfit = _outfit_from(single_valid_outfit())
        result = evaluate_outfit(outfit)
        assert result is not None
        assert render(result) == render(result)

    def test_same_result_same_text_with_echoes(self) -> None:
        outfit = {
            "base":       Garment("t_shirt",  (_red(100),)),
            "lower_body": Garment("trousers", (_teal(100),)),
            "socks":      Garment("socks",    (Colour(0.0, 80.0, 50.0, 87), Colour(180.0, 70.0, 50.0, 13))),
            "shoes":      Garment("shoes",    (_grey(100),)),
        }
        result = evaluate_outfit(outfit)
        assert result is not None
        assert render(result) == render(result)

    def test_determinism_neutral_fallback(self) -> None:
        outfit = _outfit_from(neutral_fallback_only())
        result = evaluate_outfit(outfit, is_fallback=True)
        assert result is not None
        assert render(result) == render(result)
