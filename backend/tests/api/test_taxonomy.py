"""
Tests for HUE-026: GET /api/taxonomy (contract §2.2).

Strategy (§7.2 contract tests): TestClient against the real app factory;
canonical self-classification verified directly against matcher.taxonomy.
"""

from __future__ import annotations

import pytest

from app.matcher.taxonomy import classify


@pytest.fixture()
def families(api_client):
    r = api_client.get("/api/taxonomy")
    assert r.status_code == 200
    return r.json()["families"]


# ── Response shape ────────────────────────────────────────────────────────────

class TestResponseShape:
    def test_status_200(self, api_client):
        assert api_client.get("/api/taxonomy").status_code == 200

    def test_top_level_key(self, api_client):
        assert "families" in api_client.get("/api/taxonomy").json()

    def test_twenty_families(self, families):
        assert len(families) == 20

    def test_each_family_has_name(self, families):
        for fam in families:
            assert "name" in fam
            assert isinstance(fam["name"], str)

    def test_each_family_has_neutral(self, families):
        for fam in families:
            assert "neutral" in fam
            assert isinstance(fam["neutral"], bool)

    def test_each_family_has_canonical(self, families):
        for fam in families:
            assert "canonical" in fam
            c = fam["canonical"]
            assert "h" in c and "s" in c and "l" in c


# ── Chromatic families: representative_hue and hue_arc present ───────────────

class TestChromaticFields:
    def test_chromatic_families_have_representative_hue(self, families):
        for fam in families:
            if not fam["neutral"]:
                assert "representative_hue" in fam, (
                    f"{fam['name']} is chromatic but missing representative_hue"
                )

    def test_chromatic_families_have_hue_arc(self, families):
        for fam in families:
            if not fam["neutral"]:
                assert "hue_arc" in fam, (
                    f"{fam['name']} is chromatic but missing hue_arc"
                )
                assert len(fam["hue_arc"]) == 2

    def test_neutral_families_have_no_representative_hue(self, families):
        for fam in families:
            if fam["neutral"]:
                assert "representative_hue" not in fam, (
                    f"{fam['name']} is neutral but has representative_hue"
                )

    def test_neutral_families_have_no_hue_arc(self, families):
        for fam in families:
            if fam["neutral"]:
                assert "hue_arc" not in fam, (
                    f"{fam['name']} is neutral but has hue_arc"
                )

    def test_twelve_chromatic_families(self, families):
        assert sum(1 for f in families if not f["neutral"]) == 12

    def test_eight_neutral_families(self, families):
        assert sum(1 for f in families if f["neutral"]) == 8


# ── Canonical self-classification invariant (contract §2.2) ──────────────────

class TestCanonicalSelfClassifies:
    def test_each_canonical_classifies_into_own_family(self, families):
        """
        Contract §2.2: each canonical HSL must classify back into its own family
        when passed to matcher.taxonomy.classify.
        """
        for fam in families:
            c = fam["canonical"]
            derived = classify(c["h"], c["s"], c["l"])
            assert derived == fam["name"], (
                f"canonical {c} for {fam['name']} classifies as {derived!r}"
            )


# ── GET /api/taxonomy — regions (contract §2.2, FR-16, FR-49–FR-51) ──────────

@pytest.fixture()
def regions(api_client):
    r = api_client.get("/api/taxonomy")
    assert r.status_code == 200
    return r.json()["regions"]


def _all_slots(regions: list) -> list:
    return [s for r in regions for s in r["slots"]]


class TestRegionsStructure:
    def test_regions_key_present(self, api_client):
        assert "regions" in api_client.get("/api/taxonomy").json()

    def test_four_regions(self, regions):
        assert len(regions) == 4

    def test_region_keys(self, regions):
        keys = [r["region"] for r in regions]
        assert keys == ["head", "upper_body", "lower_body", "feet"]

    def test_seventeen_slots_total(self, regions):
        assert len(_all_slots(regions)) == 17

    def test_each_slot_has_required_fields(self, regions):
        required = {"slot", "label", "categories", "role", "default_selected"}
        for slot in _all_slots(regions):
            assert required <= slot.keys(), f"slot {slot['slot']} missing fields"

    def test_each_slot_categories_nonempty(self, regions):
        for slot in _all_slots(regions):
            assert len(slot["categories"]) >= 1, f"slot {slot['slot']} has empty categories"

    def test_role_values(self, regions):
        for slot in _all_slots(regions):
            assert slot["role"] in {"anchor", "statement", "minor"}, (
                f"slot {slot['slot']} has unexpected role {slot['role']!r}"
            )


