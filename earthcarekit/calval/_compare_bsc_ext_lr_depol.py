import warnings

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.figure import Figure

from ..plot import ProfileFigure
from ..plot.figure.multi_panel import create_column_subfigures
from ..utils import (
    FileType,
    GroundSite,
    ProfileData,
    filter_radius,
    read_nc,
    read_product,
)
from ..utils.constants import CM_AS_INCH


def _extract_earthcare_profile(
    ds: xr.Dataset,
    var: str,
    site: GroundSite | str | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
) -> ProfileData:
    if site:
        ds_radius = filter_radius(
            ds=ds,
            radius_km=radius_km,
            site=site,
            closest=closest,
        )
    else:
        warnings.warn(
            "Averaging across the whole EarthCARE frame, since ground site was not specified."
        )
        ds_radius = ds

    legend_label: str = "A-EBD high res."
    if "medium_resolution" in var:
        legend_label = "A-EBD medium res."
    elif "low_resolution" in var:
        legend_label = "A-EBD low res."

    p_radius = ProfileData.from_dataset(
        ds=ds_radius,
        var=var,
        platform=legend_label,
        error_var=f"{var}_error",
    )
    return p_radius


def _extract_ground_based_profile(
    ds: xr.Dataset,
    vars: list[str | tuple[str, str]],
    time_var: str,
    height_var: str,
) -> list[ProfileData]:
    ps: list[ProfileData] = []
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
            warnings.warn(msg)
            continue
        if isinstance(_error, str) and _error not in ds:
            msg = f"Variable `{_error}` not in ground-based data."
            warnings.warn(msg)
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
    p_main: ProfileData,
    ps: list[ProfileData] = [],
    figsize: tuple[float | int, float | int] = (2.0, 5.0),
    selection_height_range: tuple[float, float] | None = None,
    height_range: tuple[float, float] | None = (0, 20e3),
    value_range: tuple[float | None, float | None] | None = None,
    ax=None,  # TODO: typing
    label: str | None = None,
    units: str | None = None,
    flip_height_axis: bool = False,
    show_height_ticks: bool = True,
    show_height_label: bool = True,
) -> ProfileFigure:
    pf = ProfileFigure(
        ax=ax,
        show_legend=True,
        figsize=figsize,
        flip_height_axis=flip_height_axis,
        show_height_ticks=show_height_ticks,
        show_height_label=show_height_label,
    )
    colors_ground = [
        "ec:blue",
        "ec:darkblue",
        "ec:green",
    ]

    for i, p in enumerate(ps):
        pf = pf.plot(p, color=colors_ground[i], legend_label=p.platform)

    pf = pf.plot(
        p_main,
        color="ec:earthcare",
        value_range=value_range,
        legend_label=p_main.platform,
        height_range=height_range,
        selection_height_range=selection_height_range,
        label=label,
        units=units,
    )

    return pf


