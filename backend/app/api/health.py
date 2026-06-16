"""GET /api/health — readiness probe for the launch script (NFR-2)."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Return ``{"status": "ok", "version": "0.1.0"}`` (contract §2.1)."""
    return {"status": "ok", "version": "0.1.0"}
