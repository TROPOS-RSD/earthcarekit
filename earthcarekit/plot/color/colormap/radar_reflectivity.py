from matplotlib import colormaps as mpl_cmaps


def get_cmap():
    cmap = mpl_cmaps.get_cmap("jet")
    cmap.name = "radar_reflectivity"
    return cmap
