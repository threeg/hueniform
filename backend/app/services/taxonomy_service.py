"""
Taxonomy service: exposes the matcher's colour families to the API layer.

Returns plain dicts so the api layer never needs to import matcher types
directly (architecture dependency rule, contract 5).
"""

from __future__ import annotations

from app.matcher.taxonomy import FAMILIES


def list_families() -> list[dict]:
    """
    Return all nineteen colour families as plain dicts (contract §2.2).

    Each dict has ``name``, ``neutral``, and ``canonical`` keys.  Chromatic
    families additionally carry ``representative_hue`` and ``hue_arc``.
    """
    result: list[dict] = []
    for fam in FAMILIES:
        entry: dict = {
            "name": fam.name,
            "neutral": fam.is_neutral,
            "canonical": {
                "h": fam.canonical[0],
                "s": fam.canonical[1],
                "l": fam.canonical[2],
            },
        }
        if not fam.is_neutral:
            entry["representative_hue"] = fam.representative_hue
            entry["hue_arc"] = fam.hue_arc  # tuple[float, float]
        result.append(entry)
    return result
