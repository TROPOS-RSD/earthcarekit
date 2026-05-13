from pathlib import Path

from matplotlib import colormaps as mpl_cmaps

from ._cmap import Cmap


def get_cmap():
    return Cmap.from_colormap(mpl_cmaps.get_cmap("YlOrRd"), name=Path(__file__).stem)
