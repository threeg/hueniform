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

import random
import uuid
from datetime import datetime, timezone

from sqlmodel import Session

from app.matcher.colour import Colour
from app.matcher.roles import Garment
from app.matcher.taxonomy import FAMILIES, classify
from app.storage.engine import Engine
from app.storage.models import GarmentColourRow, GarmentRow

# ── Colour builders (proportion set per call) ─────────────────────────────────

def _red(p: int)         -> Colour: return Colour(h=  0.0, s=80.0, l=50.0, proportion=p)
def _teal(p: int)        -> Colour: return Colour(h=180.0, s=70.0, l=50.0, proportion=p)
def _blue(p: int)        -> Colour: return Colour(h=240.0, s=70.0, l=50.0, proportion=p)
def _chartreuse(p: int)  -> Colour: return Colour(h= 90.0, s=70.0, l=40.0, proportion=p)
def _grey(p: int)        -> Colour: return Colour(h=  0.0, s= 0.0, l=50.0, proportion=p)
def _black(p: int)       -> Colour: return Colour(h=  0.0, s= 0.0, l= 6.0, proportion=p)
def _white(p: int)       -> Colour: return Colour(h=  0.0, s= 0.0, l=96.0, proportion=p)
def _navy(p: int)        -> Colour: return Colour(h=230.0, s=40.0, l=18.0, proportion=p)

# Valid garment category strings (FR-16 subset used in these fixtures).
GARMENT_TYPES = frozenset({"t_shirt", "trousers", "jumper", "jacket", "socks", "shoes", "hat", "glasses"})


# ── Scenario factories ────────────────────────────────────────────────────────

def single_valid_outfit() -> list[Garment]:
    """
    FR-13/FR-15: exactly one valid harmonious outfit possible.

    Scheme: complementary (Red t_shirt + Teal trousers; hue_distance = 180°).
    Echo slots (socks, shoes) carry neutrals and qualify unconditionally (FR-21).
    Only one garment per required slot → exactly one combination.
    """
    return [
        Garment("t_shirt",  (_red(100),)),
        Garment("trousers", (_teal(100),)),
        Garment("socks",    (_grey(100),)),
        Garment("shoes",    (_black(100),)),
    ]


def two_valid_outfits() -> list[Garment]:
    """
    FR-40/FR-39/FR-42: exactly two valid harmonious outfits.

    Two t_shirt garments both carrying Red as primary; both form a complementary
    scheme with the single Teal trousers.  Produces exactly two combinations
    without duplicate garments (FR-40).

    t_shirt_a: Red at higher saturation (s=80)
    t_shirt_b: Red at lower saturation  (s=60) — distinct value, same family
    """
    return [
        Garment("t_shirt",  (Colour(h=0.0, s=80.0, l=50.0, proportion=100),)),  # t_shirt_a
        Garment("t_shirt",  (Colour(h=0.0, s=60.0, l=50.0, proportion=100),)),  # t_shirt_b
        Garment("trousers", (_teal(100),)),
        Garment("socks",    (_grey(100),)),
        Garment("shoes",    (_black(100),)),
    ]


def neutral_fallback_only() -> list[Garment]:
    """
    FR-13 §1 / FR-14: all anchor garments are neutral; the scheme set is empty.

    evaluate_scheme(()) returns neutral-based (FR-13 rule 1), so this wardrobe
    produces valid outfits via the neutral-based path only.  No chromatic
    garment is present, so non-neutral scheme tests cannot fire.
    """
    return [
        Garment("t_shirt",  (_navy(100),)),
        Garment("trousers", (_grey(100),)),
        Garment("socks",    (_black(100),)),
        Garment("shoes",    (_white(100),)),
    ]


