import logging
import warnings
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..plot import ProfileFigure
from ..plot.figure.multi_panel import create_column_subfigures
from ..utils import (
    FileType,
    GroundSite,
    ProfileData,
    filter_radius,
    read_any,
    read_nc,
    read_polly,
    read_product,
)
from ..utils.constants import CM_AS_INCH, DEFAULT_PROFILE_SHOW_STEPS
from ..utils.typing import ValueRangeLike, validate_numeric_range


def _extract_earthcare_profile(
    ds: xr.Dataset,
    var: str | tuple[str, str],
    site: GroundSite | str | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
) -> ProfileData:
    _logger = logging.getLogger()

    _var: str
    _err: str | None = None
    if isinstance(var, tuple):
        _var = var[0]
        _err = var[1]
    else:
        _var = var

    if site:
        ds_radius = filter_radius(
            ds=ds,
            radius_km=radius_km,
            site=site,
            closest=closest,
        )
    elif ds[var].values.shape[0] == 1:
        ds_radius = ds
    else:
        msg = f"No ground site provied, so all profiles are averaged over given data set. ({var=})"
        _logger.info(msg)
        ds_radius = ds

    file_type_text = FileType.from_input(ds).to_shorthand(with_dash=True)
    legend_label: str = f"{file_type_text}"
    if file_type_text == "A-EBD":
        if "medium_resolution" in _var:
            legend_label = f"{legend_label} medium res."
        elif "low_resolution" in _var:
            legend_label = f"{legend_label} low res."
        else:
            legend_label = f"{legend_label} high res."

    p_radius = ProfileData.from_dataset(
        ds=ds_radius,
        var=_var,
        platform=legend_label,
        error_var=_err,
    )
    return p_radius


def _extract_ground_based_profile(
    ds: xr.Dataset,
    vars: list[str | tuple[str, str]],
    time_var: str,
    height_var: str,
) -> list[ProfileData | None]:
    _logger = logging.getLogger()

    ps: list[ProfileData | None] = []
    for v in vars:
        _var: str
        _error: str | None = None
        if isinstance(v, str):
            _var = v
        elif isinstance(v, tuple):
            _var = v[0]
            _error = v[1]

        if _var not in ds:
            msg = f"Variable `{_var}` not in ground-based data."
            _logger.warning(msg)
            ps.append(None)
            continue
        if isinstance(_error, str) and _error not in ds:
            msg = f"Variable `{_error}` not in ground-based data."
            _logger.warning(msg)
            _error = None

        p = ProfileData.from_dataset(
            ds=ds,
            var=_var,
            error_var=_error,
            time_var=time_var,
            height_var=height_var,
            platform=_var,
        )
        ps.append(p)
    return ps


def _plot_profiles(
    ps_main: list[ProfileData],
    ps: list[ProfileData | None] = [],
    figsize: tuple[float | int, float | int] = (2.0, 5.0),
    selection_height_range: tuple[float, float] | None = None,
    height_range: tuple[float, float] | None = (0, 20e3),
    value_range: tuple[float | None, float | None] | None = None,
    ax: Axes | None = None,
    label: str | None = None,
    units: str | None = None,
    flip_height_axis: bool = False,
    show_height_ticks: bool = True,
    show_height_label: bool = True,
    colors_ec: list[str] = [
        "ec:red",
        "ec:darkred",
        "ec:yellow",
        "ec:orange",
        "ec:lightyellow",
        "ec:darkyellow",
    ],
    colors_ground: list[str] = [
        "ec:blue",
        "ec:darkblue",
        "ec:lightgreen",
        "ec:darkgreen",
        "ec:lightpurple",
        "ec:purple",
    ],
    alpha: float = 0.7,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
) -> ProfileFigure:
    pf = ProfileFigure(
        ax=ax,
        show_legend=True,
        figsize=figsize,
        flip_height_axis=flip_height_axis,
        show_height_ticks=show_height_ticks,
        show_height_label=show_height_label,
    )

    ps.reverse()
    colors_ground = colors_ground[0 : len(ps)]
    colors_ground.reverse()
    for i, p in enumerate(ps):
        if isinstance(p, ProfileData):
            pf = pf.plot(
                p,
                color=colors_ground[i],
                alpha=alpha,
                legend_label=p.platform,
                show_steps=show_steps,
                show_error=True,
            )

    ps_main.reverse()
    colors_ec = colors_ec[0 : len(ps_main)]
    colors_ec.reverse()
    for i, p in enumerate(ps_main):
        kwargs = dict()
        if i == 0:
            kwargs = dict(
                value_range=value_range,
                height_range=height_range,
                selection_height_range=selection_height_range,
                label=label,
                units=units,
            )

        pf = pf.plot(
            p,
            color=colors_ec[i],
            alpha=alpha,
            legend_label=p.platform,
            show_steps=show_steps,
            show_error=True,
            **kwargs,  # type: ignore
        )

    return pf


