import colorsys
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex

# def generate_hsl_circle_colormap(n: int, s: float = 0.7, l: float = 0.65) -> list[str]:
#     """
#     Generates `n` distinct colors evenly spaced around the HSL color wheel.

#     Args:
#         n (int): Number of colors to generate.
#         s (float, optional): Saturation component of the HSL color, between 0 and 1. Defaults to 0.65.
#         l (float, optional): Lightness component of the HSL color, between 0 and 1. Defaults to 0.5.

#     Returns:
#         list[str]: A list of hex color strings (e.g., "#ff0000").
#     """
#     colors: list[str] = []
#     for i in range(n):
#         h = i / n  # Hue: evenly spaced around the circle
#         r, g, b = colorsys.hls_to_rgb(h, l, s)
#         hex_color = "#{:02x}{:02x}{:02x}".format(
#             int(r * 255), int(g * 255), int(b * 255)
#         )
#         colors.append(hex_color)
#     return colors


def generate_hue_circle_colormap(n: int, rotation: float = 0.0) -> List[str]:
    """
    Generate `n` evenly spaced colors around the hue circle, similar to ggplot2's HCL palette,
    using standard Python + matplotlib.

    Args:
        n (int): Number of colors.
        rotation (float): Hue rotation in degrees (default 0.0).

    Returns:
        List[str]: List of hex color strings.
    """
    # These values approximate ggplot2 defaults (HCL)
    s = 0.65  # saturation
    l = 0.6  # lightness

    colors = []
    for i in range(n):
        hue = ((i / n) + rotation / 360.0) % 1.0
        r, g, b = colorsys.hls_to_rgb(hue, l, s)
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255)
        )
        colors.append(hex_color)
    return colors


def get_cmap(n=256, interpolate=False):
    name = "hsl"
    colors = generate_hue_circle_colormap(n)
    positions = np.linspace(0, 1, n)
    color_dict = list(zip(positions, colors))
    if interpolate:
        cmap = LinearSegmentedColormap.from_list(name, color_dict)
    else:
        cmap = ListedColormap(colors, name=name)
    return cmap
