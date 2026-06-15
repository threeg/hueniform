"""
Engineered wardrobe scenario factories (test strategy §11.2).

Each factory returns a ``list[Garment]`` built entirely from matcher value types
(``Colour``, ``Garment``).  No evaluator dependency is introduced here — the
evaluation is the test's job.  The same definitions can later be materialised as
persisted rows for integration tests (one definition, two materialisations).

Colour choices use canonical HSL values that classify deterministically per §2:
  Red       h=  0°, s=80, l=50  — complementary with Teal (180° apart, FR-12/FR-13)
  Teal      h=180°, s=70, l=50
  Blue      h=240°, s=70, l=50  — not complementary/triadic with Red or Teal
  Chartreuse h= 90°, s=70, l=40 — clashes with Blue (150° apart, no valid scheme)
  Grey      h=  0°, s= 0, l=50  — neutral (FR-2 rule 3)
  Black     h=  0°, s= 0, l= 6  — neutral (FR-2 rule 1)
  White     h=  0°, s= 0, l=96  — neutral (FR-2 rule 2)
  Navy      h=230°, s=40, l=18  — neutral (FR-2 rule 4)
"""

from __future__ import annotations

from app.matcher.colour import Colour
from app.matcher.roles import Garment

# ── Colour builders (proportion set per call) ─────────────────────────────────

def _red(p: int)         -> Colour: return Colour(h=  0.0, s=80.0, l=50.0, proportion=p)
def _teal(p: int)        -> Colour: return Colour(h=180.0, s=70.0, l=50.0, proportion=p)
def _blue(p: int)        -> Colour: return Colour(h=240.0, s=70.0, l=50.0, proportion=p)
def _chartreuse(p: int)  -> Colour: return Colour(h= 90.0, s=70.0, l=40.0, proportion=p)
def _grey(p: int)        -> Colour: return Colour(h=  0.0, s= 0.0, l=50.0, proportion=p)
def _black(p: int)       -> Colour: return Colour(h=  0.0, s= 0.0, l= 6.0, proportion=p)
def _white(p: int)       -> Colour: return Colour(h=  0.0, s= 0.0, l=96.0, proportion=p)
def _navy(p: int)        -> Colour: return Colour(h=230.0, s=40.0, l=18.0, proportion=p)

# Valid garment type strings (FR-16)
GARMENT_TYPES = frozenset({"top", "bottom", "jersey", "jacket", "socks", "shoes", "hat", "accessory"})


# ── Scenario factories ────────────────────────────────────────────────────────

def single_valid_outfit() -> list[Garment]:
    """
    FR-13/FR-15: exactly one valid harmonious outfit possible.

    Scheme: complementary (Red top + Teal bottom; hue_distance = 180°).
    Echo slots (socks, shoes) carry neutrals and qualify unconditionally (FR-21).
    Only one garment per required slot → exactly one combination.
    """
    return [
        Garment("top",    (_red(100),)),
        Garment("bottom", (_teal(100),)),
        Garment("socks",  (_grey(100),)),
        Garment("shoes",  (_black(100),)),
    ]


def two_valid_outfits() -> list[Garment]:
    """
    FR-40/FR-39/FR-42: exactly two valid harmonious outfits.

    Two top garments both carrying Red as primary; both form a complementary
    scheme with the single Teal bottom.  Produces exactly two combinations
    without duplicate garments (FR-40).

    top_a: Red at higher saturation (s=80)
    top_b: Red at lower saturation  (s=60) — distinct value, same family
    """
    return [
        Garment("top",    (Colour(h=0.0, s=80.0, l=50.0, proportion=100),)),  # top_a
        Garment("top",    (Colour(h=0.0, s=60.0, l=50.0, proportion=100),)),  # top_b
        Garment("bottom", (_teal(100),)),
        Garment("socks",  (_grey(100),)),
        Garment("shoes",  (_black(100),)),
    ]


def neutral_fallback_only() -> list[Garment]:
    """
    FR-13 §1 / FR-14: all anchor garments are neutral; the scheme set is empty.

    evaluate_scheme(()) returns neutral-based (FR-13 rule 1), so this wardrobe
    produces valid outfits via the neutral-based path only.  No chromatic
    garment is present, so non-neutral scheme tests cannot fire.
    """
    return [
        Garment("top",    (_navy(100),)),
        Garment("bottom", (_grey(100),)),
        Garment("socks",  (_black(100),)),
        Garment("shoes",  (_white(100),)),
    ]


def no_valid_outfit_constrained_by(slot: str) -> list[Garment]:
    """
    FR-43: no valid outfit; the named slot is the provable constraint.

    For echo slots ('socks', 'shoes', 'hat', 'accessory'):
      The anchors form a valid complementary scheme (Red + Teal), but the
      specified slot contains only a Blue garment, which is neither neutral nor
      an echo of Red or Teal — so FR-21 fails for that slot.

    For anchor slots ('top', 'bottom'):
      The top carries Chartreuse (h=90°) and the bottom carries Blue (h=240°),
      which are 150° apart — outside the complementary tolerance (±20°) and
      outside the analogous arc (60°), so no FR-13 scheme matches.  The failing
      anchor is the named slot.
    """
    if slot in {"socks", "shoes", "hat", "accessory"}:
        garments = [
            Garment("top",    (_red(100),)),
            Garment("bottom", (_teal(100),)),
            Garment("socks",  (_grey(100),)),
            Garment("shoes",  (_grey(100),)),
        ]
        if slot in {"hat", "accessory"}:
            # Add the constrained optional slot; other echo slots remain neutral
            garments.append(Garment(slot, (_blue(100),)))
        else:
            # Replace the failing required echo slot with non-echoing Blue
            garments = [g for g in garments if g.garment_type != slot]
            garments.append(Garment(slot, (_blue(100),)))
    else:
        # Anchor slot constraint: Chartreuse + Blue = 150° apart, no valid scheme
        garments = [
            Garment("top",    (_chartreuse(100),)),
            Garment("bottom", (_blue(100),)),
            Garment("socks",  (_grey(100),)),
            Garment("shoes",  (_black(100),)),
        ]
    return garments


def rich_echo_wardrobe() -> list[Garment]:
    """
    FR-11/FR-22: minor-colour echoes earn the echo bonus in ranking.

    Top carries Red as primary (85%) and Teal as minor (15%).
    Bottom carries Teal as primary (100%).

    The Teal minor on the top echoes the Teal primary on the bottom →
    echo bonus awarded (FR-11).  Socks echo the anchor Red (FR-22).
    The scheme is complementary (Red + Teal).
    """
    return [
        Garment("top",    (_red(87), _teal(13))),
        Garment("bottom", (_teal(100),)),
        Garment("socks",  (_red(100),)),
        Garment("shoes",  (_grey(100),)),
    ]
