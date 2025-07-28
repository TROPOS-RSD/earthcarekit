import plotly.colors as pc  # type: ignore

from ..color import Color
from .cmap import Cmap


def _get_plotly_cmaps(color_scale_module: object, smooth: bool) -> dict[str, Cmap]:
    cmaps = {}
    for name in dir(color_scale_module):
        if not name.startswith("_"):
            colors = getattr(color_scale_module, name)
            if isinstance(colors, list):
                if all([isinstance(c, str) for c in colors]):
                    cmap = Cmap(
                        [Color(c).rgba for c in colors], gradient=smooth, name=name
                    )
                    cmaps.update({name: cmap})
    return cmaps


def get_all_plotly_cmaps() -> dict[str, Cmap]:
    plotly_cmaps = {}

    plotly_cmaps.update(_get_plotly_cmaps(pc.sequential, True))
    plotly_cmaps.update(_get_plotly_cmaps(pc.diverging, True))
    plotly_cmaps.update(_get_plotly_cmaps(pc.cyclical, True))
    plotly_cmaps.update(_get_plotly_cmaps(pc.qualitative, False))

    return plotly_cmaps
