import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data = [
    [-1, "#c5c9c7", "Unknown"],
    [ 0, "#a2653e", "Surface"],
    [ 1, "#ffffff", "Clear"],
    [ 2, "#ff474c", "Rain in clutter"],
    [ 3, "#0504aa", "Snow in clutter"],
    [ 4, "#009337", "Cloud in clutter"],
    [ 5, "#840000", "Heavy rain"],
    [ 6, "#042e60", "Heavy mixed-phase precip."],
    [ 7, "#d8dcd6", "Clear (possible liquid)"],
    [ 8, "#ffff84", "Liquid cloud"],
    [ 9, "#f5bf03", "Drizzling liquid cloud"],
    [10, "#f97306", "Warm rain"],
    [11, "#ff000d", "Cold rain"],
    [12, "#5539cc", "Melting snow"],
    [13, "#2976bb", "Snow (possible liquid)"],
    [14, "#0d75f8", "Snow"],
    [15, "#014182", "Rimed snow (possible liquid)"],
    [16, "#017b92", "Rimed snow + s'cooled liquid"],
    [17, "#06b48b", "Snow + liquid"],
    [18, "#aaff32", "S'cooled liquid cloud"],
    [19, "#6dedfd", "Ice cloud (possible liquid)"],
    [20, "#01f9c6", "Ice + liquid cloud"],
    [21, "#7bc8f6", "Ice cloud"],
    [22, "#d7fffe", "Strat. ice"],
    [23, "#a2cffe", "STS (PSC Type I)"],
    [24, "#04d9ff", "NAT (PSC Type II)"],
    [25, "#7a9703", "Insects"],
    [26, "#b2996e", "Dust"],
    [27, "#ffbacd", "Sea salt"],
    [28, "#d99b82", "Continental pollution"],
    [29, "#947e94", "Smoke"],
    [30, "#856798", "Dusty smoke"],
    [31, "#ac86a8", "Dusty mix"],
    [32, "#59656d", "Strat. ash"],
    [33, "#76424e", "Strat. sulfate"],
    [34, "#363737", "Strat. smoke"],
]

def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: l for k, _, l in cmap_data}
    cmap = Cmap(
        colors=colors, name="synergetic_tc").to_categorical(definitions)
    return cmap