class TestRegionsLayerOrder:
    def test_layer_order_only_on_four_upper_body_anchors(self, regions):
        upper_slots = next(r["slots"] for r in regions if r["region"] == "upper_body")
        layer_slots = {s["slot"] for s in upper_slots if "layer_order" in s}
        assert layer_slots == {"base", "shirt", "mid", "outer"}

    def test_layer_order_absent_elsewhere(self, regions):
        for slot in _all_slots(regions):
            if slot["slot"] not in {"base", "shirt", "mid", "outer"}:
                assert "layer_order" not in slot, (
                    f"layer_order unexpectedly present on {slot['slot']}"
                )

    def test_layer_order_values(self, regions):
        upper_slots = next(r["slots"] for r in regions if r["region"] == "upper_body")
        orders = {s["slot"]: s["layer_order"] for s in upper_slots if "layer_order" in s}
        assert orders == {"base": 0, "shirt": 1, "mid": 2, "outer": 3}


class TestRegionsMandatoryAndDefault:
    def test_mandatory_only_on_lower_body(self, regions):
        for slot in _all_slots(regions):
            if slot["slot"] == "lower_body":
                assert slot.get("mandatory") is True
            else:
                assert "mandatory" not in slot, (
                    f"mandatory unexpectedly present on {slot['slot']}"
                )

    def test_default_selected_slots(self, regions):
        selected = {s["slot"] for s in _all_slots(regions) if s["default_selected"]}
        assert selected == {"base", "lower_body", "socks", "shoes"}


class TestRegionsOnePiece:
    def test_one_piece_fields_only_on_lower_body(self, regions):
        for slot in _all_slots(regions):
            if slot["slot"] == "lower_body":
                assert "one_piece_categories" in slot
                assert "one_piece_also_occupies" in slot
            else:
                assert "one_piece_categories" not in slot
                assert "one_piece_also_occupies" not in slot

    def test_one_piece_categories_content(self, regions):
        lower = next(s for r in regions for s in r["slots"] if s["slot"] == "lower_body")
        assert set(lower["one_piece_categories"]) == {"dress", "jumpsuit"}

    def test_one_piece_also_occupies_base(self, regions):
        lower = next(s for r in regions for s in r["slots"] if s["slot"] == "lower_body")
        assert lower["one_piece_also_occupies"] == ["base"]


class TestRegionsSlotContent:
    def test_mid_slot_categories(self, regions):
        upper = next(r["slots"] for r in regions if r["region"] == "upper_body")
        mid = next(s for s in upper if s["slot"] == "mid")
        assert set(mid["categories"]) == {"jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat"}

    def test_outer_slot_categories(self, regions):
        upper = next(r["slots"] for r in regions if r["region"] == "upper_body")
        outer = next(s for s in upper if s["slot"] == "outer")
        assert set(outer["categories"]) == {"jacket", "blazer", "coat"}

    def test_lower_body_slot_categories(self, regions):
        lower_region = next(r for r in regions if r["region"] == "lower_body")
        lb = next(s for s in lower_region["slots"] if s["slot"] == "lower_body")
        assert set(lb["categories"]) == {"trousers", "jeans", "chinos", "shorts", "skirt", "dress", "jumpsuit"}

    def test_shoes_slot_categories(self, regions):
        feet = next(r["slots"] for r in regions if r["region"] == "feet")
        shoes = next(s for s in feet if s["slot"] == "shoes")
        assert set(shoes["categories"]) == {"shoes", "boots", "trainers", "sandals"}
