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

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.storage.engine import init_db, make_engine
from app.storage.models import GarmentColourRow, GarmentRow
from tests.fixtures.wardrobes import (
    neutral_fallback_only,
    no_valid_outfit_constrained_by,
    rich_echo_wardrobe,
    single_valid_outfit,
    two_valid_outfits,
)



# ── Wardrobe materialisation ──────────────────────────────────────────────────

def _materialise(engine, garments: list[Garment]) -> None:
    """Insert matcher Garment objects into the DB as GarmentRow/GarmentColourRow records."""
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
            for pos, c in enumerate(g.colours):
                from app.matcher.taxonomy import classify
                family = classify(c.h, c.s, c.l)
                s.add(GarmentColourRow(
                    garment_id=gid,
                    position=pos,
                    h=c.h,
                    s=c.s,
                    l=c.l,
                    family=family,
                    proportion=c.proportion,
                ))
        s.commit()


def _seed(client: TestClient, garments: list[Garment]) -> None:
    """Materialise garments into the client's engine."""
    _materialise(client.app.state.engine, garments)


# ── POST /api/suggestions — empty wardrobe / missing slot ─────────────────────

class TestEmptySlotsError:
    def test_empty_wardrobe_returns_409(self, api_client):
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 409
        body = r.json()
        assert body["error"]["code"] == "empty_slots"
        assert "empty_slots" in body["error"]["details"]

    def test_empty_slots_lists_missing_slot(self, api_client):
        # Only seed a top — bottom/socks/shoes are still empty.
        _seed(api_client, [Garment("top", (Colour(h=0.0, s=80.0, l=50.0, proportion=100),))])
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 409
        details = r.json()["error"]["details"]
        assert "bottom" in details["empty_slots"]

    def test_empty_optional_slot_409(self, api_client):
        """Requesting an include slot with no garments is a 409, not a 200 (FR-36)."""
        _seed(api_client, single_valid_outfit())
        r = api_client.post("/api/suggestions", json={"include": {"jersey": True}})
        assert r.status_code == 409
        assert "jersey" in r.json()["error"]["details"]["empty_slots"]


# ── POST /api/suggestions — invalid request ───────────────────────────────────

class TestInvalidRequest:
    def test_unknown_slot_key_422(self, api_client):
        r = api_client.post("/api/suggestions", json={"include": {"belt": True}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_multiple_unknown_keys_422(self, api_client):
        r = api_client.post("/api/suggestions", json={"include": {"belt": True, "scarf": True}})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_request"

    def test_required_slot_as_include_key_422(self, api_client):
        """Required slot keys must not appear in include — top is not optional."""
        r = api_client.post("/api/suggestions", json={"include": {"top": True}})
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

    def test_slots_contain_required_types(self, api_client):
        _seed(api_client, single_valid_outfit())
        slots = api_client.post("/api/suggestions", json={}).json()["combinations"][0]["slots"]
        for required in ("base", "lower_body", "socks", "shoes"):
            assert required in slots

    def test_slot_garment_summary_shape(self, api_client):
        _seed(api_client, single_valid_outfit())
        combo = api_client.post("/api/suggestions", json={}).json()["combinations"][0]
        garment = combo["slots"]["base"]
        assert "id" in garment
        assert "type" in garment
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
            Garment("top",    (Colour(h=0.0,   s=80.0, l=50.0, proportion=100),)),  # Red
            Garment("bottom", (Colour(h=180.0, s=70.0, l=50.0, proportion=100),)),  # Teal
            Garment("socks",  (
                Colour(h=230.0, s=40.0, l=18.0, proportion=90),   # Navy primary
                Colour(h=0.0,   s=80.0, l=50.0, proportion=10),   # Red minor → echoes anchor
            )),
            Garment("shoes",  (Colour(h=0.0, s=0.0, l=50.0, proportion=100),)),  # Grey
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
        _seed(api_client, no_valid_outfit_constrained_by("top"))
        r = api_client.post("/api/suggestions", json={})
        assert r.status_code == 200

    def test_zero_result_combinations_empty(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("top"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert body["combinations"] == []

    def test_zero_result_explanation_present(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("top"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert isinstance(body.get("explanation"), str)
        assert len(body["explanation"]) > 0

    def test_zero_result_hint_present(self, api_client):
        _seed(api_client, no_valid_outfit_constrained_by("top"))
        body = api_client.post("/api/suggestions", json={}).json()
        assert isinstance(body.get("hint"), str)
        assert len(body["hint"]) > 0


# ── POST /api/suggestions — optional slot inclusion ──────────────────────────

class TestOptionalSlots:
    def _jersey_wardrobe(self) -> list[Garment]:
        """
        All-neutral wardrobe with a jersey.  Fully neutral outfits always pass the
        scheme check (neutral-based) and the covered-layer check (FR-20 passes
        unconditionally when all anchor colours are neutral).
        """
        navy  = Colour(h=230.0, s=40.0, l=18.0, proportion=100)
        grey  = Colour(h=0.0,   s=0.0,  l=50.0, proportion=100)
        black = Colour(h=0.0,   s=0.0,  l= 6.0, proportion=100)
        white = Colour(h=0.0,   s=0.0,  l=96.0, proportion=100)
        return [
            Garment("jersey", (navy,)),
            Garment("top",    (grey,)),
            Garment("bottom", (black,)),
            Garment("socks",  (white,)),
            Garment("shoes",  (grey,)),
        ]

    def test_include_false_excludes_optional_slot(self, api_client):
        _seed(api_client, self._jersey_wardrobe())
        slots = api_client.post(
            "/api/suggestions", json={"include": {"jersey": False}}
        ).json()["combinations"][0]["slots"]
        assert "jersey" not in slots

    def test_omitted_include_key_defaults_false(self, api_client):
        """An include key not in the request body defaults to false (contract §2.12)."""
        _seed(api_client, self._jersey_wardrobe())
        slots = api_client.post("/api/suggestions", json={}).json()["combinations"][0]["slots"]
        assert "jersey" not in slots

    def test_include_true_adds_optional_slot(self, api_client):
        _seed(api_client, self._jersey_wardrobe())
        combos = api_client.post(
            "/api/suggestions", json={"include": {"jersey": True}}
        ).json()["combinations"]
        assert len(combos) >= 1
        slots = combos[0]["slots"]
        assert "mid" in slots
