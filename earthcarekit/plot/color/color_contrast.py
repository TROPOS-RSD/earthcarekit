from typing import Literal


def get_relative_luminance(rgb: tuple[int, int, int]) -> float:
    """
    Compute WCAG 2.0 relative luminance for an RGB color.

    See https://www.w3.org/TR/WCAG20/#relativeluminancedef
    """
    r, g, b = rgb

    def srgb_from_8bit(c):
        c = c / 255.0
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    R = srgb_from_8bit(r)
    G = srgb_from_8bit(g)
    B = srgb_from_8bit(b)

    L = 0.2126 * R + 0.7152 * G + 0.0722 * B

    return L


def get_contrast_ratio(l1: float, l2: float) -> float:
    """
    WCAG 2.0 contrast ratio between two luminances.

    See https://www.w3.org/TR/WCAG20/#contrast-ratiodef
    """
    L1, L2 = sorted([l1, l2])
    return (L2 + 0.05) / (L1 + 0.05)


def get_best_bw_contrast_color(rgb: tuple[int, int, int]) -> Literal["black", "white"]:
    """
    Return 'black' or 'white' according to WCAG 2.0 contrast ratio.

    See https://www.w3.org/TR/WCAG20/
    """
    L1 = get_relative_luminance(rgb)
    L_white = 1.0
    L_black = 0.0
    contrast_white = get_contrast_ratio(L1, L_white)
    contrast_black = get_contrast_ratio(L1, L_black)

    if contrast_white > contrast_black:
        return "white"
    else:
        return "black"
