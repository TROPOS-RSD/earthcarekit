from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-127, "#dedede", "Not determined"],
    [0, "#123598", "Clear"],
    [1, "#1192e8", "Prob. clear"],
    [2, "#ffaa00", "Prob. cloudy"],
    [3, "#ff2a55", "Cloudy"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
