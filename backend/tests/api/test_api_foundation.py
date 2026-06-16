"""
Tests for HUE-025: API foundation — schemas, error envelope, health, SPA serving.

Strategy: TestClient against the real ``create_app`` factory (§7.2 contract tests).
Test-only routes are injected into the app to exercise each error-handler path
without polluting production code.
"""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.errors import AppError
from app.api.schemas import ColourIn, GarmentSummary, validate_palette
from app.main import Settings, create_app


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path):
    """
    App client for health + error-envelope tests.  No SPA directory so the
    catch-all route is absent and test routes are not shadowed by it.
    """
    settings = Settings(
        data_dir=tmp_path / "data",
        spa_dir=tmp_path / "no-spa",  # does not exist → catch-all not registered
    )
    _app = create_app(settings)

    # Test-only routes: exercise each error-handler code path.
    test_router = APIRouter()

    @test_router.get("/test/app-error-404")
    def _raise_404():
        raise AppError(404, "garment_not_found", "Garment not found.")

    @test_router.get("/test/app-error-409")
    def _raise_409():
        raise AppError(
            409,
            "empty_slots",
            "You have no garments for the requested slot(s): top.",
            {"empty_slots": ["top"]},
        )

    @test_router.get("/test/internal-error")
    def _raise_500():
        raise RuntimeError("unexpected boom")

    @test_router.post("/test/validate-colour")
    def _validate_colour(c: ColourIn) -> dict:
        return c.model_dump()

    _app.include_router(test_router, prefix="/api")

    return TestClient(_app, raise_server_exceptions=False)


@pytest.fixture()
def spa_client(tmp_path):
    """App client with a real SPA directory for static-serving tests."""
    spa = tmp_path / "spa"
    spa.mkdir()
    (spa / "index.html").write_text("<html><body>SPA</body></html>")
    settings = Settings(data_dir=tmp_path / "data", spa_dir=spa)
    return TestClient(create_app(settings), raise_server_exceptions=False)


# ── GET /api/health ───────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_returns_200(self, client):
        assert client.get("/api/health").status_code == 200

    def test_body_shape(self, client):
        assert client.get("/api/health").json() == {
            "status": "ok",
            "version": "0.1.0",
        }


# ── Error envelope (contract §1.3) ───────────────────────────────────────────

class TestErrorEnvelope:
    def _error(self, r) -> dict:
        body = r.json()
        assert "error" in body, f"no 'error' key in {body}"
        err = body["error"]
        assert "code" in err
        assert "message" in err
        assert "details" in err
        return err

    def test_404_status(self, client):
        assert client.get("/api/test/app-error-404").status_code == 404

    def test_404_envelope_shape(self, client):
        err = self._error(client.get("/api/test/app-error-404"))
        assert err["code"] == "garment_not_found"

    def test_409_status(self, client):
        assert client.get("/api/test/app-error-409").status_code == 409

    def test_409_details_populated(self, client):
        err = self._error(client.get("/api/test/app-error-409"))
        assert err["details"]["empty_slots"] == ["top"]

    def test_422_uses_envelope(self, client):
        # h=360 fails ColourIn validation → RequestValidationError → 422 envelope.
        r = client.post(
            "/api/test/validate-colour",
            json={"h": 360.0, "s": 50.0, "l": 50.0, "proportion": 50},
        )
        assert r.status_code == 422
        err = self._error(r)
        assert err["code"] == "validation_error"
        assert "errors" in err["details"]

    def test_500_uses_envelope(self, client):
        r = client.get("/api/test/internal-error")
        assert r.status_code == 500
        err = self._error(r)
        assert err["code"] == "internal_error"


# ── ColourIn field validation (contract §1.1 boundaries) ─────────────────────

class TestColourInValidation:
    def test_valid_colour(self):
        c = ColourIn(h=180.0, s=50.0, l=50.0, proportion=100)
        assert c.h == 180.0

    def test_h_zero_valid(self):
        ColourIn(h=0.0, s=0.0, l=0.0, proportion=1)

    def test_h_just_below_360_valid(self):
        ColourIn(h=359.9, s=50.0, l=50.0, proportion=100)

    def test_h_360_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=360.0, s=50.0, l=50.0, proportion=100)

    def test_h_negative_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=-0.1, s=50.0, l=50.0, proportion=100)

    def test_s_zero_valid(self):
        ColourIn(h=0.0, s=0.0, l=50.0, proportion=100)

    def test_s_100_valid(self):
        ColourIn(h=0.0, s=100.0, l=50.0, proportion=100)

    def test_s_over_100_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=0.0, s=100.1, l=50.0, proportion=100)

    def test_l_negative_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=0.0, s=50.0, l=-0.1, proportion=100)

    def test_proportion_zero_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=0.0, s=50.0, l=50.0, proportion=0)

    def test_proportion_1_valid(self):
        ColourIn(h=0.0, s=50.0, l=50.0, proportion=1)

    def test_proportion_100_valid(self):
        ColourIn(h=0.0, s=50.0, l=50.0, proportion=100)

    def test_proportion_101_invalid(self):
        with pytest.raises(ValidationError):
            ColourIn(h=0.0, s=50.0, l=50.0, proportion=101)


# ── validate_palette (FR-6) ───────────────────────────────────────────────────

class TestValidatePalette:
    def _c(self, proportion: int) -> ColourIn:
        return ColourIn(h=0.0, s=50.0, l=50.0, proportion=proportion)

    def test_single_colour_100_valid(self):
        validate_palette([self._c(100)])

    def test_four_colours_25_each_valid(self):
        validate_palette([self._c(25)] * 4)

    def test_zero_colours_raises(self):
        with pytest.raises(ValueError):
            validate_palette([])

    def test_five_colours_raises(self):
        with pytest.raises(ValueError):
            validate_palette([self._c(20)] * 5)

    def test_sum_99_raises(self):
        with pytest.raises(ValueError):
            validate_palette([self._c(50), self._c(49)])

    def test_sum_101_raises(self):
        with pytest.raises(ValueError):
            validate_palette([self._c(50), self._c(51)])

    def test_sum_100_two_colours_valid(self):
        validate_palette([self._c(60), self._c(40)])


# ── Static SPA mount + history-API fallback ───────────────────────────────────

class TestStaticSpaMount:
    def test_root_serves_index(self, spa_client):
        r = spa_client.get("/")
        assert r.status_code == 200
        assert "SPA" in r.text

    def test_unknown_path_fallback_to_index(self, spa_client):
        r = spa_client.get("/wardrobe/detail/123")
        assert r.status_code == 200
        assert "SPA" in r.text

    def test_api_path_not_intercepted_by_spa(self, spa_client):
        # Unknown /api/* path → 404 JSON envelope, not the SPA HTML.
        r = spa_client.get("/api/nonexistent-endpoint")
        assert r.status_code == 404
        assert "error" in r.json()

    def test_no_spa_mount_when_dir_absent(self, tmp_path):
        settings = Settings(
            data_dir=tmp_path / "data",
            spa_dir=tmp_path / "no-such-dir",
        )
        _app = create_app(settings)
        c = TestClient(_app, raise_server_exceptions=False)
        # Without the SPA mount the root returns 404.
        assert c.get("/").status_code == 404
