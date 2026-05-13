from pathlib import Path

from cmcrameri import cm as cmcramericm  # type: ignore

from ._cmap import Cmap


def get_cmap():
    return Cmap.from_colormap(
        cmcramericm.roma_r.with_extremes(bad=cmcramericm.roma_r(0)), name=Path(__file__).stem
    )
