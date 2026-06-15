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
WEIGHT_VARIETY: int = 5

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
