"""
Storage utility helpers shared across service modules.

Importable by any layer that already depends on app.storage.
"""

from __future__ import annotations

from app.storage.models import GarmentColourRow


def group_colours_by_garment(
    rows: list[GarmentColourRow],
) -> dict[str, list[GarmentColourRow]]:
    """Group a flat list of colour rows into a dict keyed by garment_id."""
    result: dict[str, list[GarmentColourRow]] = {}
    for row in rows:
        result.setdefault(row.garment_id, []).append(row)
    return result
