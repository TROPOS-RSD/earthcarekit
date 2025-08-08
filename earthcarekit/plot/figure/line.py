import warnings
from typing import Any, Iterable, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.dates import date2num
from matplotlib.figure import Figure, SubFigure
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, AnchoredText
from matplotlib.text import Text
from numpy.typing import ArrayLike, NDArray

from ...utils.constants import (
    ALONG_TRACK_DIM,
    ELEVATION_VAR,
    FIGURE_HEIGHT_CURTAIN,
    FIGURE_HEIGHT_LINE,
    FIGURE_WIDTH_CURTAIN,
    FIGURE_WIDTH_LINE,
    HEIGHT_VAR,
    TEMP_CELSIUS_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    TROPOPAUSE_VAR,
)
from ...utils.ground_sites import GroundSite, get_ground_site
from ...utils.overpass import get_overpass_info
from ...utils.profile_data import (
    ProfileData,
    ensure_along_track_2d,
    ensure_vertical_2d,
    validate_profile_data_dimensions,
)
from ...utils.time import (
    TimedeltaLike,
    TimeRangeLike,
    TimestampLike,
    to_timedelta,
    to_timestamp,
    to_timestamps,
    validate_time_range,
)
from ...utils.typing import DistanceRangeLike, ValueRangeLike
from ..color import Cmap, Color, get_cmap
from ..save import save_plot
from ._plot_1d_integer_flag import plot_1d_integer_flag
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .annotation import (
    add_text,
    add_text_product_info,
    add_title_earthcare_frame,
    format_var_label,
)
from .colorbar import add_vertical_colorbar
from .defaults import get_default_cmap, get_default_norm, get_default_rolling_mean
from .height_ticks import format_height_ticks
from .ticks import format_numeric_ticks
from .value_range import select_value_range


