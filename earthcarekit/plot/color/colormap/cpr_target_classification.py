import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap_cpr_hydrometeor_classification():
    cmap_data = [
        ("#929591", -1, "No data"),
        ("#7f2b0a", 0, "Surface"),
        ("#ffffff", 1, "Clear"),
        ("#ffff84", 2, "Liquid cloud"),
        ("#f5bf03", 3, "Drizzling liquid clouds"),
        ("#f97306", 4, "Warm rain"),
        ("#ff000d", 5, "Cold rain"),
        ("#c071fe", 6, "Melting snow"),
        ("#004577", 7, "Rimed snow"),
        ("#0165fc", 8, "Snow"),
        ("#95d0fc", 9, "Ice"),
        ("#d7fffe", 10, "Stratospheric ice"),
        ("#7a9703", 11, "Insects"),
        ("#840000", 12, "Heavy rain likely"),
        ("#0504aa", 13, "Mixed-phase precip. likely"),
        ("#840000", 14, "Heavy rain"),
        ("#001146", 15, "Heavy mixed-phase precip."),
        ("#bb3f3f", 16, "Rain in clutter"),
        ("#5684ae", 17, "Snow in clutter"),
        ("#eedc5b", 18, "Cloud in clutter"),
        ("#d8dcd6", 19, "Clear likely"),
        ("#c5c9c7", 20, "Uncertain"),
    ]

    colors = [c[0] for c in cmap_data]
    definitions = {c[1]: c[2] for c in cmap_data}

    cmap = Cmap(
        colors=colors,
        name="cpr_hydrometeor_classification",
    ).to_categorical(definitions)
    return cmap


def get_cmap_cpr_doppler_velocity_classification():
    cmap_data = [
        ("#929591", -1, "No data"),
        ("#7f2b0a", 0, "Surface"),
        ("#ffffff", 1, "Clear"),
        ("#ff84f9", 2, "Dominated by $V_t$"),
        ("#75acff", 3, "Dominated by $\mathit{w}$"),
        ("#8811be", 4, "Contribution by $V_t$ and $\mathit{w}$"),
        ("#c5c9c7", 5, "Uncertain"),
        ("#840000", 12, "Heavy rain likely"),
        ("#0504aa", 13, "Mixed-phase precip. likely"),
        ("#840000", 14, "Heavy rain"),
        ("#001146", 15, "Heavy mixed-phase precip."),
        ("#bb3f3f", 16, "Rain in clutter"),
        ("#5684ae", 17, "Snow in clutter"),
        ("#eedc5b", 18, "Cloud in clutter"),
        ("#d8dcd6", 19, "Clear likely"),
    ]

    colors = [c[0] for c in cmap_data]
    definitions = {c[1]: c[2] for c in cmap_data}

    cmap = Cmap(
        colors=colors,
        name="cpr_doppler_velocity_classification",
    ).to_categorical(definitions)
    return cmap


def get_cmap_cpr_simplified_convective_classification():
    cmap_data = [
        ("#929591", -1, "No data"),
        ("#7f2b0a", 0, "Surface"),
        ("#ffffff", 1, "Clear"),
        ("#ffb584", 2, "Weak conv. + stratiform clouds"),
        ("#66d2da", 3, "Deep conv. clouds"),
        ("#df54bc", 4, "Dynamic conv. cores"),
        ("#c5c9c7", 5, "Uncertain"),
        ("#840000", 12, "Heavy rain likely"),
        ("#0504aa", 13, "Mixed-phase precip. likely"),
        ("#840000", 14, "Heavy rain"),
        ("#001146", 15, "Heavy mixed-phase precip."),
        ("#bb3f3f", 16, "Rain in clutter"),
        ("#5684ae", 17, "Snow in clutter"),
        ("#eedc5b", 18, "Cloud in clutter"),
        ("#d8dcd6", 19, "Clear likely"),
    ]

    colors = [c[0] for c in cmap_data]
    definitions = {c[1]: c[2] for c in cmap_data}

    cmap = Cmap(
        colors=colors,
        name="cpr_simplified_convective_classification",
    ).to_categorical(definitions)
    return cmap
