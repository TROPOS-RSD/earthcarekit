from logging import Logger
from typing import Literal, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ....utils.constants import CM_AS_INCH, DEFAULT_PROFILE_SHOW_STEPS, TIME_VAR
from ....utils.read.product.level1.atl_nom_1b import get_depol_profile
from ....utils.time import TimedeltaLike, TimeRangeLike
from ....utils.typing import DistanceRangeLike
from ....utils.xarray_utils import filter_radius, filter_time
from ...figure import (
    CurtainFigure,
    ECKFigure,
    FigureType,
    MapFigure,
    ProfileFigure,
    create_fig_layout_map_main_zoom_profile,
)
from .._cli import print_progress
from .._quicklook_results import _QuicklookResults


def ecquicklook_aebd(
    ds: xr.Dataset,
    vars: list[str] | None = None,
    show_maps: bool = True,
    show_zoom: bool = False,
    show_profile: bool = True,
    site: str | None = None,
    radius_km: float = 100.0,
    time_range: TimeRangeLike | None = None,
    height_range: DistanceRangeLike | None = (0, 30e3),
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
) -> _QuicklookResults:
    _stime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    if ds_elevation is None:
        ds_elevation = ds

    res: str
    if resolution.lower() in ["low", "l"]:
        res = "_low_resolution"
    elif resolution.lower() in ["medium", "m"]:
        res = "_medium_resolution"
    elif resolution.lower() in ["high", "h"]:
        res = ""
    else:
        raise ValueError(
            f'invalid resolution "{resolution}". valid values are: "low" or "l", "medium" or "m", "high" or "h".'
        )

    if vars is None:
        vars = [
            f"particle_backscatter_coefficient_355nm{res}",
            f"particle_extinction_coefficient_355nm{res}",
            f"lidar_ratio_355nm{res}",
            f"particle_linear_depol_ratio_355nm{res}",
        ]

    wspaces: list[float] = []

    if show_maps:
        map_rows = [FigureType.MAP_1_ROW, FigureType.MAP_1_ROW]
        wspaces.append(3.5 * CM_AS_INCH)
    else:
        map_rows = None

    main_rows = [FigureType.CURTAIN for _ in vars]

    if show_zoom:
        zoom_rows = [FigureType.CURTAIN for _ in vars]
        wspaces.append(4 * CM_AS_INCH)
    else:
        zoom_rows = None

    if show_profile:
        profile_rows = [FigureType.PROFILE for _ in vars]
        if show_zoom:
            wspaces.append(2.5 * CM_AS_INCH)
        else:
            wspaces.append(4 * CM_AS_INCH)
    else:
        profile_rows = None

    if logger:
        print_progress(f"layout", log_msg_prefix=log_msg_prefix, logger=logger)

    output = create_fig_layout_map_main_zoom_profile(
        map_rows=map_rows,
        main_rows=main_rows,
        zoom_rows=zoom_rows,
        profile_rows=profile_rows,
        wspace=wspaces,
    )

    fig, axs_map, axs_main, axs_zoom, axs_profile = output

    map_figs: list[ECKFigure] = []
    main_figs: list[ECKFigure] = []
    zoom_figs: list[ECKFigure] = []
    profile_figs: list[ECKFigure] = []

    if show_maps:
        if logger:
            print_progress(f"map globe", log_msg_prefix=log_msg_prefix, logger=logger)
        mf = MapFigure(ax=axs_map[0])
        mf = mf.ecplot(
            ds,
            site=site,
            radius_km=radius_km,
            time_range=time_range,
            selection_max_time_margin=selection_max_time_margin,
        )
        map_figs.append(mf)

        if logger:
            print_progress(f"map zoomed", log_msg_prefix=log_msg_prefix, logger=logger)
        mf = MapFigure(
            ax=axs_map[1],
            style="satellite",
            show_night_shade=False,
            show_right_labels=False,
            show_top_labels=False,
        )
        mf = mf.ecplot(
            ds,
            site=site,
            radius_km=radius_km,
            time_range=time_range,
            view="overpass",
            selection_max_time_margin=selection_max_time_margin,
        )
        map_figs.append(mf)

    for i, var in enumerate(vars):
        if logger:
            print_progress(
                f"curtain: {var=}", log_msg_prefix=log_msg_prefix, logger=logger
            )
        cf = CurtainFigure(ax=axs_main[i], mode=mode)
        cf = cf.ecplot(
            ds,
            var,
            site=site,
            radius_km=radius_km,
            selection_time_range=time_range,
            height_range=height_range,
            mark_closest_profile=closest_profile,
            selection_max_time_margin=selection_max_time_margin,
        )
        if ds_tropopause:
            if logger:
                print_progress(
                    f"tropopause", log_msg_prefix=log_msg_prefix, logger=logger
                )
            cf = cf.ecplot_tropopause(ds_tropopause)
        if ds_elevation:
            if logger:
                print_progress(
                    f"elevation", log_msg_prefix=log_msg_prefix, logger=logger
                )
            cf = cf.ecplot_elevation(ds_elevation)
        if ds_temperature:
            if logger:
                print_progress(
                    f"temperature", log_msg_prefix=log_msg_prefix, logger=logger
                )
            cf = cf.ecplot_temperature(ds_temperature)

        main_figs.append(cf)

    if show_zoom or show_profile:
        _ds = ds.copy()
        if site:
            _ds = filter_radius(_ds, radius_km=radius_km, site=site)
        elif time_range:
            _ds = filter_time(_ds, time_range)

        if show_zoom:
            _time_range = _ds[TIME_VAR].values[[0, -1]]
            for i, var in enumerate(vars):
                if logger:
                    print_progress(
                        f"{log_msg_prefix}curtain zoomed: {var=} ...",
                        log_msg_prefix=log_msg_prefix,
                        logger=logger,
                    )
                cf = CurtainFigure(
                    ax=axs_zoom[i],
                    num_ticks=4,
                    show_height_left=False,
                    show_height_right=True,
                    mode=mode,
                )
                cf = cf.ecplot(
                    ds,
                    var,
                    colorbar=False,
                    time_range=_time_range,
                    height_range=height_range,
                    mark_closest_profile=closest_profile,
                )
                if ds_tropopause:
                    if logger:
                        print_progress(
                            f"tropopause zoomed",
                            log_msg_prefix=log_msg_prefix,
                            logger=logger,
                        )
                    cf = cf.ecplot_tropopause(ds_tropopause)
                if ds_elevation:
                    if logger:
                        print_progress(
                            f"elevation zoomed",
                            log_msg_prefix=log_msg_prefix,
                            logger=logger,
                        )
                    cf = cf.ecplot_elevation(ds_elevation)
                if ds_temperature:
                    if logger:
                        print_progress(
                            f"temperature zoomed",
                            log_msg_prefix=log_msg_prefix,
                            logger=logger,
                        )
                    cf = cf.ecplot_temperature(ds_temperature)

                zoom_figs.append(cf)

        if show_profile:
            if site and closest_profile:
                _ds = filter_radius(
                    _ds, radius_km=radius_km, site=site, closest=closest_profile
                )
            for i, var in enumerate(vars):
                if logger:
                    print_progress(
                        f"profile: {var=}", log_msg_prefix=log_msg_prefix, logger=logger
                    )
                pf = ProfileFigure(
                    ax=axs_profile[i],
                    flip_height_axis=True,
                )
                pf = pf.ecplot(
                    _ds,
                    var,
                    height_range=height_range,
                    color="ec:red",
                    show_steps=show_steps,
                )

                profile_figs.append(pf)

    subfigs: list[list[ECKFigure]] = [map_figs, main_figs, zoom_figs, profile_figs]

    _etime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    _dtime: str = str(pd.Timestamp(_etime) - pd.Timestamp(_stime)).split()[-1]
    if logger:
        print_progress(
            f"Plot created (time taken {_dtime}).",
            is_last=True,
            log_msg_prefix=log_msg_prefix,
            logger=logger,
        )

    return _QuicklookResults(fig, subfigs)
