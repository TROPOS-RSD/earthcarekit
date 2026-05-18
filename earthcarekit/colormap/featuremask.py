from pathlib import Path
from typing import Any, Sequence, cast

from ..color import Color, ColorLike
from ._cmap import Cmap

cmap_data = [
    [-3, "#000000", "Surface"],
    [-2, "#FFFFFF", "No retrievals"],
    [-1, "#283E91", "Attenuated"],
    [0, "#31BAF0", "Clear sky"],
    [1, "#76CFDF", "Likely clear sky"],
    [2, "#88D4E4", "Likely clear sky"],
    [3, "#98DAE8", "Likely clear sky"],
    [4, "#A4DDF0", "Likely clear sky"],
    [5, "#BCB8B8", "Low altitude aerosols"],
    [6, "#F0DA13", "Aerosol/thin cloud"],
    [7, "#F3AA19", "Aerosol/thin cloud"],
    [8, "#CD7320", "Thick aerosol/cloud"],
    [9, "#F32320", "Thick aerosol/cloud"],
    [10, "#9F1D24", "Thick cloud"],
]


def get_cmap(
    alpha_clear: float = 1.0,
    alpha_missing: float = 1.0,
    alpha_attenuated: float = 1.0,
    alpha: float = 1.0,
    clear_values: Sequence[float] = (0, 1, 2, 3, 4),
    missing_values: Sequence[float] = (-3, -2),
    attenuated_values: Sequence[float] = (-1,),
) -> Cmap:
    definitions: dict[Any, str] = {}
    colors: list[Color] = []
    for k, c, label in cmap_data:
        c = Color(cast(ColorLike, c))
        if k in clear_values:
            c = c.set_alpha(alpha_clear)
        elif k in missing_values:
            c = c.set_alpha(alpha_missing)
        elif k in attenuated_values:
            c = c.set_alpha(alpha_attenuated)
        else:
            c = c.set_alpha(alpha)
        colors.append(c)
        definitions[k] = cast(str, label)
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