def _calulate_statistics(
    ps_main: list[ProfileData],
    ps: list[ProfileData | None] = [],
    selection_height_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    for p in ps_main:
        p_pred = p

        if len(ps) == 0 and len(ps_main) == 1:
            ps = [p_pred]  # Workaround for non comparison plots
        elif len(ps) == 0:
            continue

        for p_targ in ps:
            if isinstance(p_targ, ProfileData):
                _df = p_pred.compare_to(
                    p_targ,
                    height_range=selection_height_range,
                ).to_dataframe()
                _df.insert(0, "units", p_pred.units or "")
                _df.insert(0, "target", p_targ.platform)
                _df.insert(0, "prediction", p_pred.platform)
                dfs.append(_df)

    for p_targ in ps_main[1:]:
        p_pred = ps_main[0]

        if isinstance(p_targ, ProfileData):
            _df = p_pred.compare_to(
                p_targ,
                height_range=selection_height_range,
            ).to_dataframe()
            _df.insert(0, "units", p_pred.units or "")
            _df.insert(0, "target", p_targ.platform)
            _df.insert(0, "prediction", p_pred.platform)
            dfs.append(_df)

    if len(dfs) == 0:
        return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)
    return df


def compare_ec_profiles_with_target(
    ds_ec: xr.Dataset,
    var_ec: str | tuple[str, str],
    ds_target: xr.Dataset | None = None,
    var_target: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    ds_ec2: xr.Dataset | None = None,
    var_ec2: str | tuple[str, str] | None = None,
    ds_ec3: xr.Dataset | None = None,
    var_ec3: str | tuple[str, str] | None = None,
    ds_ec4: xr.Dataset | None = None,
    var_ec4: str | tuple[str, str] | None = None,
    selection_height_range: tuple[float, float] | None = None,
    height_range: tuple[float, float] | None = (0, 20e3),
    site: GroundSite | str | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
    closest2: bool = False,
    closest3: bool = False,
    closest4: bool = False,
    time_var_target: str = "start_time",
    height_var_target: str = "height",
    ax: Axes | None = None,
    label: str | None = "Bsc. coeff.",
    units: str | None = "m$^{-1}$ sr$^{-1}$",
    value_range: tuple[float | None, float | None] | None = None,
    flip_height_axis: bool = False,
    show_height_ticks: bool = True,
    show_height_label: bool = True,
    colors_ec: list[str] = [
        "ec:red",
        "ec:darkred",
        "ec:yellow",
        "ec:orange",
        "ec:lightyellow",
        "ec:darkyellow",
    ],
    colors_ground: list[str] = [
        "ec:blue",
        "ec:darkblue",
        "ec:lightgreen",
        "ec:darkgreen",
        "ec:lightpurple",
        "ec:purple",
    ],
    alpha: float = 0.7,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    to_mega: bool = False,
    single_figsize: tuple[float | int, float | int] = (2.0, 5.0),
) -> tuple[ProfileFigure, pd.DataFrame]:
    if isinstance(var_target, (str, tuple)):
        var_target = [var_target]

    ps_main: list[ProfileData] = []

    _closest: list[bool] = [closest, closest2, closest3, closest4]
    _dss_ec: list[xr.Dataset | None] = [ds_ec, ds_ec2, ds_ec3, ds_ec4]
    _vars_ec: list[str | tuple[str, str] | None] = [var_ec, var_ec2, var_ec3, var_ec4]
    for i, _ds in enumerate(_dss_ec):
        _var = _vars_ec[i]
        if isinstance(_ds, xr.Dataset) and isinstance(_var, (str, tuple)):
            p_main = _extract_earthcare_profile(
                ds=_ds,
                var=_var,
                site=site,
                radius_km=radius_km,
                closest=_closest[i],
            )
            ps_main.append(p_main)

    ps: list[ProfileData | None] = []
    if isinstance(ds_target, xr.Dataset):
        ps = _extract_ground_based_profile(
            ds=ds_target,
            vars=var_target,
            time_var=time_var_target,
            height_var=height_var_target,
        )

    _units = f"{units}"
    _value_range = value_range
    if to_mega:
        _units = f"M{units}"
        if isinstance(_value_range, (Sequence, np.ndarray)):
            _v0 = _value_range[0]
            _v1 = _value_range[1]
            if isinstance(_v0, (int | float)):
                _v0 = _v0 * 1e6
            if isinstance(_v1, (int | float)):
                _v1 = _v1 * 1e6
            _value_range = (_v0, _v1)
        for p in ps + ps_main:
            if isinstance(p, ProfileData):
                p.values = p.values * 1e6
                if isinstance(p.error, np.ndarray):
                    p.error = p.error * 1e6
                if isinstance(p.units, str):
                    p.units = f"M{p.units}"

    pf = _plot_profiles(
        ps_main=ps_main,
        ps=ps,
        ax=ax,
        label=label,
        units=_units,
        selection_height_range=selection_height_range,
        height_range=height_range,
        value_range=_value_range,
        flip_height_axis=flip_height_axis,
        show_height_ticks=show_height_ticks,
        show_height_label=show_height_label,
        colors_ec=colors_ec,
        colors_ground=colors_ground,
        alpha=alpha,
        show_steps=show_steps,
        figsize=single_figsize,
    )

    df = _calulate_statistics(
        ps_main=ps_main,
        ps=ps,
        selection_height_range=selection_height_range,
    )

    return (pf, df)


