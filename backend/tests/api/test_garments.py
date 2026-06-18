"""
Tests for HUE-028/HUE-029/HUE-030: garment CRUD and regeneration endpoints
(contract §2.5–§2.11, FR-6, FR-25, FR-29–FR-35).

Strategy (§7.2 contract tests): TestClient with lifespan (context-manager form)
so the engine and data directories are initialised.  Successful saves exercise
the real garment service; error paths need only a valid staged entry.
POST /api/garments/{id}/regenerate mocks ``run_regeneration`` to avoid loading
the rembg model.  PUT tests create staging tokens directly via ``staging.stage``
with a ``garment_id`` binding, bypassing the detection pipeline.
"""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from unittest.mock import patch

from app.matcher.taxonomy import classify
from app.services.detection_service import ColourProposal, DetectionResult
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



# ── POST /api/garments — success ──────────────────────────────────────────────

class TestCreateGarmentSuccess:
    def test_status_201(self, api_client, api_settings):
        token = _stage(api_settings)
        r = api_client.post("/api/garments", json=_create_body(token))
        assert r.status_code == 201

    def test_id_is_present(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        assert "id" in body
        assert len(body["id"]) == 36  # UUID4 string

    def test_type_matches_request(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token, "jersey")).json()
        assert body["type"] == "jersey"

    def test_colours_present(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        assert len(body["colours"]) == 1
        c = body["colours"][0]
        assert "h" in c and "s" in c and "l" in c
        assert "family" in c and "neutral" in c and "hex" in c and "proportion" in c

    def test_server_derives_family(self, api_client, api_settings):
        """Server must derive family from submitted HSL, not trust any implied value (FR-1)."""
        h, s, l = 174.0, 58.0, 41.0
        token = _stage(api_settings)
        body = api_client.post(
            "/api/garments",
            json=_create_body(token, colours=[{"h": h, "s": s, "l": l, "proportion": 100}]),
        ).json()
        expected_family = classify(h, s, l)
        assert body["colours"][0]["family"] == expected_family

    def test_thumbnail_url_format(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        garment_id = body["id"]
        assert body["thumbnail_url"] == f"/api/garments/{garment_id}/thumbnail"

    def test_image_url_format(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        garment_id = body["id"]
        assert body["image_url"] == f"/api/garments/{garment_id}/image"

    def test_created_at_present(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        assert "created_at" in body
        assert body["created_at"]  # non-empty string

    def test_regenerated_at_is_none(self, api_client, api_settings):
        token = _stage(api_settings)
        body = api_client.post("/api/garments", json=_create_body(token)).json()
        assert body["regenerated_at"] is None

    def test_token_consumed_on_success(self, api_client, api_settings):
        token = _stage(api_settings)
        api_client.post("/api/garments", json=_create_body(token))
        # Second call with the same token must return 404.
        r2 = api_client.post("/api/garments", json=_create_body(token))
        assert r2.status_code == 404
        assert r2.json()["error"]["code"] == "detection_not_found"

    def test_multi_colour_palette(self, api_client, api_settings):
        token = _stage(api_settings)
        colours = [
            {"h": 0.0,   "s": 80.0, "l": 50.0, "proportion": 60},
            {"h": 120.0, "s": 60.0, "l": 40.0, "proportion": 40},
        ]
        body = api_client.post("/api/garments", json=_create_body(token, colours=colours)).json()
        assert len(body["colours"]) == 2


# ── POST /api/garments — palette validation errors ────────────────────────────

class TestPaletteErrors:
    def test_zero_colours(self, api_client, api_settings):
        token = _stage(api_settings)
        r = api_client.post("/api/garments", json=_create_body(token, colours=[]))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_five_colours(self, api_client, api_settings):
        token = _stage(api_settings)
        colours = [{"h": float(i * 60), "s": 50.0, "l": 50.0, "proportion": 20} for i in range(5)]
        r = api_client.post("/api/garments", json=_create_body(token, colours=colours))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_proportions_not_summing_to_100(self, api_client, api_settings):
        token = _stage(api_settings)
        colours = [
            {"h": 0.0,   "s": 50.0, "l": 50.0, "proportion": 60},
            {"h": 120.0, "s": 50.0, "l": 50.0, "proportion": 30},
        ]
        r = api_client.post("/api/garments", json=_create_body(token, colours=colours))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"

    def test_palette_error_does_not_consume_token(self, api_client, api_settings):
        token = _stage(api_settings)
        # Bad payload — proportions don't sum to 100.
        bad_colours = [{"h": 0.0, "s": 50.0, "l": 50.0, "proportion": 50}]
        api_client.post("/api/garments", json=_create_body(token, colours=bad_colours))
        # Token must still be live for a valid retry.
        r2 = api_client.post("/api/garments", json=_create_body(token))
        assert r2.status_code == 201


# ── POST /api/garments — type validation errors ───────────────────────────────

class TestTypeErrors:
    def test_unknown_type_returns_422(self, api_client, api_settings):
        token = _stage(api_settings)
        r = api_client.post("/api/garments", json=_create_body(token, garment_type="jumpsuit"))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_type"


# ── POST /api/garments — token errors ────────────────────────────────────────

class TestTokenErrors:
    def test_unknown_token_404(self, api_client):
        r = api_client.post("/api/garments", json=_create_body("no-such-token"))
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "detection_not_found"


# ── Seeded wardrobe fixture ───────────────────────────────────────────────────
#
# Creates three garments:
#   g_top    — type=top,    primary=Blue  (h=240, s=70, l=50)
#   g_bottom — type=bottom, primary=Red   (h=0,   s=80, l=50)
#   g_jersey — type=jersey, Red 80% + Blue 20% (Blue is a minor role)

def _save(api_client: object, api_settings: Settings, garment_type: str, colours: list) -> dict:
    token = _stage(api_settings)
    r = api_client.post("/api/garments", json=_create_body(token, garment_type, colours))
    assert r.status_code == 201, r.json()
    return r.json()


_BLUE_COLOUR  = [{"h": 240.0, "s": 70.0, "l": 50.0, "proportion": 100}]
_RED_COLOUR   = [{"h":   0.0, "s": 80.0, "l": 50.0, "proportion": 100}]
_RED_BLUE_COLOURS = [
    {"h":   0.0, "s": 80.0, "l": 50.0, "proportion": 80},
    {"h": 240.0, "s": 70.0, "l": 50.0, "proportion": 20},
]


@pytest.fixture()
def seeded(api_client, api_settings):
    g_top    = _save(api_client, api_settings, "top",    _BLUE_COLOUR)
    g_bottom = _save(api_client, api_settings, "bottom", _RED_COLOUR)
    g_jersey = _save(api_client, api_settings, "jersey", _RED_BLUE_COLOURS)
    return {"top": g_top, "bottom": g_bottom, "jersey": g_jersey}


# ── GET /api/garments — list ──────────────────────────────────────────────────

class TestListGarments:
    def test_empty_returns_empty_list(self, api_client):
        r = api_client.get("/api/garments")
        assert r.status_code == 200
        body = r.json()
        assert body["garments"] == []
        assert body["total"] == 0

    def test_total_matches_garment_count(self, api_client, seeded):
        body = api_client.get("/api/garments").json()
        assert body["total"] == 3
        assert len(body["garments"]) == 3

    def test_summary_shape(self, api_client, seeded):
        garment = api_client.get("/api/garments").json()["garments"][0]
        assert "id" in garment
        assert "type" in garment
        assert "colours" in garment
        assert "thumbnail_url" in garment
        assert "image_url" not in garment  # GarmentSummary, not detail

    def test_type_filter(self, api_client, seeded):
        body = api_client.get("/api/garments", params={"type": "top"}).json()
        assert body["total"] == 1
        assert body["garments"][0]["type"] == "top"

    def test_family_filter_matches_primary_colour(self, api_client, seeded):
        # Blue is primary in the top.
        body = api_client.get("/api/garments", params={"family": "Blue"}).json()
        assert body["total"] == 2  # top (primary Blue) + jersey (minor Blue)
        ids = {g["id"] for g in body["garments"]}
        assert seeded["top"]["id"] in ids
        assert seeded["jersey"]["id"] in ids

    def test_family_filter_matches_minor_role(self, api_client, seeded):
        # jersey has Blue as a 20 % minor colour — must still match.
        body = api_client.get("/api/garments", params={"family": "Blue"}).json()
        ids = {g["id"] for g in body["garments"]}
        assert seeded["jersey"]["id"] in ids

    def test_family_filter_red(self, api_client, seeded):
        body = api_client.get("/api/garments", params={"family": "Red"}).json()
        assert body["total"] == 2  # bottom + jersey
        ids = {g["id"] for g in body["garments"]}
        assert seeded["bottom"]["id"] in ids
        assert seeded["jersey"]["id"] in ids

    def test_type_and_family_combined_match(self, api_client, seeded):
        # jersey type AND Blue family → 1 result
        body = api_client.get("/api/garments", params={"type": "jersey", "family": "Blue"}).json()
        assert body["total"] == 1
        assert body["garments"][0]["id"] == seeded["jersey"]["id"]

    def test_type_and_family_combined_no_match(self, api_client, seeded):
        # bottom type AND Blue family → 0 results (bottom is Red only)
        body = api_client.get("/api/garments", params={"type": "bottom", "family": "Blue"}).json()
        assert body["total"] == 0
        assert body["garments"] == []

    def test_limit_reduces_page(self, api_client, seeded):
        body = api_client.get("/api/garments", params={"limit": 2}).json()
        assert len(body["garments"]) == 2
        assert body["total"] == 3  # total unchanged

    def test_offset_pages_results(self, api_client, seeded):
        first  = api_client.get("/api/garments", params={"limit": 2, "offset": 0}).json()
        second = api_client.get("/api/garments", params={"limit": 2, "offset": 2}).json()
        assert len(first["garments"]) == 2
        assert len(second["garments"]) == 1
        ids_first  = {g["id"] for g in first["garments"]}
        ids_second = {g["id"] for g in second["garments"]}
        assert ids_first.isdisjoint(ids_second)

    def test_total_unchanged_under_paging(self, api_client, seeded):
        body = api_client.get("/api/garments", params={"limit": 1, "offset": 2}).json()
        assert body["total"] == 3

    def test_invalid_type_422(self, api_client):
        r = api_client.get("/api/garments", params={"type": "onesie"})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_filter"

    def test_invalid_family_422(self, api_client):
        r = api_client.get("/api/garments", params={"family": "Khaki"})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_filter"


# ── GET /api/garments/{id} — detail ──────────────────────────────────────────

class TestGetGarmentDetail:
    def test_returns_full_detail(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        body = api_client.get(f"/api/garments/{garment_id}").json()
        assert body["id"] == garment_id
        assert body["type"] == "top"
        assert "image_url" in body
        assert "thumbnail_url" in body
        assert "created_at" in body
        assert "regenerated_at" in body

    def test_unknown_id_404(self, api_client):
        r = api_client.get("/api/garments/no-such-id")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"


# ── GET /api/garments/{id}/image and /thumbnail ───────────────────────────────

class TestGarmentFiles:
    def test_image_serves_binary(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        r = api_client.get(f"/api/garments/{garment_id}/image")
        assert r.status_code == 200
        assert len(r.content) > 0

    def test_thumbnail_serves_binary(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        r = api_client.get(f"/api/garments/{garment_id}/thumbnail")
        assert r.status_code == 200
        assert len(r.content) > 0

    def test_image_not_found_404(self, api_client):
        r = api_client.get("/api/garments/no-such-id/image")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_thumbnail_not_found_404(self, api_client):
        r = api_client.get("/api/garments/no-such-id/thumbnail")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_image_file_missing_returns_404(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        for f in (api_settings.data_dir / "images").glob(f"{garment_id}.*"):
            f.unlink()
        r = api_client.get(f"/api/garments/{garment_id}/image")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "image_not_found"

    def test_thumbnail_file_missing_returns_404(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        (api_settings.data_dir / "thumbnails" / f"{garment_id}.webp").unlink()
        r = api_client.get(f"/api/garments/{garment_id}/thumbnail")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "thumbnail_not_found"


# ── Helpers for HUE-030 ───────────────────────────────────────────────────────

_FAKE_REGEN_COLOUR = ColourProposal(
    h=0.0, s=80.0, l=50.0, family="Red", neutral=False, hex="#f02600", proportion=100
)


def _fake_regen_result(token: str, garment_id: str) -> DetectionResult:
    return DetectionResult(
        token=token,
        expires_at="2099-01-01T00:00:00Z",
        fallback_used=False,
        image_width=8,
        image_height=8,
        colours=(_FAKE_REGEN_COLOUR,),
        garment_id=garment_id,
    )


def _stage_regen_token(settings: Settings, garment_id: str) -> str:
    """Create a staging token bound to *garment_id* — simulates what run_regeneration does."""
    return staging.stage(
        data=_tiny_jpeg(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={"colours": [{"h": 0, "s": 80, "l": 50, "proportion": 100}]},
        staging_dir=settings.data_dir / "staging",
        garment_id=garment_id,
    )


def _put_body(token: str, garment_type: str = "bottom") -> dict:
    return {
        "regeneration_token": token,
        "type": garment_type,
        "colours": [{"h": 120.0, "s": 60.0, "l": 40.0, "proportion": 100}],
    }


# ── POST /api/garments/{id}/regenerate ────────────────────────────────────────

class TestRegenerateGarment:
    def test_returns_200_with_proposal_shape(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        with patch(
            "app.api.garments.run_regeneration",
            return_value=_fake_regen_result(token, garment_id),
        ):
            r = api_client.post(f"/api/garments/{garment_id}/regenerate")
        assert r.status_code == 200
        body = r.json()
        assert body["garment_id"] == garment_id
        assert "token" in body
        assert "expires_at" in body
        assert "fallback_used" in body
        assert "image" in body
        assert "colours" in body

    def test_image_url_points_to_detections(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        with patch(
            "app.api.garments.run_regeneration",
            return_value=_fake_regen_result(token, garment_id),
        ):
            body = api_client.post(f"/api/garments/{garment_id}/regenerate").json()
        assert body["image"]["url"].startswith("/api/detections/")

    def test_colour_shape_returned(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        with patch(
            "app.api.garments.run_regeneration",
            return_value=_fake_regen_result(token, garment_id),
        ):
            body = api_client.post(f"/api/garments/{garment_id}/regenerate").json()
        colour = body["colours"][0]
        assert "h" in colour and "family" in colour and "hex" in colour

    def test_unknown_garment_404(self, api_client):
        r = api_client.post("/api/garments/no-such-id/regenerate")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_record_unchanged_after_regenerate(self, api_client, api_settings, seeded):
        """The original garment record must not be mutated by the regenerate call (FR-33)."""
        garment_id = seeded["top"]["id"]
        original = api_client.get(f"/api/garments/{garment_id}").json()
        token = _stage_regen_token(api_settings, garment_id)
        with patch(
            "app.api.garments.run_regeneration",
            return_value=_fake_regen_result(token, garment_id),
        ):
            api_client.post(f"/api/garments/{garment_id}/regenerate")
        after = api_client.get(f"/api/garments/{garment_id}").json()
        assert after["type"] == original["type"]
        assert after["colours"] == original["colours"]
        assert after["regenerated_at"] == original["regenerated_at"]


# ── PUT /api/garments/{id} — update ──────────────────────────────────────────

class TestUpdateGarment:
    def test_put_replaces_type_and_palette(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        r = api_client.put(f"/api/garments/{garment_id}", json=_put_body(token, "bottom"))
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == garment_id  # id unchanged
        assert body["type"] == "bottom"
        assert body["colours"][0]["family"] == "Green"  # h=120 → Green

    def test_put_sets_regenerated_at(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        body = api_client.put(f"/api/garments/{garment_id}", json=_put_body(token)).json()
        assert body["regenerated_at"] is not None

    def test_put_keeps_same_image(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        before_image = api_client.get(f"/api/garments/{garment_id}/image").content
        token = _stage_regen_token(api_settings, garment_id)
        api_client.put(f"/api/garments/{garment_id}", json=_put_body(token))
        after_image = api_client.get(f"/api/garments/{garment_id}/image").content
        assert before_image == after_image

    def test_put_token_consumed(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        api_client.put(f"/api/garments/{garment_id}", json=_put_body(token))
        r2 = api_client.put(f"/api/garments/{garment_id}", json=_put_body(token))
        assert r2.status_code == 409
        assert r2.json()["error"]["code"] == "invalid_regeneration_token"

    def test_put_missing_token_409(self, api_client, seeded):
        """FR-32: no valid regen token → always fails."""
        garment_id = seeded["top"]["id"]
        r = api_client.put(f"/api/garments/{garment_id}", json=_put_body("no-such-token"))
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "invalid_regeneration_token"

    def test_put_foreign_garment_token_409(self, api_client, api_settings, seeded):
        """Token bound to a different garment must be rejected (FR-32)."""
        other_garment_id = seeded["bottom"]["id"]
        foreign_token = _stage_regen_token(api_settings, other_garment_id)
        garment_id = seeded["top"]["id"]
        r = api_client.put(f"/api/garments/{garment_id}", json=_put_body(foreign_token))
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "invalid_regeneration_token"

    def test_put_unknown_garment_404(self, api_client, api_settings, seeded):
        # Token must be bound to the *same* id to pass the token check; only then
        # does confirm_regeneration discover the garment doesn't exist in the DB.
        fake_id = "00000000-0000-0000-0000-000000000000"
        token = _stage_regen_token(api_settings, fake_id)
        r = api_client.put(f"/api/garments/{fake_id}", json=_put_body(token))
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_put_invalid_type_422(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        body = {**_put_body(token), "type": "onesie"}
        r = api_client.put(f"/api/garments/{garment_id}", json=body)
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_type"

    def test_put_invalid_palette_422(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        token = _stage_regen_token(api_settings, garment_id)
        body = {
            "regeneration_token": token,
            "type": "top",
            "colours": [
                {"h": 0.0, "s": 80.0, "l": 50.0, "proportion": 60},
                {"h": 120.0, "s": 60.0, "l": 40.0, "proportion": 30},
            ],
        }
        r = api_client.put(f"/api/garments/{garment_id}", json=body)
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "invalid_palette"


# ── DELETE /api/garments/{id} ─────────────────────────────────────────────────

class TestDeleteGarment:
    def test_delete_returns_204(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        r = api_client.delete(f"/api/garments/{garment_id}")
        assert r.status_code == 204
        assert r.content == b""

    def test_deleted_garment_absent_from_inventory(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        api_client.delete(f"/api/garments/{garment_id}")
        body = api_client.get("/api/garments").json()
        assert body["total"] == 2
        ids = {g["id"] for g in body["garments"]}
        assert garment_id not in ids

    def test_deleted_garment_returns_404_on_detail(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        api_client.delete(f"/api/garments/{garment_id}")
        r = api_client.get(f"/api/garments/{garment_id}")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_deleted_image_returns_404(self, api_client, api_settings, seeded):
        garment_id = seeded["top"]["id"]
        api_client.delete(f"/api/garments/{garment_id}")
        r = api_client.get(f"/api/garments/{garment_id}/image")
        assert r.status_code == 404

    def test_delete_unknown_garment_404(self, api_client):
        r = api_client.delete("/api/garments/no-such-id")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "garment_not_found"

    def test_double_delete_returns_404(self, api_client, seeded):
        garment_id = seeded["top"]["id"]
        api_client.delete(f"/api/garments/{garment_id}")
        r2 = api_client.delete(f"/api/garments/{garment_id}")
        assert r2.status_code == 404
