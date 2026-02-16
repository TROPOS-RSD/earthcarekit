import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data_cpr_hydromet = [
    [-1, "#929591", "No data"],
    [0, "#7f2b0a", "Surface"],
    [1, "#ffffff", "Clear"],
    [2, "#ffff84", "Liquid cloud"],
    [3, "#f5bf03", "Drizzling liquid clouds"],
    [4, "#f97306", "Warm rain"],
    [5, "#ff000d", "Cold rain"],
    [6, "#c071fe", "Melting snow"],
    [7, "#004577", "Rimed snow"],
    [8, "#0165fc", "Snow"],
    [9, "#95d0fc", "Ice"],
    [10, "#d7fffe", "Stratospheric ice"],
    [11, "#7a9703", "Insects"],
    [12, "#840000", "Heavy rain likely"],
    [13, "#0504aa", "Mixed-phase precip. likely"],
    [14, "#840000", "Heavy rain"],
    [15, "#001146", "Heavy mixed-phase precip."],
    [16, "#bb3f3f", "Rain in clutter"],
    [17, "#5684ae", "Snow in clutter"],
    [18, "#eedc5b", "Cloud in clutter"],
    [19, "#d8dcd6", "Clear likely"],
    [20, "#c5c9c7", "Uncertain"],
]

def get_cmap_cpr_hydrometeor_classification():

    colors = [c[1] for c in cmap_data_cpr_hydromet]
    definitions = {c[0]: c[2] for c in cmap_data_cpr_hydromet}

    cmap = Cmap(
        colors=colors,
        name="cpr_hydrometeor_classification",
    ).to_categorical(definitions)
    return cmap

cmap_data_cpr_vel = [
    [-1, "#929591", "No data"],
    [0, "#7f2b0a", "Surface"],
    [1, "#ffffff", "Clear"],
    [2, "#ff84f9", "Dominated by $V_t$"],
    [3, "#75acff", "Dominated by $\mathit{w}$"],
    [4, "#8811be", "Contribution by $V_t$ and $\mathit{w}$"],
    [5, "#c5c9c7", "Uncertain"],
    [12, "#840000", "Heavy rain likely"],
    [13, "#0504aa", "Mixed-phase precip. likely"],
    [14, "#840000", "Heavy rain"],
    [15, "#001146", "Heavy mixed-phase precip."],
    [16, "#bb3f3f", "Rain in clutter"],
    [17, "#5684ae", "Snow in clutter"],
    [18, "#eedc5b", "Cloud in clutter"],
    [19, "#d8dcd6", "Clear likely"],
]

def get_cmap_cpr_doppler_velocity_classification():

    colors = [c[1] for c in cmap_data_cpr_vel]
    definitions = {c[0]: c[2] for c in cmap_data_cpr_vel}

    cmap = Cmap(
        colors=colors,
        name="cpr_doppler_velocity_classification",
    ).to_categorical(definitions)
    return cmap

cmap_data_cpr_conv = [
    [-1, "#929591", "No data"],
    [0, "#7f2b0a", "Surface"],
    [1, "#ffffff", "Clear"],
    [2, "#ffb584", "Weak conv. + stratiform clouds"],
    [3, "#66d2da", "Deep conv. clouds"],
    [4, "#df54bc", "Dynamic conv. cores"],
    [5, "#c5c9c7", "Uncertain"],
    [12, "#840000", "Heavy rain likely"],
    [13, "#0504aa", "Mixed-phase precip. likely"],
    [14, "#840000", "Heavy rain"],
    [15, "#001146", "Heavy mixed-phase precip."],
    [16, "#bb3f3f", "Rain in clutter"],
    [17, "#5684ae", "Snow in clutter"],
    [18, "#eedc5b", "Cloud in clutter"],
    [19, "#d8dcd6", "Clear likely"],
]

def get_cmap_cpr_simplified_convective_classification():

    colors = [c[1] for c in cmap_data_cpr_conv]
    definitions = {c[0]: c[2] for c in cmap_data_cpr_conv}

    cmap = Cmap(
        colors=colors,
        name="cpr_simplified_convective_classification",
    ).to_categorical(definitions)
    return cmap
