from pathlib import Path

import cmcrameri  # type: ignore

from ._cmap import Cmap
from ._shift_mpl_cmap import shift_mpl_colormap


def get_cmap(midpoint: float | None = None) -> Cmap:
    if midpoint is None:
        midpoint = 1 / 3

    return Cmap.from_colormap(
        shift_mpl_colormap(
            cmap=cmcrameri.cm.vik,
            midpoint=midpoint,
            name=Path(__file__).stem,
        )
    )
