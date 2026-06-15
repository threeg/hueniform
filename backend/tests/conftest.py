import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import settings

from app.main import Settings, create_app

# ── Hypothesis profiles (test strategy §4.8) ─────────────────────────────────
# "deterministic" profile is activated by HYPOTHESIS_PROFILE=deterministic in
# make test-backend. Local runs use "default" (randomised, finds new examples).
settings.register_profile("deterministic", derandomize=True)
settings.register_profile("default")
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


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
