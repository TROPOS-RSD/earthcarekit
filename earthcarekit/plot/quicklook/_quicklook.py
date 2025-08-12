from logging import Logger
from typing import Literal, Sequence

import xarray as xr

from ...utils.constants import DEFAULT_PROFILE_SHOW_STEPS
from ...utils.ground_sites import GroundSite
from ...utils.read.product._generic import read_product
from ...utils.read.product.auxiliary import rebin_xmet_to_vertical_track
from ...utils.read.product.file_info.type import FileType
from ...utils.time import TimedeltaLike, TimeRangeLike
from ...utils.typing import DistanceRangeLike
from ..figure import ECKFigure
from ._level1 import ecquicklook_anom
from ._level2a import (
    ecquicklook_aaer,
    ecquicklook_acth,
    ecquicklook_aebd,
    ecquicklook_atc,
)
from ._quicklook_results import _QuicklookResults


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
    site: GroundSite | str | None = None,
    radius_km: float = 100.0,
    time_range: TimeRangeLike | None = None,
    height_range: DistanceRangeLike | None = (0, 30e3),
    ds_tropopause: xr.Dataset | str | None = None,
    ds_elevation: xr.Dataset | str | None = None,
    ds_temperature: xr.Dataset | str | None = None,
    resolution: Literal["low", "medium", "high", "l", "m", "h"] = "low",
    ds2: xr.Dataset | str | None = None,
    ds_xmet: xr.Dataset | str | None = None,
    logger: Logger | None = None,
    log_msg_prefix: str = "",
    selection_max_time_margin: TimedeltaLike | Sequence[TimedeltaLike] | None = None,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    mode: Literal["fast", "exact"] = "fast",
) -> _QuicklookResults:
    """
    Generate a preview visualization of an EarthCARE dataset with optional maps, zoomed views, and profiles.

    Args:
        ds (xr.Dataset | str): EarthCARE dataset or path.
        vars (str | list[str] | None, otional): List of variable to plot. Automatically sets product-specific default list of variables if None.
        show_maps (bool, optional): Whether to include map view. Dafaults to True.
        show_zoom (bool, optional): Whether to show an additional column of zoomed plots. Defaults to False.
        show_profile (bool, optional): Whether to include vertical profile plots. Dfaults to True.
        site (GroundSite | str | None, optional): Ground site object or name identifier.
        radius_km (float, optional): Search radius around site in kilometers. Defaults to 100.
        time_range (TimeRangeLike | None, optional): Time range filter.
        height_range (DistanceRangeLike | None, optional): Height range in meters. Defaults to (0, 30_000).
        ds_tropopause (xr.Dataset | str | None, optional): Optional dataset or path containing tropopause data to add it to the plot.
        ds_elevation (xr.Dataset | str | None, optional): Optional dataset or path containing elevation data to add it to the plot.
        ds_temperature (xr.Dataset | str | None, optional): Optional dataset or path containing temperature data to add it to the plot.
        resolution (Literal["low", "medium", "high", "l", "m", "h"], optional): Resolution of A-PRO data. Defaults to "low".
        ds2 (xr.Dataset | str | None, optional): Secondary dataset required for certain product quicklook (e.g., A-LAY products need A-NOM or A-EBD to serve as background curtain plots).
        ds_xmet(xr.Dataset | str | None, optional): Optional auxiliary meteorological dataset used to plot tropopause, elevation and temperature from.
        logger (Logger, optional): Logger instance for output messages.
        log_msg_prefix (str, optional): Prefix for log messages.
        selection_max_time_margin (TimedeltaLike | Sequence[TimedeltaLike] | None, optional): Allowed time difference for selection.
        show_steps (bool, optional): Whether to plot profiles as height bin step functions or instead plot only the line through bin centers. Defaults to True.
        mode (Literal["fast", "exact"], optional): Processing mode.

    Returns:
        _QuicklookResults: Object containing figures and metadata.
    """
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
        selection_max_time_margin=selection_max_time_margin,
        mode=mode,
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
        raise TypeError(f"""Missing dataset "ds2" to plot a background for the CTH""")

    raise NotImplementedError()
