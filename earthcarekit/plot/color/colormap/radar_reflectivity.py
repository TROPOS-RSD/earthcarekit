from matplotlib import colormaps as mpl_cmaps

from .chiljet2 import get_cmap as get_cmap_chiljet2


def get_cmap():
    cmap = get_cmap_chiljet2()
    cmap.name = "radar_reflectivity"
    return cmap
