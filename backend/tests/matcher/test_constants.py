"""
Drift-guard for matcher.constants (test strategy §4.1).

Every constant is asserted equal to its documented value.  A failure here
means a threshold was changed without a matching requirements §1.4 update —
fix the requirements first, then update both the constant and this assertion.
Each failure message cites the requirements section it mirrors.
"""

from app.matcher import constants as C


# ── §2.2 Chromatic arc width (FR-4) ─────────────────────────────────────────

def test_chromatic_arc() -> None:
    assert C.CHROMATIC_ARC == 30.0, (
        "CHROMATIC_ARC must be 30° — requirements §2.2 / FR-4"
    )


# ── §2.1 Neutral rule thresholds (FR-2) ──────────────────────────────────────

def test_black_l_max() -> None:
    assert C.BLACK_L_MAX == 12.0, "BLACK_L_MAX — requirements §2.1 rule 1"

def test_white_l_min() -> None:
    assert C.WHITE_L_MIN == 92.0, "WHITE_L_MIN — requirements §2.1 rule 2"

def test_white_s_max() -> None:
    assert C.WHITE_S_MAX == 20.0, "WHITE_S_MAX — requirements §2.1 rule 2"

def test_grey_s_max() -> None:
    assert C.GREY_S_MAX == 10.0, "GREY_S_MAX — requirements §2.1 rule 3"

def test_grey_l_min() -> None:
    assert C.GREY_L_MIN == 12.0, "GREY_L_MIN — requirements §2.1 rule 3"

def test_grey_l_max() -> None:
    assert C.GREY_L_MAX == 92.0, "GREY_L_MAX — requirements §2.1 rule 3"

def test_navy_h_low() -> None:
    assert C.NAVY_H_LOW == 200.0, "NAVY_H_LOW — requirements §2.1 rule 4"

def test_navy_h_high() -> None:
    assert C.NAVY_H_HIGH == 260.0, "NAVY_H_HIGH — requirements §2.1 rule 4"

def test_navy_s_min() -> None:
    assert C.NAVY_S_MIN == 10.0, "NAVY_S_MIN — requirements §2.1 rule 4"

def test_navy_l_max() -> None:
    assert C.NAVY_L_MAX == 25.0, "NAVY_L_MAX — requirements §2.1 rule 4"

def test_denim_h_low() -> None:
    assert C.DENIM_H_LOW == 200.0, "DENIM_H_LOW — requirements §2.1 rule 5"

def test_denim_h_high() -> None:
    assert C.DENIM_H_HIGH == 250.0, "DENIM_H_HIGH — requirements §2.1 rule 5"

def test_denim_s_low() -> None:
    assert C.DENIM_S_LOW == 10.0, "DENIM_S_LOW — requirements §2.1 rule 5"

def test_denim_s_high() -> None:
    assert C.DENIM_S_HIGH == 50.0, "DENIM_S_HIGH — requirements §2.1 rule 5"

def test_denim_l_low() -> None:
    assert C.DENIM_L_LOW == 25.0, "DENIM_L_LOW — requirements §2.1 rule 5"

def test_denim_l_high() -> None:
    assert C.DENIM_L_HIGH == 65.0, "DENIM_L_HIGH — requirements §2.1 rule 5"

def test_brown_h_low() -> None:
    assert C.BROWN_H_LOW == 15.0, "BROWN_H_LOW — requirements §2.1 rule 6"

def test_brown_h_high() -> None:
    assert C.BROWN_H_HIGH == 50.0, "BROWN_H_HIGH — requirements §2.1 rule 6"

def test_brown_s_low() -> None:
    assert C.BROWN_S_LOW == 10.0, "BROWN_S_LOW — requirements §2.1 rule 6"

def test_brown_s_high() -> None:
    assert C.BROWN_S_HIGH == 70.0, "BROWN_S_HIGH — requirements §2.1 rule 6"

def test_brown_l_low() -> None:
    assert C.BROWN_L_LOW == 15.0, "BROWN_L_LOW — requirements §2.1 rule 6"

def test_brown_l_high() -> None:
    assert C.BROWN_L_HIGH == 45.0, "BROWN_L_HIGH — requirements §2.1 rule 6"

def test_beige_h_low() -> None:
    assert C.BEIGE_H_LOW == 20.0, "BEIGE_H_LOW — requirements §2.1 rule 7"

def test_beige_h_high() -> None:
    assert C.BEIGE_H_HIGH == 60.0, "BEIGE_H_HIGH — requirements §2.1 rule 7"

def test_beige_s_low() -> None:
    assert C.BEIGE_S_LOW == 10.0, "BEIGE_S_LOW — requirements §2.1 rule 7"

def test_beige_s_high() -> None:
    assert C.BEIGE_S_HIGH == 45.0, "BEIGE_S_HIGH — requirements §2.1 rule 7"

def test_beige_l_low() -> None:
    assert C.BEIGE_L_LOW == 60.0, "BEIGE_L_LOW — requirements §2.1 rule 7"

