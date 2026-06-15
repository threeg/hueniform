"""
Pure colour mathematics for the Hueniform matcher (requirements §1.3, FR-12).

All operations work in HSL space:
  H — degrees in [0, 360), wrapping
  S — saturation percentage [0, 100]
  L — lightness percentage [0, 100]

Standard library only (NFR-9).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Colour:
    """
    Immutable colour value used throughout the matcher.

    ``proportion`` is an integer percentage (1–100); a garment's colours
    must sum to exactly 100 (FR-6).  The matcher never reads proportion
    directly — proportion rules live in ``matcher.roles``.
    """
    h: float  # hue, degrees in [0, 360)
    s: float  # saturation, percentage [0, 100]
    l: float  # lightness, percentage [0, 100]
    proportion: int = 0  # percentage share; 0 is the sentinel for "unset"


# ── RGB ↔ HSL conversion ──────────────────────────────────────────────────────

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """
    Convert 8-bit RGB (0–255 each) to HSL (H in [0,360), S and L in [0,100]).

    Implements the standard algorithm; hue is normalised to [0, 360).
    """
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    cmax = max(rf, gf, bf)
    cmin = min(rf, gf, bf)
    delta = cmax - cmin

    # Lightness
    l = (cmax + cmin) / 2.0

    # Saturation
    if delta == 0.0:
        s = 0.0
    else:
        s = delta / (1.0 - abs(2.0 * l - 1.0))

    # Hue
    if delta == 0.0:
        h = 0.0
    elif cmax == rf:
        h = 60.0 * (((gf - bf) / delta) % 6)
    elif cmax == gf:
        h = 60.0 * (((bf - rf) / delta) + 2)
    else:
        h = 60.0 * (((rf - gf) / delta) + 4)

    return h, s * 100.0, l * 100.0


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """
    Convert HSL (H in [0,360), S and L in [0,100]) to 8-bit RGB (0–255 each).
    """
    s_f = s / 100.0
    l_f = l / 100.0

    c = (1.0 - abs(2.0 * l_f - 1.0)) * s_f
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = l_f - c / 2.0

    sector = int(h / 60.0) % 6
    if sector == 0:
        rf, gf, bf = c, x, 0.0
    elif sector == 1:
        rf, gf, bf = x, c, 0.0
    elif sector == 2:
        rf, gf, bf = 0.0, c, x
    elif sector == 3:
        rf, gf, bf = 0.0, x, c
    elif sector == 4:
        rf, gf, bf = x, 0.0, c
    else:
        rf, gf, bf = c, 0.0, x

    return (
        round((rf + m) * 255),
        round((gf + m) * 255),
        round((bf + m) * 255),
    )


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Return the CSS hex string for a given HSL colour (e.g. ``'#2CADA0'``).

    Used by the API layer to populate the ``hex`` field in ``ColourOut``
    (contract §1.1, FR-5).
    """
    r, g, b = hsl_to_rgb(h, s, l)
    return f"#{r:02X}{g:02X}{b:02X}"


# ── Hue operations (requirements §1.3, FR-12) ─────────────────────────────────

def hue_distance(a: float, b: float) -> float:
    """
    Shorter-arc distance between two hues on the colour wheel (requirements §1.3).

    Result is in [0, 180]; wraps correctly (e.g. d(350, 10) = 20).
    """
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


def circular_mean(hues: list[float]) -> float:
    """
    Circular (vector) mean of a list of hue angles (FR-12).

    Correct across the 0°/360° wrap — e.g. mean([350, 10]) = 0, not 180.
    Returns a value in [0, 360).
    """
    if not hues:
        raise ValueError("circular_mean requires at least one hue")
    sin_sum = sum(math.sin(math.radians(h)) for h in hues)
    cos_sum = sum(math.cos(math.radians(h)) for h in hues)
    mean = math.degrees(math.atan2(sin_sum, cos_sum))
    return mean % 360.0
