"""
Tests for HUE-031: POST /api/suggestions endpoint
(contract §2.12, FR-17, FR-36–FR-43).

Strategy (§7.4 / §8.1):
- Wardrobes are inserted directly via GarmentRow/GarmentColourRow rather than
  through the upload flow, keeping tests fast and fixture-exact.
- FR-42-safe invariant pattern: assert structure (≤3 results, correct slots),
  not exact garment identity, since identical requests may legitimately differ.
- §4.9.4 oracle: for known engineered wardrobes, assert scheme/fallback/
  zero-result match the expected outcome derived from evaluate_outfit.
- Error paths: 409 empty_slots, 422 invalid_request.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.storage.models import GarmentRow
from tests.conftest import materialise_garments
from tests.fixtures.wardrobes import (
    neutral_fallback_only,
    no_valid_outfit_constrained_by,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
)


def _seed(client: TestClient, garments: list[Garment]) -> None:
    """Materialise garments into the client's engine with accurate family values."""
    materialise_garments(client.app.state.engine, garments, derive_families=True)


# ── POST /api/suggestions — empty wardrobe / missing slot ─────────────────────

class TestEmptySlotsError:
    def test_empty_wardrobe_returns_409(self, api_client):
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 409
        body = r.json()
        assert body["error"]["code"] == "empty_slots"
        assert "empty_slots" in body["error"]["details"]

    def test_empty_slots_lists_missing_slot(self, api_client):
        # Only seed a t_shirt (base slot) — lower_body/socks/shoes still empty.
        _seed(api_client, [Garment("t_shirt", (Colour(h=0.0, s=80.0, l=50.0, proportion=100),))])
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 409
        details = r.json()["error"]["details"]
        assert "lower_body" in details["empty_slots"]

    def test_empty_optional_slot_409(self, api_client):
        """Requesting an include slot with no garments is a 409, not a 200 (FR-36)."""
        _seed(api_client, single_valid_outfit())
        r = api_client.post("/api/suggestions", json={"slots": {"mid": True}})
        assert r.status_code == 409
        assert "mid" in r.json()["error"]["details"]["empty_slots"]


# ── POST /api/suggestions — invalid request ───────────────────────────────────

