"""Shared fixtures for API contract tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import Settings, create_app


@pytest.fixture()
def api_settings(tmp_path):
    data = tmp_path / "data"
    (data / "staging").mkdir(parents=True)
    return Settings(data_dir=data, spa_dir=tmp_path / "no-spa")


@pytest.fixture()
def api_client(api_settings):
    with TestClient(create_app(api_settings)) as c:
        yield c
