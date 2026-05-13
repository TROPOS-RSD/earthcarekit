from pathlib import Path

from ._cmap import Cmap

cmap_data = [
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


def get_cmap():

    colors = [c[1] for c in cmap_data]
    definitions = {c[0]: c[2] for c in cmap_data}

    cmap = Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
    return cmap
