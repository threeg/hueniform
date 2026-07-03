"""Shared fixtures and helpers for the services test suite."""

from __future__ import annotations

import pytest

from app.storage.engine import init_db, make_engine


@pytest.fixture()
def engine(tmp_path):
    e = make_engine(tmp_path / "test.db")
    init_db(e)
    yield e
    e.dispose()


@pytest.fixture()
def dirs(tmp_path):
    d = {
        "staging": tmp_path / "staging",
        "images": tmp_path / "images",
        "thumbnails": tmp_path / "thumbnails",
    }
    for p in d.values():
        p.mkdir()
    return d
