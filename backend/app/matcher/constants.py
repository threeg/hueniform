"""
Named constants for the colour matcher (requirements §1.4).

Every numeric threshold in requirements §2–§5 and §7 is defined here so
that tuning a value requires a single change.  Changing a constant fails
the drift-guard test in ``tests/matcher/test_constants.py``, which forces
the change to be recorded in requirements before the test is updated.

Standard library only (NFR-9).
"""

# ── §2.2 Chromatic arc width (FR-4) ─────────────────────────────────────────
# Each chromatic family owns a half-open 30° hue arc.
CHROMATIC_ARC: float = 30.0

# ── §2.1 Neutral rule thresholds (FR-2) — evaluated in this order ─────────────

# 1. Black — L < BLACK_L_MAX
BLACK_L_MAX: float = 12.0

# 2. White — L > WHITE_L_MIN and S < WHITE_S_MAX
WHITE_L_MIN: float = 92.0
WHITE_S_MAX: float = 20.0

# 3. Grey — S < GREY_S_MAX and GREY_L_MIN ≤ L ≤ GREY_L_MAX
GREY_S_MAX: float = 10.0
GREY_L_MIN: float = 12.0
GREY_L_MAX: float = 92.0

# 4. Navy — NAVY_H_LOW ≤ H ≤ NAVY_H_HIGH and S ≥ NAVY_S_MIN and L < NAVY_L_MAX
NAVY_H_LOW:  float = 200.0
NAVY_H_HIGH: float = 260.0
NAVY_S_MIN:  float = 10.0
NAVY_L_MAX:  float = 25.0

# 5. Denim — DENIM_H_LOW ≤ H ≤ DENIM_H_HIGH and DENIM_S_LOW ≤ S < DENIM_S_HIGH
#            and DENIM_L_LOW ≤ L ≤ DENIM_L_HIGH
DENIM_H_LOW:  float = 200.0
DENIM_H_HIGH: float = 250.0
DENIM_S_LOW:  float = 10.0
DENIM_S_HIGH: float = 50.0
DENIM_L_LOW:  float = 25.0
DENIM_L_HIGH: float = 65.0

# 6. Brown — BROWN_H_LOW ≤ H ≤ BROWN_H_HIGH and BROWN_S_LOW ≤ S ≤ BROWN_S_HIGH
#            and BROWN_L_LOW ≤ L < BROWN_L_HIGH
BROWN_H_LOW:  float = 15.0
BROWN_H_HIGH: float = 50.0
BROWN_S_LOW:  float = 10.0
BROWN_S_HIGH: float = 70.0
BROWN_L_LOW:  float = 15.0
BROWN_L_HIGH: float = 45.0

# 7. Beige/Tan — BEIGE_H_LOW ≤ H ≤ BEIGE_H_HIGH and BEIGE_S_LOW ≤ S ≤ BEIGE_S_HIGH
#               and BEIGE_L_LOW ≤ L ≤ BEIGE_L_HIGH
BEIGE_H_LOW:  float = 20.0
BEIGE_H_HIGH: float = 60.0
BEIGE_S_LOW:  float = 10.0
BEIGE_S_HIGH: float = 45.0
BEIGE_L_LOW:  float = 60.0
BEIGE_L_HIGH: float = 88.0

# 8. Cream — CREAM_H_LOW ≤ H ≤ CREAM_H_HIGH and CREAM_S_LOW ≤ S ≤ CREAM_S_HIGH
#            and L ≥ CREAM_L_MIN  (lighter than Beige — see FR-2)
CREAM_H_LOW:  float = 20.0
CREAM_H_HIGH: float = 70.0
CREAM_S_LOW:  float = 10.0
CREAM_S_HIGH: float = 45.0
CREAM_L_MIN:  float = 88.0

