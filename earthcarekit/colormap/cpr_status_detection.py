from pathlib import Path

from ._cmap import Cmap

# Colormap self-designed
cmap_data = [
    [-1, "#999999", "Not detected"],
    [0, "#a65628", "Ground"],
    [1, "#ffffff", "Clear"],
    [2, "#636363", "Extinguished"],
    [3, "#7b4173", "Likely extinguished"],
    [4, "#1e206e", "Target det., no reliable meas."],
    [5, "#9c9ede", "Target det., only refl. reliable"],
    [6, "#6b5ecf", "Target det., refl. enhanced MS"],
    [7, "#c6dbef", "Target det., only Doppler reliable"],
    [8, "#c7e9c0", "Target det., both reliable"],
    [9, "#e7ba52", "Ground clutter (separated)"],
    [10, "#c49c94", "Ground clutter (overlapping)"],
    [11, "#fd8d3c", "Uncertain"],
    [12, "#e7969c", "Second-trip echo"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
