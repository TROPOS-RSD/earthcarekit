from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-127, "#E6E6E6", "No data"],
    [0, "#FFFFFF", "Clear"],
    [1, "#0B4D79", "Cumulus"],
    [2, "#17BECF", "Altocumulus"],
    [3, "#93FBFF", "Cirrus"],
    [4, "#2CA02C", "Stratocumulus"],
    [5, "#FFFF9A", "Altostratus"],
    [6, "#E5AE38", "Cirrostratus"],
    [7, "#FF7E0E", "Stratus"],
    [8, "#D62628", "Nimbostratus"],
    [9, "#5D003F", "Deep convection"],
]


def get_cmap() -> Cmap:
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: str(label) for k, _, label in cmap_data}
    return Cmap.from_colormap(
        Cmap(colors=colors, name=Path(__file__).stem)
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