# ── §3 Role cut-offs (FR-7) ──────────────────────────────────────────────────
# proportion ≥ PRIMARY_THRESHOLD → primary (or dual-primary when two qualify)
# SECONDARY_THRESHOLD ≤ proportion < PRIMARY_THRESHOLD → secondary
# proportion < SECONDARY_THRESHOLD → minor
PRIMARY_THRESHOLD:   int = 30
SECONDARY_THRESHOLD: int = 15

# ── §4 Harmony tolerances (FR-13) ────────────────────────────────────────────
# Complementary: two clusters whose hues are 180° ± COMPLEMENTARY_TOLERANCE
COMPLEMENTARY_TOLERANCE: float = 20.0
# Triadic: three clusters pairwise 120° ± TRIADIC_TOLERANCE
TRIADIC_TOLERANCE: float = 15.0
# Analogous: all scheme-set hues within a single ANALOGOUS_ARC° window
ANALOGOUS_ARC: float = 60.0

# ── §7 / FR-41 Ranking weights ────────────────────────────────────────────────
# Score = WEIGHT_SCHEME_STRENGTH × scheme_strength
#       + WEIGHT_ECHO_BONUS × echo_count
# Variety is applied as a post-score greedy penalty (see matcher.ranking).
WEIGHT_SCHEME_STRENGTH: int = 100
WEIGHT_ECHO_BONUS:      int = 10

# ── §7 / FR-41 Variety penalty ────────────────────────────────────────────────
# Greedy variety selection: each garment shared with an already-selected outfit
# subtracts this value from the candidate's adjusted score (FR-41.3).
# Raised from 5 → 15 in v0.2.0 to strengthen outfit diversity (F5).
WEIGHT_VARIETY: int = 15

# ── §7 / FR-41 All-neutral strength ──────────────────────────────────────────
# Outfits with an empty chromatic scheme set score at this fixed strength —
# just below a perfect chromatic scheme (1.0) so they are first-class results
# that still rank below an otherwise equal chromatic outfit (FR-41).
NEUTRAL_BASED_STRENGTH: float = 0.98

# ── §7 / FR-48 Suggestion count bounds ───────────────────────────────────────
COUNT_MIN:     int = 1
COUNT_MAX:     int = 25
COUNT_DEFAULT: int = 3

# ── §6.1 / FR-27 Detection fallback threshold ────────────────────────────────
# If the fraction of non-transparent pixels in the rembg mask falls below this
# value the pipeline treats segmentation as failed and falls back to whole-image
# clustering, setting fallback_used = True (FR-27).
MINIMUM_FOREGROUND: float = 0.15

# ── §6.1 Detection k-selection elbow factor ───────────────────────────────────
# select_k stops adding clusters when the marginal inertia improvement falls
# below K_ELBOW_FACTOR × the first improvement (k=1→k=2).
K_ELBOW_FACTOR: float = 0.05

# ── Architecture §4.3 / FR-42 Candidate cap ──────────────────────────────────
# Anchor enumeration is shuffled and capped at this value.  Keeps NFR-5's
# 2-second bound at 500 garments while supplying FR-42's permitted
# non-determinism via the shuffle.
MAX_ANCHOR_CANDIDATES: int = 200

# Echo-slot combinations are shuffled and capped per anchor to prevent
# combinatorial explosion when echo slots (socks, shoes, hat, accessory) are
# numerous (NFR-5).  The shuffle is seeded from the same injected RNG that
# shuffles anchors, preserving FR-42 non-determinism.
MAX_ECHO_COMBOS: int = 50

# ── §5 / FR-16 Slot model (v0.2.0) ───────────────────────────────────────────

# Four-level upper-body layer order, innermost→outermost (FR-49.1).
# `jersey` is no longer a slot key; the four new keys are `base`, `shirt`, `mid`, `outer`.
UPPER_BODY_LAYERS: tuple[str, ...] = ("base", "shirt", "mid", "outer")

