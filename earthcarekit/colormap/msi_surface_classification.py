from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [0, "#808080", "Undefined"],
    [1, "#010080", "Water"],
    [2, "#FF6448", "Land"],
    [3, "#FFD801", "Desert"],
    [4, "#008001", "Vegetation NDVI"],
    [5, "#81007F", "Snow XMET"],
    [6, "#9470DC", "Snow NDSI"],
    [7, "#FEA501", "Sea ice XMET"],
    [8, "#8C0001", "Sunglint"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
