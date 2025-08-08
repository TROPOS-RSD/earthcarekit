import logging
import warnings
from typing import Iterable, Literal, Sequence

logger = logging.getLogger()

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.dates import date2num
from matplotlib.figure import Figure, SubFigure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, AnchoredText
from matplotlib.text import Text
from numpy.typing import ArrayLike, NDArray

from ...utils.constants import *
from ...utils.ground_sites import GroundSite, get_ground_site
from ...utils.overpass import get_overpass_info
from ...utils.profile_data import (
    ProfileData,
    ensure_along_track_2d,
    ensure_vertical_2d,
    validate_profile_data_dimensions,
)
from ...utils.statistics import nan_max, nan_mean, nan_min, nan_sem, nan_std
from ...utils.time import (
    TimeRangeLike,
    TimestampLike,
    to_timestamp,
    to_timestamps,
    validate_time_range,
)
from ...utils.typing import DistanceRangeLike, ValueRangeLike, validate_numeric_range
from ..color import Cmap, Color, ColorLike, get_cmap
from ..save import save_plot
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .annotation import (
    add_text,
    add_text_product_info,
    add_title,
    add_title_earthcare_frame,
    format_var_label,
)
from .colorbar import add_vertical_colorbar
from .defaults import (
    get_default_cmap,
    get_default_norm,
    get_default_profile_range,
    get_default_rolling_mean,
)
from .height_ticks import format_height_ticks
from .ticks import format_numeric_ticks
from .value_range import select_value_range


def _convert_vertical_profile_to_step_function(
    values: ArrayLike, height: ArrayLike
) -> tuple[NDArray, NDArray]:
    values = np.asarray(values)
    height = np.asarray(height)

    hd1 = np.diff(height)
    hd2 = np.append(hd1[0], hd1)
    hd3 = np.append(hd1, hd1[-1])

    hnew1 = height - hd2 / 2
    hnew2 = height + hd3 / 2

    hnew = np.column_stack([hnew1, hnew2]).reshape(-1)
    vnew = np.repeat(values, 2)
    return vnew, hnew


def _highlight_height_range(
    ax: Axes,
    height_range: tuple[float, float],
    color: ColorLike | None = "gray",
    linewidth: float = 1,
    linestyle: str = "dashed",
    zorder: int | float | None = 0.9,
    alpha_fill: float = 0.15,
) -> None:
    _color = Color.from_optional(color)
    ax.axhspan(
        ymin=height_range[0],
        ymax=height_range[1],
        alpha=alpha_fill,
        color=_color,
        zorder=zorder,
        linewidth=0,
    )
    ax.axhline(
        y=height_range[0],
        color=_color,
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=zorder,
    )
    ax.axhline(
        y=height_range[1],
        color=_color,
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=zorder,
    )


