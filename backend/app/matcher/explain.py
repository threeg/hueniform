"""
Plain-language outfit explanation (FR-37, FR-38).

Public API
----------
``render(result: EvaluationResult) -> str``
    Generate a deterministic plain-language description from the evaluation.

Standard library only (NFR-9).
"""

from __future__ import annotations

from app.matcher.ranking import EvaluationResult
from app.matcher.roles import GarmentRoles
from app.matcher.slots import (
    ECHO_SLOTS,
    get_anchor_chromatic_families,
    get_anchor_types,
    qualify_echo_slot,
)
from app.matcher.taxonomy import classify as _classify
from app.matcher.taxonomy import is_neutral as _is_neutral

# Presentation order for deterministic slot listing (outermost → innermost → adornments)
_SLOT_ORDER: tuple[str, ...] = (
    "outer", "mid", "shirt", "base", "lower_body",
    "hat", "tie", "scarf", "belt", "socks", "shoes",
    "glasses", "earrings", "necklace", "watch", "ring", "bracelet",
)


def _primary_families(roles: GarmentRoles) -> list[str]:
    """Colour family names for all primary colours, proportion-order."""
    return [_classify(c.h, c.s, c.l) for c in roles.primaries]


def render(result: EvaluationResult) -> str:
    """
    Produce a plain-language explanation of *result* (FR-37, FR-38).

    Text is derived solely from the EvaluationResult — no canned phrases
    independent of the result's fields.

    Three output shapes:
      - Sentinel (empty outfit): names the constraining slot.
      - Fallback: labelled as a neutral fallback; lists slot colours.
      - Normal: names the scheme, each slot's colour and role, plus any
        minor-colour echoes.
    """
    # ── Zero-result sentinel ──────────────────────────────────────────────────
    if not result.outfit:
        slot = result.constraining_slot
        if slot:
            return (
                f"No harmonious outfit could be assembled. "
                f"The most constrained slot was '{slot}'."
            )
        return "No harmonious outfit could be assembled."

    # ── Per-slot colour descriptions ──────────────────────────────────────────
    anchor_types = set(get_anchor_types(result.outfit))
    slot_descs: list[str] = []
    for gtype in _SLOT_ORDER:
        if gtype not in result.outfit:
            continue
        roles = result.garment_roles[gtype]
        families = _primary_families(roles)
        if not families:
            colour_str = "no primary colour"
        else:
            colour_str = "/".join(families)

        if gtype in anchor_types:
            role_label = "anchor"
        elif not families or all(_is_neutral(f) for f in families):
            role_label = "neutral"
        else:
            role_label = "echo"

        slot_descs.append(f"{gtype}: {colour_str} ({role_label})")

    slots_text = "; ".join(slot_descs)

    # ── Minor-colour echo summary ─────────────────────────────────────────────
    anchor_chromatic = get_anchor_chromatic_families(result.outfit)
    echo_families: set[str] = set()
    for gtype in sorted(ECHO_SLOTS):
        if gtype in result.outfit:
            eq = qualify_echo_slot(result.outfit[gtype], anchor_chromatic)
            echo_families.update(eq.minor_echoes)

    echo_text = ""
    if echo_families:
        families_str = ", ".join(sorted(echo_families))
        echo_text = f" Minor echoes: {families_str}."

    # ── Scheme label ──────────────────────────────────────────────────────────
    if result.is_fallback:
        return f"Neutral fallback. {slots_text}.{echo_text}"

    scheme = result.scheme_result.scheme if result.scheme_result else "neutral-based"
    scheme_label = scheme.replace("-", " ").capitalize()
    return f"{scheme_label} scheme. {slots_text}.{echo_text}"