def test_beige_l_high() -> None:
    assert C.BEIGE_L_HIGH == 88.0, "BEIGE_L_HIGH — requirements §2.1 rule 7"


# ── §2.1 Cream thresholds (FR-2 rule 8) ──────────────────────────────────────

def test_cream_h_low() -> None:
    assert C.CREAM_H_LOW == 20.0, "CREAM_H_LOW — requirements §2.1 rule 8"

def test_cream_h_high() -> None:
    assert C.CREAM_H_HIGH == 70.0, "CREAM_H_HIGH — requirements §2.1 rule 8"

def test_cream_s_low() -> None:
    assert C.CREAM_S_LOW == 10.0, "CREAM_S_LOW — requirements §2.1 rule 8"

def test_cream_s_high() -> None:
    assert C.CREAM_S_HIGH == 45.0, "CREAM_S_HIGH — requirements §2.1 rule 8"

def test_cream_l_min() -> None:
    assert C.CREAM_L_MIN == 88.0, "CREAM_L_MIN — requirements §2.1 rule 8"


# ── §3 Role cut-offs (FR-7) ──────────────────────────────────────────────────

def test_primary_threshold() -> None:
    assert C.PRIMARY_THRESHOLD == 30, (
        "PRIMARY_THRESHOLD must be 30 — requirements §3 / FR-7"
    )

def test_secondary_threshold() -> None:
    assert C.SECONDARY_THRESHOLD == 15, (
        "SECONDARY_THRESHOLD must be 15 — requirements §3 / FR-7"
    )


# ── §4 Harmony tolerances (FR-13) ────────────────────────────────────────────

def test_complementary_tolerance() -> None:
    assert C.COMPLEMENTARY_TOLERANCE == 20.0, (
        "COMPLEMENTARY_TOLERANCE must be 20° — requirements §4 / FR-13"
    )

def test_triadic_tolerance() -> None:
    assert C.TRIADIC_TOLERANCE == 15.0, (
        "TRIADIC_TOLERANCE must be 15° — requirements §4 / FR-13"
    )

def test_analogous_arc() -> None:
    assert C.ANALOGOUS_ARC == 60.0, (
        "ANALOGOUS_ARC must be 60° — requirements §4 / FR-13"
    )


# ── §7 / FR-41 Ranking weights ────────────────────────────────────────────────

def test_weight_scheme_strength() -> None:
    assert C.WEIGHT_SCHEME_STRENGTH == 100, (
        "WEIGHT_SCHEME_STRENGTH — requirements §7 / FR-41 (named constant)"
    )

def test_weight_echo_bonus() -> None:
    assert C.WEIGHT_ECHO_BONUS == 10, (
        "WEIGHT_ECHO_BONUS — requirements §7 / FR-41 (named constant)"
    )


# ── §7 / FR-41 Variety penalty ────────────────────────────────────────────────

def test_weight_variety() -> None:
    assert C.WEIGHT_VARIETY == 15, (
        "WEIGHT_VARIETY — requirements §7 / FR-41.3 (raised to 15 in v0.2.0 — F5)"
    )


# ── §7 / FR-41 All-neutral strength ──────────────────────────────────────────

def test_neutral_based_strength() -> None:
    assert C.NEUTRAL_BASED_STRENGTH == 0.98, (
        "NEUTRAL_BASED_STRENGTH — requirements §7 / FR-41 (named constant)"
    )


# ── §7 / FR-48 Suggestion count bounds ───────────────────────────────────────

def test_count_min() -> None:
    assert C.COUNT_MIN == 1, "COUNT_MIN — requirements §7 / FR-48 (named constant)"

def test_count_max() -> None:
    assert C.COUNT_MAX == 25, "COUNT_MAX — requirements §7 / FR-48 (named constant)"

def test_count_default() -> None:
    assert C.COUNT_DEFAULT == 3, "COUNT_DEFAULT — requirements §7 / FR-48 (named constant)"


# ── §6.1 / FR-27 Detection thresholds ────────────────────────────────────────

def test_minimum_foreground() -> None:
    assert C.MINIMUM_FOREGROUND == 0.15, (
        "MINIMUM_FOREGROUND — requirements §6.1 / FR-27 (named constant)"
    )

def test_k_elbow_factor() -> None:
    assert C.K_ELBOW_FACTOR == 0.05, (
        "K_ELBOW_FACTOR — detection k-selection elbow threshold (named constant)"
    )


# ── Architecture §4.3 / FR-42 Candidate cap ──────────────────────────────────

def test_max_anchor_candidates() -> None:
    assert C.MAX_ANCHOR_CANDIDATES == 200, (
        "MAX_ANCHOR_CANDIDATES — architecture §4.3 / FR-42 (named constant)"
    )


# ── §5 / FR-16 Slot model (v0.2.0) ───────────────────────────────────────────

def test_upper_body_layers() -> None:
    assert C.UPPER_BODY_LAYERS == ("base", "shirt", "mid", "outer"), (
        "UPPER_BODY_LAYERS — requirements §5 / FR-49.1 (innermost→outermost)"
    )


