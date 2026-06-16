"""
Tests for HUE-028: POST /api/garments (contract §2.5, FR-6, FR-25, FR-29–FR-31).

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
