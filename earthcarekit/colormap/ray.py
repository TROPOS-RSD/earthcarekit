from pathlib import Path

from cmcrameri import cm as cmcramericm  # type: ignore

from ._cmap import Cmap


def get_cmap():
    return Cmap.from_colormap(
        cmcramericm.lipari.with_extremes(bad="black"), name=Path(__file__).stem
    )