class TestInvalidRequest:
    def test_unknown_slot_key_422(self, api_client):
        r = api_client.post("/api/suggestions", json={"slots": {"dungarees": True}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_multiple_unknown_keys_422(self, api_client):
        r = api_client.post("/api/suggestions", json={"slots": {"dungarees": True, "kilt": True}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_deselect_mandatory_slot_422(self, api_client):
        """Deselecting the mandatory slot (lower_body) is a 422 invalid_request (FR-51.2)."""
        r = api_client.post("/api/suggestions", json={"slots": {"lower_body": False}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"


# ── POST /api/suggestions — found: response structure ─────────────────────────

class TestSuggestionFound:
    def test_returns_200(self, api_client):
        _seed(api_client, single_valid_outfit())
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 200

    def test_combinations_non_empty(self, api_client):
        _seed(api_client, single_valid_outfit())
        body = api_client.post("/api/suggestions", json={}).json()
        assert len(body["combinations"]) >= 1

    def test_at_most_three_combinations(self, api_client):
        _seed(api_client, two_valid_outfits())
        body = api_client.post("/api/suggestions", json={}).json()
        assert len(body["combinations"]) <= 3

    def test_combination_shape(self, api_client):
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert "rank" in combo
        assert "scheme" in combo
        assert "fallback" in combo
        assert "slots" in combo
        assert "echoes" in combo
        assert "explanation" in combo

    def test_rank_starts_at_1(self, api_client):
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert combo["rank"] == 1

    def test_slots_contain_required_slots(self, api_client):
        _seed(api_client, single_valid_outfit())
        slots = api_client.post("/api/suggestions", json={}).json()["combinations"][0]["slots"]
        for required in ("base", "lower_body", "socks", "shoes"):
            assert required in slots

    def test_slot_garment_summary_shape(self, api_client):
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        garment = combo["slots"]["base"]
        assert "id" in garment
        assert "category" in garment
        assert "colours" in garment
        assert "thumbnail_url" in garment
        assert "image_url" not in garment  # GarmentSummary, not detail

    def test_explanation_is_non_empty_string(self, api_client):
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert isinstance(combo["explanation"], str)
        assert len(combo["explanation"]) > 0

    def test_zero_result_fields_absent_on_success(self, api_client):
        """explanation and hint at top level must be absent (or null) when combinations found."""
        _seed(api_client, single_valid_outfit())
        body = api_client.post("/api/suggestions", json={}).json()
        assert body.get("explanation") is None
        assert body.get("hint") is None

    def test_combinations_ranked_in_order(self, api_client):
        _seed(api_client, two_valid_outfits())
        combos = api_client.post("/api/suggestions", json={}).json()["combinations"]
        ranks = [c["rank"] for c in combos]
        assert ranks == sorted(ranks)


# ── POST /api/suggestions — §4.9.4 oracle: known-wardrobe scheme assertions ───

class TestSchemeOracle:
    def test_single_valid_outfit_scheme_is_complementary(self, api_client):
        """single_valid_outfit: Red top + Teal bottom → complementary (180° apart)."""
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert combo["scheme"] == "complementary"
        assert combo["fallback"] is False

    def test_neutral_wardrobe_scheme_and_fallback_flag(self, api_client):
        """
        neutral_fallback_only: all anchors neutral → neutral-based scheme via the
        normal evaluation path (evaluate_scheme returns neutral-based for an empty
        scheme set), so fallback=False.  The fallback ladder is only entered when the
        normal path finds zero valid chromatic outfits.
        """
        _seed(api_client, neutral_fallback_only())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert combo["scheme"] == "neutral-based"
        assert combo["fallback"] is False

    def test_echo_wardrobe_includes_echo_records(self, api_client):
        """
        Wardrobe where socks have a MINOR colour (Red) that echoes an anchor chromatic.
        socks: Navy primary (80%) + Red minor (20%) → minor_echo for Red → echo record.
        """
        # Build the wardrobe inline so we control the exact minor-colour proportion.
        # Minor requires proportion < SECONDARY_THRESHOLD (15); use 90/10 split.
        garments = [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("socks",    (
                Colour(h=230.0, s=40.0, l=18.0, proportion=90),   # Navy primary
                Colour(h=0.0,   s=80.0, l=50.0, proportion=10),   # Red minor → echoes anchor
            )),
            Garment("shoes",    (Colour(h=0.0, s=0.0, l=50.0, proportion=100),)),  # Grey
        ]
        _seed(api_client, garments)
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        assert len(combo["echoes"]) >= 1
        echo = combo["echoes"][0]
        assert "family" in echo
        assert "from_slot" in echo
        assert "to_slot" in echo


# ── POST /api/suggestions — zero result ──────────────────────────────────────

class TestZeroResult:
    def test_zero_result_returns_200(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 200

    def test_zero_result_combinations_empty(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert body["combinations"] == []

    def test_zero_result_explanation_present(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert isinstance(body.get("explanation"), str)
        assert len(body["explanation"]) > 0

    def test_zero_result_hint_present(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert isinstance(body.get("hint"), str)
        assert len(body["hint"]) > 0


# ── POST /api/suggestions — optional slot inclusion ──────────────────────────

class TestOptionalSlots:
    def _mid_wardrobe(self) -> list[Garment]:
        """
        All-neutral wardrobe with a mid-layer (jumper).  Fully neutral outfits always
        pass the scheme check (neutral-based) and the covered-layer check (FR-20 passes
        unconditionally when all anchor colours are neutral).
        """
        navy  = Colour(h=230.0, s=40.0, l=18.0, proportion=100)
        grey  = Colour(h=0.0,   s=0.0,  l=50.0, proportion=100)
        black = Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100)
        white = Colour(h=0.0,   s=0.0,  l=96.0, proportion=100)
        return [
            Garment("jumper",   (navy,)),
            Garment("t_shirt",  (grey,)),
            Garment("trousers", (black,)),
            Garment("socks",    (white,)),
            Garment("shoes",    (grey,)),
        ]

    def test_slots_false_excludes_optional_slot(self, api_client):
        _seed(api_client, self._mid_wardrobe())
        slots = api_client.post(
            "/api/suggestions", json={"slots": {"mid": False}}
        ).json()["combinations"][0]["slots"]
        assert "mid" not in slots

    def test_omitted_slots_key_defaults_false(self, api_client):
        """A slot key not in the request body defaults to false (contract §2.12)."""
        _seed(api_client, self._mid_wardrobe())
        slots = api_client.post("/api/suggestions", json={}).json()["combinations"][0]["slots"]
        assert "mid" not in slots

    def test_slots_true_adds_optional_slot(self, api_client):
        _seed(api_client, self._mid_wardrobe())
        combos = api_client.post(
            "/api/suggestions", json={"slots": {"mid": True}}
        ).json()["combinations"]
        assert len(combos) >= 1
        slots = combos[0]["slots"]
        assert "mid" in slots


# ── POST /api/suggestions — count field (FR-39, FR-48) ───────────────────────

class TestCountField:
    def test_count_default_requested_count_is_three(self, api_client):
        """FR-48: omitting count echoes requested_count=3 in the response."""
        _seed(api_client, single_valid_outfit())
        body = api_client.post("/api/suggestions", json={}).json()
        assert body["requested_count"] == 3

    def test_count_echoed_in_requested_count(self, api_client):
        """FR-48: explicit count is echoed back as requested_count."""
        _seed(api_client, single_valid_outfit())
        body = api_client.post("/api/suggestions", json={"count": 1}).json()
        assert body["requested_count"] == 1

    def test_count_one_limits_combinations_to_one(self, api_client):
        """FR-39: count=1 returns exactly 1 combination even with two available."""
        _seed(api_client, two_valid_outfits())
        body = api_client.post("/api/suggestions", json={"count": 1}).json()
        assert len(body["combinations"]) == 1

    def test_count_zero_returns_422(self, api_client):
        """count=0 is out of range (1–25); must return 422 invalid_request."""
        r = api_client.post("/api/suggestions", json={"count": 0})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_count_26_returns_422(self, api_client):
        """count=26 is out of range (1–25); must return 422 invalid_request."""
        r = api_client.post("/api/suggestions", json={"count": 26})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_count_error_details_include_value(self, api_client):
        """Error details must include the submitted count value (contract §2.12)."""
        r = api_client.post("/api/suggestions", json={"count": 26})
        assert r.json()["error"]["details"]["count"] == 26

    def test_count_25_accepted(self, api_client):
        """count=25 is in range and must return 200."""
        _seed(api_client, single_valid_outfit())
        r = api_client.post("/api/suggestions", json={"count": 25})
        assert r.status_code == 200

    def test_zero_result_requested_count_echoed(self, api_client):
        """requested_count is present even in the zero-result response."""
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        body = api_client.post("/api/suggestions", json={"count": 2}).json()
        assert body["combinations"] == []
        assert body["requested_count"] == 2


# ── POST /api/suggestions — pins (FR-44) ─────────────────────────────────────

def _first_id_of_type(engine, garment_type: str) -> str:
    """Return the DB id of the first garment with the given type."""
    with Session(engine) as s:
        row = s.exec(select(GarmentRow).where(GarmentRow.type == garment_type)).first()
    assert row is not None, f"No garment of type {garment_type!r}"
    return row.id


class TestPinsField:
    def test_pin_honoured_in_every_combination(self, api_client):
        """FR-44: the pinned garment appears in its slot in every returned combination."""
        _seed(api_client, two_valid_outfits())
        pinned_id = _first_id_of_type(api_client.app.state.engine, "t_shirt")
        body = api_client.post("/api/suggestions", json={"pins": {"base": pinned_id}}).json()
        assert body["combinations"], "Expected at least one combination"
        for combo in body["combinations"]:
            assert combo["slots"]["base"]["id"] == pinned_id

    def test_pin_unknown_slot_422(self, api_client):
        """FR-44: unknown slot key in pins → 422 invalid_request."""
        r = api_client.post("/api/suggestions", json={"pins": {"nonexistent": "some-id"}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_pin_garment_not_found_422(self, api_client):
        """FR-44: garment ID that does not exist → 422 invalid_request."""
        _seed(api_client, single_valid_outfit())
        r = api_client.post(
            "/api/suggestions",
            json={"pins": {"base": "00000000-0000-0000-0000-000000000000"}},
        )
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_pin_wrong_slot_422(self, api_client):
        """FR-44: garment category does not map to pinned slot → 422."""
        _seed(api_client, single_valid_outfit())
        trousers_id = _first_id_of_type(api_client.app.state.engine, "trousers")
        r = api_client.post("/api/suggestions", json={"pins": {"base": trousers_id}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_pin_constraint_conflict_422(self, api_client):
        """FR-44+FR-52: pin's category not in same-slot constraint → 422."""
        _seed(api_client, [
            Garment("t_shirt",  (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("jeans",    (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),
            Garment("socks",    (Colour(h=0.0,   s=0.0,  l=50.0, proportion=100),)),
            Garment("shoes",    (Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100),)),
        ])
        trousers_id = _first_id_of_type(api_client.app.state.engine, "trousers")
        r = api_client.post("/api/suggestions", json={
            "slots": {"lower_body": {"categories": ["jeans"]}},
            "pins": {"lower_body": trousers_id},
        })
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_pin_unsatisfiable_returns_zero_result(self, api_client):
        """FR-44: pin that makes no valid outfit → 200 zero-result shape."""
        _seed(api_client, no_valid_outfit_constrained_by("base"))
        # Pin the t_shirt that makes no valid outfit with the existing wardrobe
        tshirt_id = _first_id_of_type(api_client.app.state.engine, "t_shirt")
        r = api_client.post("/api/suggestions", json={"pins": {"base": tshirt_id}})
        assert r.status_code == 200
        body = r.json()
        assert body["combinations"] == []
        assert body.get("explanation") is not None


# ── POST /api/suggestions — anchor (FR-45) ───────────────────────────────────

class TestAnchorField:
    def test_anchor_scheme_filters_combinations(self, api_client):
        """FR-45: anchor scheme keeps only combos matching that scheme."""
        _seed(api_client, single_valid_outfit())
        body = api_client.post(
            "/api/suggestions", json={"anchor": {"scheme": "complementary"}}
        ).json()
        assert len(body["combinations"]) >= 1
        for combo in body["combinations"]:
            assert combo["scheme"] == "complementary"

    def test_anchor_scheme_no_match_zero_result(self, api_client):
        """FR-45: anchor scheme with no matching combination → 200 zero-result."""
        _seed(api_client, single_valid_outfit())
        body = api_client.post(
            "/api/suggestions", json={"anchor": {"scheme": "monochromatic"}}
        ).json()
        assert body["combinations"] == []
        assert body.get("explanation") is not None

    def test_anchor_family_filters_combinations(self, api_client):
        """FR-45: pre-filter keeps anchor garments that carry the family."""
        # All anchor garments are Red so the pre-filter keeps them.
        _seed(api_client, [
            Garment("t_shirt",  (Colour(h=  0.0, s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("trousers", (Colour(h=  0.0, s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("socks",    (Colour(h=  0.0, s= 0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=  0.0, s= 0.0, l= 6.0, proportion=100),)),  # Black
        ])
        body = api_client.post(
            "/api/suggestions", json={"anchor": {"family": "Red"}}
        ).json()
        assert len(body["combinations"]) >= 1

    def test_anchor_family_no_match_409(self, api_client):
        """FR-45: pre-filter removes all anchor garments → 409 empty_slots."""
        _seed(api_client, single_valid_outfit())  # Red t_shirt + Teal trousers
        r = api_client.post(
            "/api/suggestions", json={"anchor": {"family": "Blue"}}
        )
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "empty_slots"

    def test_anchor_unknown_family_422(self, api_client):
        """FR-45: unknown anchor family name → 422 invalid_request."""
        r = api_client.post("/api/suggestions", json={"anchor": {"family": "Ultraviolet"}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_anchor_unknown_scheme_422(self, api_client):
        """FR-45: unknown anchor scheme name → 422 invalid_request."""
        r = api_client.post("/api/suggestions", json={"anchor": {"scheme": "tetrachromatic"}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_anchor_both_compose(self, api_client):
        """FR-45: family pre-filter + scheme post-filter both apply."""
        # All-Teal anchors → monochromatic scheme; complementary won't match.
        _seed(api_client, [
            Garment("t_shirt",  (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("trousers", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("socks",    (Colour(h=  0.0, s= 0.0, l=50.0, proportion=100),)),  # Grey
            Garment("shoes",    (Colour(h=  0.0, s= 0.0, l= 6.0, proportion=100),)),  # Black
        ])
        body = api_client.post(
            "/api/suggestions",
            json={"anchor": {"family": "Teal", "scheme": "monochromatic"}},
        ).json()
        assert len(body["combinations"]) >= 1
        body2 = api_client.post(
            "/api/suggestions",
            json={"anchor": {"family": "Teal", "scheme": "complementary"}},
        ).json()
        assert body2["combinations"] == []
