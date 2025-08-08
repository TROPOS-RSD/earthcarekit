import numpy as np
import xarray as xr
from matplotlib.colors import Colormap
from matplotlib.figure import Figure

from ...utils.constants import CM_AS_INCH, FIGURE_HEIGHT_CURTAIN, FIGURE_WIDTH_CURTAIN
from ...utils.read import read_product
from ...utils.time import to_timestamp
from ...utils.typing import ValueRangeLike
from ..color import ColorLike, get_cmap
from ..figure import MapFigure, create_column_subfigures


def ecswath(
    ds: xr.Dataset | str,
    var: str | None = None,
    n: int = 1,
    time_var: str = "time",
    style: str = "gray",
    border_color: ColorLike | None = "white",
    cmap: str | Colormap | None = "viridis",
    value_range: ValueRangeLike | None = None,
    show_colorbar: bool = True,
    track_color: ColorLike | None = "black",
    linewidth: float = 3.5,
    linestyle: str = "dashed",
    single_figsize: tuple[float, float] = (3, 8),
) -> tuple[Figure, list[MapFigure]]:
    ds = read_product(ds, in_memory=True)

    fig, axs = create_column_subfigures(n, single_figsize=single_figsize)
    tmin = to_timestamp(np.nanmin(ds[time_var].values))
    tmax = to_timestamp(np.nanmax(ds[time_var].values))
    tspan = (tmax - tmin) / n
    cb_alignment = "center"
    if n % 2 == 0:
        cb_alignment = "left"
    cb_height_ratio = "200%"
    if n == 1:
        cb_height_ratio = "100%"
    map_figs: list[MapFigure] = []
    for i in range(n):
        _show_colorbar = False
        if i == (n - 1) // 2:
            _show_colorbar = True
        show_text_time = False
        show_text_frame = False
        if i == 0:
            show_text_time = True
        if i == (n - 1):
            show_text_frame = True
        p = MapFigure(
            ax=axs[i],
            figsize=single_figsize,
            show_right_labels=False,
            show_top_labels=False,
            pad=0,
            style=style,
            show_text_time=show_text_time,
            show_text_frame=show_text_frame,
            border_color=border_color,
        )
        p = p.ecplot(
            ds,
            var,
            view="data",
            zoom_tmin=tmin + i * tspan,
            zoom_tmax=tmin + (i + 1) * tspan,
            colorbar=show_colorbar & _show_colorbar,
            cb_height_ratio=cb_height_ratio,
            cb_alignment=cb_alignment,
            cmap=get_cmap(cmap),
            value_range=value_range,
            color=track_color,
            linewidth=linewidth,
            linestyle=linestyle,
        )
        p.grid_lines.ypadding = -3  # type: ignore
        p.grid_lines.ylabel_style = {  # type: ignore
            "color": "white",
            "fontsize": "small",
            "weight": "bold",
        }
        p.grid_lines.xpadding = -3  # type: ignore
        p.grid_lines.xlabel_style = {  # type: ignore
            "color": "white",
            "fontsize": "small",
            "weight": "bold",
        }

        map_figs.append(p)
    return fig, map_figs
