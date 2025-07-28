import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap():
    colors = [
        "#c5c9c7",
        "#a2653e",
        "#ffffff",
        "#ff474c",
        "#0504aa",
        "#009337",
        "#840000",
        "#042e60",
        "#d8dcd6",
        "#ffff84",
        "#f5bf03",
        "#f97306",
        "#ff000d",
        "#5539cc",
        "#2976bb",
        "#0d75f8",
        "#014182",
        "#017b92",
        "#06b48b",
        "#aaff32",
        "#6dedfd",
        "#01f9c6",
        "#7bc8f6",
        "#d7fffe",
        "#a2cffe",
        "#04d9ff",
        "#7a9703",
        "#b2996e",
        "#ffbacd",
        "#d99b82",
        "#947e94",
        "#856798",
        "#ac86a8",
        "#59656d",
        "#76424e",
        "#363737",
    ]
    definitions = {
        -1: "unknown",
        0: "ground",
        1: "clear",
        2: "possible rain (clutter)",
        3: "possible snow (clutter)",
        4: "possible cloud (clutter)",
        5: "heavy rain",
        6: "heavy mixed-phase precipitation",
        7: "no rain or ice (possible liquid)",
        8: "liquid cloud",
        9: "drizzling liquid cloud",
        10: "warm rain",
        11: "cold rain",
        12: "melting snow",
        13: "snow (possible liquid)",
        14: "snow (no liquid)",
        15: "rimed snow (possible liquid)",
        16: "rimed snow and supercooled liquid",
        17: "snow and supercooled liquid",
        18: "supercooled liquid",
        19: "ice cloud (possible liquid)",
        20: "ice and supercooled liquid",
        21: "ice cloud (no liquid)",
        22: "stratospheric ice",
        23: "STS (PSC Type I)",
        24: "NAT (PSC Type II)",
        25: "insects",
        26: "dust",
        27: "sea salt",
        28: "continental pollution",
        29: "smoke",
        30: "dusty smoke",
        31: "dusty mix",
        32: "stratospheric ash",
        33: "stratospheric sulfate",
        34: "stratospheric smoke",
    }
    cmap = Cmap(colors=colors, name="synergistic_target_classification").to_categorical(
        definitions
    )
    return cmap
