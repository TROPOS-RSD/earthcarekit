from pathlib import Path

from ._cmap import Cmap

# Colormap self-designed
cmap_data = [
    [-4, "#000000", "No info"],
    [-3, "#542d16", "Subsurface (both)"],
    [-2, "#a6761d", "Subsurface (lidar)"],
    [-1, "#6e5526", "Subsurface (radar)"],
    [0, "#999999", "Unassigned"],
    [1, "#ffffff", "Clear (both)"],
    [2, "#fead5c", "Clear (lidar)"],
    [3, "#fff4c2", "Clear (radar)"],
    [4, "#56c749", "Target (both)"],
    [5, "#bbb47b", "Target (lidar)"],
    [6, "#31a354", "Target (radar)"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
