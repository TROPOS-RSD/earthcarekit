from logging import Logger
from typing import Literal, Sequence

import numpy as np
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
from .._quicklook_results import _QuicklookResults
from ._ecql_atl_ebd_2a import ecquicklook_aebd


def ecquicklook_aaer(
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
    return ecquicklook_aebd(
        ds=ds,
        vars=vars,
        show_maps=show_maps,
        show_zoom=show_zoom,
        show_profile=show_profile,
        site=site,
        radius_km=radius_km,
        time_range=time_range,
        height_range=height_range,
        ds_tropopause=ds_tropopause,
        ds_elevation=ds_elevation,
        ds_temperature=ds_temperature,
        resolution="high",
        closest_profile=closest_profile,
        logger=logger,
        log_msg_prefix=log_msg_prefix,
        selection_max_time_margin=selection_max_time_margin,
        show_steps=show_steps,
        mode=mode,
    )