def no_valid_outfit_constrained_by(slot: str) -> list[Garment]:
    """
    FR-43: no valid outfit; the named slot is the provable constraint.

    For echo/adornment slots ('socks', 'shoes', 'hat', 'glasses', …):
      The anchors form a valid complementary scheme (Red + Teal), but the
      specified slot contains only a Blue garment, which is neither neutral nor
      an echo of Red or Teal — so FR-21 fails for that slot.
      Required echo slots ('socks', 'shoes') are replaced; optional adornment
      slots are appended.

    For anchor slots ('base', 'lower_body'):
      A t_shirt carrying Chartreuse (h=90°) and trousers carrying Blue (h=240°)
      are 150° apart — outside complementary tolerance (±20°) and the analogous
      arc (60°), so no FR-13 scheme matches.
    """
    _required_echo = {"socks", "shoes"}
    _optional_echo = {"hat", "glasses", "tie", "scarf", "belt",
                      "earrings", "necklace", "watch", "ring", "bracelet"}
    if slot in _required_echo | _optional_echo:
        garments = [
            Garment("t_shirt",  (_red(100),)),
            Garment("trousers", (_teal(100),)),
            Garment("socks",    (_grey(100),)),
            Garment("shoes",    (_grey(100),)),
        ]
        if slot in _optional_echo:
            # Add the constrained optional slot; required echo slots remain neutral
            garments.append(Garment(slot, (_blue(100),)))
        else:
            # Replace the failing required echo slot with non-echoing Blue
            garments = [g for g in garments if g.garment_type != slot]
            garments.append(Garment(slot, (_blue(100),)))
    else:
        # Anchor slot constraint ('base', 'lower_body'): Chartreuse + Blue = 150° apart
        garments = [
            Garment("t_shirt",  (_chartreuse(100),)),
            Garment("trousers", (_blue(100),)),
            Garment("socks",    (_grey(100),)),
            Garment("shoes",    (_black(100),)),
        ]
    return garments


def rich_echo_wardrobe() -> list[Garment]:
    """
    FR-11/FR-22: minor-colour echoes earn the echo bonus in ranking.

    T_shirt carries Red as primary (85%) and Teal as minor (15%).
    Trousers carries Teal as primary (100%).

    The Teal minor on the t_shirt echoes the Teal primary on the trousers →
    echo bonus awarded (FR-11).  Socks echo the anchor Red (FR-22).
    The scheme is complementary (Red + Teal).
    """
    return [
        Garment("t_shirt",  (_red(87), _teal(13))),
        Garment("trousers", (_teal(100),)),
        Garment("socks",    (_red(100),)),
        Garment("shoes",    (_grey(100),)),
    ]


# ── 500-garment performance fixture (§11.2, NFR-5/NFR-6) ─────────────────────

# Realistic category distribution across 500 garments.
_SLOT_COUNTS: dict[str, int] = {
    "t_shirt":  120,
    "trousers": 100,
    "socks":     70,
    "shoes":     70,
    "jumper":    50,
    "jacket":    50,
    "hat":       20,
    "glasses":   20,
}

# All taxonomy family canonical (h, s, l) values, used as colour anchors.
_CANONICAL: list[tuple[float, float, float]] = [f.canonical for f in FAMILIES]


def _random_colour(rng: random.Random, proportion: int) -> Colour:
    h, s, l = _CANONICAL[rng.randrange(len(_CANONICAL))]
    return Colour(h=h, s=s, l=l, proportion=proportion)


def _random_garment(rng: random.Random, garment_type: str) -> Garment:
    """1–2 colours summing to 100, drawn from canonical family values."""
    if rng.random() < 0.7:
        colours: tuple[Colour, ...] = (_random_colour(rng, 100),)
    else:
        split = rng.randint(60, 85)
        colours = (_random_colour(rng, split), _random_colour(rng, 100 - split))
    return Garment(garment_type, colours)


def wardrobe_500(seed: int = 42) -> list[Garment]:
    """
    500 garments generated from a seeded RNG (§11.2, NFR-5/NFR-6).

    Reproducible: the same *seed* always produces the same list.
    Distribution across all eight garment types (§_SLOT_COUNTS) and all
    taxonomy families ensures the suggestion and inventory services exercise
    realistic workloads.
    """
    rng = random.Random(seed)
    garments: list[Garment] = []
    for slot, count in _SLOT_COUNTS.items():
        for _ in range(count):
            garments.append(_random_garment(rng, slot))
    return garments


def materialise_wardrobe(engine: Engine, garments: list[Garment]) -> None:
    """
    Persist *garments* into *engine* as GarmentRow/GarmentColourRow records.

    Used by perf tests and the seeding script — inserts everything in a single
    transaction so the fixture is fast to set up.
    """
    now = datetime.now(timezone.utc).isoformat()
    with Session(engine) as session:
        for g in garments:
            gid = str(uuid.uuid4())
            session.add(GarmentRow(
                id=gid,
                type=g.garment_type,
                image_file=f"{gid}.jpg",
                thumbnail_file=f"{gid}.webp",
                created_at=now,
            ))
            session.flush()
            for pos, c in enumerate(g.colours):
                session.add(GarmentColourRow(
                    garment_id=gid,
                    position=pos,
                    h=c.h,
                    s=c.s,
                    l=c.l,
                    family=classify(c.h, c.s, c.l),
                    proportion=c.proportion,
                ))
        session.commit()