# All slot keys in the v0.2.0 model (FR-16).
ALL_SLOTS: frozenset[str] = frozenset({
    "base", "shirt", "mid", "outer",    # upper-body layers
    "hat", "glasses", "earrings",       # head
    "tie", "scarf", "necklace",         # neck
    "watch", "ring", "bracelet",        # hand
    "lower_body",                       # lower body
    "belt",                             # waist
    "socks", "shoes",                   # feet
})

# All garment categories in the v0.2.0 model (FR-16).
# Note: `jersey` is not a category — superseded by `jumper` et al. in the `mid` slot.
ALL_CATEGORIES: frozenset[str] = frozenset({
    # upper body — base slot
    "t_shirt", "vest", "long_sleeve",
    # upper body — shirt slot
    "shirt", "blouse", "polo",
    # upper body — mid slot
    "jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat",
    # upper body — outer slot
    "jacket", "blazer", "coat",
    # head
    "hat", "cap", "beanie",
    "glasses", "sunglasses",
    "earrings",
    # neck
    "tie", "scarf",
    "necklace",
    # hand
    "watch", "ring", "bracelet",
    # lower body
    "trousers", "jeans", "chinos", "shorts", "skirt",
    # one-piece (lower body + base simultaneously)
    "dress", "jumpsuit",
    # waist
    "belt",
    # feet
    "socks",
    "shoes", "boots", "trainers", "sandals",
})

# Category → primary slot mapping (FR-16).
# One-piece categories map to `lower_body`; they additionally occupy `base` (FR-49.2).
CATEGORY_SLOT: dict[str, str] = {
    # upper body
    "t_shirt": "base",    "vest": "base",     "long_sleeve": "base",
    "shirt": "shirt",     "blouse": "shirt",  "polo": "shirt",
    "jumper": "mid",      "hoodie": "mid",    "cardigan": "mid",
    "sweatshirt": "mid",  "track_top": "mid", "waistcoat": "mid",
    "jacket": "outer",    "blazer": "outer",  "coat": "outer",
    # head
    "hat": "hat",      "cap": "hat",       "beanie": "hat",
    "glasses": "glasses", "sunglasses": "glasses",
    "earrings": "earrings",
    # neck
    "tie": "tie",    "scarf": "scarf",
    "necklace": "necklace",
    # hand
    "watch": "watch",  "ring": "ring",  "bracelet": "bracelet",
    # lower body
    "trousers": "lower_body", "jeans": "lower_body", "chinos": "lower_body",
    "shorts": "lower_body",   "skirt": "lower_body",
    # one-piece (primary slot is lower_body; also occupies base — see ONE_PIECE_UPPER_SLOT)
    "dress": "lower_body", "jumpsuit": "lower_body",
    # waist
    "belt": "belt",
    # feet
    "socks": "socks",
    "shoes": "shoes", "boots": "shoes", "trainers": "shoes", "sandals": "shoes",
}

# One-piece categories and the additional upper-body slot they occupy (FR-49.2).
ONE_PIECE_CATEGORIES: frozenset[str] = frozenset({"dress", "jumpsuit"})
ONE_PIECE_UPPER_SLOT: str = "base"

# Statement adornment slot keys — visible anchors that drive scheme evaluation (FR-49.3).
STATEMENT_ADORNMENT_SLOTS: frozenset[str] = frozenset({
    "hat", "tie", "scarf", "belt", "socks", "shoes",
})

# Minor adornment slot keys — echo-only, never disqualify (FR-49.3).
MINOR_ADORNMENT_SLOTS: frozenset[str] = frozenset({
    "glasses", "earrings", "necklace", "watch", "ring", "bracelet",
})

# Default-selected slots for a new suggestion request (FR-51.1).
DEFAULT_SLOTS: frozenset[str] = frozenset({"base", "lower_body", "socks", "shoes"})

# The mandatory slot that may never be deselected from a request (FR-51.2).
MANDATORY_SLOT: str = "lower_body"
