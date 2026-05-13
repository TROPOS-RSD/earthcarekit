from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-3, "#E6E6E6", "Missing"],
    [-2, "#000000", "Surface"],
    [-1, "#999999", "Attenuated"],
    [1, "#b1c59b", "Not attenuated"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
