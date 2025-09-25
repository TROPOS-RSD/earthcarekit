import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap2():
    cmap_data = [
        (-3, "#F2F3DE", "Missing"),
        (-2, "#000000", "Surface"),
        (-1, "#696969", "Attenuated"),
        (0, "#FFFFFF", "Clear"),
        (1, "#0000FF", "(Warm) Liquid cloud"),
        (2, "#010089", "S'cooled cloud"),
        (3, "#00FFFF", "Ice cloud"),
        (10, "#A52A2C", "Dust"),
        (11, "#ADD8E6", "Sea salt"),
        (12, "#01FD80", "Continental pollution"),
        (13, "#2B4F52", "Smoke"),
        (14, "#CE853E", "Dusty smoke"),
        (15, "#DFB788", "Dusty mix"),
        (20, "#FF00FF", "STS"),
        (21, "#8929E1", "NAT"),
        (22, "#4B0080", "Strat. ice"),
        (25, "#FBE5B5", "Strat. ash"),
        (26, "#FEFF00", "Strat. sulfate"),
        (27, "#BDB66C", "Strat. smoke"),
        (101, "#E6E6E6", "Unknown"),
        # (101, , 'Unknown: Aerosol Target has a very low probability (no class assigned)')
        # (102, , 'Unknown: Aerosol classification outside of param space')
        # (104, , 'Unknown: Strat. Aerosol Target has a very low probability (no class assigned)')
        # (105, , 'Unknown: Strat. Aerosol classification outside of param space')
        # (106, , 'Unknown: PSC Target has a very low probability (no class assigned)')
        # (107, , 'Unknown: PSC classification outside of param space')
    ]
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: l for k, _, l in cmap_data}
    cmap = Cmap(colors=colors, name="atl_tc2").to_categorical(definitions)
    return cmap


def get_cmap():
    cmap_data = [
        (-3, "#E6E6E6", "Missing"),
        (-2, "#000000", "Surface"),
        (-1, "#999999", "Attenuated"),
        (0, "#FFFFFF", "Clear"),
        (1, "#1192E8", "(Warm) liquid cloud"),
        (2, "#004489", "S'cooled cloud"),
        (3, "#93FBFF", "Ice cloud"),
        (10, "#FF7E0E", "Dust"),
        (11, "#62BACD", "Sea salt"),
        (12, "#D62728", "Continental pollution"),
        (13, "#004D52", "Smoke"),
        (14, "#8C564B", "Dusty smoke"),
        (15, "#FFC197", "Dusty mix"),
        (20, "#FFA0F1", "STS"),
        (21, "#9367BC", "NAT"),
        (22, "#3A0182", "Strat. ice"),
        (25, "#FFFF9A", "Strat. ash"),
        (26, "#FFDB00", "Strat. sulfate"),
        (27, "#BCBD22", "Strat. smoke"),
        (101, "#E6E6E6", "Unknown"),
    ]
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: l for k, _, l in cmap_data}
    cmap = Cmap(colors=colors, name="atl_tc").to_categorical(definitions)
    return cmap
