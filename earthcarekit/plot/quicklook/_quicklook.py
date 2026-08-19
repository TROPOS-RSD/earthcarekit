import warnings
from logging import Logger
from typing import Any, Literal, Sequence

import xarray as xr

from ...constants import DEFAULT_PROFILE_SHOW_STEPS
from ...read.info.type import FileType
from ...read.product._generic import read_product
from ...read.product._rebin_xmet_to_vertical_track import (
    rebin_xmet_to_vertical_track,
)
from ...site import SiteLike
from ...typing import DistanceRangeNoneLike
from ...utils.time import TimedeltaLike, TimeRangeLike
from ._level1 import ecquicklook_anom
from ._level2a import (
    ecquicklook_aaer,
    ecquicklook_acth,
    ecquicklook_aebd,
    ecquicklook_atc,
    ecquicklook_ccd,
    ecquicklook_ccld,
    ecquicklook_cfmr,
    ecquicklook_ctc,
)
from ._level2b import ecquicklook_acmcap, ecquicklook_actc
from ._quicklook_results import QuicklookFigure


def _get_addon_ds(
    ds: xr.Dataset,
    ds_filepath: str | None,
    ds_tropopause: xr.Dataset | str | None,
    ds_elevation: xr.Dataset | str | None,
    ds_temperature: xr.Dataset | str | None,
) -> tuple[xr.Dataset | None, xr.Dataset | None, xr.Dataset | None]:
    if (
        isinstance(ds_filepath, str)
        and isinstance(ds_tropopause, str)
        and ds_filepath == ds_tropopause
    ):
        ds_tropopause = ds

    if (
        isinstance(ds_filepath, str)
        and isinstance(ds_elevation, str)
        and ds_filepath == ds_elevation
    ):
        ds_elevation = ds

    if (
        isinstance(ds_filepath, str)
        and isinstance(ds_temperature, str)
        and ds_filepath == ds_temperature
    ):
        ds_temperature = ds

    if (
        isinstance(ds_tropopause, str)
        and isinstance(ds_elevation, str)
        and ds_tropopause == ds_elevation
    ):
        ds_elevation = ds_tropopause

    if (
        isinstance(ds_tropopause, str)
        and isinstance(ds_temperature, str)
        and ds_tropopause == ds_temperature
    ):
        ds_temperature = ds_tropopause

    if (
        isinstance(ds_elevation, str)
        and isinstance(ds_temperature, str)
        and ds_elevation == ds_temperature
    ):
        ds_temperature = ds_elevation

    if isinstance(ds_tropopause, str):
        ds_tropopause = read_product(ds_tropopause, in_memory=True)
    if isinstance(ds_elevation, str):
        ds_elevation = read_product(ds_elevation, in_memory=True)
    if isinstance(ds_temperature, str):
        ds_temperature = read_product(ds_temperature, in_memory=True)

    return ds_tropopause, ds_elevation, ds_temperature


