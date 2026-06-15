"""
Boundary HSL tables and canonical values for the colour taxonomy.

All values are taken directly from requirements §2.1–§2.2 (FR-1–FR-5).  This
module has *no* imports from the matcher so it can be loaded before the matcher
is implemented — changing a threshold here is the first step of a requirements
§1.4 change.

Rows are (h, s, l, expected_family) unless noted.  Edge notation in comments:
  - "boundary−" means one small step (0.1) below the threshold
  - "boundary+" means the threshold value itself or one small step above it,
    whichever crosses from one side of the rule to the other
"""

from __future__ import annotations

# ── Neutral rule boundaries (FR-2, §2.1) ────────────────────────────────────
# Each block pairs the "just inside" and "just outside" value.

BLACK_THRESHOLD_L = 12.0     # L < 12 → Black
WHITE_THRESHOLD_L = 92.0     # L > 92 (and S < 20) → White
WHITE_THRESHOLD_S = 20.0
GREY_THRESHOLD_S = 10.0      # S < 10 (and 12 ≤ L ≤ 92) → Grey
NAVY_H_LOW  = 200.0          # 200 ≤ H ≤ 260
NAVY_H_HIGH = 260.0
NAVY_S_MIN  = 10.0           # S ≥ 10
NAVY_L_MAX  = 25.0           # L < 25
DENIM_H_LOW  = 200.0         # 200 ≤ H ≤ 250
DENIM_H_HIGH = 250.0
DENIM_S_LOW  = 10.0          # 10 ≤ S < 50
DENIM_S_HIGH = 50.0
DENIM_L_LOW  = 25.0          # 25 ≤ L ≤ 65
DENIM_L_HIGH = 65.0
BROWN_H_LOW  = 15.0          # 15 ≤ H ≤ 50
BROWN_H_HIGH = 50.0
BROWN_S_LOW  = 10.0          # 10 ≤ S ≤ 70
BROWN_S_HIGH = 70.0
BROWN_L_LOW  = 15.0          # 15 ≤ L < 45
BROWN_L_HIGH = 45.0
BEIGE_H_LOW  = 20.0          # 20 ≤ H ≤ 60
BEIGE_H_HIGH = 60.0
BEIGE_S_LOW  = 10.0          # 10 ≤ S ≤ 45
BEIGE_S_HIGH = 45.0
BEIGE_L_LOW  = 60.0          # 60 ≤ L ≤ 88
BEIGE_L_HIGH = 88.0

# ── Chromatic arc width (FR-4, §2.2) ────────────────────────────────────────
CHROMATIC_ARC = 30.0         # each family owns a 30° half-open arc

# ── Chromatic arc boundaries — every boundary between adjacent families ──────
# Rows: (h_boundary, family_at_boundary, family_just_below)
# FR-4: boundary value belongs to the arc that *starts* there.
CHROMATIC_ARC_BOUNDARIES: list[tuple[float, str, str]] = [
    (15.0,  "Orange",     "Red"),
    (45.0,  "Yellow",     "Orange"),
    (75.0,  "Chartreuse", "Yellow"),
    (105.0, "Green",      "Chartreuse"),
    (135.0, "Mint",       "Green"),
    (165.0, "Teal",       "Mint"),
    (195.0, "Azure",      "Teal"),
    (225.0, "Blue",       "Azure"),
    (255.0, "Violet",     "Blue"),
    (285.0, "Magenta",    "Violet"),
    (315.0, "Pink",       "Magenta"),
    (345.0, "Red",        "Pink"),
]

# ── Canonical HSL values (contract §2.2, GET /api/taxonomy) ─────────────────
# Each canonical must classify into its own family (FR-1, contract §2.2).
# Format: {family: (h, s, l)}
CANONICAL: dict[str, tuple[float, float, float]] = {
    # Neutrals
    "Black":    (0.0,   0.0,  6.0),
    "White":    (0.0,   0.0, 96.0),
    "Grey":     (0.0,   0.0, 50.0),
    "Navy":     (230.0, 40.0, 18.0),
    "Denim":    (215.0, 30.0, 45.0),
    "Brown":    (25.0,  40.0, 30.0),
    "Beige/Tan":(35.0,  30.0, 72.0),
    # Chromatics — canonical is the representative hue (arc centre)
    "Red":      (0.0,   80.0, 50.0),
    "Orange":   (30.0,  90.0, 55.0),
    "Yellow":   (60.0,  90.0, 50.0),
    "Chartreuse":(90.0, 70.0, 40.0),
    "Green":    (120.0, 60.0, 40.0),
    "Mint":     (150.0, 60.0, 45.0),
    "Teal":     (180.0, 70.0, 50.0),
    "Azure":    (210.0, 70.0, 50.0),
    "Blue":     (240.0, 70.0, 50.0),
    "Violet":   (270.0, 60.0, 45.0),
    "Magenta":  (300.0, 70.0, 45.0),
    "Pink":     (330.0, 70.0, 65.0),
}

ALL_FAMILIES: list[str] = list(CANONICAL.keys())
NEUTRAL_FAMILIES: list[str] = [
    "Black", "White", "Grey", "Navy", "Denim", "Brown", "Beige/Tan"
]
CHROMATIC_FAMILIES: list[str] = [f for f in ALL_FAMILIES if f not in NEUTRAL_FAMILIES]

# ── Representative hues (§2.2) — arc centres ────────────────────────────────
REPRESENTATIVE_HUES: dict[str, float] = {
    "Red": 0.0, "Orange": 30.0, "Yellow": 60.0, "Chartreuse": 90.0,
    "Green": 120.0, "Mint": 150.0, "Teal": 180.0, "Azure": 210.0,
    "Blue": 240.0, "Violet": 270.0, "Magenta": 300.0, "Pink": 330.0,
}

# ── Role cut-offs (FR-7) ─────────────────────────────────────────────────────
PRIMARY_THRESHOLD   = 30    # proportion ≥ 30 → primary (or dual-primary)
SECONDARY_THRESHOLD = 15    # 15 ≤ proportion < 30 → secondary; < 15 → minor

# ── Harmony tolerances (FR-13) ───────────────────────────────────────────────
COMPLEMENTARY_TOLERANCE = 20.0   # 180° ± 20
TRIADIC_TOLERANCE       = 15.0   # 120° ± 15
ANALOGOUS_ARC           = 60.0   # all scheme-set hues within 60°