def _get_resolution(resolustion: str) -> str:
    res: str
    if resolustion.lower() in ["low", "l", "_low_resolution"]:
        res = "_low_resolution"
    elif resolustion.lower() in ["medium", "m", "_medium_resolution"]:
        res = "_medium_resolution"
    elif resolustion.lower() in ["high", "h", "_high_resolution"] or resolustion == "":
        res = ""
    else:
        raise ValueError(
            f'invalid resolution "{resolustion}". valid values are: "low" or "l", "medium" or "m", "high" or "h".'
        )
    return res


def _get_ec_vars(
    input_ec: str | xr.Dataset, resolution: str, show_error: bool
) -> list[str | tuple[str, str]]:
    res: str = _get_resolution(resolution)
    file_type = FileType.from_input(input_ec)
    vars_main: list[str]
    if file_type == FileType.ATL_EBD_2A:
        vars_main = [
            f"particle_backscatter_coefficient_355nm{res}",
            f"particle_extinction_coefficient_355nm{res}",
            f"lidar_ratio_355nm{res}",
            f"particle_linear_depol_ratio_355nm{res}",
        ]
    elif file_type == FileType.ATL_AER_2A:
        vars_main = [
            f"particle_backscatter_coefficient_355nm",
            f"particle_extinction_coefficient_355nm",
            f"lidar_ratio_355nm",
            f"particle_linear_depol_ratio_355nm",
        ]
    else:
        raise NotImplementedError(
            f"'{file_type.name}' products are not yet supported by this function."
        )

    if show_error:
        return [(v, f"{v}_error") for v in vars_main]
    return list(vars_main)


def _get_ec_is_closest(input_ec: str | xr.Dataset) -> bool:
    file_type = FileType.from_input(input_ec)
    _closest: bool = False
    if file_type == FileType.ATL_EBD_2A:
        _closest = True
    elif file_type == FileType.ATL_AER_2A:
        _closest = True
    else:
        raise NotImplementedError(
            f"'{file_type.name}' products are not yet supported by this function."
        )
    return _closest


