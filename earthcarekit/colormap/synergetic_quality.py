from pathlib import Path

from ._cmap import Cmap

# Colormap from ACTC file baseline BC
cmap_data = [
    [0, "#a2653e", "Surface (high conf."],
    [1, "#ffffff", "Clear (high conf.)"],
    [2, "#75bbfd", "Hydrometeor (high conf. both)"],
    [3, "#d0fefe", "Hydrometeor (high conf. lidar-only)"],
    [4, "#ff000d", "Aerosol (mod conf.)"],
    [5, "#01ff07", "Stratosphere (mod conf.)"],
    [6, "#ffffe4", "Clear (mod conf. lidar only)"],
    [7, "#c7fdb5", "Stratosphere (mod conf. lidar only)"],
    [8, "#0165fc", "Hydrometeor (mod conf.)"],
    [9, "#fdfdfe", "Clear (mod conf.)"],
    [10, "#d8dcd6", "Clear (low conf.)"],
    [11, "#04d9ff", "Hydrometeor (low conf.)"],
    [12, "#929591", "Unknown (low conf.)"],
    [13, "#7a9703", "Radar artefact (low conf.)"],
    [14, "#03012d", "Extinguished (low conf.)"],
    [15, "#cfaf7b", "Surface (low conf.)"],
    [16, "#bf00bf", "No data"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: label for k, _, label in cmap_data}
    return Cmap(colors=colors, name=Path(__file__).stem).to_categorical(definitions)
