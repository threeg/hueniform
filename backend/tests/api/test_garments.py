"""
Tests for HUE-028/HUE-029: garment create and read endpoints
(contract §2.5–§2.8, FR-6, FR-25, FR-29–FR-31, FR-35).

Strategy (§7.2 contract tests): TestClient with lifespan (context-manager form)
so the engine and data directories are initialised.  Successful saves exercise
the real garment service; error paths need only a valid staged entry.
"""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import Settings, create_app
from app.matcher.taxonomy import classify
from app.storage import staging


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tiny_jpeg() -> bytes:
    """Return a minimal valid JPEG that Pillow and the thumbnail generator accept."""
    buf = BytesIO()
    Image.new("RGB", (8, 8), (180, 90, 45)).save(buf, format="JPEG")
    return buf.getvalue()


def _stage(settings: Settings, data: bytes = b"") -> str:
    """Stage *data* (defaulting to a tiny JPEG) and return the token."""
    return staging.stage(
        data=data or _tiny_jpeg(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={"colours": [{"h": 0, "s": 50, "l": 50, "proportion": 100}]},
        staging_dir=settings.data_dir / "staging",
    )


def _create_body(token: str, garment_type: str = "top", colours: list | None = None) -> dict:
    if colours is None:
        colours = [{"h": 210.0, "s": 60.0, "l": 50.0, "proportion": 100}]
    return {"detection_token": token, "type": garment_type, "colours": colours}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def settings(tmp_path):
    return Settings(data_dir=tmp_path / "data", spa_dir=tmp_path / "no-spa")


@pytest.fixture()
def client(settings):
    with TestClient(create_app(settings)) as c:
        yield c


# ── POST /api/garments — success ──────────────────────────────────────────────

class TestCreateGarmentSuccess:
    def test_status_201(self, client, settings):
        token = _stage(settings)
        r = client.post("/api/garments", json=_create_body(token))
        assert r.status_code == 201

    def test_id_is_present(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        assert "id" in body
        assert len(body["id"]) == 36  # UUID4 string

    def test_type_matches_request(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token, "jersey")).json()
        assert body["type"] == "jersey"

    def test_colours_present(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        assert len(body["colours"]) == 1
        c = body["colours"][0]
        assert "h" in c and "s" in c and "l" in c
        assert "family" in c and "neutral" in c and "hex" in c and "proportion" in c

    def test_server_derives_family(self, client, settings):
        """Server must derive family from submitted HSL, not trust any implied value (FR-1)."""
        h, s, l = 174.0, 58.0, 41.0
        token = _stage(settings)
        body = client.post(
            "/api/garments",
            json=_create_body(token, colours=[{"h": h, "s": s, "l": l, "proportion": 100}]),
        ).json()
        expected_family = classify(h, s, l)
        assert body["colours"][0]["family"] == expected_family

    def test_thumbnail_url_format(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        garment_id = body["id"]
        assert body["thumbnail_url"] == f"/api/garments/{garment_id}/thumbnail"

    def test_image_url_format(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        garment_id = body["id"]
        assert body["image_url"] == f"/api/garments/{garment_id}/image"

    def test_created_at_present(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        assert "created_at" in body
        assert body["created_at"]  # non-empty string

    def test_regenerated_at_is_none(self, client, settings):
        token = _stage(settings)
        body = client.post("/api/garments", json=_create_body(token)).json()
        assert body["regenerated_at"] is None

    def test_token_consumed_on_success(self, client, settings):
        token = _stage(settings)
        client.post("/api/garments", json=_create_body(token))
        # Second call with the same token must return 404.
        r2 = client.post("/api/garments", json=_create_body(token))
        assert r2.status_code == 404
        assert r2.json()["error"]["code"] == "detection_not_found"

    def test_multi_colour_palette(self, client, settings):
        token = _stage(settings)
        colours = [
            {"h": 0.0,   "s": 80.0, "l": 50.0, "proportion": 60},
            {"h": 120.0, "s": 60.0, "l": 40.0, "proportion": 40},
        ]
        body = client.post("/api/garments", json=_create_body(token, colours=colours)).json()
        assert len(body["colours"]) == 2


# ── POST /api/garments — palette validation errors ────────────────────────────

class TestPaletteErrors:
    def test_zero_colours(self, client, settings):
        token = _stage(settings)
        r = client.post("/api/garments", json=_create_body(token, colours=[]))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_five_colours(self, client, settings):
        token = _stage(settings)
        colours = [{"h": float(i * 60), "s": 50.0, "l": 50.0, "proportion": 20} for i in range(5)]
        r = client.post("/api/garments", json=_create_body(token, colours=colours))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_proportions_not_summing_to_100(self, client, settings):
        token = _stage(settings)
        colours = [
            {"h": 0.0,   "s": 50.0, "l": 50.0, "proportion": 60},
            {"h": 120.0, "s": 50.0, "l": 50.0, "proportion": 30},
        ]
        r = client.post("/api/garments", json=_create_body(token, colours=colours))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_palette_error_does_not_consume_token(self, client, settings):
        token = _stage(settings)
        # Bad payload — proportions don't sum to 100.
        bad_colours = [{"h": 0.0, "s": 50.0, "l": 50.0, "proportion": 50}]
        client.post("/api/garments", json=_create_body(token, colours=bad_colours))
        # Token must still be live for a valid retry.
        r2 = client.post("/api/garments", json=_create_body(token))
        assert r2.status_code == 201


# ── POST /api/garments — type validation errors ───────────────────────────────

class TestTypeErrors:
    def test_unknown_type_returns_422(self, client, settings):
        token = _stage(settings)
        r = client.post("/api/garments", json=_create_body(token, garment_type="jumpsuit"))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_type"


# ── POST /api/garments — token errors ────────────────────────────────────────

class TestTokenErrors:
    def test_unknown_token_404(self, client):
        r = client.post("/api/garments", json=_create_body("no-such-token"))
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "detection_not_found"


# ── Seeded wardrobe fixture ───────────────────────────────────────────────────
#
# Creates three garments:
#   g_top    — type=top,    primary=Blue  (h=240, s=70, l=50)
#   g_bottom — type=bottom, primary=Red   (h=0,   s=80, l=50)
#   g_jersey — type=jersey, Red 80% + Blue 20% (Blue is a minor role)

def _save(client: object, settings: Settings, garment_type: str, colours: list) -> dict:
    token = _stage(settings)
    r = client.post("/api/garments", json=_create_body(token, garment_type, colours))
    assert r.status_code == 201, r.json()
    return r.json()


_BLUE_COLOUR  = [{"h": 240.0, "s": 70.0, "l": 50.0, "proportion": 100}]
_RED_COLOUR   = [{"h":   0.0, "s": 80.0, "l": 50.0, "proportion": 100}]
_RED_BLUE_COLOURS = [
    {"h":   0.0, "s": 80.0, "l": 50.0, "proportion": 80},
    {"h": 240.0, "s": 70.0, "l": 50.0, "proportion": 20},
]


@pytest.fixture()
def seeded(client, settings):
    g_top    = _save(client, settings, "top",    _BLUE_COLOUR)
    g_bottom = _save(client, settings, "bottom", _RED_COLOUR)
    g_jersey = _save(client, settings, "jersey", _RED_BLUE_COLOURS)
    return {"top": g_top, "bottom": g_bottom, "jersey": g_jersey}


# ── GET /api/garments — list ──────────────────────────────────────────────────

class TestListGarments:
    def test_empty_returns_empty_list(self, client):
        r = client.get("/api/garments")
        assert r.status_code == 200
        body = r.json()
        assert body["garments"] == []
        assert body["total"] == 0

    def test_total_matches_garment_count(self, client, seeded):
        body = client.get("/api/garments").json()
        assert body["total"] == 3
        assert len(body["garments"]) == 3

    def test_summary_shape(self, client, seeded):
        garment = client.get("/api/garments").json()["garments"][0]
        assert "id" in garment
        assert "type" in garment
        assert "colours" in garment
        assert "thumbnail_url" in garment
        assert "image_url" not in garment  # GarmentSummary, not detail

    def test_type_filter(self, client, seeded):
        body = client.get("/api/garments", params={"type": "top"}).json()
        assert body["total"] == 1
        assert body["garments"][0]["type"] == "top"

    def test_family_filter_matches_primary_colour(self, client, seeded):
        # Blue is primary in the top.
        body = client.get("/api/garments", params={"family": "Blue"}).json()
        assert body["total"] == 2  # top (primary Blue) + jersey (minor Blue)
        ids = {g["id"] for g in body["garments"]}
        assert seeded["top"]["id"] in ids
        assert seeded["jersey"]["id"] in ids

    def test_family_filter_matches_minor_role(self, client, seeded):
        # jersey has Blue as a 20 % minor colour — must still match.
        body = client.get("/api/garments", params={"family": "Blue"}).json()
        ids = {g["id"] for g in body["garments"]}
        assert seeded["jersey"]["id"] in ids

    def test_family_filter_red(self, client, seeded):
        body = client.get("/api/garments", params={"family": "Red"}).json()
        assert body["total"] == 2  # bottom + jersey
        ids = {g["id"] for g in body["garments"]}
        assert seeded["bottom"]["id"] in ids
        assert seeded["jersey"]["id"] in ids

    def test_type_and_family_combined_match(self, client, seeded):
        # jersey type AND Blue family → 1 result
        body = client.get("/api/garments", params={"type": "jersey", "family": "Blue"}).json()
        assert body["total"] == 1
        assert body["garments"][0]["id"] == seeded["jersey"]["id"]

    def test_type_and_family_combined_no_match(self, client, seeded):
        # bottom type AND Blue family → 0 results (bottom is Red only)
        body = client.get("/api/garments", params={"type": "bottom", "family": "Blue"}).json()
        assert body["total"] == 0
        assert body["garments"] == []

    def test_limit_reduces_page(self, client, seeded):
        body = client.get("/api/garments", params={"limit": 2}).json()
        assert len(body["garments"]) == 2
        assert body["total"] == 3  # total unchanged

    def test_offset_pages_results(self, client, seeded):
        first  = client.get("/api/garments", params={"limit": 2, "offset": 0}).json()
        second = client.get("/api/garments", params={"limit": 2, "offset": 2}).json()
        assert len(first["garments"]) == 2
        assert len(second["garments"]) == 1
        ids_first  = {g["id"] for g in first["garments"]}
        ids_second = {g["id"] for g in second["garments"]}
        assert ids_first.isdisjoint(ids_second)

    def test_total_unchanged_under_paging(self, client, seeded):
        body = client.get("/api/garments", params={"limit": 1, "offset": 2}).json()
        assert body["total"] == 3

    def test_invalid_type_422(self, client):
        r = client.get("/api/garments", params={"type": "onesie"})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_filter"

    def test_invalid_family_422(self, client):
        r = client.get("/api/garments", params={"family": "Khaki"})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_filter"


# ── GET /api/garments/{id} — detail ──────────────────────────────────────────

class TestGetGarmentDetail:
    def test_returns_full_detail(self, client, seeded):
        garment_id = seeded["top"]["id"]
        body = client.get(f"/api/garments/{garment_id}").json()
        assert body["id"] == garment_id
        assert body["type"] == "top"
        assert "image_url" in body
        assert "thumbnail_url" in body
        assert "created_at" in body
        assert "regenerated_at" in body

    def test_unknown_id_404(self, client):
        r = client.get("/api/garments/no-such-id")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"


# ── GET /api/garments/{id}/image and /thumbnail ───────────────────────────────

class TestGarmentFiles:
    def test_image_serves_binary(self, client, seeded):
        garment_id = seeded["top"]["id"]
        r = client.get(f"/api/garments/{garment_id}/image")
        assert r.status_code == 200
        assert len(r.content) > 0

    def test_thumbnail_serves_binary(self, client, seeded):
        garment_id = seeded["top"]["id"]
        r = client.get(f"/api/garments/{garment_id}/thumbnail")
        assert r.status_code == 200
        assert len(r.content) > 0

    def test_image_not_found_404(self, client):
        r = client.get("/api/garments/no-such-id/image")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_thumbnail_not_found_404(self, client):
        r = client.get("/api/garments/no-such-id/thumbnail")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"
