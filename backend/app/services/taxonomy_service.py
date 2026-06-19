"""
Taxonomy service: exposes the matcher's colour families and slot/region model to the API layer.

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


def list_regions() -> list[dict]:
    """
    Return the slot/region model as plain dicts (contract §2.2).

    Four regions: head, upper_body, lower_body, feet.  Each slot dict carries
    slot, label, categories, role, default_selected, plus the optional fields
    layer_order (anchor layers only), mandatory/one_piece_* (lower_body only).
    """
    return [
        {
            "region": "head",
            "slots": [
                {"slot": "hat",      "label": "Hat",      "categories": ["hat", "cap", "beanie"],      "role": "statement", "default_selected": False},
                {"slot": "glasses",  "label": "Glasses",  "categories": ["glasses", "sunglasses"],     "role": "minor",     "default_selected": False},
                {"slot": "earrings", "label": "Earrings", "categories": ["earrings"],                  "role": "minor",     "default_selected": False},
            ],
        },
        {
            "region": "upper_body",
            "slots": [
                {"slot": "base",     "label": "Base",        "categories": ["t_shirt", "vest", "long_sleeve"],                                   "role": "anchor", "layer_order": 0, "default_selected": True},
                {"slot": "shirt",    "label": "Shirt",       "categories": ["shirt", "blouse", "polo"],                                          "role": "anchor", "layer_order": 1, "default_selected": False},
                {"slot": "mid",      "label": "Mid-layer",   "categories": ["jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat"], "role": "anchor", "layer_order": 2, "default_selected": False},
                {"slot": "outer",    "label": "Outer layer", "categories": ["jacket", "blazer", "coat"],                                          "role": "anchor", "layer_order": 3, "default_selected": False},
                {"slot": "tie",      "label": "Tie",         "categories": ["tie"],       "role": "statement", "default_selected": False},
                {"slot": "scarf",    "label": "Scarf",       "categories": ["scarf"],     "role": "statement", "default_selected": False},
                {"slot": "necklace", "label": "Necklace",    "categories": ["necklace"],  "role": "minor",     "default_selected": False},
                {"slot": "watch",    "label": "Watch",       "categories": ["watch"],     "role": "minor",     "default_selected": False},
                {"slot": "ring",     "label": "Ring",        "categories": ["ring"],      "role": "minor",     "default_selected": False},
                {"slot": "bracelet", "label": "Bracelet",    "categories": ["bracelet"],  "role": "minor",     "default_selected": False},
            ],
        },
        {
            "region": "lower_body",
            "slots": [
                {
                    "slot": "lower_body", "label": "Lower body",
                    "categories": ["trousers", "jeans", "chinos", "shorts", "skirt", "dress", "jumpsuit"],
                    "role": "anchor", "mandatory": True, "default_selected": True,
                    "one_piece_categories": ["dress", "jumpsuit"],
                    "one_piece_also_occupies": ["base"],
                },
                {"slot": "belt", "label": "Belt", "categories": ["belt"], "role": "statement", "default_selected": False},
            ],
        },
        {
            "region": "feet",
            "slots": [
                {"slot": "socks", "label": "Socks", "categories": ["socks"],                              "role": "statement", "default_selected": True},
                {"slot": "shoes", "label": "Shoes", "categories": ["shoes", "boots", "trainers", "sandals"], "role": "statement", "default_selected": True},
            ],
        },
    ]
