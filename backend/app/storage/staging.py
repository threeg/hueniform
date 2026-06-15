"""
Staging store for unconfirmed detection uploads (architecture §3.3, FR-24).

Unconfirmed detections live entirely on disk — nothing is written to the
database until the user confirms (FR-24).  Each entry is a pair of files:

  data/staging/{token}.{ext}   — the uploaded image bytes
  data/staging/{token}.json    — sidecar with metadata and a 1-hour TTL

Public API
----------
``stage(...)``   Write file + sidecar; return the UUID4 token.
``load(...)``    Read a live entry; return None if missing or expired (lazy sweep).
``move(...)``    Promote a staged image into data/images/; delete sidecar.
``sweep(...)``   Remove all expired entries (called at startup).

Storage imports nothing from matcher/detection/services/api (contract 4).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_TTL_HOURS: int = 1


# ── Value type ────────────────────────────────────────────────────────────────

@dataclass
class StagingEntry:
    """In-memory representation of one live staging entry."""
    token: str
    ext: str
    content_type: str
    fallback_used: bool
    proposal: dict[str, Any]
    garment_id: str | None   # set for regeneration flows; None for new garments


# ── Internal helpers ──────────────────────────────────────────────────────────

def _sidecar(staging_dir: Path, token: str) -> Path:
    return staging_dir / f"{token}.json"


def _delete_entry(staging_dir: Path, token: str, ext: str) -> None:
    (staging_dir / f"{token}.{ext}").unlink(missing_ok=True)
    _sidecar(staging_dir, token).unlink(missing_ok=True)


# ── Public API ────────────────────────────────────────────────────────────────

def stage(
    data: bytes,
    ext: str,
    content_type: str,
    fallback_used: bool,
    proposal: dict[str, Any],
    staging_dir: Path,
    garment_id: str | None = None,
) -> str:
    """
    Write *data* and a JSON sidecar to *staging_dir*; return the UUID4 token.

    The sidecar stores ``expires_at`` (ISO 8601 UTC, TTL = 1 hour), ``ext``,
    ``content_type``, ``fallback_used``, ``proposal``, and the optional
    ``garment_id`` for regeneration flows.
    """
    token = str(uuid.uuid4())
    (staging_dir / f"{token}.{ext}").write_bytes(data)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=_TTL_HOURS)
    sidecar_data: dict[str, Any] = {
        "token": token,
        "ext": ext,
        "expires_at": expires_at.isoformat(),
        "content_type": content_type,
        "fallback_used": fallback_used,
        "proposal": proposal,
        "garment_id": garment_id,
    }
    _sidecar(staging_dir, token).write_text(
        json.dumps(sidecar_data), encoding="utf-8"
    )
    return token


def load(token: str, staging_dir: Path) -> StagingEntry | None:
    """
    Return the staging entry for *token*, or ``None`` if absent or expired.

    Expired entries are deleted on access (lazy sweep).
    """
    sc = _sidecar(staging_dir, token)
    if not sc.exists():
        return None
    try:
        data = json.loads(sc.read_text(encoding="utf-8"))
        expires_at = datetime.fromisoformat(data["expires_at"])
    except (json.JSONDecodeError, KeyError, ValueError):
        sc.unlink(missing_ok=True)
        return None

    if datetime.now(timezone.utc) >= expires_at:
        _delete_entry(staging_dir, token, data.get("ext", ""))
        return None

    return StagingEntry(
        token=token,
        ext=data["ext"],
        content_type=data["content_type"],
        fallback_used=data["fallback_used"],
        proposal=data["proposal"],
        garment_id=data.get("garment_id"),
    )


def move(
    token: str,
    ext: str,
    garment_id: str,
    staging_dir: Path,
    images_dir: Path,
) -> Path:
    """
    Move the staged image to ``images_dir/{garment_id}.{ext}`` and delete the sidecar.

    Uses ``Path.rename`` for an atomic move when both directories share the
    same filesystem (both live under ``data/``).  Returns the destination path.
    """
    src = staging_dir / f"{token}.{ext}"
    dst = images_dir / f"{garment_id}.{ext}"
    src.rename(dst)
    _sidecar(staging_dir, token).unlink(missing_ok=True)
    return dst


def sweep(staging_dir: Path) -> int:
    """
    Remove all expired staging entries from *staging_dir*.

    Called at startup (architecture §3.3).  Returns the number of entries removed.
    Malformed sidecars (unreadable JSON, missing keys) are also removed.
    """
    now = datetime.now(timezone.utc)
    removed = 0
    for sc in sorted(staging_dir.glob("*.json")):
        try:
            data = json.loads(sc.read_text(encoding="utf-8"))
            expires_at = datetime.fromisoformat(data["expires_at"])
            ext = data["ext"]
        except (json.JSONDecodeError, KeyError, ValueError):
            sc.unlink(missing_ok=True)
            removed += 1
            continue
        if now >= expires_at:
            _delete_entry(staging_dir, sc.stem, ext)
            removed += 1
    return removed
