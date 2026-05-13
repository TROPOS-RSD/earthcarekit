from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-127, "#E6E6E6", "No data"],
    [0, "#FFFFFF", "Clear"],
    [1, "#0B4D79", "Cu"],
    [2, "#17BECF", "Ac"],
    [3, "#93FBFF", "Ci"],
    [4, "#2CA02C", "Sc"],
    [5, "#FFFF9A", "As"],
    [6, "#E5AE38", "Cs"],
    [7, "#FF7E0E", "St"],
    [8, "#D62628", "Ns"],
    [9, "#5D003F", "Dcv"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: short_label for k, _, short_label in cmap_data}
    cmap = (
        Cmap(colors=colors, name=Path(__file__).stem)
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap
