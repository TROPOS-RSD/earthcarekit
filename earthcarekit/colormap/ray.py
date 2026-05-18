from pathlib import Path

from cmcrameri import cm as cmcramericm  # type: ignore

from ._cmap import Cmap


def get_cmap() -> Cmap:
    return Cmap.from_colormap(
        cmap=cmcramericm.lipari.with_extremes(bad="black"),
        name=Path(__file__).stem,
    )
