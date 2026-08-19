import logging
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..constants import CM_AS_INCH, DEFAULT_PROFILE_SHOW_STEPS
from ..data.profile import Profile
from ..filter import filter_radius
from ..plot import ProfileFigure
from ..plot.figure.multi_panel import create_column_figure_layout
from ..read import (
    FileType,
    read_any,
    read_product,
)
from ..site import SiteLike
from ..typing import ValueRangeLike
from ..utils.logging import silence_logger


def _extract_earthcare_profile(
    ds: xr.Dataset,
    var: str | tuple[str, str],
    site: SiteLike | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
) -> Profile:
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
    elif ds[_var].values.shape[0] == 1:
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

    p_radius = Profile.from_dataset(
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
) -> list[Profile | None]:
    _logger = logging.getLogger()

    ps: list[Profile | None] = []
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

        p = Profile.from_dataset(
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
    ps_main: list[Profile],
    ps: list[Profile | None] = [],
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
    linewidth_ec: list[float | int] | float | int = 1.5,
    linewidth_ground: list[float | int] | float | int = 1.5,
    linestyle_ec: list[str] | str = "solid",
    linestyle_ground: list[str] | str = "solid",
    label_ec: list[str | None] = [],
    label_ground: list[str | None] = [],
    alpha: float = 0.7,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
) -> ProfileFigure:
    _ps_main = ps_main.copy()
    _ps = ps.copy()
    pf = ProfileFigure(
        ax=ax,
        show_legend=True,
        figsize=figsize,
        flip_height_axis=flip_height_axis,
        show_height_ticks=show_height_ticks,
        show_height_label=show_height_label,
    )

    lw_ec = [float(x) for x in np.atleast_1d(linewidth_ec)][0 : len(ps_main)]
    lw_ec.reverse()
    lw_ground = [float(x) for x in np.atleast_1d(linewidth_ground)][0 : len(ps)]
    lw_ground.reverse()
    ls_ec = [str(x) for x in np.atleast_1d(linestyle_ec)][0 : len(ps_main)]
    ls_ec.reverse()
    ls_ground = [str(x) for x in np.atleast_1d(linestyle_ground)][0 : len(ps)]
    ls_ground.reverse()

    _label_ec = label_ec.copy()[0 : len(ps_main)]
    _label_ground = label_ground.copy()[0 : len(ps)]
    _label_ec.reverse()
    _label_ground.reverse()

    _ps.reverse()
    colors_ground = colors_ground[0 : len(_ps)]
    colors_ground.reverse()
    for i, p in enumerate(_ps):
        if len(lw_ground) < len(_ps):
            lw_ground.insert(i, lw_ground[0])
        if len(ls_ground) < len(_ps):
            ls_ground.insert(i, ls_ground[0])
        if len(_label_ground) < len(_ps):
            _label_ground.insert(i, None if not isinstance(p, Profile) else p.platform)
        if isinstance(p, Profile):
            pf = pf.plot(
                p,
                color=colors_ground[i],
                alpha=alpha,
                linewidth=lw_ground[i],
                linestyle=ls_ground[i],
                legend_label=_label_ground[i],
                show_steps=show_steps,
                show_error=True,
                value_range=value_range,
            )

    _ps_main.reverse()
    colors_ec = colors_ec[0 : len(_ps_main)]
    colors_ec.reverse()
    for i, p in enumerate(_ps_main):
        if len(lw_ec) < len(_ps_main):
            lw_ec.insert(i, lw_ec[0])
        if len(ls_ec) < len(_ps_main):
            ls_ec.insert(i, ls_ec[0])
        if len(_label_ec) < len(_ps_main):
            _label_ec.insert(i, p.platform)

        kwargs = dict()
        if i == 0:
            kwargs = dict(
                selection_height_range=selection_height_range,
            )
        pf = pf.plot(
            p,
            color=colors_ec[i],
            alpha=alpha,
            linewidth=lw_ec[i],
            linestyle=ls_ec[i],
            legend_label=_label_ec[i],
            show_steps=show_steps,
            show_error=True,
            label=label,
            units=units,
            value_range=value_range,
            height_range=height_range,
            **kwargs,  # type: ignore
        )

    return pf


