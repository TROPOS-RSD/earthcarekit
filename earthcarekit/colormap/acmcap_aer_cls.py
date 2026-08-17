from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [0, "#FFFFFF", "None"],
    [1, "#FF7E0E", "Dust"],
    [2, "#62BACD", "Sea salt"],
    [3, "#D62728", "Continental pollution"],
    [4, "#004D52", "Smoke"],
    [5, "#8C564B", "Dusty smoke"],
    [6, "#FFC197", "Dusty mix"],
    [7, "#FFDB00", "Strat. sulfate"],
]


def get_cmap() -> Cmap:
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: str(label) for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
