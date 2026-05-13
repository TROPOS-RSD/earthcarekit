from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-3, "#E6E6E6", "Missing"],
    [-2, "#000000", "Surface"],
    [-1, "#999999", "Attenuated"],
    [0, "#FFFFFF", "Clear"],
    [1, "#1192E8", "(Warm) liquid cloud"],
    [2, "#004489", "S'cooled cloud"],
    [3, "#93FBFF", "Ice cloud"],
    [10, "#FF7E0E", "Dust"],
    [11, "#62BACD", "Sea salt"],
    [12, "#D62728", "Continental pollution"],
    [13, "#004D52", "Smoke"],
    [14, "#8C564B", "Dusty smoke"],
    [15, "#FFC197", "Dusty mix"],
    [20, "#FFA0F1", "STS"],
    [21, "#9367BC", "NAT"],
    [22, "#3A0182", "Strat. ice"],
    [25, "#FFFF9A", "Strat. ash"],
    [26, "#FFDB00", "Strat. sulfate"],
    [27, "#BCBD22", "Strat. smoke"],
    [101, "#E6E6E6", "Unknown"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
