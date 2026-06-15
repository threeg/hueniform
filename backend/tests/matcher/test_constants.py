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
    assert C.WEIGHT_VARIETY == 5, (
        "WEIGHT_VARIETY — requirements §7 / FR-41.3 (named constant)"
    )


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