def _calulate_statistics(
    p_main: ProfileData,
    ps: list[ProfileData] = [],
    selection_height_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    p_pred = p_main

    # Workaround for non comparison plots
    if len(ps) == 0:
        ps = [p_pred]

    for p_targ in ps:
        _df = p_pred.compare_to(
            p_targ,
            height_range=selection_height_range,
        ).to_dataframe()
        _df.insert(0, "target", p_targ.platform)
        _df.insert(0, "prediction", p_pred.platform)
        dfs.append(_df)
    df = pd.concat(dfs, ignore_index=True)
    return df


def compare_ec_profiles_with_target(
    ds_ec: xr.Dataset,
    ds_target: xr.Dataset,
    var_ec: str,
    var_target: str | tuple[str, str] | list[str | tuple[str, str]],
    selection_height_range: tuple[float, float] | None = None,
    height_range: tuple[float, float] | None = (0, 20e3),
    site: GroundSite | str | None = None,
    radius_km: int | float = 100.0,
    closest: bool = False,
    time_var_target: str = "start_time",
    height_var_target: str = "height",
    ax=None,  # TODO: typing
    label: str | None = "Bsc. coeff.",
    units: str | None = "m$^{-1}$ sr$^{-1}$",
    value_range: tuple[float | None, float | None] | None = None,
    flip_height_axis: bool = False,
    show_height_ticks: bool = True,
    show_height_label: bool = True,
):
    if isinstance(var_target, (str, tuple)):
        var_target = [var_target]

    p_main = _extract_earthcare_profile(
        ds=ds_ec,
        var=var_ec,
        site=site,
        radius_km=radius_km,
        closest=closest,
    )

    ps = _extract_ground_based_profile(
        ds=ds_target,
        vars=var_target,
        time_var=time_var_target,
        height_var=height_var_target,
    )

    pf = _plot_profiles(
        p_main=p_main,
        ps=ps,
        ax=ax,
        label=label,
        units=units,
        selection_height_range=selection_height_range,
        height_range=height_range,
        value_range=value_range,
        flip_height_axis=flip_height_axis,
        show_height_ticks=show_height_ticks,
        show_height_label=show_height_label,
    )

    df = _calulate_statistics(
        p_main=p_main,
        ps=ps,
        selection_height_range=selection_height_range,
    )

    return df


def compare_bsc_ext_lr_depol(
    fp_ec: str,
    fp_target: str,
    time_var_target: str,
    height_var_target: str,
    site: GroundSite | str | None = None,
    radius_km: float = 100.0,
    resolustion: str = "_low_resolution",
    bsc_var_target=str | tuple[str, str] | list[str | tuple[str, str]],
    ext_var_target=str | tuple[str, str] | list[str | tuple[str, str]],
    lr_var_target=str | tuple[str, str] | list[str | tuple[str, str]],
    depol_var_target=str | tuple[str, str] | list[str | tuple[str, str]],
    height_range: tuple[float, float] | None = (0, 30e3),
    selection_height_range: tuple[float, float] | None = None,
    selection_height_range_bsc: tuple[float, float] | None = None,
    selection_height_range_ext: tuple[float, float] | None = None,
    selection_height_range_lr: tuple[float, float] | None = None,
    selection_height_range_depol: tuple[float, float] | None = None,
    vmax_bsc: float | None = 8e-6,
    vmax_ext: float | None = 3e-4,
    vmax_lr: float | None = 100,
    vmax_depol: float | None = 0.6,
) -> tuple[Figure, pd.DataFrame]:
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

    file_type = FileType.from_input(fp_ec)
    vars_main: list[str]
    _closest: bool = False
    if file_type == FileType.ATL_EBD_2A:
        vars_main = [
            f"particle_backscatter_coefficient_355nm{res}",
            f"particle_extinction_coefficient_355nm{res}",
            f"lidar_ratio_355nm{res}",
            f"particle_linear_depol_ratio_355nm{res}",
        ]
        _closest = True
    elif file_type == FileType.ATL_AER_2A:
        vars_main = [
            f"particle_backscatter_coefficient_355nm",
            f"particle_extinction_coefficient_355nm",
            f"lidar_ratio_355nm",
            f"particle_linear_depol_ratio_355nm",
        ]
        _closest = True
    else:
        raise NotImplementedError(
            f"'{file_type.name}' products are not yet supported by this function."
        )

    with (
        read_product(fp_ec) as ds_ec,
        read_nc(fp_target) as ds_target,
    ):
        fig, axs = create_column_subfigures(
            ncols=4,
            single_figsize=(5 * CM_AS_INCH, 12 * CM_AS_INCH),
            margin=0.6,
        )

        vars_target: list[str | tuple[str, str] | list[str | tuple[str, str]]] = [
            bsc_var_target,
            ext_var_target,
            lr_var_target,
            depol_var_target,
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
        vmax = [
            vmax_bsc,
            vmax_ext,
            vmax_lr,
            vmax_depol,
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

        dfs: list[pd.DataFrame] = []
        for i in range(len(vars_main)):
            _flip_height_axis: bool = False
            _show_height_ticks: bool = True
            _show_height_label: bool = False

            if i == 0:
                _show_height_label = True
                _show_height_ticks = True

            _df = compare_ec_profiles_with_target(
                ds_ec=ds_ec,
                ds_target=ds_target,
                var_ec=vars_main[i],
                var_target=vars_target[i],
                selection_height_range=_selection_height_range[i],
                height_range=height_range,
                site=site,
                radius_km=radius_km,
                closest=_closest,
                time_var_target=time_var_target,
                height_var_target=height_var_target,
                ax=axs[i],
                label=label[i],
                units=units[i],
                value_range=(0, vmax[i]),
                flip_height_axis=_flip_height_axis,
                show_height_ticks=_show_height_ticks,
                show_height_label=_show_height_label,
            )
            dfs.append(_df)
        df = pd.concat(dfs, ignore_index=True)

    return fig, df
