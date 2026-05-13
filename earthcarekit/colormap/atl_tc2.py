from pathlib import Path

from ._cmap import Cmap

cmap_data = [
    [-3, "#F2F3DE", "Missing"],
    [-2, "#000000", "Surface"],
    [-1, "#696969", "Attenuated"],
    [0, "#FFFFFF", "Clear"],
    [1, "#0000FF", "(Warm) Liquid cloud"],
    [2, "#010089", "S'cooled cloud"],
    [3, "#00FFFF", "Ice cloud"],
    [10, "#A52A2C", "Dust"],
    [11, "#ADD8E6", "Sea salt"],
    [12, "#01FD80", "Continental pollution"],
    [13, "#2B4F52", "Smoke"],
    [14, "#CE853E", "Dusty smoke"],
    [15, "#DFB788", "Dusty mix"],
    [20, "#FF00FF", "STS"],
    [21, "#8929E1", "NAT"],
    [22, "#4B0080", "Strat. ice"],
    [25, "#FBE5B5", "Strat. ash"],
    [26, "#FEFF00", "Strat. sulfate"],
    [27, "#BDB66C", "Strat. smoke"],
    [101, "#E6E6E6", "Unknown"],
    # (101, , 'Unknown: Aerosol Target has a very low probability (no class assigned)')
    # (102, , 'Unknown: Aerosol classification outside of param space')
    # (104, , 'Unknown: Strat. Aerosol Target has a very low probability (no class assigned)')
    # (105, , 'Unknown: Strat. Aerosol classification outside of param space')
    # (106, , 'Unknown: PSC Target has a very low probability (no class assigned)')
    # (107, , 'Unknown: PSC classification outside of param space')
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
