from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [0, "#b3de69", "Good, Nominal"],
    [1, "#8dd3c7", "Likely good"],
    [2, "#e78ac3", "Likely bad"],
    [3, "#fc8d62", "Bad"],
    [4, "#666666", "L1 missing"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
