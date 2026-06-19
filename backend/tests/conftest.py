import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import settings

from app.main import Settings, create_app
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
