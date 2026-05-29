from pathlib import Path

from matplotlib import colormaps as mpl_cmaps

from ._cmap import Cmap
from ._combine_mpl_cmaps import combine_mpl_cmaps
from ._shift_mpl_cmap import shift_mpl_colormap


def get_cmap(midpoint: float | None = None) -> Cmap:
    if midpoint is None:
        midpoint = (240 - 180) / (320 - 180)

    return Cmap.from_colormap(
        shift_mpl_colormap(
            cmap=combine_mpl_cmaps(mpl_cmaps.get_cmap("jet_r"), mpl_cmaps.get_cmap("Greys")),
            midpoint=midpoint,
            name=Path(__file__).stem,
        )
    )
