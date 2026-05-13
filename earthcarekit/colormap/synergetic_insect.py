from pathlib import Path

from ._cmap import Cmap

# Colormap self-designed
cmap_data = [
    [-3, "#000000", "No data"],
    [-2, "#65ffff", "Hydrometeors"],
    [-1, "#fff4c2", "No insect (no lidar)"],
    [0, "#ffffff", "No insect (lidar clear)"],
    [1, "#9e669b", "Poss. insects in clutter (no lidar)"],
    [2, "#dcafba", "Poss. insects (no lidar)"],
    [3, "#9e4c37", "Likely insects in clutter"],
    [4, "#eb3e13", "Likely insects"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