def _calulate_statistics(
    ps_main: list[Profile],
    ps: list[Profile | None] = [],
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
            if isinstance(p_targ, Profile):
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

        if isinstance(p_targ, Profile):
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
    ds_target2: xr.Dataset | None = None,
    var_target2: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    ds_target3: xr.Dataset | None = None,
    var_target3: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    ds_target4: xr.Dataset | None = None,
    var_target4: str | tuple[str, str] | list[str | tuple[str, str]] = [],
    selection_height_range: tuple[float, float] | None = None,
    height_range: tuple[float, float] | None = (0, 20e3),
    site: SiteLike | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
    closest2: bool = False,
    closest3: bool = False,
    closest4: bool = False,
    time_var_target: str = "start_time",
    height_var_target: str = "height",
    time_var_target2: str = "start_time",
    height_var_target2: str = "height",
    time_var_target3: str = "start_time",
    height_var_target3: str = "height",
    time_var_target4: str = "start_time",
    height_var_target4: str = "height",
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
    linewidth_ec: list[float | int] | float | int = 1.5,
    linewidth_ground: list[float | int] | float | int = 1.5,
    linestyle_ec: list[str] | str = "solid",
    linestyle_ground: list[str] | str = "solid",
    label_ec: list[str | None] = [],
    label_ground: list[str | None] = [],
    alpha: float = 0.7,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    show_rebinned: bool = False,
    to_mega: bool = False,
    single_figsize: tuple[float | int, float | int] = (2.0, 5.0),
) -> tuple[ProfileFigure, pd.DataFrame]:
    if isinstance(var_target, (str, tuple)):
        var_target = [var_target]
    if isinstance(var_target2, (str, tuple)):
        var_target2 = [var_target2]
    if isinstance(var_target3, (str, tuple)):
        var_target3 = [var_target3]
    if isinstance(var_target4, (str, tuple)):
        var_target4 = [var_target4]

    ps_main: list[Profile] = []

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

    ps: list[Profile | None] = []
    if isinstance(ds_target, xr.Dataset):
        _ps = _extract_ground_based_profile(
            ds=ds_target,
            vars=var_target,
            time_var=time_var_target,
            height_var=height_var_target,
        )
        ps.extend(_ps)
    if isinstance(ds_target2, xr.Dataset):
        _ps = _extract_ground_based_profile(
            ds=ds_target2,
            vars=var_target2,
            time_var=time_var_target2,
            height_var=height_var_target2,
        )
        ps.extend(_ps)
    if isinstance(ds_target3, xr.Dataset):
        _ps = _extract_ground_based_profile(
            ds=ds_target3,
            vars=var_target3,
            time_var=time_var_target3,
            height_var=height_var_target3,
        )
        ps.extend(_ps)
    if isinstance(ds_target4, xr.Dataset):
        _ps = _extract_ground_based_profile(
            ds=ds_target4,
            vars=var_target4,
            time_var=time_var_target4,
            height_var=height_var_target4,
        )
        ps.extend(_ps)

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
            if isinstance(p, Profile):
                p.values = p.values * 1e6
                if isinstance(p.error, np.ndarray):
                    p.error = p.error * 1e6
                if isinstance(p.units, str):
                    p.units = f"M{p.units}"

    _ps = ps
    if show_rebinned and len(ps_main) > 1:
        _ps = []
        _p0 = ps_main[0].copy()
        for p in ps:
            if isinstance(p, Profile):
                _ps.append(p.rebin_height(_p0.height))
            else:
                _ps.append(p)
    pf = _plot_profiles(
        ps_main=ps_main,
        ps=_ps,
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
        linewidth_ec=linewidth_ec,
        linewidth_ground=linewidth_ground,
        linestyle_ec=linestyle_ec,
        linestyle_ground=linestyle_ground,
        label_ec=label_ec,
        label_ground=label_ground,
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
            "particle_backscatter_coefficient_355nm",
            "particle_extinction_coefficient_355nm",
            "lidar_ratio_355nm",
            "particle_linear_depol_ratio_355nm",
        ]
    elif file_type == FileType.ATL_CLA_2A:
        vars_main = [
            "aerosol_backscatter_10km",
            "aerosol_extinction_10km",
            "aerosol_lidar_ratio_10km",
            "aerosol_depolarization_10km",
        ]
        show_error = False
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
    elif file_type == FileType.ATL_CLA_2A:
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
    input_ground2: str | xr.Dataset | None = None,
    input_ground3: str | xr.Dataset | None = None,
    input_ground4: str | xr.Dataset | None = None,
    time_var_ground2: str | None = None,
    height_var_ground2: str | None = None,
    time_var_ground3: str | None = None,
    height_var_ground3: str | None = None,
    time_var_ground4: str | None = None,
    height_var_ground4: str | None = None,
    bsc_var_ground2: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    ext_var_ground2: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    lr_var_ground2: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    depol_var_ground2: (str | tuple[str, str] | list[str | tuple[str, str]] | None) = None,
    bsc_var_ground3: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    ext_var_ground3: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    lr_var_ground3: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    depol_var_ground3: (str | tuple[str, str] | list[str | tuple[str, str]] | None) = None,
    bsc_var_ground4: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    ext_var_ground4: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    lr_var_ground4: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
    depol_var_ground4: (str | tuple[str, str] | list[str | tuple[str, str]] | None) = None,
    site: SiteLike | None = None,
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
    linewidth_ec: list[float | int] | float | int = 1.5,
    linewidth_ground: list[float | int] | float | int = 1.5,
    linestyle_ec: list[str] | str = "solid",
    linestyle_ground: list[str] | str = "solid",
    label_ec: list[str | None] = [],
    label_ground: list[str | None] = [],
    alpha: float = 1.0,
    show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    show_error_ec: bool = False,
    show_quality_status: bool = False,
    show_rebinned: bool = False,
    quality_status_width_scale: float = 1.0,
    quality_status_var: str = "quality_status",
    quality_status_value_range: tuple[float | None, float | None] | None = None,
    to_mega: bool = False,
    single_figsize: tuple[float | int, float | int] = (5 * CM_AS_INCH, 12 * CM_AS_INCH),
    label_bsc: str = "Bsc. coeff.",
    label_ext: str = "Ext. coeff.",
    label_lr: str = "Lidar ratio",
    label_depol: str = "Depol. ratio",
    units_bsc: str = "m$^{-1}$ sr$^{-1}$",
    units_ext: str = "m$^{-1}$",
    units_lr: str = "sr",
    units_depol: str = "",
    verbose: bool = True,
) -> _CompareBscExtLRDepolResults:
    """Compares Lidar profiles from up to 4 EarthCARE and 4 ground-based datasets.

    Creates plots and statistics for backscatter, extinction, lidar ratio, and depolarization.

    Args:
        input_ec: EarthCARE dataset or path (primary).
        input_ground: Ground-based dataset or path (primary).
        time_var_ground: Time variable name in ground dataset.
        height_var_ground: Height variable name in ground dataset.
        bsc_var_ground: Backscatter variable name(s) in ground dataset (e.g., `"bsc"` or `[("bsc", "bsc_err"), "bsc2"]`).
        ext_var_ground: Extinction variable name(s) in ground dataset.
        lr_var_ground: Lidar ratio variable name(s) in ground dataset.
        depol_var_ground: Depolarization ratio variable name(s) in ground dataset.
        input_ec2: Optional second EarthCARE dataset.
        input_ec3: Optional third EarthCARE dataset.
        input_ec4: Optional fourth EarthCARE dataset.
        input_ground2: Optional second ground-based dataset.
        input_ground3: Optional third ground-based dataset.
        input_ground4: Optional fourth ground-based dataset.
        time_var_ground2: Time variable name in second ground dataset.
        height_var_ground2: Height variable name in second ground dataset.
        time_var_ground3: Time variable name in third ground dataset.
        height_var_ground3: Height variable name in third ground dataset.
        time_var_ground4: Time variable name in fourth ground dataset.
        height_var_ground4: Height variable name in fourth ground dataset.
        bsc_var_ground2: Backscatter variable name(s) in second ground dataset.
        ext_var_ground2: Extinction variable name(s) in second ground dataset.
        lr_var_ground2: Lidar ratio variable name(s) in second ground dataset.
        depol_var_ground2: Depolarization ratio variable name(s) in second ground dataset.
        bsc_var_ground3: Backscatter variable name(s) in third ground dataset.
        ext_var_ground3: Extinction variable name(s) in third ground dataset.
        lr_var_ground3: Lidar ratio variable name(s) in third ground dataset.
        depol_var_ground3: Depolarization ratio variable name(s) in third ground dataset.
        bsc_var_ground4: Backscatter variable name(s) in fourth ground dataset.
        ext_var_ground4: Extinction variable name(s) in fourth ground dataset.
        lr_var_ground4: Lidar ratio variable name(s) in fourth ground dataset.
        depol_var_ground4: Depolarization ratio variable name(s) in fourth ground dataset.
        site: Ground site for spatial filtering.
        radius_km: Search radius around site in kilometers.
        resolution: EarthCARE resolution suffix (e.g., "_low_resolution").
        resolution2: Resolution suffix for second EarthCARE dataset.
        resolution3: Resolution suffix for third EarthCARE dataset.
        resolution4: Resolution suffix for fourth EarthCARE dataset.
        height_range: Plot height range in meters.
        selection_height_range: Height range for statistics (applies to all variables).
        selection_height_range_bsc: Height range for backscatter statistics.
        selection_height_range_ext: Height range for extinction statistics.
        selection_height_range_lr: Height range for lidar ratio statistics.
        selection_height_range_depol: Height range for depolarization statistics.
        value_range_bsc: X-axis limits for backscatter plot.
        value_range_ext: X-axis limits for extinction plot.
        value_range_lr: X-axis limits for lidar ratio plot.
        value_range_depol: X-axis limits for depolarization plot.
        colors_ec: Colors for EarthCARE profiles.
        colors_ground: Colors for ground-based profiles.
        linewidth_ec: Line width(s) for EarthCARE profiles.
        linewidth_ground: Line width(s) for ground-based profiles.
        linestyle_ec: Line style(s) for EarthCARE profiles.
        linestyle_ground: Line style(s) for ground-based profiles.
        label_ec: Legend labels for EarthCARE profiles.
        label_ground: Legend labels for ground-based profiles.
        alpha: Line transparency (0-1).
        show_steps: Plot step functions instead of bin centers if True.
        show_error_ec: Plot error ribbons for EarthCARE profiles if True.
        show_rebinned: Rebin ground data to EarthCARE grid if True.
        show_quality_status: Plot quality status bars if True.
        show_rebinned: Rebin ground data to EarthCARE grid if True.
        quality_status_width_scale: Scale factor for quality status bar width.
        quality_status_var: Variable name for quality status.
        quality_status_value_range: Value range for quality status display.
        to_mega: Convert units to Mm-1 sr-1/Mm-1 if True.
        single_figsize: Subfigure size (width, height) in inches.
        label_bsc: Label for backscatter subfigure.
        label_ext: Label for extinction subfigure.
        label_lr: Label for lidar ratio subfigure.
        label_depol: Label for depolarization subfigure.
        units_bsc: Units for backscatter axis.
        units_ext: Units for extinction axis.
        units_lr: Units for lidar ratio axis.
        units_depol: Units for depolarization axis.
        verbose: Print logs to console if True.

    Returns:
        Results as a `_CompareBscExtLRDepolResults` object with figures and statistics

            - `results.fig`: The `matplotlib` figure
            - `results.fig_bsc`: Backscatter subfigure as `ProfileFigure`
            - `results.fig_ext`: Extinction subfigure as `ProfileFigure`
            - `results.fig_lr`: Lidar ratio subfigure as `ProfileFigure`
            - `results.fig_depol`: Depol. ratio subfigure as `ProfileFigure`
            - `results.stats`: Statistical results as a `pandas.DataFrame`
    """
    _logger = logging.getLogger()
    ctx = nullcontext() if verbose else silence_logger(_logger)
    with ctx:
        _vars_main: list[str | tuple[str, str]] = _get_ec_vars(
            input_ec,
            resolution,
            show_error=show_error_ec,
        )
        _closest: bool = _get_ec_is_closest(input_ec)

        label = [
            label_bsc,
            label_ext,
            label_lr,
            label_depol,
        ]

        units = [
            units_bsc,
            units_ext,
            units_lr,
            units_depol,
        ]

        if not isinstance(resolution2, str):
            resolution2 = resolution
        if not isinstance(resolution3, str):
            resolution3 = resolution
        if not isinstance(resolution4, str):
            resolution4 = resolution

        if not isinstance(time_var_ground2, str):
            time_var_ground2 = time_var_ground
        if not isinstance(time_var_ground3, str):
            time_var_ground3 = time_var_ground
        if not isinstance(time_var_ground4, str):
            time_var_ground4 = time_var_ground

        if not isinstance(height_var_ground2, str):
            height_var_ground2 = height_var_ground
        if not isinstance(height_var_ground3, str):
            height_var_ground3 = height_var_ground
        if not isinstance(height_var_ground4, str):
            height_var_ground4 = height_var_ground

        if bsc_var_ground2 is None:
            bsc_var_ground2 = bsc_var_ground
        if bsc_var_ground3 is None:
            bsc_var_ground3 = bsc_var_ground
        if bsc_var_ground4 is None:
            bsc_var_ground4 = bsc_var_ground

        if ext_var_ground2 is None:
            ext_var_ground2 = ext_var_ground
        if ext_var_ground3 is None:
            ext_var_ground3 = ext_var_ground
        if ext_var_ground4 is None:
            ext_var_ground4 = ext_var_ground

        if lr_var_ground2 is None:
            lr_var_ground2 = lr_var_ground
        if lr_var_ground3 is None:
            lr_var_ground3 = lr_var_ground
        if lr_var_ground4 is None:
            lr_var_ground4 = lr_var_ground

        if depol_var_ground2 is None:
            depol_var_ground2 = depol_var_ground
        if depol_var_ground3 is None:
            depol_var_ground3 = depol_var_ground
        if depol_var_ground4 is None:
            depol_var_ground4 = depol_var_ground

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
            nullcontext(None if input_ground is None else read_any(input_ground)) as ds_target,
            nullcontext(None if input_ground2 is None else read_any(input_ground2)) as ds_target2,
            nullcontext(None if input_ground3 is None else read_any(input_ground3)) as ds_target3,
            nullcontext(None if input_ground4 is None else read_any(input_ground4)) as ds_target4,
        ):
            ncols: int = 4
            width_scale: float | list[float] = 1.0
            if show_quality_status:
                ncols = 5
                width_scale = [1.0, 1.0, 1.0, 1.0, quality_status_width_scale]
            _output = create_column_figure_layout(
                ncols=ncols,
                single_figsize=single_figsize,
                margin=0.6,
                width_scale=width_scale,
            )
            fig = _output.fig
            axs = _output.axs

            vars_target: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
                bsc_var_ground,
                ext_var_ground,
                lr_var_ground,
                depol_var_ground,
            ]

            vars_target2: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
                bsc_var_ground2,
                ext_var_ground2,
                lr_var_ground2,
                depol_var_ground2,
            ]

            vars_target3: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
                bsc_var_ground3,
                ext_var_ground3,
                lr_var_ground3,
                depol_var_ground3,
            ]

            vars_target4: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
                bsc_var_ground4,
                ext_var_ground4,
                lr_var_ground4,
                depol_var_ground4,
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
                    ds_target2=ds_target2,
                    ds_target3=ds_target3,
                    ds_target4=ds_target4,
                    var_ec=_vars_main[i],
                    var_ec2=None if _vars_main2 is None else _vars_main2[i],
                    var_ec3=None if _vars_main3 is None else _vars_main3[i],
                    var_ec4=None if _vars_main4 is None else _vars_main4[i],
                    var_target=vars_target[i],
                    var_target2=vars_target2[i],
                    var_target3=vars_target3[i],
                    var_target4=vars_target4[i],
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
                    time_var_target2=time_var_ground2,
                    height_var_target2=height_var_ground2,
                    time_var_target3=time_var_ground3,
                    height_var_target3=height_var_ground3,
                    time_var_target4=time_var_ground4,
                    height_var_target4=height_var_ground4,
                    ax=axs[i],
                    label=label[i],
                    units=units[i],
                    value_range=value_range[i],
                    flip_height_axis=_flip_height_axis,
                    show_height_ticks=_show_height_ticks,
                    show_height_label=_show_height_label,
                    colors_ec=colors_ec,
                    colors_ground=colors_ground,
                    linewidth_ec=linewidth_ec,
                    linewidth_ground=linewidth_ground,
                    linestyle_ec=linestyle_ec,
                    linestyle_ground=linestyle_ground,
                    label_ec=label_ec,
                    label_ground=label_ground,
                    alpha=alpha,
                    show_steps=show_steps,
                    show_rebinned=show_rebinned,
                    to_mega=False if i > 1 else to_mega,
                    single_figsize=single_figsize,
                )
                pfs.append(_pf)
                dfs.append(_df)
            df = pd.concat(dfs, ignore_index=True)

            # Optional: plot quality status
            if show_quality_status:
                _dss: list = []
                _var: str = quality_status_var
                _ps_qs: list[Profile] = []
                for _ds in [ds_ec, ds_ec2, ds_ec3, ds_ec4]:
                    if (
                        isinstance(_ds, xr.Dataset)
                        and not any([_ds.equals(x) for x in _dss])
                        and _var in _ds
                    ):
                        p_qs = _extract_earthcare_profile(
                            ds=_ds,
                            var=_var,
                            site=site,
                            radius_km=radius_km,
                            closest=True,
                        )
                        p_qs.platform = (
                            "EC"
                            if p_qs.platform is None
                            else (
                                p_qs.platform.replace("res.", "")
                                .replace("low", "")
                                .replace("medium", "")
                                .replace("high", "")
                                .strip()
                            )
                        )
                        _ps_qs.append(p_qs)
                        _dss.append(_ds)
                vrange = quality_status_value_range
                if vrange is None and _var == "quality_status":
                    vrange = (-0.2, 4.2)
                _plot_profiles(
                    _ps_qs,
                    ax=axs[-1],
                    selection_height_range=selection_height_range,
                    height_range=height_range,
                    value_range=vrange,
                    flip_height_axis=False,
                    show_height_ticks=True,
                    show_height_label=False,
                    colors_ec=colors_ec,
                    linewidth_ec=linewidth_ec,
                    linestyle_ec=linestyle_ec,
                    label_ec=label_ec,
                    alpha=alpha,
                    show_steps=show_steps,
                    figsize=single_figsize,
                )

    return _CompareBscExtLRDepolResults(
        fig=fig,
        fig_bsc=pfs[0],
        fig_ext=pfs[1],
        fig_lr=pfs[2],
        fig_depol=pfs[3],
        stats=df,
    )
