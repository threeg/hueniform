"""Shared fixtures and helpers for the services test suite."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from app.storage import staging
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


def _make_jpeg_bytes(colour: tuple[int, int, int] = (200, 30, 30)) -> bytes:
    buf = BytesIO()
    Image.new("RGB", (200, 200), colour).save(buf, format="JPEG")
    return buf.getvalue()


def _stage_image(staging_dir: Path, data: bytes | None = None) -> str:
    """Stage a JPEG and return the token."""
    return staging.stage(
        data=data or _make_jpeg_bytes(),
        ext="jpg",
        content_type="image/jpeg",
        fallback_used=False,
        proposal={},
        staging_dir=staging_dir,
    )
