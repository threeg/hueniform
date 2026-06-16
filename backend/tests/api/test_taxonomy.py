"""
Tests for HUE-026: GET /api/taxonomy (contract §2.2).

Strategy (§7.2 contract tests): TestClient against the real app factory;
canonical self-classification verified directly against matcher.taxonomy.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import Settings, create_app
from app.matcher.taxonomy import classify


@pytest.fixture()
def client(tmp_path):
    settings = Settings(
        data_dir=tmp_path / "data",
        spa_dir=tmp_path / "no-spa",
    )
    return TestClient(create_app(settings))


@pytest.fixture()
def families(client):
    r = client.get("/api/taxonomy")
    assert r.status_code == 200
    return r.json()["families"]


# ── Response shape ────────────────────────────────────────────────────────────

class TestResponseShape:
    def test_status_200(self, client):
        assert client.get("/api/taxonomy").status_code == 200

    def test_top_level_key(self, client):
        assert "families" in client.get("/api/taxonomy").json()

    def test_nineteen_families(self, families):
        assert len(families) == 19

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

    def test_seven_neutral_families(self, families):
        assert sum(1 for f in families if f["neutral"]) == 7


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
