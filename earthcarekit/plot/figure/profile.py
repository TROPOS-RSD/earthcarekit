import logging
import warnings
from typing import Iterable, Literal

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
from ...utils.typing import DistanceRangeLike, ValueRangeLike
from ..color import Cmap, Color, ColorLike, get_cmap
from ..save import save_plot
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .annotation import (
    add_text,
    add_text_product_info,
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
    ):
        self.fig: Figure
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp
            self.ax = ax
        else:
            # self.fig: Figure = plt.figure(figsize=figsize, dpi=dpi)  # type: ignore
            # self.ax = self.fig.add_subplot()
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))
        self.title = title
        if self.title:
            self.fig.suptitle(self.title)

        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None
        self.info_text: AnchoredText | None = None

        self.ax_fill_between = (
            self.ax.fill_betweenx if height_axis == "y" else self.ax.fill_between
        )
        self.ax_set_hlim = self.ax.set_ylim if height_axis == "y" else self.ax.set_xlim
        self.ax_set_vlim = self.ax.set_ylim if height_axis == "x" else self.ax.set_xlim

        self.hmin: int | float | None = None
        self.hmax: int | float | None = None

        self.vmin: int | float | None = None
        self.vmax: int | float | None = None

        self.height_axis: Literal["x", "y"] = height_axis
        self.flip_height_axis = flip_height_axis
        self.value_axis: Literal["x", "y"] = "x" if height_axis == "y" else "y"

        self.show_grid: bool = show_grid

        self.label: str | None = ""
        self.units: str | None = ""

        self.ax_right: Axes | None = None
        self.ax_top: Axes | None = None

        self._init_axes()

    def _init_axes(self) -> None:
        self.ax.grid(self.show_grid)

        self.ax_set_hlim(self.hmin, self.hmax)
        if self.vmin or self.vmax:
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
            format_height_ticks(self.ax_right, axis=self.height_axis)
            self.ax.set_yticklabels([])
        else:
            format_height_ticks(self.ax, axis=self.height_axis)
        format_numeric_ticks(
            self.ax,
            axis=self.value_axis,
            label=format_var_label(self.label, self.units),
        )

    def plot(
        self,
        profiles: ProfileData | None = None,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        label: str | None = None,
        units: str | None = None,
        value_range: ValueRangeLike | None = None,
        height_range: DistanceRangeLike | None = (0, 40e3),
        time_range: TimeRangeLike | None = None,
        show_mean: bool = True,
        show_std: bool = True,
        show_min: bool = False,
        show_max: bool = False,
        show_sem: bool = False,
        color: str | ColorLike | None = None,
        ribbon_alpha: float = 0.2,
        show_grid: bool | None = None,
    ) -> "ProfileFigure":
        color = Color.from_optional(color)

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
        )

        vp.select_time_range(time_range)

        self.label = vp.label
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
            h = nan_mean(vp.height)
        else:
            h = vp.height

        handle_mean: PolyCollection | list[Line2D] | list = [None]
        handle_std: PolyCollection | list[Line2D] | list = [None]
        handle_min: PolyCollection | list[Line2D] | list = [None]
        handle_max: PolyCollection | list[Line2D] | list = [None]
        handle_sem: PolyCollection | list[Line2D] | list = [None]

        if show_mean:
            if vp.values.shape[0] == 1:
                vmean = vp.values[0]
                show_std = False
                show_sem = False
                show_min = False
                show_max = False
            else:
                vmean = nan_mean(vp.values)
            xy = (vmean, h) if self.height_axis == "y" else (h, vmean)
            handle_mean = self.ax.plot(*xy, color=color)
            color = handle_mean[0].get_color()  # type: ignore

            value_range = select_value_range(vmean, value_range, pad_frac=0.01)
            self.vmin = value_range[0]
            self.vmax = value_range[1]

        if show_sem:
            vsem = nan_sem(vp.values)
            handle_sem = self.ax_fill_between(
                h,
                vmean - vsem,
                vmean + vsem,
                alpha=ribbon_alpha,
                color=color,
                linewidth=0,
            )
        elif show_std:
            vstd = nan_std(vp.values)
            handle_std = self.ax_fill_between(
                h,
                vmean - vstd,
                vmean + vstd,
                alpha=ribbon_alpha,
                color=color,
                linewidth=0,
            )

        if show_min:
            vmin = nan_min(vp.values)
            xy = (vmin, h) if self.height_axis == "y" else (h, vmin)
            handle_min = self.ax.plot(*xy, color=color, linestyle="dashed")
            color = handle_min[0].get_color()  # type: ignore

        if show_max:
            vmax = nan_max(vp.values)
            xy = (vmax, h) if self.height_axis == "y" else (h, vmax)
            handle_max = self.ax.plot(*xy, color=color, linestyle="dashed")
            color = handle_max[0].get_color()  # type: ignore

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
        along_track_dim: str = ALONG_TRACK_DIM,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        height_range: DistanceRangeLike | None = (0, 40e3),
        time_range: TimeRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
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

    def savefig(self, *args, **kwargs):
        self.fig.savefig(*args, **kwargs)
