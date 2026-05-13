from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-127, "#dedede", "Not determined"],
    [1, "#1192e8", "Water"],
    [2, "#93fbff", "Ice"],
    [3, "#123598", "S'cooled"],
    [4, "#ff2a55", "overlap"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