def test_all_slots() -> None:
    assert C.ALL_SLOTS == frozenset({
        "base", "shirt", "mid", "outer",
        "hat", "glasses", "earrings",
        "tie", "scarf", "necklace",
        "watch", "ring", "bracelet",
        "lower_body",
        "belt",
        "socks", "shoes",
    }), "ALL_SLOTS — requirements §5 / FR-16"


def test_all_categories() -> None:
    assert C.ALL_CATEGORIES == frozenset({
        "t_shirt", "vest", "long_sleeve",
        "shirt", "blouse", "polo",
        "jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat",
        "jacket", "blazer", "coat",
        "hat", "cap", "beanie",
        "glasses", "sunglasses",
        "earrings",
        "tie", "scarf",
        "necklace",
        "watch", "ring", "bracelet",
        "trousers", "jeans", "chinos", "shorts", "skirt",
        "dress", "jumpsuit",
        "belt",
        "socks",
        "shoes", "boots", "trainers", "sandals",
    }), "ALL_CATEGORIES — requirements §5 / FR-16 (`jersey` not a v0.2.0 category)"


def test_jersey_not_in_all_categories() -> None:
    assert "jersey" not in C.ALL_CATEGORIES, (
        "`jersey` was superseded in v0.2.0 — must not appear in ALL_CATEGORIES (FR-16)"
    )


def test_category_slot() -> None:
    assert C.CATEGORY_SLOT == {
        "t_shirt": "base",    "vest": "base",     "long_sleeve": "base",
        "shirt": "shirt",     "blouse": "shirt",  "polo": "shirt",
        "jumper": "mid",      "hoodie": "mid",    "cardigan": "mid",
        "sweatshirt": "mid",  "track_top": "mid", "waistcoat": "mid",
        "jacket": "outer",    "blazer": "outer",  "coat": "outer",
        "hat": "hat",         "cap": "hat",       "beanie": "hat",
        "glasses": "glasses", "sunglasses": "glasses",
        "earrings": "earrings",
        "tie": "tie",         "scarf": "scarf",
        "necklace": "necklace",
        "watch": "watch",     "ring": "ring",     "bracelet": "bracelet",
        "trousers": "lower_body", "jeans": "lower_body", "chinos": "lower_body",
        "shorts": "lower_body",   "skirt": "lower_body",
        "dress": "lower_body",    "jumpsuit": "lower_body",
        "belt": "belt",
        "socks": "socks",
        "shoes": "shoes",  "boots": "shoes",  "trainers": "shoes",  "sandals": "shoes",
    }, "CATEGORY_SLOT — requirements §5 / FR-16"


def test_one_piece_categories() -> None:
    assert C.ONE_PIECE_CATEGORIES == frozenset({"dress", "jumpsuit"}), (
        "ONE_PIECE_CATEGORIES — requirements §5 / FR-49.2"
    )


def test_one_piece_upper_slot() -> None:
    assert C.ONE_PIECE_UPPER_SLOT == "base", (
        "ONE_PIECE_UPPER_SLOT — requirements §5 / FR-49.2 (one-piece also occupies `base`)"
    )


def test_statement_adornment_slots() -> None:
    assert C.STATEMENT_ADORNMENT_SLOTS == frozenset({
        "hat", "tie", "scarf", "belt", "socks", "shoes",
    }), "STATEMENT_ADORNMENT_SLOTS — requirements §5 / FR-49.3"


def test_minor_adornment_slots() -> None:
    assert C.MINOR_ADORNMENT_SLOTS == frozenset({
        "glasses", "earrings", "necklace", "watch", "ring", "bracelet",
    }), "MINOR_ADORNMENT_SLOTS — requirements §5 / FR-49.3"


def test_statement_minor_adornments_disjoint() -> None:
    overlap = C.STATEMENT_ADORNMENT_SLOTS & C.MINOR_ADORNMENT_SLOTS
    assert not overlap, (
        f"Statement and minor adornment slot sets must be disjoint — overlap: {overlap}"
    )


def test_default_slots() -> None:
    assert C.DEFAULT_SLOTS == frozenset({"base", "lower_body", "socks", "shoes"}), (
        "DEFAULT_SLOTS — requirements §5 / FR-51.1"
    )


def test_mandatory_slot() -> None:
    assert C.MANDATORY_SLOT == "lower_body", (
        "MANDATORY_SLOT — requirements §5 / FR-51.2"
    )


def test_mandatory_slot_in_default_slots() -> None:
    assert C.MANDATORY_SLOT in C.DEFAULT_SLOTS, (
        "MANDATORY_SLOT must be a member of DEFAULT_SLOTS (FR-51.1 / FR-51.2)"
    )


def test_category_slot_covers_all_categories() -> None:
    unmapped = C.ALL_CATEGORIES - C.CATEGORY_SLOT.keys()
    assert not unmapped, (
        f"Every category in ALL_CATEGORIES must appear in CATEGORY_SLOT — missing: {unmapped}"
    )
