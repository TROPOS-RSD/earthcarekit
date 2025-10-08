from typing import Literal

import numpy as np
import xarray as xr
from matplotlib.colors import Colormap
from matplotlib.figure import Figure

from ...utils.constants import CM_AS_INCH, FIGURE_HEIGHT_CURTAIN, FIGURE_WIDTH_CURTAIN
from ...utils.read import read_product
from ...utils.time import to_timestamp
from ...utils.typing import ValueRangeLike
from ..color import Color, ColorLike, get_cmap
from ..figure import MapFigure, create_column_figure_layout


def ecswath(
    ds: xr.Dataset | str,
    var: str | None = None,
    n: int = 1,
    time_var: str = "time",
    style: str = "gray",
    border_color: ColorLike | None = "white",
    cmap: str | Colormap | None = None,
    value_range: ValueRangeLike | None = None,
    show_colorbar: bool = True,
    track_color: ColorLike | None = "black",
    color_ticks: ColorLike | None = "white",
    linewidth: float = 3.5,
    linestyle: str = "dashed",
    single_figsize: tuple[float, float] = (3, 8),
    colorbar_position: str | Literal["left", "right", "top", "bottom"] = "bottom",
) -> tuple[Figure, list[MapFigure]]:
    ds = read_product(ds, in_memory=True)

    color_ticks = Color.from_optional(color_ticks) or "white"

    _output = create_column_figure_layout(n, single_figsize=single_figsize)
    fig = _output.fig
    axs = _output.axs
    tmin = to_timestamp(np.nanmin(ds[time_var].values))
    tmax = to_timestamp(np.nanmax(ds[time_var].values))
    tspan = (tmax - tmin) / n
    colorbar_alignment = "center"
    colorbar_length_ratio = "100%"
    if colorbar_position in ["top", "bottom"]:
        if n % 2 == 0:
            colorbar_alignment = "left"
        if n != 1:
            colorbar_length_ratio = "200%"
    map_figs: list[MapFigure] = []
    coastlines_resolution: Literal["10m", "50m", "110m"] = "50m"
    if n > 3:
        coastlines_resolution = "10m"
    for i in range(n):
        _show_colorbar = False
        if colorbar_position in ["top", "bottom"]:
            if i == (n - 1) // 2:
                _show_colorbar = True
        elif i == n - 1:
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
            coastlines_resolution=coastlines_resolution,
        )
        p = p.ecplot(
            ds,
            var,
            view="overpass",
            zoom_tmin=tmin + i * tspan,
            zoom_tmax=tmin + (i + 1) * tspan,
            colorbar=show_colorbar & _show_colorbar,
            colorbar_length_ratio=colorbar_length_ratio,
            colorbar_position=colorbar_position,
            colorbar_alignment=colorbar_alignment,
            colorbar_spacing=0.1,
            cmap=None,
            value_range=value_range,
            color=track_color,
            linewidth=linewidth,
            linestyle=linestyle,
        )
        p.grid_lines.ypadding = -3  # type: ignore
        p.grid_lines.ylabel_style = {  # type: ignore
            "color": color_ticks,
            "fontsize": "small",
            "weight": "bold",
        }
        p.grid_lines.xpadding = -3  # type: ignore
        p.grid_lines.xlabel_style = {  # type: ignore
            "color": color_ticks,
            "fontsize": "small",
            "weight": "bold",
        }
        p.grid_lines.zorder = 5  # type: ignore

        map_figs.append(p)
    return fig, map_figs