@dataclass(frozen=True)
class _CompareBscExtLRDepolResults:
    fig: Figure
    fig_bsc: ProfileFigure
    fig_ext: ProfileFigure
    fig_lr: ProfileFigure
    fig_depol: ProfileFigure
    stats: pd.DataFrame


def compare_bsc_ext_lr_depol(
    input_ec: str | xr.Dataset,
    input_ground: str | xr.Dataset | None = None,
    time_var_ground: str = "time",
    height_var_ground: str = "height",
    bsc_var_ground: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    ext_var_ground: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    lr_var_ground: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    depol_var_ground: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    input_ec2: str | xr.Dataset | None = None,
    input_ec3: str | xr.Dataset | None = None,
    input_ec4: str | xr.Dataset | None = None,
    site: GroundSite | str | None = None,
    radius_km: float = 100.0,
    resolution: str = "_low_resolution",
    resolution2: str | None = None,
    resolution3: str | None = None,
    resolution4: str | None = None,
    height_range: tuple[float, float] | None = (0, 30e3),
    selection_height_range: tuple[float, float] | None = None,
    selection_height_range_bsc: tuple[float, float] | None = None,
    selection_height_range_ext: tuple[float, float] | None = None,
    selection_height_range_lr: tuple[float, float] | None = None,
    selection_height_range_depol: tuple[float, float] | None = None,
    value_range_bsc: ValueRangeLike | None = (0, 8e-6),
    value_range_ext: ValueRangeLike | None = (0, 3e-4),
    value_range_lr: ValueRangeLike | None = (0, 100),
    value_range_depol: ValueRangeLike | None = (0, 0.6),
    colors_ec: list[str] = [
        "ec:red",
        "ec:orange",
        "ec:yellow",
        "ec:purple",
    ],
    colors_ground: list[str] = [
        "ec:blue",
        "ec:darkblue",
        "ec:lightgreen",
        "ec:darkgreen",
        "ec:purple",
    ],
    alpha: float = 1.0,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    show_error_ec: bool = False,
    to_mega: bool = False,
    single_figsize: tuple[float | int, float | int] = (5 * CM_AS_INCH, 12 * CM_AS_INCH),
) -> _CompareBscExtLRDepolResults:
    """Compares Lidar profiles from up to 3 EarthCARE source dataset an one ground-based dataset by creating plots and statistics dataframe.

    Args:
        input_ec (str | xr.Dataset): A opened EarthCARE or file path.
        input_ground (str | xr.Dataset, optional): A opened ground-based NetCDF dataset or file path (e.g., PollyNET data).
        time_var_ground (str, optional): The name of the time variable in the ground-based dataset (e.g., for single profile PollyNET data use `"start_time"`). Defaults to `"height"`.
        height_var_ground (str, optional): The name of the height variable in the ground-based dataset. Defaults to `"height"`.
        bsc_var_ground (str | tuple | list[str | tuple], optional): Backscatter variable name in the ground-based dataset.
            Multiple variables can be provided as list. Variable errors can be provided as tuples (e.g., `[("bsc", "bsc_err"), ("bsc2", "bsc2_err"), ...]`). Defaults to empty list.
        ext_var_ground (str | tuple | list[str | tuple], optional): Extinction variable name in the ground-based dataset.
            Multiple variables can be provided as list. Variable errors can be provided as tuples (e.g., `[("ext", "ext_err"), ("ext2", "ext2_err"), ...]`). Defaults to empty list.
        lr_var_ground (str | tuple | list[str | tuple], optional): Lidar ratio variable name in the ground-based dataset.
            Multiple variables can be provided as list. Variable errors can be provided as tuples (e.g., `[("lr", "lr_err"), ("lr2", "lr2_err"), ...]`). Defaults to empty list.
        depol_var_ground (str | tuple | list[str | tuple], optional): Depol. ratio variable name in the ground-based dataset.
            Multiple variables can be provided as list. Variable errors can be provided as tuples (e.g., `[("depol", "depol_err"), ("depol2", "depol2_err"), ...]`). Defaults to empty list.
        input_ec2 (str | xr.Dataset, optional): An optional seconds EarthCARE dataset to compare. Defaults to None.
        input_ec3 (str | xr.Dataset, optional): An optional third EarthCARE dataset to compare. Defaults to None.
        site (GroundSite | str | None, optional): Ground site or location of the ground-based data as a `GroundSite` object or by name string (e.g., `"mindelo"`). Defaults to None.
        radius_km (float, optional): Radius around the ground site. Defaults to 100.0.
        resolution (str, optional): Sets the used resolution of the EarthCARE data if applicable (e.g., for A-EBD). Defaults to "_low_resolution".
        height_range (tuple[float, float] | None, optional): Height range in meters to restrict the data for plotting. Defaults to (0, 30e3).
        selection_height_range (tuple[float, float] | None, optional): Height range in meters to select data for statistsics. Defaults to None.
        selection_height_range_bsc (tuple[float, float] | None, optional): Height range in meters to select bsc. data for statistsics. Defaults to None (i.e., `selection_height_range`).
        selection_height_range_ext (tuple[float, float] | None, optional): Height range in meters to select ext. data for statistsics. Defaults to None (i.e., `selection_height_range`).
        selection_height_range_lr (tuple[float, float] | None, optional): Height range in meters to select LR data for statistsics. Defaults to None (i.e., `selection_height_range`).
        selection_height_range_depol (tuple[float, float] | None, optional): Height range in meters to select depol. data for statistsics. Defaults to None (i.e., `selection_height_range`).
        value_range_bsc (ValueRangeLike | None, optional): Tuple setting minimum and maximum value on x-axis. Defaults to (0, 8e-6).
        value_range_ext (ValueRangeLike | None, optional): Tuple setting minimum and maximum value on x-axis. Defaults to (0, 3e-4).
        value_range_lr (ValueRangeLike | None, optional): Tuple setting minimum and maximum value on x-axis. Defaults to (0, 100).
        value_range_depol (ValueRangeLike | None, optional): Tuple setting minimum and maximum value on x-axis. Defaults to (0, 0.6).
        colors_ec (list[str], optional): List of colors for the EarthCARE profiles.
        colors_ground (list[str], optional): List of colors for the ground-based profiles.
        alpha (float, optional): Transparency value for the profile lines (value between 0 and 1). Defaults to 1.0.
        show_steps (bool, optional): If True, profiles will be plotted as step functions instead of bin centers.
        show_error_ec (bool, optional): If True, plot error ribbons for EarthCARE profiles.
        to_mega (bool, optional): If Ture, converts bsc. and ext. data results (i.e., plot and statistics) to [Mm-1 sr-1] and [Mm-1]. Defaults to False.
        single_figsize (tuple[float, float], optional): 2-element tuple setting width and height of the subfigures (i.e., for each profile plot).
    Returns:
        results (_CompareBscExtLRDepolResults): An object containing the plot and statistical results.
            - `results.fig`: The `matplotlib` figure
            - `results.fig_bsc`: Backscatter subfigure as `ProfileFigure`
            - `results.fig_ext`: Extinction subfigure as `ProfileFigure`
            - `results.fig_lr`: Lidar ratio subfigure as `ProfileFigure`
            - `results.fig_depol`: Depol. ratio subfigure as `ProfileFigure`
            - `results.stats`: Statistical results as a `pandas.DataFrame`
    """
    _vars_main: list[str | tuple[str, str]] = _get_ec_vars(
        input_ec,
        resolution,
        show_error=show_error_ec,
    )
    _closest: bool = _get_ec_is_closest(input_ec)

    if not isinstance(resolution2, str):
        resolution2 = resolution

    if not isinstance(resolution3, str):
        resolution3 = resolution

    if not isinstance(resolution4, str):
        resolution4 = resolution

    _vars_main2: list[str | tuple[str, str]] | None = None
    _closest2: bool | None = None
    if input_ec2 is not None:
        _vars_main2 = _get_ec_vars(
            input_ec2,
            resolution2,
            show_error=show_error_ec,
        )
        _closest2 = _get_ec_is_closest(input_ec2)

    _vars_main3: list[str | tuple[str, str]] | None = None
    _closest3: bool | None = None
    if input_ec3 is not None:
        _vars_main3 = _get_ec_vars(
            input_ec3,
            resolution3,
            show_error=show_error_ec,
        )
        _closest3 = _get_ec_is_closest(input_ec3)

    _vars_main4: list[str | tuple[str, str]] | None = None
    _closest4: bool | None = None
    if input_ec4 is not None:
        _vars_main4 = _get_ec_vars(
            input_ec4,
            resolution4,
            show_error=show_error_ec,
        )
        _closest4 = _get_ec_is_closest(input_ec4)

    with (
        read_product(input_ec) as ds_ec,
        nullcontext(None if input_ec2 is None else read_product(input_ec2)) as ds_ec2,
        nullcontext(None if input_ec3 is None else read_product(input_ec3)) as ds_ec3,
        nullcontext(None if input_ec4 is None else read_product(input_ec4)) as ds_ec4,
        nullcontext(
            None if input_ground is None else read_any(input_ground)
        ) as ds_target,
    ):
        fig, axs = create_column_subfigures(
            ncols=4,
            single_figsize=single_figsize,
            margin=0.6,
        )

        vars_target: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
            bsc_var_ground,
            ext_var_ground,
            lr_var_ground,
            depol_var_ground,
        ]

        label = [
            "Bsc. coeff.",
            "Ext. coeff.",
            "Lidar ratio",
            "Depol. ratio",
        ]
        units = [
            "m$^{-1}$ sr$^{-1}$",
            "m$^{-1}$",
            "sr",
            "",
        ]
        value_range: list = [
            value_range_bsc,
            value_range_ext,
            value_range_lr,
            value_range_depol,
        ]

        if selection_height_range_bsc is None:
            selection_height_range_bsc = selection_height_range
        if selection_height_range_ext is None:
            selection_height_range_ext = selection_height_range
        if selection_height_range_lr is None:
            selection_height_range_lr = selection_height_range
        if selection_height_range_depol is None:
            selection_height_range_depol = selection_height_range

        _selection_height_range = [
            selection_height_range_bsc,
            selection_height_range_ext,
            selection_height_range_lr,
            selection_height_range_depol,
        ]

        pfs: list[ProfileFigure] = []
        dfs: list[pd.DataFrame] = []
        for i in range(len(_vars_main)):
            _flip_height_axis: bool = False
            _show_height_ticks: bool = True
            _show_height_label: bool = False

            if i == 0:
                _show_height_label = True
                _show_height_ticks = True

            _pf, _df = compare_ec_profiles_with_target(
                ds_ec=ds_ec,
                ds_ec2=ds_ec2,
                ds_ec3=ds_ec3,
                ds_ec4=ds_ec4,
                ds_target=ds_target,
                var_ec=_vars_main[i],
                var_ec2=None if _vars_main2 is None else _vars_main2[i],
                var_ec3=None if _vars_main3 is None else _vars_main3[i],
                var_ec4=None if _vars_main4 is None else _vars_main4[i],
                var_target=vars_target[i],
                selection_height_range=_selection_height_range[i],
                height_range=height_range,
                site=site,
                radius_km=radius_km,
                closest=_closest,
                closest2=False if _closest2 is None else _closest2,
                closest3=False if _closest3 is None else _closest3,
                closest4=False if _closest4 is None else _closest4,
                time_var_target=time_var_ground,
                height_var_target=height_var_ground,
                ax=axs[i],
                label=label[i],
                units=units[i],
                value_range=value_range[i],
                flip_height_axis=_flip_height_axis,
                show_height_ticks=_show_height_ticks,
                show_height_label=_show_height_label,
                colors_ec=colors_ec,
                colors_ground=colors_ground,
                alpha=alpha,
                show_steps=show_steps,
                to_mega=False if i > 1 else to_mega,
                single_figsize=single_figsize,
            )
            pfs.append(_pf)
            dfs.append(_df)
        df = pd.concat(dfs, ignore_index=True)

    return _CompareBscExtLRDepolResults(
        fig=fig,
        fig_bsc=pfs[0],
        fig_ext=pfs[1],
        fig_lr=pfs[2],
        fig_depol=pfs[3],
        stats=df,
    )