class LineFigure:
    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_LINE, FIGURE_HEIGHT_LINE),
        dpi: int | None = None,
        title: str | None = None,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        num_ticks: int = 10,
        show_value_left: bool = True,
        show_value_right: bool = False,
        mode: str | Literal["line", "scatter", "area"] = "line",
        show_grid: bool = True,
        grid_color: str | None = Color("lightgray"),
        grid_which: Literal["major", "minor", "both"] = "major",
        grid_axis: Literal["both", "x", "y"] = "both",
        grid_linestyle: str = "dashed",
        grid_linewidth: float = 1,
    ):
        self.fig: Figure
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp  # type: ignore
            self.ax = ax
        else:
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_subplot()  # add_axes((0.0, 0.0, 1.0, 1.0))
        self.title = title
        if self.title:
            self.fig.suptitle(self.title, y=1.4)

        self.ax_top: Axes
        self.ax_right: Axes
        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None
        self.ax_style_top: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(
            ax_style_top
        )
        self.ax_style_bottom: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(
            ax_style_bottom
        )

        self.info_text: AnchoredText | None = None
        self.info_text_loc: str = "upper right"
        self.num_ticks = num_ticks
        self.show_value_left: bool = show_value_left
        self.show_value_right: bool = show_value_right
        self.mode: str | Literal["line", "scatter", "area"] = mode

        self.show_grid = show_grid
        self.grid_color = Color.from_optional(grid_color)
        self.grid_which = grid_which
        self.grid_axis = grid_axis
        self.grid_linestyle = grid_linestyle
        self.grid_linewidth = grid_linewidth

        self.ax_right = self.ax.twinx()
        self.ax_right.set_ylim(self.ax.get_ylim())
        self.ax_right.set_yticks([])

        self.ax_top = self.ax.twiny()
        self.ax_top.set_xlim(self.ax.get_xlim())

    def _set_info_text_loc(self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def _set_axes(
        self,
        tmin: np.datetime64,
        tmax: np.datetime64,
        vmin: float,
        vmax: float,
        time: NDArray,
        tmin_original: np.datetime64 | None = None,
        tmax_original: np.datetime64 | None = None,
        longitude: NDArray | None = None,
        latitude: NDArray | None = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
    ) -> "LineFigure":
        if ax_style_top is not None:
            self.ax_style_top = AlongTrackAxisStyle.from_input(self.ax_style_top)
        if ax_style_bottom is not None:
            self.ax_style_bottom = AlongTrackAxisStyle.from_input(self.ax_style_bottom)
        if not isinstance(tmin_original, np.datetime64):
            tmin_original = tmin
        if not isinstance(tmax_original, np.datetime64):
            tmax_original = tmax

        self.ax.set_xlim((tmin, tmax))  # type: ignore
        self.ax.set_ylim((vmin, vmax))

        self.ax.grid(
            visible=self.show_grid,
            which=self.grid_which,
            axis=self.grid_axis,
            color=self.grid_color,
            linestyle=self.grid_linestyle,
            linewidth=self.grid_linewidth,
        )

        self.ax_right.set_ylim(self.ax.get_ylim())
        self.ax_top.set_xlim(self.ax.get_xlim())

        format_along_track_axis(
            self.ax,
            self.ax_style_bottom,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude,
            latitude,
            num_ticks=self.num_ticks,
        )
        format_along_track_axis(
            self.ax_top,
            self.ax_style_top,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude,
            latitude,
            num_ticks=self.num_ticks,
        )
        return self

    def plot(
        self,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        mode: str | Literal["line", "scatter", "area"] | None = None,
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        color: str | None = Color("ec:blue"),
        alpha: float = 1.0,
        linestyle: str | None = "solid",
        linewidth: float | int | None = 2.0,
        marker: str | None = "s",
        markersize: float | int | None = 2.0,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str | None = Color("white"),
        selection_highlight_alpha: float = 0.5,
        selection_max_time_margin: (
            TimedeltaLike | Sequence[TimedeltaLike] | None
        ) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        mark_profiles_at: Sequence[TimestampLike] | None = None,
        classes: Sequence[int] | dict[int, str] | None = None,
        classes_kwargs: dict[str, Any] = {},
        **kwargs,
    ) -> "LineFigure":
        # Parse colors
        color = Color.from_optional(color)
        selection_color = Color.from_optional(selection_color)
        selection_highlight_color = Color.from_optional(selection_highlight_color)

        if isinstance(mode, str):
            if mode in ["line", "scatter", "area"]:
                self.mode = mode
            else:
                raise ValueError(
                    f'invalid `mode` "{mode}", expected either "line", "scatter" or "area"'
                )

        if isinstance(value_range, Iterable):
            if len(value_range) != 2:
                raise ValueError(
                    f"invalid `value_range`: {value_range}, expecting (vmin, vmax)"
                )
        else:
            value_range = (None, None)

        if isinstance(norm, Normalize):
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
        value_range = (norm.vmin, norm.vmax)

        values = np.asarray(values)
        time = np.asarray(time)
        if latitude is not None:
            latitude = np.asarray(latitude)
        if longitude is not None:
            longitude = np.asarray(longitude)

        # Validate inputs
        if len(values.shape) != 1:
            raise ValueError(
                f"Values must be 1D, but has {len(values.shape)} dimensions (shape={values.shape})"
            )

        tmin_original = time[0]
        tmax_original = time[-1]
        vmin_original = values[0]
        vmax_original = values[-1]

        if selection_time_range is not None:
            self.selection_time_range = validate_time_range(selection_time_range)
            _selection_max_time_margin: tuple[pd.Timedelta, pd.Timedelta] | None = None
            if isinstance(selection_max_time_margin, (Sequence, np.ndarray)):
                _selection_max_time_margin = (
                    to_timedelta(selection_max_time_margin[0]),
                    to_timedelta(selection_max_time_margin[1]),
                )
            elif selection_max_time_margin is not None:
                _selection_max_time_margin = (
                    to_timedelta(selection_max_time_margin),
                    to_timedelta(selection_max_time_margin),
                )

            if _selection_max_time_margin is not None:
                time_range = [
                    np.max(
                        [
                            time[0],
                            (
                                self.selection_time_range[0]
                                - _selection_max_time_margin[0]
                            ).to_datetime64(),
                        ]
                    ),
                    np.min(
                        [
                            time[-1],
                            (
                                self.selection_time_range[1]
                                + _selection_max_time_margin[1]
                            ).to_datetime64(),
                        ]
                    ),
                ]

        if time_range is not None:
            if isinstance(time_range, Iterable) and len(time_range) == 2:
                for i in [0, -1]:
                    time_range = list(time_range)
                    if time_range[i] is None:
                        time_range[i] = time[i]
                    time_range = tuple(time_range)  # type: ignore
        else:
            time_range = (time[0], time[-1])

        _value_range: tuple[float, float] = select_value_range(
            data=values,
            value_range=value_range,
            pad_frac=0.0,
            use_min_max=True,
        )

        tmin = np.datetime64(time_range[0])
        tmax = np.datetime64(time_range[1])

        vmin: float = _value_range[0]
        vmax: float = _value_range[1]

        x: NDArray = time
        y: NDArray = values

        if classes is not None:
            _yaxis_position = classes_kwargs.get("yaxis_position", "left")
            _is_left = _yaxis_position == "left"
            _label = format_var_label(label, units, label_len=30)

            plot_1d_integer_flag(
                ax=self.ax if _is_left else self.ax_right,
                ax2=self.ax_right if _is_left else self.ax,
                data=y,
                x=x,
                classes=classes,
                ax_label=_label,
                **classes_kwargs,
            )
        else:
            line: list[Line2D] | PathCollection | PolyCollection
            if "line" in self.mode:
                line = self.ax.plot(
                    x,
                    y,
                    marker="none",
                    linewidth=linewidth,
                    linestyle=linestyle,
                    color=color,
                    alpha=alpha,
                )
            elif "scatter" in self.mode:
                line = self.ax.scatter(
                    x,
                    y,
                    marker=marker,
                    s=markersize,
                    color=color,
                    alpha=alpha,
                )  # , **plot_kwargs)
            elif "area" in self.mode:
                line = self.ax.fill_between(
                    x,
                    [0] * x.shape[0],
                    y,
                    zorder=0,
                    color=color,
                    alpha=alpha,
                )
            else:
                raise ValueError(f"invalid `mode` {self.mode}")

            format_numeric_ticks(
                ax=self.ax,
                axis="y",
                label=format_var_label(label, units),
                show_label=self.show_value_left,
                show_values=self.show_value_left,
            )
            format_numeric_ticks(
                ax=self.ax_right,
                axis="y",
                label=format_var_label(label, units),
                show_label=self.show_value_right,
                show_values=self.show_value_right,
            )

        if selection_time_range is not None:
            if selection_highlight:
                if selection_highlight_inverted:
                    self.ax.axvspan(
                        tmin,  # type: ignore
                        self.selection_time_range[0],  # type: ignore
                        color=selection_highlight_color,
                        alpha=selection_highlight_alpha,
                    )
                    self.ax.axvspan(
                        self.selection_time_range[1],  # type: ignore
                        tmax,  # type: ignore
                        color=selection_highlight_color,
                        alpha=selection_highlight_alpha,
                    )
                else:
                    self.ax.axvspan(
                        self.selection_time_range[0],  # type: ignore
                        self.selection_time_range[1],  # type: ignore
                        color=selection_highlight_color,
                        alpha=selection_highlight_alpha,
                    )

            for t in self.selection_time_range:  # type: ignore
                self.ax.axvline(
                    x=t,  # type: ignore
                    color=selection_color,
                    linestyle=selection_linestyle,
                    linewidth=selection_linewidth,
                )

        self._set_axes(
            tmin=tmin,
            tmax=tmax,
            vmin=vmin,
            vmax=vmax,
            time=time,
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            latitude=latitude,
            longitude=longitude,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        if mark_profiles_at is not None:
            for t in to_timestamps(mark_profiles_at):
                self.ax.axvline(t, color=selection_color, linestyle="solid", linewidth=selection_linewidth)  # type: ignore

        return self

    def ecplot(
        self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        values: NDArray | None = None,
        time: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        mark_closest_profile: bool = False,
        show_info: bool = True,
        info_text_loc: str | None = None,
        # Common args for wrappers
        mode: str | Literal["line", "scatter", "area"] | None = None,
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        color: str | None = Color("ec:blue"),
        alpha: float = 1.0,
        linestyle: str | None = "solid",
        linewidth: float | int | None = 2.0,
        marker: str | None = "s",
        markersize: float | int | None = 2.0,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str | None = Color("white"),
        selection_highlight_alpha: float = 0.5,
        selection_max_time_margin: (
            TimedeltaLike | Sequence[TimedeltaLike] | None
        ) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        mark_profiles_at: Sequence[TimestampLike] | None = None,
        classes: Sequence[int] | dict[int, str] | None = None,
        classes_kwargs: dict[str, Any] = {},
        **kwargs,
    ) -> "LineFigure":
        # Collect all common args for wrapped plot function call
        local_args = locals()
        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        del local_args["along_track_dim"]
        del local_args["site"]
        del local_args["radius_km"]
        del local_args["show_info"]
        del local_args["info_text_loc"]
        del local_args["mark_closest_profile"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        if all_args["values"] is None:
            all_args["values"] = ds[var].values
        if all_args["time"] is None:
            all_args["time"] = ds[time_var].values
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
        if classes is not None and len(classes) > 0:
            all_args["value_range"] = (-0.5, len(classes) - 0.5)
        elif value_range is None and log_scale is None and norm is None:
            all_args["norm"] = get_default_norm(var)

        # Handle overpass
        _site: GroundSite | None = None
        if isinstance(site, GroundSite):
            _site = site
        elif isinstance(site, str):
            _site = get_ground_site(site)
        else:
            pass

        if isinstance(_site, GroundSite):
            info_overpass = get_overpass_info(
                ds,
                site_radius_km=radius_km,
                site=_site,
                time_var=time_var,
                lat_var=lat_var,
                lon_var=lon_var,
                along_track_dim=along_track_dim,
            )
            overpass_time_range = info_overpass.time_range
            all_args["selection_time_range"] = overpass_time_range
            if mark_closest_profile:
                _mark_profiles_at = all_args["mark_profiles_at"]
                if isinstance(_mark_profiles_at, (Sequence, np.ndarray)):
                    list(_mark_profiles_at).append(info_overpass.closest_time)
                    all_args["mark_profiles_at"] = _mark_profiles_at
                else:
                    all_args["mark_profiles_at"] = [info_overpass.closest_time]

        self.plot(**all_args)

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self.ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self

    def to_texture(self) -> "LineFigure":
        # Remove anchored text and other artist text objects
        for artist in reversed(self.ax.artists):
            if isinstance(artist, (Text, AnchoredOffsetbox)):
                artist.remove()

        # Completely remove axis ticks and labels
        self.ax.axis("off")

        if self.ax_top:
            self.ax_top.axis("off")

        if self.ax_right:
            self.ax_right.axis("off")

        # Remove white frame around figure
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        return self

    def show(self):
        self.fig.tight_layout()
        self.fig.show()

    def save(self, filename: str = "", filepath: str | None = None, **kwargs):
        save_plot(fig=self.fig, filename=filename, filepath=filepath, **kwargs)