class ProfileFigure:
    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (3, 4),
        dpi: int | None = None,
        title: str | None = None,
        height_axis: Literal["x", "y"] = "y",
        show_grid: bool = True,
        flip_height_axis: bool = False,
        show_legend: bool = False,
        show_height_ticks: bool = True,
        show_height_label: bool = True,
        height_range: DistanceRangeLike | None = None,
        value_range: ValueRangeLike | None = (0, None),
        label: str = "",
        units: str = "",
    ):
        self.fig: Figure
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp  # type: ignore
            self.ax = ax
        else:
            # self.fig: Figure = plt.figure(figsize=figsize, dpi=dpi)  # type: ignore
            # self.ax = self.fig.add_subplot()
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))
        self.title = title
        if isinstance(self.title, str):
            add_title(self.ax, title=self.title)
            # self.fig.suptitle(self.title)

        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None
        self.info_text: AnchoredText | None = None

        self.ax_fill_between = (
            self.ax.fill_betweenx if height_axis == "y" else self.ax.fill_between
        )
        self.ax_set_hlim = self.ax.set_ylim if height_axis == "y" else self.ax.set_xlim
        self.ax_set_vlim = self.ax.set_ylim if height_axis == "x" else self.ax.set_xlim

        self.hmin: int | float | None = 0
        self.hmax: int | float | None = 40e3
        if isinstance(height_range, (Sequence, np.ndarray)):
            self.hmin = height_range[0]
            self.hmax = height_range[1]

        self.vmin: int | float | None = None
        self.vmax: int | float | None = None
        if isinstance(value_range, (Sequence, np.ndarray)):
            self.vmin = value_range[0]
            self.vmax = value_range[1]

        self.height_axis: Literal["x", "y"] = height_axis
        self.flip_height_axis = flip_height_axis
        self.value_axis: Literal["x", "y"] = "x" if height_axis == "y" else "y"

        self.show_grid: bool = show_grid

        self.label: str | None = label
        self.units: str | None = units

        self.ax_right: Axes | None = None
        self.ax_top: Axes | None = None

        self.show_legend: bool = show_legend
        self.legend_handles: list = []
        self.legend_labels: list[str] = []
        self.legend: Legend | None = None

        self.show_height_ticks: bool = show_height_ticks
        self.show_height_label: bool = show_height_label

        self._init_axes()

    def _init_axes(self) -> None:
        self.ax.grid(self.show_grid)

        self.ax_set_hlim(self.hmin, self.hmax)
        if self.vmin or self.vmax:
            if self.vmin and np.isnan(self.vmin):
                self.vmin = None
            if self.vmax and np.isnan(self.vmax):
                self.vmax = None
            self.ax_set_vlim(self.vmin, self.vmax)

        is_init = not isinstance(self.ax_right, Axes)

        if isinstance(self.ax_right, Axes):
            self.ax_right.remove()
        self.ax_right = self.ax.twinx()
        self.ax_right.set_ylim(self.ax.get_ylim())
        self.ax_right.set_yticklabels([])

        if isinstance(self.ax_top, Axes):
            self.ax_top.remove()
        self.ax_top = self.ax.twiny()
        self.ax_top.set_xlim(self.ax.get_xlim())
        format_numeric_ticks(
            self.ax_top,
            axis=self.value_axis,
            label=format_var_label(self.label, self.units),
            show_label=False,
        )
        self.ax_top.set_xticklabels([])

        if self.flip_height_axis:
            format_height_ticks(
                self.ax_right,
                axis=self.height_axis,
                show_tick_labels=self.show_height_ticks,
                label="Height" if self.show_height_label else None,
            )
            self.ax.set_yticklabels([])
        else:
            format_height_ticks(
                self.ax,
                axis=self.height_axis,
                show_tick_labels=self.show_height_ticks,
                label="Height" if self.show_height_label else None,
            )
        format_numeric_ticks(
            self.ax,
            axis=self.value_axis,
            label=format_var_label(self.label, self.units),
        )

        if self.show_legend and len(self.legend_handles) > 0:
            self.legend = self.ax.legend(
                handles=self.legend_handles,
                labels=self.legend_labels,
                fontsize="small",
                #   bbox_to_anchor=(1, 1),
                #   loc=2,
                bbox_to_anchor=(0, 1.015),
                loc="lower left",
                borderaxespad=0.25,
                edgecolor="white",
            )
        elif isinstance(self.legend, Legend):
            self.legend.remove()

    def plot(
        self,
        profiles: ProfileData | None = None,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        error: NDArray | None = None,
        # Common args for wrappers
        label: str | None = None,
        units: str | None = None,
        value_range: ValueRangeLike | None = (0, None),
        height_range: DistanceRangeLike | None = None,
        time_range: TimeRangeLike | None = None,
        selection_height_range: DistanceRangeLike | None = None,
        show_mean: bool = True,
        show_std: bool = True,
        show_min: bool = False,
        show_max: bool = False,
        show_sem: bool = False,
        show_error: bool = False,
        color: str | ColorLike | None = None,
        alpha: float = 1.0,
        linestyle: str = "solid",
        linewidth: int | float = 1.5,
        ribbon_alpha: float = 0.2,
        show_grid: bool | None = None,
        zorder: int | float | None = 1,
        legend_label: str | None = None,
        show_legend: bool | None = None,
        show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
    ) -> "ProfileFigure":
        color = Color.from_optional(color)

        if isinstance(show_legend, bool):
            self.show_legend = show_legend

        if isinstance(show_grid, bool):
            self.show_grid = show_grid
            self.ax.grid(self.show_grid)

        if isinstance(value_range, Iterable):
            if len(value_range) != 2:
                raise ValueError(
                    f"invalid `value_range`: {value_range}, expecting (vmin, vmax)"
                )
            else:
                if value_range[0] is not None:
                    self.vmin = value_range[0]
                if value_range[1] is not None:
                    self.vmax = value_range[1]
        else:
            value_range = (None, None)
        logger.debug(f"{value_range=}")

        if isinstance(profiles, ProfileData):
            values = profiles.values
            time = profiles.time
            height = profiles.height
            latitude = profiles.latitude
            longitude = profiles.longitude
            if not isinstance(label, str):
                label = profiles.label
            if not isinstance(units, str):
                units = profiles.units
            error = profiles.error
        elif values is None or height is None:
            raise ValueError(
                "Missing required arguments. Provide either a `VerticalProfiles` or all of `values` and `height`"
            )

        values = np.asarray(np.atleast_2d(values))
        if time is None:
            time = np.array([pd.Timestamp.now()] * values.shape[0])
        time = np.asarray(np.atleast_1d(time))
        height = np.asarray(height)
        if latitude is not None:
            latitude = np.asarray(latitude)
        if longitude is not None:
            longitude = np.asarray(longitude)

        vp = ProfileData(
            values=values,
            time=time,
            height=height,
            latitude=latitude,
            longitude=longitude,
            label=label,
            units=units,
            error=error,
        )

        vp.select_time_range(time_range)

        if isinstance(vp.label, str):
            self.label = vp.label
        if isinstance(vp.units, str):
            self.units = vp.units

        if height_range is not None:
            if isinstance(height_range, Iterable) and len(height_range) == 2:
                for i in [0, -1]:
                    height_range = list(height_range)
                    if height_range[i] is None:
                        height_range[i] = np.atleast_2d(vp.height)[0, i]
                    elif i == 0:
                        self.hmin = height_range[0]
                    elif i == -1:
                        self.hmax = height_range[-1]
                    height_range = tuple(height_range)
        else:
            height_range = (
                np.atleast_2d(vp.height)[0, 0],
                np.atleast_2d(vp.height)[0, -1],
            )

        if len(vp.height.shape) == 2 and vp.height.shape[0] == 1:
            h = vp.height[0]
        elif len(vp.height.shape) == 2:
            h = nan_mean(vp.height, axis=0)
        else:
            h = vp.height

        handle_mean: list[Line2D] | list[None] = [None]
        handle_min: list[Line2D] | list[None] = [None]
        handle_max: list[Line2D] | list[None] = [None]
        handle_std: PolyCollection | None = None
        handle_sem: PolyCollection | None = None

        if show_mean:
            if vp.values.shape[0] == 1:
                vmean = vp.values[0]
                show_std = False
                show_sem = False
                show_min = False
                show_max = False
            else:
                vmean = nan_mean(vp.values, axis=0)
            vnew, hnew = vmean, h
            if show_steps:
                vnew, hnew = _convert_vertical_profile_to_step_function(vmean, h)
            xy = (vnew, hnew) if self.height_axis == "y" else (hnew, vnew)
            handle_mean = self.ax.plot(
                *xy,
                color=color,
                alpha=alpha,
                zorder=zorder,
                linestyle=linestyle,
                linewidth=linewidth,
            )
            color = handle_mean[0].get_color()  # type: ignore

            value_range = select_value_range(vmean, value_range, pad_frac=0.01)
            if not (self.vmin is not None and self.vmin < value_range[0]):
                self.vmin = value_range[0]
            if not (self.vmax is not None and self.vmax > value_range[1]):
                self.vmax = value_range[1]

            if show_error and vp.error is not None:
                verror = vp.error.flatten()
                if show_steps:
                    verror, _ = _convert_vertical_profile_to_step_function(verror, h)
                handle_std = self.ax_fill_between(
                    hnew,
                    vnew - verror,
                    vnew + verror,
                    alpha=ribbon_alpha,
                    color=color,
                    linewidth=0,
                )

        if show_sem:
            vsem = nan_sem(vp.values, axis=0)
            if show_steps:
                vsem, _ = _convert_vertical_profile_to_step_function(vsem, h)
            handle_sem = self.ax_fill_between(
                hnew,
                vnew - vsem,
                vnew + vsem,
                alpha=ribbon_alpha,
                color=color,
                linewidth=0,
            )
        elif show_std:
            vstd = nan_std(vp.values, axis=0)
            if show_steps:
                vstd, _ = _convert_vertical_profile_to_step_function(vstd, h)
            handle_std = self.ax_fill_between(
                hnew,
                vnew - vstd,
                vnew + vstd,
                alpha=ribbon_alpha,
                color=color,
                linewidth=0,
            )

        if show_min:
            vmin = nan_min(vp.values, axis=0)
            vnew, hnew = vmin, h
            if show_steps:
                vnew, hnew = _convert_vertical_profile_to_step_function(vmin, h)
            xy = (vnew, hnew) if self.height_axis == "y" else (hnew, vnew)
            handle_min = self.ax.plot(
                *xy,
                color=color,
                alpha=alpha,
                zorder=zorder,
                linestyle="dashed",
                linewidth=linewidth,
            )
            color = handle_min[0].get_color()  # type: ignore

        if show_max:
            vmax = nan_max(vp.values, axis=0)
            vnew, hnew = vmax, h
            if show_steps:
                vnew, hnew = _convert_vertical_profile_to_step_function(vmax, h)
            xy = (vnew, hnew) if self.height_axis == "y" else (hnew, vnew)
            handle_max = self.ax.plot(
                *xy,
                color=color,
                alpha=alpha,
                zorder=zorder,
                linestyle="dashed",
                linewidth=linewidth,
            )
            color = handle_max[0].get_color()  # type: ignore

        # Legend labels
        if isinstance(legend_label, str):
            handle_std

            _handle: tuple | list = [
                *handle_mean,
                handle_std,
                handle_sem,
                *handle_min,
                *handle_max,
            ]
            _default_h = next(_h for _h in _handle if _h is not None)
            _handle = tuple([_h if _h is not None else _default_h for _h in _handle])
            self.legend_handles.append(_handle)
            self.legend_labels.append(legend_label)

        if selection_height_range:
            _shr: tuple[float, float] = validate_numeric_range(selection_height_range)
            _highlight_height_range(
                ax=self.ax,
                height_range=_shr,
            )

        self._init_axes()

        # format_height_ticks(self.ax, axis=self.height_axis)
        # format_numeric_ticks(self.ax, axis=self.value_axis, label=self.label)

        return self

    def ecplot(
        self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        error_var: str | None = None,
        along_track_dim: str = ALONG_TRACK_DIM,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        error: NDArray | None = None,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        height_range: DistanceRangeLike | None = (0, 40e3),
        time_range: TimeRangeLike | None = None,
        selection_height_range: DistanceRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        zorder: int | float | None = 1,
        legend_label: str | None = "EarthCARE",
        show_legend: bool | None = None,
        show_steps: bool = DEFAULT_PROFILE_SHOW_STEPS,
        **kwargs,
    ) -> "ProfileFigure":
        # Collect all common args for wrapped plot function call
        local_args = locals()
        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["height_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        del local_args["error_var"]
        del local_args["along_track_dim"]
        del local_args["site"]
        del local_args["radius_km"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        if all_args["values"] is None:
            all_args["values"] = ds[var].values
        if all_args["time"] is None:
            all_args["time"] = ds[time_var].values
        if all_args["height"] is None:
            all_args["height"] = ds[height_var].values
        if all_args["latitude"] is None:
            all_args["latitude"] = ds[lat_var].values
        if all_args["longitude"] is None:
            all_args["longitude"] = ds[lon_var].values
        if all_args["error"] is None and isinstance(error_var, str):
            all_args["error"] = ds[error_var].values

        # Set default values depending on variable name
        if label is None:
            all_args["label"] = (
                "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
            )
        if units is None:
            all_args["units"] = "-" if not hasattr(ds[var], "units") else ds[var].units
        if value_range is None:
            all_args["value_range"] = get_default_profile_range(var)

        self.plot(**all_args)

        return self

    def show(self):
        self.fig.tight_layout()
        self.fig.show()

    def save(self, filename: str = "", filepath: str | None = None, **kwargs):
        save_plot(fig=self.fig, filename=filename, filepath=filepath, **kwargs)
