from pathlib import Path

import cmcrameri  # type: ignore

from .shift import shift_mpl_colormap


def get_cmap():
    cmap = shift_mpl_colormap(cmcrameri.cm.vik, midpoint=1 / 3, name=Path(__file__).stem)
    return cmap