def ecquicklook(
    ds: xr.Dataset | str,
    vars: str | list[str] | None = None,
    show_maps: bool = True,
    show_zoom: bool = False,
    show_profile: bool = True,
    site: SiteLike | None = None,
    radius_km: float = 100.0,
    time_range: TimeRangeLike | None = None,
    height_range: DistanceRangeNoneLike | None = None,
    ds_tropopause: xr.Dataset | str | None = None,
    ds_elevation: xr.Dataset | str | None = None,
    ds_temperature: xr.Dataset | str | None = None,
    resolution: Literal["low", "medium", "high", "l", "m", "h"] = "medium",
    ds2: xr.Dataset | str | None = None,
    ds_xmet: xr.Dataset | str | None = None,
    logger: Logger | None = None,
    log_msg_prefix: str = "",
    selection_pad_time: TimedeltaLike | Sequence[TimedeltaLike] | None = None,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    mode: Literal["fast", "exact"] = "fast",
    map_style: (
        str
        | Literal[
            "none",
            "stock_img",
            "gray",
            "osm",
            "satellite",
            "mtg",
            "msg",
            "blue_marble",
            "land_ocean",
            "land_ocean_lakes_rivers",
        ]
        | None
    ) = "blue_marble",
    curtain_kwargs: dict[str, Any] = {},
    map_kwargs: dict[str, Any] = {},
    profile_kwargs: dict[str, Any] = {},
    **kwargs,
) -> QuicklookFigure:
    """Generate a preview visualization of an EarthCARE dataset with optional maps, zoomed views, and profiles.

    Args:
        ds: EarthCARE dataset or path.
        vars: Variables to plot; auto-selects defaults if None.
        show_maps: Include map view if True.
        show_zoom: Show additional column of zoomed plots if True.
        show_profile: Include vertical profile plots if True.
        site: Ground site object or name identifier.
        radius_km: Search radius around site in kilometers; defaults to 100.
        time_range: Time range filter.
        height_range: Height range in meters.
        ds_tropopause: Optional tropopause dataset; adds to plot if given.
        ds_elevation: Optional elevation dataset; adds to plot if given.
        ds_temperature: Optional temperature dataset; adds to plot if given.
        resolution: A-PRO data resolution ("low"/"medium"/"high" or "l"/"m"/"h"); defaults to "medium".
        ds2: Secondary dataset (e.g., A-NOM for A-LAY background).
        ds_xmet: Auxiliary meteorological dataset for tropopause/elevation/temperature.
        logger: Logger instance for output messages.
        log_msg_prefix: Prefix for log messages.
        selection_pad_time: Allowed time difference for selection.
        show_steps: Plot profiles as step functions if True; line through bin centers otherwise.
        mode: Processing mode ("fast" or "exact").
        map_style: Background style for zoomed map; defaults to "blue_marble".
        curtain_kwargs: Passed to `CurtainFigure`.
        map_kwargs: Passed to `MapFigure`.
        profile_kwargs: Passed to `ProfileFigure`.
        **kwargs: Passed to underlying plotting functions.

    Returns:
        A `QuicklookFigure` object containing the generated figures and metadata.
    """
    # Handle deprecated arguments
    if "selection_max_time_margin" in kwargs:
        msg = "'selection_max_time_margin' is deprecated and will be removed in future versions; use 'selection_pad_time' instead."
        warnings.warn(msg, FutureWarning)
        selection_pad_time = kwargs["selection_max_time_margin"]
        del kwargs["selection_max_time_margin"]
    if len(set(kwargs)) != 0:
        raise TypeError(
            f"{ecquicklook.__name__}() got an unexpected keyword argument '{list(kwargs)[0]}'"
        )

    if isinstance(vars, str):
        vars = [vars]

    filepath: str | None = None
    if isinstance(ds, str):
        filepath = ds

    ds = read_product(ds, in_memory=True)
    file_type = FileType.from_input(ds)

    if isinstance(ds_xmet, (xr.Dataset, str)):
        ds_xmet = read_product(ds_xmet, in_memory=True)
        if file_type in [
            FileType.ATL_NOM_1B,
            FileType.ATL_FM__2A,
            FileType.ATL_AER_2A,
            FileType.ATL_EBD_2A,
            FileType.ATL_ICE_2A,
            FileType.ATL_TC__2A,
            FileType.ATL_CLA_2A,
            FileType.CPR_NOM_1B,
        ]:
            ds_xmet = rebin_xmet_to_vertical_track(ds_xmet, ds)

    ds_tropopause, ds_elevation, ds_temperature = _get_addon_ds(
        ds,
        filepath,
        ds_tropopause or ds_xmet,
        ds_elevation or ds_xmet,
        ds_temperature or ds_xmet,
    )

    kwargs = dict(
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
        logger=logger,
        log_msg_prefix=log_msg_prefix,
        selection_pad_time=selection_pad_time,
        mode=mode,
        map_style=map_style,
        curtain_kwargs=curtain_kwargs,
        map_kwargs=map_kwargs,
        profile_kwargs=profile_kwargs,
    )

    if file_type == FileType.ATL_NOM_1B:
        kwargs["show_steps"] = show_steps
        return ecquicklook_anom(**kwargs)  # type: ignore
    elif file_type == FileType.ATL_EBD_2A:
        kwargs["show_steps"] = show_steps
        kwargs["resolution"] = resolution
        return ecquicklook_aebd(**kwargs)  # type: ignore
    elif file_type == FileType.ATL_AER_2A:
        kwargs["show_steps"] = show_steps
        kwargs["resolution"] = resolution
        return ecquicklook_aaer(**kwargs)  # type: ignore
    elif file_type == FileType.ATL_TC__2A:
        return ecquicklook_atc(**kwargs)  # type: ignore
    elif file_type == FileType.ATL_CTH_2A:
        if ds2 is not None:
            ds2 = read_product(ds2, in_memory=True)
            file_type2 = FileType.from_input(ds2)
            if file_type2 in [
                FileType.ATL_NOM_1B,
                FileType.ATL_EBD_2A,
                FileType.ATL_AER_2A,
                FileType.ATL_TC__2A,
            ]:
                kwargs["ds_bg"] = ds2
                kwargs["resolution"] = resolution
                return ecquicklook_acth(**kwargs)  # type: ignore
            raise ValueError(
                f"There is no CTH background curtain plotting for {str(file_type2)} products. Use instead: {str(FileType.ATL_NOM_1B)}, {str(FileType.ATL_EBD_2A)}, {str(FileType.ATL_AER_2A)}, {str(FileType.ATL_TC__2A)}"
            )
        raise TypeError("""Missing dataset "ds2" to plot a background for the CTH""")
    elif file_type == FileType.CPR_FMR_2A:
        return ecquicklook_cfmr(**kwargs)  # type: ignore
    elif file_type == FileType.CPR_CD__2A:
        return ecquicklook_ccd(**kwargs)  # type: ignore
    elif file_type == FileType.CPR_CLD_2A:
        return ecquicklook_ccld(**kwargs)  # type: ignore
    elif file_type == FileType.CPR_TC__2A:
        return ecquicklook_ctc(**kwargs)  # type: ignore
    elif file_type == FileType.AC__TC__2B:
        return ecquicklook_actc(**kwargs)  # type: ignore
    elif file_type == FileType.ACM_CAP_2B:
        return ecquicklook_acmcap(**kwargs)  # type: ignore
    raise NotImplementedError()
