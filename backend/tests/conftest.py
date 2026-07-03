from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import settings
from PIL import Image
from sqlmodel import Session

from app.main import Settings, create_app
from app.matcher.roles import Garment
from app.storage import staging
from app.storage.models import GarmentColourRow, GarmentRow
from tests.fixtures.generate_images import generate_all as _generate_synthetic


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Regenerate matcher golden files (test strategy §4.10).",
    )

# ── Hypothesis profiles (test strategy §4.8) ─────────────────────────────────
# "deterministic" profile is activated by HYPOTHESIS_PROFILE=deterministic in
# make test-backend. Local runs use "default" (randomised, finds new examples).
settings.register_profile("deterministic", derandomize=True)
settings.register_profile("default")
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


# ── Synthetic image session fixture (test strategy §11.1) ───────────────────

@pytest.fixture(scope="session")
def synthetic_images_dir() -> Path:
    """
    Generate the synthetic garment images on first use and return their
    directory.  Idempotent — subsequent calls in the same session return the
    cached directory without re-rendering.
    """
    return _generate_synthetic()


@pytest.fixture(scope="session")
def oversize_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    A >20 MB blob for testing FR-23 / FR-24 rejection of oversized uploads.
    Generated at test time — never committed (test strategy §11.1).
    """
    p = tmp_path_factory.mktemp("oversize") / "oversize.jpg"
    # Write a valid JPEG header followed by enough zeros to exceed 20 MB.
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * (21 * 1024 * 1024))
    return p


# ── Core fixtures (test strategy §7.1) ───────────────────────────────────────

@pytest.fixture
def app_settings(tmp_path: Path) -> Settings:
    """App settings pointing at a fresh temporary data directory."""
    return Settings(data_dir=tmp_path)


@pytest.fixture
def test_app(app_settings: Settings):
    """FastAPI app instance wired to the temporary data directory."""
    return create_app(settings=app_settings)


@pytest.fixture
def client(test_app) -> TestClient:
    """Synchronous TestClient; lifespan runs on enter, creating data subdirs."""
    with TestClient(test_app) as c:
        yield c


# ── Shared test helpers ───────────────────────────────────────────────────────

def make_test_jpeg(colour: tuple[int, int, int] = (200, 30, 30)) -> bytes:
    """Return a minimal valid JPEG for use in tests."""
    buf = BytesIO()
    Image.new("RGB", (200, 200), colour).save(buf, format="JPEG")
    return buf.getvalue()


def stage_test_image(staging_dir: Path, data: bytes | None = None) -> str:
    """Stage a JPEG and return the token."""
    return staging.stage(
        data=data or make_test_jpeg(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={},
        staging_dir=staging_dir,
    )


def materialise_garments(
    engine,
    garments: list[Garment],
    *,
    derive_families: bool = False,
) -> None:
    """Insert matcher Garment objects into the DB as GarmentRow/GarmentColourRow records.

    When ``derive_families`` is True, family values are derived via ``classify()``;
    otherwise a placeholder ``"Red"`` is used (sufficient for tests that don't inspect
    family values).
    """
    if derive_families:
        from app.matcher.taxonomy import classify

    now = datetime.now(timezone.utc).isoformat()
    with Session(engine) as s:
        for g in garments:
            gid = str(uuid.uuid4())
            s.add(GarmentRow(
                id=gid,
                type=g.garment_type,
                image_file=f"{gid}.jpg",
                thumbnail_file=f"{gid}.webp",
                created_at=now,
            ))
            s.flush()
            for i, c in enumerate(g.colours):
                family = classify(c.h, c.s, c.l) if derive_families else "Red"
                s.add(GarmentColourRow(
                    garment_id=gid,
                    position=i,
                    h=c.h,
                    s=c.s,
                    l=c.l,
                    family=family,
                    proportion=c.proportion,
                ))
        s.commit()
