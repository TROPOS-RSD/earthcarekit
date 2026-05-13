from pathlib import Path

from ._cmap import Cmap

# Colormap self-designed
cmap_data = [
    [0, "#ffffff", "Not detmined"],
    [1, "#aec7e8", "Single scat."],
    [2, "#6b5ecf", "Moderate multi. scat."],
    [3, "#393b79", "Strong multi. scat."],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
