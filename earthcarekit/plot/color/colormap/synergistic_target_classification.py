import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap():
    cmap_data = [
        ("#c5c9c7", -1, "Unknown"),
        ("#a2653e", 0, "Surface"),
        ("#ffffff", 1, "Clear"),
        ("#ff474c", 2, "Rain in clutter"),
        ("#0504aa", 3, "Snow in clutter"),
        ("#009337", 4, "Cloud in clutter"),
        ("#840000", 5, "Heavy rain"),
        ("#042e60", 6, "Heavy mixed-phase precip."),
        ("#d8dcd6", 7, "Clear (possible liquid)"),
        ("#ffff84", 8, "Liquid cloud"),
        ("#f5bf03", 9, "Drizzling liquid cloud"),
        ("#f97306", 10, "Warm rain"),
        ("#ff000d", 11, "Cold rain"),
        ("#5539cc", 12, "Melting snow"),
        ("#2976bb", 13, "Snow (possible liquid)"),
        ("#0d75f8", 14, "Snow"),
        ("#014182", 15, "Rimed snow (possible liquid)"),
        ("#017b92", 16, "Rimed snow + s'cooled liquid"),
        ("#06b48b", 17, "Snow + liquid"),
        ("#aaff32", 18, "S'cooled liquid cloud"),
        ("#6dedfd", 19, "Ice cloud (possible liquid)"),
        ("#01f9c6", 20, "Ice + liquid cloud"),
        ("#7bc8f6", 21, "Ice cloud"),
        ("#d7fffe", 22, "Strat. ice"),
        ("#a2cffe", 23, "STS (PSC Type I)"),
        ("#04d9ff", 24, "NAT (PSC Type II)"),
        ("#7a9703", 25, "Insects"),
        ("#b2996e", 26, "Dust"),
        ("#ffbacd", 27, "Sea salt"),
        ("#d99b82", 28, "Continental pollution"),
        ("#947e94", 29, "Smoke"),
        ("#856798", 30, "Dusty smoke"),
        ("#ac86a8", 31, "Dusty mix"),
        ("#59656d", 32, "Strat. ash"),
        ("#76424e", 33, "Strat. sulfate"),
        ("#363737", 34, "Strat. smoke"),
    ]
    colors = [c for c, _, _ in cmap_data]
    definitions = {k: l for _, k, l in cmap_data}
    cmap = Cmap(colors=colors, name="synergetic_tc").to_categorical(definitions)
    return cmap
