import logging
from typing import Iterable, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.dates import date2num
from matplotlib.figure import Figure, SubFigure
from numpy.typing import ArrayLike, NDArray

from ...utils.constants import *
from ...utils.profile_data import (
    ProfileData,
    ensure_along_track_2d,
    ensure_vertical_2d,
    validate_profile_data_dimensions,
)
from ...utils.swath_data import SwathData
from ...utils.swath_data.across_track_distance import get_nadir_index
from ...utils.time import TimeRangeLike, to_timestamp, validate_time_range
from ...utils.typing import DistanceRangeLike, ValueRangeLike
from ..color import Cmap, Color, get_cmap
from ..save import save_plot
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .colorbar import add_vertical_colorbar
from .defaults import get_default_cmap, get_default_norm, get_default_rolling_mean
from .height_ticks import format_height_ticks

logger = logging.getLogger(__name__)


class SwathFigure:
    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (12, 4),
        dpi: int | None = None,
        title: str | None = None,
    ):
        self.fig: Figure
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp  # type: ignore
            self.ax = ax
        else:
            # self.fig = plt.figure(figsize=figsize, dpi=dpi)
            # self.ax = self.fig.add_subplot()
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))

        self.title = title
        if self.title:
            self.fig.suptitle(self.title)

        self.ax_top: Axes | None = None
        self.ax_right: Axes | None = None
        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None

    def plot(
        self,
        swath: SwathData | None = None,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        nadir_index: int | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        from_track_range: DistanceRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str = Color("white"),
        selection_highlight_alpha: float = 0.5,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        ax_style_y: Literal[
            "from_track_distance", "across_track_distance", "pixel"
        ] = "from_track_distance",
        show_nadir: bool = True,
        **kwargs,
    ):
        if isinstance(value_range, Iterable):
            if len(value_range) != 2:
                raise ValueError(
                    f"invalid `value_range`: {value_range}, expecting (vmin, vmax)"
                )
        else:
            value_range = (None, None)

        cmap = get_cmap(cmap)

        if isinstance(cmap, Cmap) and cmap.categorical == True:
            norm = cmap.norm
        elif isinstance(norm, Normalize):
            if log_scale == True and not isinstance(norm, LogNorm):
                norm = LogNorm(norm.vmin, norm.vmax)
            elif log_scale == False and isinstance(norm, LogNorm):
                norm = Normalize(norm.vmin, norm.vmax)
            if value_range[0] is not None:
                norm.vmin = value_range[0]
            if value_range[1] is not None:
                norm.vmax = value_range[1]
        else:
            if log_scale == True:
                norm = LogNorm(value_range[0], value_range[1])
            else:
                norm = Normalize(value_range[0], value_range[1])

        assert isinstance(norm, Normalize)
        value_range = (norm.vmin, norm.vmax)

        if isinstance(swath, SwathData):
            values = swath.values
            time = swath.time
            nadir_index = swath.nadir_index
            latitude = swath.latitude
            longitude = swath.longitude
            label = swath.label
            units = swath.units
        elif (
            values is None
            or time is None
            or nadir_index is None
            or latitude is None
            or longitude is None
        ):
            raise ValueError(
                "Missing required arguments. Provide either a `SwathData` or all of `values`, `time`, `nadir_index`, `latitude` and `longitude`"
            )

        values = np.asarray(values)
        time = np.asarray(time)
        latitude = np.asarray(latitude)
        longitude = np.asarray(longitude)

        # Validate inputs
        logger.warning(f"Input validation not implemented")

        swath_data = SwathData(
            values=values,
            time=time,
            latitude=latitude,
            longitude=longitude,
            nadir_index=nadir_index,
            label=label,
            units=units,
        )

        tmin_original = swath_data.time[0]
        tmax_original = swath_data.time[-1]

        if from_track_range is not None:
            if isinstance(from_track_range, Iterable) and len(from_track_range) == 2:
                from_track_range = list(from_track_range)
                for i in [0, -1]:
                    if from_track_range[i] is None:
                        from_track_range[i] = swath_data.across_track_distance[i]
            swath_data = swath_data.select_from_track_range(from_track_range)
        else:
            from_track_range = (
                swath_data.across_track_distance[0],
                swath_data.across_track_distance[-1],
            )

        if time_range is not None:
            if isinstance(time_range, Iterable) and len(time_range) == 2:
                time_range = list(time_range)
                for i in [0, -1]:
                    if time_range[i] is None:
                        time_range[i] = to_timestamp(swath_data.time[i])
                    else:
                        time_range[i] = to_timestamp(time_range[i])
            swath_data = swath_data.select_time_range(time_range)
        else:
            time_range = (swath_data.time[0], swath_data.time[-1])

        values = swath_data.values
        time = swath_data.time
        latitude = swath_data.latitude
        longitude = swath_data.longitude
        across_track_distance = swath_data.across_track_distance
        from_track_distance = swath_data.from_track_distance
        label = swath_data.label
        units = swath_data.units
        nadir_index = swath_data.nadir_index

        is_from_track = ax_style_y != "across_track_distance"
        if ax_style_y == "from_track_distance":
            ydata = from_track_distance
            ylabel = "Distance from track"
        elif ax_style_y == "across_track_distance":
            ydata = across_track_distance
            ylabel = "Distance"
        elif ax_style_y == "pixel":
            ydata = np.arange(len(from_track_distance))
            ylabel = "Pixel"
        ynadir = ydata[nadir_index]

        tmin = np.datetime64(time_range[0])
        tmax = np.datetime64(time_range[1])

        if len(values.shape) == 3 and values.shape[2] == 3:
            mesh = self.ax.pcolormesh(time, ydata, values, **kwargs)
        else:
            mesh = self.ax.pcolormesh(
                time,
                ydata,
                values.T,
                norm=norm,
                cmap=cmap,
                **kwargs,
            )

            if colorbar:
                if cmap.categorical:
                    add_vertical_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        label=f"{label} [{units}]",
                        ticks=cmap.ticks,
                        tick_labels=cmap.labels,
                    )
                else:
                    add_vertical_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        label=f"{label} [{units}]",
                        ticks=colorbar_ticks,
                        tick_labels=colorbar_tick_labels,
                    )

        if selection_time_range is not None:
            self.selection_time_range = validate_time_range(selection_time_range)

            if selection_highlight:
                if selection_highlight_inverted:
                    self.ax.axvspan(  # type: ignore
                        tmin,  # type: ignore
                        self.selection_time_range[0],  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore
                    self.ax.axvspan(  # type: ignore
                        self.selection_time_range[1],  # type: ignore
                        tmax,  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore
                else:
                    self.ax.axvspan(  # type: ignore
                        self.selection_time_range[0],  # type: ignore
                        self.selection_time_range[1],  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore

            for t in self.selection_time_range:
                self.ax.axvline(  # type: ignore
                    x=t,  # type: ignore
                    color=selection_color,  # type: ignore
                    linestyle=selection_linestyle,  # type: ignore
                    linewidth=selection_linewidth,  # type: ignore
                )  # type: ignore

        if show_nadir:
            self.ax.axhline(
                y=ynadir,
                color=Color("red"),
                linestyle="dashed",
                linewidth=2,
            )

        self.ax.set_xlim((tmin, tmax))  # type: ignore
        # self.ax.set_ylim((hmin, hmax))

        self.ax_right = self.ax.twinx()
        self.ax_right.set_ylim(self.ax.get_ylim())

        self.ax_top = self.ax.twiny()
        self.ax_top.set_xlim(self.ax.get_xlim())

        if ax_style_y == "pixel":
            format_height_ticks(self.ax, label=ylabel, show_units=False)
        else:
            format_height_ticks(self.ax, label=ylabel)
        format_height_ticks(
            self.ax_right, show_tick_labels=False, show_units=False, label=""
        )

        ax_style_bottom = AlongTrackAxisStyle.from_input(ax_style_bottom)
        ax_style_top = AlongTrackAxisStyle.from_input(ax_style_top)

        format_along_track_axis(
            self.ax,
            ax_style_bottom,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude[:, nadir_index],
            latitude[:, nadir_index],
        )
        format_along_track_axis(
            self.ax_top,
            ax_style_top,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude[:, nadir_index],
            latitude[:, nadir_index],
        )

    def ecplot(
        self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        lat_var: str = SWATH_LAT_VAR,
        lon_var: str = SWATH_LON_VAR,
        values: NDArray | None = None,
        time: NDArray | None = None,
        nadir_index: int | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        from_track_range: DistanceRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str = Color("white"),
        selection_highlight_alpha: float = 0.5,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        ax_style_y: Literal[
            "from_track_distance", "across_track_distance", "pixel"
        ] = "from_track_distance",
        show_nadir: bool = True,
        **kwargs,
    ):
        # Collect all common args for wrapped plot function call
        local_args = locals()
        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        if all_args["values"] is None:
            all_args["values"] = ds[var].values
        if all_args["time"] is None:
            all_args["time"] = ds[time_var].values
        if all_args["nadir_index"] is None:
            all_args["nadir_index"] = get_nadir_index(ds)
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
        if value_range is None and log_scale is None and norm is None:
            all_args["norm"] = get_default_norm(var)
        if cmap is None:
            all_args["cmap"] = get_default_cmap(var)

        return self.plot(**all_args)

    def show(self):
        self.fig.tight_layout()
        self.fig.show()

    def save(self, filename: str = "", filepath: str | None = None, **kwargs):
        save_plot(fig=self.fig, filename=filename, filepath=filepath, **kwargs)
