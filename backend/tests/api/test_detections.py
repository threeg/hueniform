"""
Tests for HUE-027: POST /api/detections and GET /api/detections/{token}/image
(contract §2.3–§2.4, FR-23, FR-24, FR-26, FR-27, FR-28).

Strategy (§7.2 contract tests):
- Upload and format/size errors exercised via TestClient; run_detection is
  mocked so no real rembg model is required for the default gate.
- Staged-image serving uses the real staging store with tmp_path.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.detection_service import (
    ColourProposal,
    DetectionResult,
    UnreadableImageError,
)
from app.storage import staging



def _fake_result(token: str = "tok-abc") -> DetectionResult:
    return DetectionResult(
        token=token,
        expires_at="2026-06-16T01:00:00+00:00",
        fallback_used=False,
        image_width=800,
        image_height=600,
        colours=(
            ColourProposal(
                h=210.0, s=60.0, l=50.0,
                family="blue", neutral=False,
                hex="#3380BF", proportion=100,
            ),
        ),
    )


def _jpeg_upload(data: bytes = b"fake-jpeg") -> dict:
    return {"file": ("photo.jpg", data, "image/jpeg")}


# ── POST /api/detections — happy path ─────────────────────────────────────────

class TestUploadSuccess:
    def test_status_201(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            r = api_client.post("/api/detections", files=_jpeg_upload())
        assert r.status_code == 201

    def test_token_in_body(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result("abc")):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["token"] == "abc"

    def test_expires_at_in_body(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["expires_at"] == "2026-06-16T01:00:00+00:00"

    def test_fallback_used_false(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["fallback_used"] is False

    def test_image_url(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result("tok-abc")):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["image"]["url"] == "/api/detections/tok-abc/image"

    def test_image_dimensions(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["image"]["width"] == 800
        assert body["image"]["height"] == 600

    def test_colours_list(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert len(body["colours"]) == 1
        c = body["colours"][0]
        assert c["family"] == "blue"
        assert c["neutral"] is False
        assert c["proportion"] == 100
        assert "hex" in c

    def test_fallback_used_true_surfaced(self, api_client):
        result = DetectionResult(
            token="tok-fb",
            expires_at="2026-06-16T01:00:00+00:00",
            fallback_used=True,
            image_width=400,
            image_height=300,
            colours=(_fake_result().colours[0],),
        )
        with patch("app.api.detections.run_detection", return_value=result):
            body = api_client.post("/api/detections", files=_jpeg_upload()).json()
        assert body["fallback_used"] is True

    def test_png_accepted(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            r = api_client.post(
                "/api/detections",
                files={"file": ("photo.png", b"fake-png", "image/png")},
            )
        assert r.status_code == 201

    def test_webp_accepted(self, api_client):
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            r = api_client.post(
                "/api/detections",
                files={"file": ("photo.webp", b"fake-webp", "image/webp")},
            )
        assert r.status_code == 201

    def test_no_db_write(self, api_client):
        # The endpoint delegates solely to detection_service.run_detection which
        # uses the staging store only (FR-24).  No DB connection exists in this
        # test setup, and the endpoint has no code path to the database layer.
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            r = api_client.post("/api/detections", files=_jpeg_upload())
        assert r.status_code == 201  # if DB were touched this fixture would error


# ── POST /api/detections — format rejection ───────────────────────────────────

class TestUnsupportedFormat:
    def test_gif_rejected(self, api_client):
        r = api_client.post(
            "/api/detections",
            files={"file": ("anim.gif", b"GIF89a", "image/gif")},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "unsupported_format"

    def test_bmp_rejected(self, api_client):
        r = api_client.post(
            "/api/detections",
            files={"file": ("img.bmp", b"BM", "image/bmp")},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "unsupported_format"

    def test_run_detection_not_called_for_bad_format(self, api_client):
        with patch("app.api.detections.run_detection") as mock_run:
            api_client.post(
                "/api/detections",
                files={"file": ("img.gif", b"GIF89a", "image/gif")},
            )
        mock_run.assert_not_called()


# ── POST /api/detections — size rejection ─────────────────────────────────────

class TestFileTooLarge:
    def test_oversized_returns_413(self, api_client):
        big = b"\x00" * (20 * 1024 * 1024 + 1)
        r = api_client.post("/api/detections", files=_jpeg_upload(big))
        assert r.status_code == 413
        assert r.json()["error"]["code"] == "file_too_large"

    def test_exactly_at_limit_accepted(self, api_client):
        at_limit = b"\xff" * (20 * 1024 * 1024)
        with patch("app.api.detections.run_detection", return_value=_fake_result()):
            r = api_client.post("/api/detections", files=_jpeg_upload(at_limit))
        assert r.status_code == 201


# ── POST /api/detections — unreadable image ───────────────────────────────────

class TestUnreadableImage:
    def test_returns_400(self, api_client):
        with patch(
            "app.api.detections.run_detection",
            side_effect=UnreadableImageError("bad jpeg"),
        ):
            r = api_client.post("/api/detections", files=_jpeg_upload(b"notajpeg"))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "unreadable_image"


# ── GET /api/detections/{token}/image ─────────────────────────────────────────

class TestImageServing:
    def test_serves_staged_bytes(self, api_client, api_settings):
        staging_dir = api_settings.data_dir / "staging"
        token = staging.stage(
            data=b"fake-image-content",
            ext="jpg",
            content_type="image/jpeg",
            fallback_used=False,
            proposal={},
            staging_dir=staging_dir,
        )
        r = api_client.get(f"/api/detections/{token}/image")
        assert r.status_code == 200
        assert r.content == b"fake-image-content"

    def test_content_type_header(self, api_client, api_settings):
        staging_dir = api_settings.data_dir / "staging"
        token = staging.stage(
            data=b"fake-png",
            ext="png",
            content_type="image/png",
            fallback_used=False,
            proposal={},
            staging_dir=staging_dir,
        )
        r = api_client.get(f"/api/detections/{token}/image")
        assert r.status_code == 200
        assert "image/png" in r.headers["content-type"]

    def test_unknown_token_returns_404(self, api_client):
        r = api_client.get("/api/detections/no-such-token/image")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "detection_not_found"

    def test_expired_token_returns_404(self, api_client, api_settings, monkeypatch):
        staging_dir = api_settings.data_dir / "staging"
        token = staging.stage(
            data=b"data",
            ext="jpg",
            content_type="image/jpeg",
            fallback_used=False,
            proposal={},
            staging_dir=staging_dir,
        )
        # Simulate expiry by making staging.load return None.
        monkeypatch.setattr("app.services.detection_service.staging.load", lambda *a: None)
        r = api_client.get(f"/api/detections/{token}/image")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "detection_not_found"
