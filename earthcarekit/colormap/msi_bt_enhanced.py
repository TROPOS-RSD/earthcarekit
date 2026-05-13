from pathlib import Path

from matplotlib import colormaps as mpl_cmaps

from ._combine._mpl_combine_cmaps import _combine_mpl_cmaps
from ._shift._mpl_shift_cmap import _shift_mpl_colormap


def get_cmap(vmin: float = 180, vmax: float = 320, split: float = 240):
    return _shift_mpl_colormap(
        _combine_mpl_cmaps(mpl_cmaps.get_cmap("jet_r"), mpl_cmaps.get_cmap("Greys")),
        midpoint=(split - vmin) / (vmax - vmin),
        name=Path(__file__).stem,
    )
