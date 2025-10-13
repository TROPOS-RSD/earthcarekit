from logging import Logger
from typing import Literal, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ....utils.constants import (
    ACROSS_TRACK_DIM,
    ALONG_TRACK_DIM,
    CM_AS_INCH,
    DEFAULT_PROFILE_SHOW_STEPS,
    TIME_VAR,
    VERTICAL_DIM,
)
from ....utils.read.product.level1.atl_nom_1b import get_depol_profile
from ....utils.time import TimedeltaLike, TimeRangeLike
from ....utils.typing import DistanceRangeLike
from ....utils.xarray_utils import filter_radius, filter_time
from ...figure import (
    CurtainFigure,
    ECKFigure,
    FigureType,
    LineFigure,
    MapFigure,
    ProfileFigure,
    create_multi_figure_layout,
)
from .._cli import print_progress
from .._quicklook_results import QuicklookFigure
from ..set_default_height_range import set_none_height_range_to_default


def is_curtain_var(ds: xr.Dataset, var: str):
    return all(s in ds[var].dims for s in (ALONG_TRACK_DIM, VERTICAL_DIM))


def is_swath_var(ds: xr.Dataset, var: str):
    return all(s in ds[var].dims for s in (ALONG_TRACK_DIM, ACROSS_TRACK_DIM))


def is_1d_var(ds: xr.Dataset, var: str):
    return ds[var].dims == (ALONG_TRACK_DIM,)


def ecquicklook_ccld(
    ds: xr.Dataset,
    vars: list[str] | None = None,
    show_maps: bool = True,
    show_zoom: bool = False,
    show_profile: bool = False,
    site: str | None = None,
    radius_km: float = 100.0,
    time_range: TimeRangeLike | None = None,
    height_range: DistanceRangeLike | None = None,
    ds_tropopause: xr.Dataset | None = None,
    ds_elevation: xr.Dataset | None = None,
    ds_temperature: xr.Dataset | None = None,
    resolution: Literal["low", "medium", "high", "l", "m", "h"] = "medium",
    closest_profile: bool = True,
    logger: Logger | None = None,
    log_msg_prefix: str = "",
    selection_max_time_margin: TimedeltaLike | Sequence[TimedeltaLike] | None = None,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    mode: Literal["fast", "exact"] = "fast",
) -> QuicklookFigure:

    map_figs: list[ECKFigure] = []

    common_kwargs = dict(
        time_range=time_range,
        site=site,
        radius_km=radius_km,
        selection_max_time_margin=selection_max_time_margin,
    )

    height_range = set_none_height_range_to_default(height_range, -250, 20e3)

    show_profile = False

    _stime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    if ds_elevation is None:
        ds_elevation = ds

    map_rows = None
    if show_maps:
        map_rows = [
            FigureType.MAP_1_ROW,
            FigureType.MAP_2_ROW,
        ]
    layout = create_multi_figure_layout(
        rows=[
            FigureType.CURTAIN_75,
            FigureType.CURTAIN_75,
            FigureType.CURTAIN_75,
            FigureType.CURTAIN_75,
            FigureType.CURTAIN_75,
            FigureType.LINE,
            FigureType.LINE,
            FigureType.LINE,
        ],
        map_rows=map_rows,
        hspace=[
            1.2,
            1.2,
            1.2,
            1.2,
            1.2,
            0.3,
            0.3,
        ],
    )

    if show_maps:
        ax_map1 = layout.axs_map[0]
        ax_map2 = layout.axs_map[1]

        fig_map1 = MapFigure(ax=ax_map1)
        fig_map1 = fig_map1.ecplot(
            ds=ds,
            view="global",
            **common_kwargs,  # type: ignore
        )
        fig_map2 = MapFigure(
            ax=ax_map2,
            style="blue_marble",
            coastlines_resolution="50m",
            show_right_labels=False,
            show_top_labels=False,
        )
        fig_map2 = fig_map2.ecplot(
            ds=ds,
            view="overpass",
            **common_kwargs,  # type: ignore
        )

        map_figs = [fig_map1, fig_map2]

    ax1 = layout.axs[0]
    ax2 = layout.axs[1]
    ax3 = layout.axs[2]
    ax4 = layout.axs[3]
    ax5 = layout.axs[4]
    ax6 = layout.axs[5]
    ax7 = layout.axs[6]
    ax8 = layout.axs[7]

    if ds_elevation is None:
        ds_elevation = ds

    figs: list[ECKFigure] = []

    for _var, _ax in {
        "water_content": ax1,
        "characteristic_diameter": ax2,
        "maximum_dimension_L": ax3,
        "liquid_water_content": ax4,
        "liquid_effective_radius": ax5,
    }.items():
        _fig = CurtainFigure(
            ax=_ax,
        )
        _fig = _fig.ecplot(
            ds=ds,
            var=_var,
            height_range=height_range,
            **common_kwargs,  # type: ignore
        )
        _fig = _fig.ecplot_elevation(ds_elevation)
        figs.append(_fig)

    fig6 = LineFigure(
        ax=ax6,
        ax_style_bottom="geo_nolabels",
    )
    fig6 = fig6.ecplot(
        ds=ds,
        var="ice_water_path",
        **common_kwargs,  # type: ignore
    )
    figs.append(fig6)
    fig7 = LineFigure(
        ax=ax7,
        ax_style_top="geo_nolabels",
        ax_style_bottom="geo_nolabels",
    )
    fig7 = fig7.ecplot(
        ds=ds,
        var="rain_water_path",
        **common_kwargs,  # type: ignore
    )
    figs.append(fig7)
    fig8 = LineFigure(
        ax=ax8,
        ax_style_top="geo_nolabels",
        ax_style_bottom="time",
    )
    fig8 = fig8.ecplot(
        ds=ds,
        var="liquid_water_path",
        **common_kwargs,  # type: ignore
    )
    figs.append(fig8)

    main_figs: list[ECKFigure] = figs

    subfigs: list[list[ECKFigure]] = [map_figs, main_figs]

    _etime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    _dtime: str = str(pd.Timestamp(_etime) - pd.Timestamp(_stime)).split()[-1]
    if logger:
        print_progress(
            f"Plot created (time taken {_dtime}).",
            is_last=True,
            log_msg_prefix=log_msg_prefix,
            logger=logger,
        )

    return QuicklookFigure(layout.fig, subfigs)
