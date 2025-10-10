import warnings
from typing import Iterable, Literal, Sequence

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.dates import date2num
from matplotlib.figure import Figure, SubFigure
from matplotlib.legend import Legend
from matplotlib.offsetbox import AnchoredOffsetbox, AnchoredText
from matplotlib.text import Text
from numpy.typing import ArrayLike, NDArray

from ...utils.constants import (
    ALONG_TRACK_DIM,
    DEFAULT_COLORBAR_WIDTH,
    ELEVATION_VAR,
    FIGURE_HEIGHT_CURTAIN,
    FIGURE_WIDTH_CURTAIN,
    HEIGHT_VAR,
    LAND_FLAG_VAR,
    PRESSURE_VAR,
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
from ...utils.typing import DistanceRangeLike, ValueRangeLike, validate_numeric_range
from ..color import Cmap, Color, ColorLike, get_cmap
from ..save import save_plot
from ..text import add_shade_to_text
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .annotation import (
    add_text,
    add_text_product_info,
    add_title_earthcare_frame,
    format_var_label,
)
from .colorbar import add_colorbar
from .defaults import get_default_cmap, get_default_norm, get_default_rolling_mean
from .height_ticks import format_height_ticks


def warn_about_variable_limitations(var: str) -> None:
    """Warns about known limitations or caveats for the given variable."""
    if var in ["radarReflectivityFactor", "dopplerVelocity"]:
        msg = f'For a better quicklook, use "plot_{var}" to apply improved default settings.'
        warnings.warn(msg)


def create_time_grid(time: NDArray, N: int) -> NDArray:
    # Convert time to numeric format for matplotlib
    time_num = date2num(time)

    # Compute time edges (1D -> shape (M+1,))
    dt = np.diff(time_num)
    dt = np.append(dt, dt[-1])
    time_edges = np.concatenate([[time_num[0] - dt[0] / 2], time_num + dt / 2])

    # Expand time_edges to shape (M+1, N+1)
    time_grid = ensure_along_track_2d(time_edges, N + 1)

    return time_grid


def create_height_grid(height: NDArray, M: int) -> NDArray:
    # Expand height to shape (M, N)
    height = ensure_vertical_2d(height, M)

    # Compute height edges (2D -> shape (M, N+1))
    dh = np.diff(height, axis=1)
    dh_last = dh[:, [-1]]
    dh = np.concatenate([dh, dh_last], axis=1)
    height_edges = np.concatenate(
        [height[:, [0]] - dh[:, [0]] / 2, height + dh / 2], axis=1
    )

    # Compute height edge rows (M+1, N+1) by copying last row
    last_row = height_edges[[-1], :]
    height_grid = np.vstack([height_edges, last_row])

    return height_grid


def create_time_height_grids(
    values: NDArray, time: NDArray, height: NDArray
) -> tuple[NDArray, NDArray]:
    M, N = values.shape

    time_grid = create_time_grid(time, N)
    height_grid = create_height_grid(height, M)
    assert time_grid.shape == height_grid.shape == (M + 1, N + 1)

    return time_grid, height_grid


def _convert_height_line_to_time_bin_step_function(
    height: ArrayLike,
    time: ArrayLike,
) -> tuple[NDArray, NDArray]:
    h = np.asarray(height)
    t = np.asarray(time)

    # t = t.astype("datetime64[s]").astype(np.float64)

    td1 = np.diff(t)
    td2 = np.append(td1[0], td1)
    td3 = np.append(td1, td1[-1])

    tnew1 = t - td2 / 2
    tnew2 = t + td3 / 2

    tnew = np.column_stack([tnew1, tnew2]).reshape(-1).astype("datetime64[ns]")
    # t = t.astype("datetime64[ns]")
    hnew = np.repeat(h, 2)
    return hnew, tnew


class CurtainFigure:
    """Figure object for displaying EarthCARE curtain data (e.g., ATLID and CPR L1/L2 profiles) along the satellite track.

    This class sets up a horizontal-along-track or time vs. vertical-height plot (a "curtain" view), for profiling
    atmospheric quantities retrieved from ground-based or nadir-viewing air/space-bourne instruments (like EarthCARE).
    It displays dual top/bottom x-axes (e.g., geolocation and time), and left/right y-axes for height labels.

    Args:
        ax (Axes | None, optional): Existing matplotlib axes to plot on; if not provided, a new figure and axes will be created. Defaults to None.
        figsize (tuple[float, float], optional): Size of the figure in inches. Defaults to (FIGURE_WIDTH_CURTAIN, FIGURE_HEIGHT_CURTAIN).
        dpi (int | None, optional): Resolution of the figure in dots per inch. Defaults to None.
        title (str | None, optional): Title to display above the curtain plot. Defaults to None.
        ax_style_top (AlongTrackAxisStyle | str, optional): Style of the top x-axis, e.g., "geo", "time", or "frame". Defaults to "geo".
        ax_style_bottom (AlongTrackAxisStyle | str, optional): Style of the bottom x-axis, e.g., "geo", "time", or "frame". Defaults to "time".
        num_ticks (int, optional): Maximum number of tick marks to be place along the x-axis. Defaults to 10.
        show_height_left (bool, optional): Whether to show height labels on the left y-axis. Defaults to True.
        show_height_right (bool, optional): Whether to show height labels on the right y-axis. Defaults to False.
        mode (Literal["exact", "fast"], optional): Curtain plotting mode. Use "fast" to speed up plotting by coarsening data to at least `min_num_profiles`; "exact" plots full resolution. Defaults to None.
        min_num_profiles (int, optional): Minimum number of profiles to keep when using "fast" mode. Defaults to 1000.
    """

    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_CURTAIN, FIGURE_HEIGHT_CURTAIN),
        dpi: int | None = None,
        title: str | None = None,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        num_ticks: int = 10,
        show_height_left: bool = True,
        show_height_right: bool = False,
        mode: Literal["exact", "fast"] = "fast",
        min_num_profiles: int = 1000,
        colorbar_tick_scale: float | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
    ):
        self.fig: Figure
        figsize = (figsize[0] * fig_width_scale, figsize[1] * fig_height_scale)
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp  # type: ignore
            self.ax = ax
        else:
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))
        self.title = title
        if self.title:
            self.fig.suptitle(self.title)

        self.ax_top: Axes | None = None
        self.ax_right: Axes | None = None
        self.colorbar: Colorbar | None = None
        self.colorbar_tick_scale: float | None = colorbar_tick_scale
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
        self.show_height_left = show_height_left
        self.show_height_right = show_height_right

        if mode in ["exact", "fast"]:
            self.mode = mode
        else:
            self.mode = "fast"

        if isinstance(min_num_profiles, int):
            self.min_num_profiles = min_num_profiles
        else:
            self.min_num_profiles = 1000

        self.legend: Legend | None = self.ax.get_legend()
        self._legend_handles: list = []
        self._legend_labels: list = []

    def _set_info_text_loc(self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def _set_axes(
        self,
        tmin: np.datetime64,
        tmax: np.datetime64,
        hmin: float,
        hmax: float,
        time: NDArray,
        tmin_original: np.datetime64 | None = None,
        tmax_original: np.datetime64 | None = None,
        longitude: NDArray | None = None,
        latitude: NDArray | None = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
    ) -> "CurtainFigure":

        self.set_colorbar_tick_scale(multiplier=self.colorbar_tick_scale)

        if ax_style_top is not None:
            self.ax_style_top = AlongTrackAxisStyle.from_input(ax_style_top)
        if ax_style_bottom is not None:
            self.ax_style_bottom = AlongTrackAxisStyle.from_input(ax_style_bottom)
        if not isinstance(tmin_original, np.datetime64):
            tmin_original = tmin
        if not isinstance(tmax_original, np.datetime64):
            tmax_original = tmax

        self.ax.set_xlim((tmin, tmax))  # type: ignore
        self.ax.set_ylim((hmin, hmax))

        self.ax_right = self.ax.twinx()
        self.ax_right.set_ylim(self.ax.get_ylim())

        self.ax_top = self.ax.twiny()
        self.ax_top.set_xlim(self.ax.get_xlim())

        format_height_ticks(
            self.ax,
            show_tick_labels=self.show_height_left,
            show_units=self.show_height_left,
            label="Height" if self.show_height_left else "",
        )
        format_height_ticks(
            self.ax_right,
            show_tick_labels=self.show_height_right,
            show_units=self.show_height_right,
            label="Height" if self.show_height_right else "",
        )

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
        profiles: ProfileData | None = None,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        values_temperature: NDArray | None = None,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        height_range: DistanceRangeLike | None = (0, 40e3),
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        colorbar_position: str | Literal["left", "right", "top", "bottom"] = "right",
        colorbar_alignment: str | Literal["left", "center", "right"] = "center",
        colorbar_width: float = DEFAULT_COLORBAR_WIDTH,
        colorbar_spacing: float = 0.2,
        colorbar_length_ratio: float | str = "100%",
        colorbar_label_outside: bool = True,
        colorbar_ticks_outside: bool = True,
        colorbar_ticks_both: bool = False,
        rolling_mean: int | None = None,
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
        show_temperature: bool = False,
        mode: Literal["exact", "fast"] | None = None,
        min_num_profiles: int = 1000,
        mark_profiles_at: Sequence[TimestampLike] | None = None,
        mark_profiles_at_color: (
            str | Color | Sequence[str | Color | None] | None
        ) = None,
        mark_profiles_at_linestyle: str | Sequence[str] = "solid",
        mark_profiles_at_linewidth: float | Sequence[float] = 2.5,
        label_length: int = 40,
        **kwargs,
    ) -> "CurtainFigure":
        # Parse colors
        selection_color = Color.from_optional(selection_color)
        selection_highlight_color = Color.from_optional(selection_highlight_color)

        _mark_profiles_at_color: list[Color | None] = []
        _mark_profiles_at_linestyle: list[str] = []
        _mark_profiles_at_linewidth: list[float] = []
        if isinstance(mark_profiles_at, (Sequence, np.ndarray)):
            if mark_profiles_at_color is None:
                _mark_profiles_at_color = [selection_color] * len(mark_profiles_at)
            elif isinstance(mark_profiles_at_color, (str, Color)):
                _mark_profiles_at_color = [
                    Color.from_optional(mark_profiles_at_color)
                ] * len(mark_profiles_at)
            elif len(mark_profiles_at_color) != len(mark_profiles_at):
                raise ValueError(
                    f"length of mark_profiles_at_color ({len(mark_profiles_at_color)}) must be same as length of mark_profiles_at ({len(mark_profiles_at)})"
                )
            else:
                _mark_profiles_at_color = [
                    Color.from_optional(c) for c in mark_profiles_at_color
                ]

            if isinstance(mark_profiles_at_linestyle, str):
                _mark_profiles_at_linestyle = [mark_profiles_at_linestyle] * len(
                    mark_profiles_at
                )
            elif len(mark_profiles_at_linestyle) != len(mark_profiles_at):
                raise ValueError(
                    f"length of mark_profiles_at_linestyle ({len(mark_profiles_at_linestyle)}) must be same as length of mark_profiles_at ({len(mark_profiles_at)})"
                )
            else:
                _mark_profiles_at_linestyle = [ls for ls in mark_profiles_at_linestyle]

            if isinstance(mark_profiles_at_linewidth, (int, float)):
                _mark_profiles_at_linewidth = [mark_profiles_at_linewidth] * len(
                    mark_profiles_at
                )
            elif len(mark_profiles_at_linewidth) != len(mark_profiles_at):
                raise ValueError(
                    f"length of mark_profiles_at_linewidth ({len(mark_profiles_at_linewidth)}) must be same as length of mark_profiles_at ({len(mark_profiles_at)})"
                )
            else:
                _mark_profiles_at_linewidth = [lw for lw in mark_profiles_at_linewidth]

        if mode in ["exact", "fast"]:
            self.mode = mode

        if isinstance(min_num_profiles, int):
            self.min_num_profiles = min_num_profiles

        if isinstance(value_range, Sequence):
            if len(value_range) != 2:
                raise ValueError(
                    f"invalid `value_range`: {value_range}, expecting (vmin, vmax)"
                )
        else:
            value_range = (None, None)

        cmap = get_cmap(cmap)

        if cmap.categorical:
            norm = cmap.norm
        if isinstance(norm, Normalize):
            if log_scale == True and not isinstance(norm, LogNorm):
                norm = LogNorm(norm.vmin, norm.vmax)
            elif log_scale == False and isinstance(norm, LogNorm):
                norm = Normalize(norm.vmin, norm.vmax)
            if value_range[0] is not None:
                norm.vmin = value_range[0]  # type: ignore
            if value_range[1] is not None:
                norm.vmax = value_range[1]  # type: ignore
        else:
            if log_scale == True:
                norm = LogNorm(value_range[0], value_range[1])  # type: ignore
            else:
                norm = Normalize(value_range[0], value_range[1])  # type: ignore
        value_range = (norm.vmin, norm.vmax)

        if isinstance(profiles, ProfileData):
            values = profiles.values
            time = profiles.time
            height = profiles.height
            latitude = profiles.latitude
            longitude = profiles.longitude
            label = profiles.label
            units = profiles.units
        elif values is None or time is None or height is None:
            raise ValueError(
                "Missing required arguments. Provide either a `VerticalProfiles` or all of `values`, `time`, and `height`"
            )

        values = np.asarray(values)
        time = np.asarray(time)
        height = np.asarray(height)
        if latitude is not None:
            latitude = np.asarray(latitude)
        if longitude is not None:
            longitude = np.asarray(longitude)

        # Validate inputs
        if len(values.shape) != 2:
            raise ValueError(
                f"Values must be either 2D, but has {len(values.shape)} dimensions (shape={values.shape})"
            )

        validate_profile_data_dimensions(
            values=values,
            time=time,
            height=height,
            latitude=latitude,
            longitude=longitude,
        )

        vp = ProfileData(
            values=values,
            time=time,
            height=height,
            latitude=latitude,
            longitude=longitude,
            label=label,
            units=units,
        )

        tmin_original = vp.time[0]
        tmax_original = vp.time[-1]
        hmin_original = vp.height[0]
        hmax_original = vp.height[-1]

        if selection_time_range is not None:
            if selection_max_time_margin is not None and not (
                isinstance(selection_max_time_margin, (Sequence, np.ndarray))
                and not isinstance(selection_max_time_margin, str)
            ):
                selection_max_time_margin = (
                    to_timedelta(selection_max_time_margin),
                    to_timedelta(selection_max_time_margin),
                )

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
                            vp.time[0],
                            (
                                self.selection_time_range[0]
                                - _selection_max_time_margin[0]
                            ).to_datetime64(),
                        ]
                    ),
                    np.min(
                        [
                            vp.time[-1],
                            (
                                self.selection_time_range[1]
                                + _selection_max_time_margin[1]
                            ).to_datetime64(),
                        ]
                    ),
                ]

        if isinstance(rolling_mean, int):
            vp = vp.rolling_mean(rolling_mean)

        if height_range is not None:
            if isinstance(height_range, Iterable) and len(height_range) == 2:
                for i in [0, -1]:
                    height_range = list(height_range)
                    if height_range[i] is None:
                        height_range[i] = [
                            np.nanmin(vp.height),
                            np.nanmax(vp.height),
                        ][i]
                    height_range = tuple(height_range)
            vp = vp.select_height_range(height_range, pad_idx=1)
        else:
            height_range = (
                np.nanmin(vp.height),
                np.nanmax(vp.height),
            )

        if time_range is not None:
            if isinstance(time_range, Iterable) and len(time_range) == 2:
                for i in [0, -1]:
                    time_range = list(time_range)
                    if time_range[i] is None:
                        time_range[i] = vp.time[i]
                    time_range = tuple(time_range)  # type: ignore
            pad_idxs = 0
            if isinstance(rolling_mean, int):
                pad_idxs = rolling_mean
            vp = vp.select_time_range(time_range, pad_idxs=pad_idxs)

        # else:
        time_range = (vp.time[0], vp.time[-1])
        tmin = np.datetime64(time_range[0])
        tmax = np.datetime64(time_range[1])

        hmin = height_range[0]
        hmax = height_range[1]

        time_non_coarsened = vp.time
        lat_non_coarsened = vp.latitude
        lon_non_coarsened = vp.longitude

        if (
            self.mode == "fast"
            and not cmap.categorical
            and not np.issubdtype(vp.values.dtype, np.integer)
        ):
            n = vp.time.shape[0] // self.min_num_profiles
            if n > 1:
                vp = vp.coarsen_mean(n)

        time_grid, height_grid = create_time_height_grids(
            values=vp.values, time=vp.time, height=vp.height
        )

        mesh = self.ax.pcolormesh(
            time_grid,
            height_grid,
            vp.values,
            cmap=cmap,
            norm=norm,
            shading="auto",
            linewidth=0,
            rasterized=True,
            **kwargs,
        )
        mesh.set_edgecolor("face")

        if colorbar:
            cb_kwargs = dict(
                label=format_var_label(vp.label, vp.units, label_len=label_length),
                position=colorbar_position,
                alignment=colorbar_alignment,
                width=colorbar_width,
                spacing=colorbar_spacing,
                length_ratio=colorbar_length_ratio,
                label_outside=colorbar_label_outside,
                ticks_outside=colorbar_ticks_outside,
                ticks_both=colorbar_ticks_both,
            )
            if cmap.categorical:
                self.colorbar = add_colorbar(
                    fig=self.fig,
                    ax=self.ax,
                    data=mesh,
                    cmap=cmap,
                    **cb_kwargs,  # type: ignore
                )
            else:
                self.colorbar = add_colorbar(
                    fig=self.fig,
                    ax=self.ax,
                    data=mesh,
                    ticks=colorbar_ticks,
                    tick_labels=colorbar_tick_labels,
                    **cb_kwargs,  # type: ignore
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
                    zorder=20,
                )

        _latitude = None
        if isinstance(vp.latitude, (np.ndarray)) and isinstance(
            lat_non_coarsened, (np.ndarray)
        ):
            _latitude = np.concatenate(
                ([lat_non_coarsened[0]], vp.latitude, [lat_non_coarsened[-1]])
            )

        _longitude = None
        if isinstance(vp.longitude, (np.ndarray)) and isinstance(
            lon_non_coarsened, (np.ndarray)
        ):
            _longitude = np.concatenate(
                ([lon_non_coarsened[0]], vp.longitude, [lon_non_coarsened[-1]])
            )

        self._set_axes(
            tmin=tmin,
            tmax=tmax,
            hmin=hmin,  # type: ignore
            hmax=hmax,  # type: ignore
            time=np.concatenate(
                ([time_non_coarsened[0]], vp.time, [time_non_coarsened[-1]])
            ),
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            latitude=_latitude,
            longitude=_longitude,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        if show_temperature and values_temperature is not None:
            self.plot_contour(
                values=values_temperature,
                time=time,
                height=height,
            )

        if mark_profiles_at is not None:
            for i, t in enumerate(to_timestamps(mark_profiles_at)):
                self.ax.axvline(
                    t,  # type: ignore
                    color=_mark_profiles_at_color[i],
                    linestyle=_mark_profiles_at_linestyle[i],
                    linewidth=_mark_profiles_at_linewidth[i],
                    zorder=20,
                )  # type: ignore

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
        temperature_var: str = TEMP_CELSIUS_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        values_temperature: NDArray | None = None,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        mark_closest_profile: bool = False,
        show_info: bool = True,
        show_radius: bool = True,
        info_text_loc: str | None = None,
        # Common args for wrappers
        value_range: ValueRangeLike | Literal["default"] | None = "default",
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        height_range: DistanceRangeLike | None = (0, 40e3),
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        colorbar_position: str | Literal["left", "right", "top", "bottom"] = "right",
        colorbar_alignment: str | Literal["left", "center", "right"] = "center",
        colorbar_width: float = DEFAULT_COLORBAR_WIDTH,
        colorbar_spacing: float = 0.2,
        colorbar_length_ratio: float | str = "100%",
        colorbar_label_outside: bool = True,
        colorbar_ticks_outside: bool = True,
        colorbar_ticks_both: bool = False,
        rolling_mean: int | None = None,
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
        show_temperature: bool = False,
        mode: Literal["exact", "fast"] | None = None,
        min_num_profiles: int = 5000,
        mark_profiles_at: Sequence[TimestampLike] | None = None,
        mark_profiles_at_color: (
            str | Color | Sequence[str | Color | None] | None
        ) = None,
        mark_profiles_at_linestyle: str | Sequence[str] = "solid",
        mark_profiles_at_linewidth: float | Sequence[float] = 2.5,
        label_length: int = 40,
        **kwargs,
    ) -> "CurtainFigure":
        """Plot a vertical curtain (i.e. cross-section) of a variable along the satellite track a EarthCARE dataset.

        This method collections all required data from a EarthCARE `xarray.dataset`, such as time, height, latitude and longitude.
        It supports various forms of customization through the use of arguments listed below.

        Args:
            ds (xr.Dataset): The EarthCARE dataset from with data will be plotted.
            var (str): Name of the variable to plot.
            time_var (str, optional): Name of the time variable. Defaults to TIME_VAR.
            height_var (str, optional): Name of the height variable. Defaults to HEIGHT_VAR.
            lat_var (str, optional): Name of the latitude variable. Defaults to TRACK_LAT_VAR.
            lon_var (str, optional): Name of the longitude variable. Defaults to TRACK_LON_VAR.
            temperature_var (str, optional): Name of the temperature variable; ignored if `show_temperature` is set to False. Defaults to TEMP_CELSIUS_VAR.
            along_track_dim (str, optional): Dimension name representing the along-track direction. Defaults to ALONG_TRACK_DIM.
            values (NDArray | None, optional): Data values to be used instead of values found in the `var` variable of the dataset. Defaults to None.
            time (NDArray | None, optional): Time values to be used instead of values found in the `time_var` variable of the dataset. Defaults to None.
            height (NDArray | None, optional): Height values to be used instead of values found in the `height_var` variable of the dataset. Defaults to None.
            latitude (NDArray | None, optional): Latitude values to be used instead of values found in the `lat_var` variable of the dataset. Defaults to None.
            longitude (NDArray | None, optional): Longitude values to be used instead of values found in the `lon_var` variable of the dataset. Defaults to None.
            values_temperature (NDArray | None, optional): Temperature values to be used instead of values found in the `temperature_var` variable of the dataset. Defaults to None.
            site (str | GroundSite | None, optional): Highlights data within `radius_km` of a ground site (given either as a `GroundSite` object or name string); ignored if not set. Defaults to None.
            radius_km (float, optional): Radius around the ground site to highlight data from; ignored if `site` not set. Defaults to 100.0.
            mark_closest_profile (bool, optional): Mark the closest profile to the ground site in the plot; ignored if `site` not set. Defaults to False.
            show_info (bool, optional): If True, show text on the plot containing EarthCARE frame and baseline info. Defaults to True.
            info_text_loc (str | None, optional): Place info text at a specific location of the plot, e.g. "upper right" or "lower left". Defaults to None.
            value_range (ValueRangeLike | None, optional): Min and max range for the variable values. Defaults to None.
            log_scale (bool | None, optional): Whether to apply a logarithmic color scale. Defaults to None.
            norm (Normalize | None, optional): Matplotlib norm to use for color scaling. Defaults to None.
            time_range (TimeRangeLike | None, optional): Time range to restrict the data for plotting. Defaults to None.
            height_range (DistanceRangeLike | None, optional): Height range to restrict the data for plotting. Defaults to (0, 40e3).
            label (str | None, optional): Label to use for colorbar. Defaults to None.
            units (str | None, optional): Units of the variable to show in the colorbar label. Defaults to None.
            cmap (str | Colormap | None, optional): Colormap to use for plotting. Defaults to None.
            colorbar (bool, optional): Whether to display a colorbar. Defaults to True.
            colorbar_ticks (ArrayLike | None, optional): Custom tick values for the colorbar. Defaults to None.
            colorbar_tick_labels (ArrayLike | None, optional): Custom labels for the colorbar ticks. Defaults to None.
            rolling_mean (int | None, optional): Apply rolling mean along time axis with this window size. Defaults to None.
            selection_time_range (TimeRangeLike | None, optional): Time range to highlight as a selection; ignored if `site` is set. Defaults to None.
            selection_color (_type_, optional): Color for the selection range marker lines. Defaults to Color("ec:earthcare").
            selection_linestyle (str | None, optional): Line style for selection range markers. Defaults to "dashed".
            selection_linewidth (float | int | None, optional): Line width for selection range markers. Defaults to 2.5.
            selection_highlight (bool, optional): Whether to highlight the selection region by shading outside or inside areas. Defaults to False.
            selection_highlight_inverted (bool, optional): If True and `selection_highlight` is also set to True, areas outside the selection are shaded. Defaults to True.
            selection_highlight_color (str | None, optional): If True and `selection_highlight` is also set to True, sets color used for shading selected outside or inside areas. Defaults to Color("white").
            selection_highlight_alpha (float, optional): If True and `selection_highlight` is also set to True, sets transparency used for shading selected outside or inside areas.. Defaults to 0.5.
            selection_max_time_margin (TimedeltaLike | Sequence[TimedeltaLike], optional): Zooms the time axis to a given maximum time from a selected time area. Defaults to None.
            ax_style_top (AlongTrackAxisStyle | str | None, optional): Style for the top axis (e.g., geo, lat, lon, distance, time, utc, lst, none). Defaults to None.
            ax_style_bottom (AlongTrackAxisStyle | str | None, optional): Style for the bottom axis (e.g., geo, lat, lon, distance, time, utc, lst, none). Defaults to None.
            show_temperature (bool, optional): Whether to overlay temperature as contours; requires either `values_temperature` or `temperature_var`. Defaults to False.
            mode (Literal["exact", "fast"] | None, optional): Overwrites the curtain plotting mode. Use "fast" to speed up plotting by coarsening data to at least `min_num_profiles`; "exact" plots full resolution. Defaults to None.
            min_num_profiles (int, optional): Overwrites the minimum number of profiles to keep when using "fast" mode. Defaults to 1000.
            mark_profiles_at (Sequence[TimestampLike] | None, optional): Timestamps at which to mark vertical profiles. Defaults to None.

        Returns:
            CurtainFigure: The figure object containing the curtain plot.

        Example:
            ```python
            import earthcarekit as eck

            filepath = "path/to/mydata/ECA_EXAE_ATL_NOM_1B_20250606T132535Z_20250606T150730Z_05813D.h5"
            with eck.read_product(filepath) as ds:
                cf = eck.CurtainFigure()
                cf = cf.ecplot(ds, "mie_attenuated_backscatter", height_range=(0, 20e3))
            ```
        """

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
        del local_args["temperature_var"]
        del local_args["along_track_dim"]
        del local_args["site"]
        del local_args["radius_km"]
        del local_args["show_info"]
        del local_args["show_radius"]
        del local_args["info_text_loc"]
        del local_args["mark_closest_profile"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        warn_about_variable_limitations(var)

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
        if all_args["values_temperature"] is None:
            if show_temperature == False:
                all_args["values_temperature"] = None
            elif ds.get(temperature_var, None) is None:
                warnings.warn(
                    f'No temperature variable called "{temperature_var}" found in given dataset.'
                )
                all_args["values_temperature"] = None
            else:
                all_args["values_temperature"] = ds[temperature_var].values

        # Set default values depending on variable name
        if label is None:
            all_args["label"] = (
                "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
            )
        if units is None:
            all_args["units"] = "-" if not hasattr(ds[var], "units") else ds[var].units
        if isinstance(value_range, str) and value_range == "default":
            value_range = None
            all_args["value_range"] = None
            if log_scale is None and norm is None:
                all_args["norm"] = get_default_norm(var, file_type=ds)
        if rolling_mean is None:
            all_args["rolling_mean"] = get_default_rolling_mean(var, file_type=ds)
        if cmap is None:
            all_args["cmap"] = get_default_cmap(var, file_type=ds)
        all_args["cmap"] = get_cmap(all_args["cmap"])

        if all_args["cmap"] == get_cmap("synergetic_tc"):
            self.colorbar_tick_scale = 0.8

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
            if show_radius:
                overpass_time_range = info_overpass.time_range
                all_args["selection_time_range"] = overpass_time_range
            else:
                mark_closest_profile = True
            if mark_closest_profile:
                _mark_profiles_at = all_args["mark_profiles_at"]
                _mark_profiles_at_color = all_args["mark_profiles_at_color"]
                _mark_profiles_at_linestyle = all_args["mark_profiles_at_linestyle"]
                _mark_profiles_at_linewidth = all_args["mark_profiles_at_linewidth"]
                if isinstance(_mark_profiles_at, (Sequence, np.ndarray)):
                    list(_mark_profiles_at).append(info_overpass.closest_time)
                    all_args["mark_profiles_at"] = _mark_profiles_at
                else:
                    all_args["mark_profiles_at"] = [info_overpass.closest_time]

                if not isinstance(_mark_profiles_at_color, str) and isinstance(
                    _mark_profiles_at_color, (Sequence, np.ndarray)
                ):
                    list(_mark_profiles_at_color).append("ec:earthcare")
                    all_args["mark_profiles_at_color"] = _mark_profiles_at_color

                if not isinstance(_mark_profiles_at_linestyle, str) and isinstance(
                    _mark_profiles_at_linestyle, (Sequence, np.ndarray)
                ):
                    list(_mark_profiles_at_linestyle).append("solid")
                    all_args["mark_profiles_at_linestyle"] = _mark_profiles_at_linestyle

                if isinstance(_mark_profiles_at_linewidth, (Sequence, np.ndarray)):
                    list(_mark_profiles_at_linewidth).append(2.5)
                    all_args["mark_profiles_at_linewidth"] = _mark_profiles_at_linewidth

                all_args["selection_linestyle"] = "none"
                all_args["selection_linewidth"] = 0.1
        self.plot(**all_args)

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self.ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self

    def plot_height(
        self,
        height: NDArray,
        time: NDArray,
        linewidth: int | float | None = 1.5,
        linestyle: str | None = "solid",
        color: Color | str | None = None,
        alpha: float | None = 1.0,
        zorder: int | float | None = 2,
        marker: str | None = None,
        markersize: int | float | None = None,
        fill: bool = False,
        legend_label: str | None = None,
    ) -> "CurtainFigure":
        """Adds height line to the plot."""
        color = Color.from_optional(color)

        height = np.asarray(height)
        time = np.asarray(time)

        hnew, tnew = _convert_height_line_to_time_bin_step_function(height, time)

        fb: list = []
        if fill:
            _fb1 = self.ax.fill_between(
                tnew,
                hnew,
                y2=-5e3,
                color=color,
                alpha=alpha,
                zorder=zorder,
            )
            from matplotlib.patches import Patch

            # Proxy for the legend
            _fb2 = Patch(facecolor=color, alpha=alpha, linewidth=0.0)
            fb = [_fb1, _fb2]

        hl = self.ax.plot(
            tnew,
            hnew,
            linestyle=linestyle,
            linewidth=linewidth,
            marker=marker,
            markersize=markersize,
            color=color,
            alpha=alpha,
            zorder=zorder,
        )

        if isinstance(legend_label, str):
            self._legend_handles.append(tuple(hl + fb))
            self._legend_labels.append(legend_label)

        return self

    def ecplot_height(
        self,
        ds: xr.Dataset,
        var: str,
        time_var: str = TIME_VAR,
        linewidth: int | float | None = 1.5,
        linestyle: str | None = "none",
        color: Color | str | None = "black",
        zorder: int | float | None = 2.1,
        marker: str | None = "s",
        markersize: int | float | None = 1,
        show_info: bool = True,
        info_text_loc: str | None = None,
        legend_label: str | None = None,
    ) -> "CurtainFigure":
        """Adds height line to the plot."""
        height = ds[var].values
        time = ds[time_var].values
        self.plot_height(
            height=height,
            time=time,
            linewidth=linewidth,
            linestyle=linestyle,
            color=color,
            zorder=zorder,
            marker=marker,
            markersize=markersize,
            legend_label=legend_label,
        )

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self.ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self

    def plot_contour(
        self,
        values: NDArray,
        time: NDArray,
        height: NDArray,
        label_levels: list | NDArray | None = None,
        label_format: str | None = None,
        levels: list | NDArray | None = None,
        linewidths: int | float | list | NDArray | None = 1.5,
        linestyles: str | list | NDArray | None = "solid",
        colors: Color | str | list | NDArray | None = "black",
        zorder: int | float | None = 2,
    ) -> "CurtainFigure":
        """Adds contour lines to the plot."""
        values = np.asarray(values)
        time = np.asarray(time)
        height = np.asarray(height)

        if len(height.shape) == 2:
            height = height[0]

        if isinstance(colors, str):
            colors = Color.from_optional(colors)
        elif isinstance(colors, (Iterable, np.ndarray)):
            colors = [Color.from_optional(c) for c in colors]
        else:
            colors = Color.from_optional(colors)

        x = time
        y = height
        z = values.T

        if len(y.shape) == 2:
            y = y[len(y) // 2]

        if isinstance(colors, list):
            shade_color = Color.from_optional(colors[0])
        else:
            shade_color = Color.from_optional(colors)

        if isinstance(shade_color, Color):
            shade_color = shade_color.get_best_bw_contrast_color()

        linewidths2: int | float | np.ndarray
        if not isinstance(linewidths, (int, float, np.number, np.ndarray)):
            linewidths2 = np.array(linewidths) * 2.5
        else:
            linewidths2 = linewidths * 2.5

        cn2 = self.ax.contour(
            x,
            y,
            z,
            levels=levels,
            linewidths=linewidths2,
            colors=shade_color,
            alpha=0.5,
            linestyles="solid",
            zorder=zorder,
        )

        cn = self.ax.contour(
            x,
            y,
            z,
            levels=levels,
            linewidths=linewidths,
            colors=colors,
            linestyles=linestyles,
            zorder=zorder,
        )

        labels: Iterable[float]
        if label_levels:
            labels = [l for l in label_levels if l in cn.levels]
        else:
            labels = cn.levels

        cl = self.ax.clabel(
            cn,
            labels,  # type: ignore
            inline=True,
            fmt=label_format,
            fontsize="small",
            zorder=zorder,
        )

        for t in cn.labelTexts:
            add_shade_to_text(t, alpha=0.5)
            t.set_rotation(0)

        return self

    def plot_hatch(
        self,
        values: NDArray,
        time: NDArray,
        height: NDArray,
        value_range: tuple[float, float],
        hatch: str = "/////",
        linewidth: float = 1,
        linewidth_border: float = 0,
        color: ColorLike | None = "black",
        color_border: ColorLike | None = None,
        zorder: int | float | None = 2,
        legend_label: str | None = None,
    ) -> "CurtainFigure":
        """Adds hatched/filled areas to the plot."""
        values = np.asarray(values)
        time = np.asarray(time)
        height = np.asarray(height)

        if len(height.shape) == 2:
            height = height[0]

        color = Color.from_optional(color)
        color_border = Color.from_optional(color_border)

        cnf = self.ax.contourf(
            time,
            height,
            values.T,
            levels=[value_range[0], value_range[1]],
            colors=["none"],
            hatches=[hatch],
            zorder=zorder,
        )
        cnf.set_edgecolors(color)  # type: ignore
        cnf.set_hatch_linewidth(linewidth)

        color = Color(cnf.get_edgecolors()[0], is_normalized=True)  # type: ignore
        if color_border is None:
            color_border = color.hex
        cnf.set_color(color_border)  # type: ignore
        cnf.set_linewidth(linewidth_border)

        if isinstance(legend_label, str):
            from matplotlib.patches import Patch

            _facecolor = "none"
            if color.is_close_to_white():
                _facecolor = color.blend(0.7, "black").hex

            hatch_patch = Patch(
                linewidth=linewidth_border,
                facecolor=_facecolor,
                edgecolor=color.hex,
                hatch=hatch,
                label=legend_label,
            )

            self._legend_handles.append(hatch_patch)
            self._legend_labels.append(legend_label)

        return self

    def ecplot_hatch(
        self,
        ds: xr.Dataset,
        var: str,
        value_range: tuple[float, float],
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        hatch: str = "/////",
        linewidth: float = 1,
        linewidth_border: float = 0,
        color: ColorLike | None = "black",
        color_border: ColorLike | None = None,
        zorder: int | float | None = 2,
        legend_label: str | None = None,
    ) -> "CurtainFigure":
        """Adds hatched/filled areas to the plot."""
        height = ds[height_var].values
        time = ds[time_var].values
        values = ds[var].values

        return self.plot_hatch(
            values=values,
            time=time,
            height=height,
            value_range=value_range,
            hatch=hatch,
            linewidth=linewidth,
            linewidth_border=linewidth_border,
            color=color,
            color_border=color_border,
            zorder=zorder,
            legend_label=legend_label,
        )

    def ecplot_hatch_attenuated(
        self,
        ds: xr.Dataset,
        var: str = "simple_classification",
        value_range: tuple[float, float] = (-1.5, -0.5),
        **kwargs,
    ) -> "CurtainFigure":
        """Adds hatched area where ATLID "simple_classification" shows "attenuated" (-1)."""
        return self.ecplot_hatch(
            ds=ds,
            var=var,
            value_range=value_range,
            **kwargs,
        )

    def ecplot_contour(
        self,
        ds: xr.Dataset,
        var: str,
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        levels: list | NDArray | None = None,
        label_format: str | None = None,
        label_levels: list | NDArray | None = None,
        linewidths: int | float | list | NDArray | None = 1.5,
        linestyles: str | list | NDArray | None = "solid",
        colors: Color | str | list | NDArray | None = "black",
        zorder: float | int = 3,
    ) -> "CurtainFigure":
        """Adds contour lines to the plot."""
        values = ds[var].values
        time = ds[time_var].values
        height = ds[height_var].values
        tp = ProfileData(values=values, time=time, height=height)
        self.plot_contour(
            values=tp.values,
            time=tp.time,
            height=tp.height,
            levels=levels,
            linewidths=linewidths,
            linestyles=linestyles,
            colors=colors,
            zorder=zorder,
            label_format=label_format,
            label_levels=label_levels,
        )
        return self

    def ecplot_temperature(
        self,
        ds: xr.Dataset,
        var: str = TEMP_CELSIUS_VAR,
        label_format: str | None = "$%.0f^{\circ}$C",
        label_levels: list | NDArray | None = [-80, -40, 0],
        levels=[
            -80,
            -70,
            -60,
            -50,
            -40,
            -30,
            -20,
            -10,
            0,
            10,
            20,
        ],
        linewidths=[
            0.75,  # -80
            0.25,  # -70
            0.50,  # -60
            0.50,  # -50
            0.75,  # -40
            0.50,  # -30
            0.75,  # -20
            0.50,  # -10
            1.00,  # 0
            0.50,  # 10
            0.75,  # 20
        ],
        linestyles=[
            "dashed",  # -80
            "dashed",  # -70
            "dashed",  # -60
            "dashed",  # -50
            "dashed",  # -40
            "dashed",  # -30
            "dashed",  # -20
            "dashed",  # -10
            "solid",  # 0
            "solid",  # 10
            "solid",  # 20
        ],
        colors="black",
        **kwargs,
    ) -> "CurtainFigure":
        """Adds temperature contour lines to the plot."""
        return self.ecplot_contour(
            ds=ds,
            var=var,
            label_format=label_format,
            levels=levels,
            label_levels=label_levels,
            linewidths=linewidths,
            linestyles=linestyles,
            colors=colors,
            **kwargs,
        )

    def ecplot_pressure(
        self,
        ds: xr.Dataset,
        var: str = PRESSURE_VAR,
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        label_format: str | None = r"%d hPa",
        **kwargs,
    ) -> "CurtainFigure":
        """Adds pressure contour lines to the plot."""
        values = ds[var].values / 100.0
        time = ds[time_var].values
        height = ds[height_var].values
        return self.plot_contour(
            values=values,
            time=time,
            height=height,
            label_format=label_format,
            **kwargs,
        )

    def ecplot_elevation(
        self,
        ds: xr.Dataset,
        var: str = ELEVATION_VAR,
        time_var: str = TIME_VAR,
        land_flag_var: str = LAND_FLAG_VAR,
        color: Color | str | None = "ec:land",
        color_water: Color | str | None = "ec:water",
        legend_label: str | None = None,
        legend_label_water: str | None = None,
    ) -> "CurtainFigure":
        """Adds filled elevation/surface area to the plot."""
        height = ds[var].copy().values
        time = ds[time_var].copy().values

        kwargs = dict(
            linewidth=0,
            linestyle="none",
            marker="none",
            markersize=0,
            fill=True,
            zorder=10,
        )

        is_water = land_flag_var in ds.variables

        if is_water:
            land_flag = ds[land_flag_var].copy().values == 1
            height_water = height.copy()
            height_water[land_flag] = np.nan
            height[~land_flag] = np.nan

        self.plot_height(
            height=height,
            time=time,
            color=color,
            legend_label=legend_label,
            **kwargs,  # type: ignore
        )

        if is_water:
            self.plot_height(
                height=height_water,
                time=time,
                color=color_water,
                legend_label=legend_label_water,
                **kwargs,  # type: ignore
            )

        return self

    def ecplot_tropopause(
        self,
        ds: xr.Dataset,
        var: str = TROPOPAUSE_VAR,
        time_var: str = TIME_VAR,
        color: Color | str | None = "ec:tropopause",
        linewidth: float = 2,
        linestyle: str = "solid",
        legend_label: str | None = None,
    ) -> "CurtainFigure":
        """Adds tropopause line to the plot."""
        height = ds[var].values
        time = ds[time_var].values
        self.plot_height(
            height=height,
            time=time,
            linewidth=linewidth,
            linestyle=linestyle,
            color=color,
            marker="none",
            markersize=0,
            fill=False,
            zorder=12,
            legend_label=legend_label,
        )

        return self

    def to_texture(self) -> "CurtainFigure":
        """Convert the figure to a texture by removing all axis ticks, labels, annotations, and text."""
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

        # Remove colorbar
        if self.colorbar:
            self.colorbar.remove()
            self.colorbar = None

        # Remove legend
        if self.legend:
            self.legend.remove()
            self.legend = None

        return self

    def invert_xaxis(self) -> "CurtainFigure":
        """Invert the x-axis."""
        self.ax.invert_xaxis()
        if self.ax_top:
            self.ax_top.invert_xaxis()
        return self

    def invert_yaxis(self) -> "CurtainFigure":
        """Invert the y-axis."""
        self.ax.invert_yaxis()
        if self.ax_right:
            self.ax_right.invert_yaxis()
        return self

    def show_legend(
        self,
        loc: str = "upper left",
        markerscale: float = 1.5,
        frameon: bool = True,
        facecolor: ColorLike = "white",
        edgecolor: ColorLike = "black",
        framealpha: float = 0.8,
        edgewidth: float = 1.5,
        fancybox: bool = False,
        handlelength: float = 0.7,
        handletextpad: float = 0.5,
        borderaxespad: float = 0,
        ncols: int = 8,
        textcolor: ColorLike = "black",
        textweight: int | str = "normal",
        textshadealpha: float = 0.0,
        textshadewidth: float = 3.0,
        textshadecolor: ColorLike = "white",
        **kwargs,
    ) -> "CurtainFigure":
        from matplotlib.legend_handler import HandlerTuple

        facecolor = Color(facecolor)
        edgecolor = Color(edgecolor)
        textcolor = Color(textcolor)
        textshadecolor = Color(textshadecolor)

        if len(self._legend_handles) > 0:
            self.legend = self.ax.legend(
                self._legend_handles,
                self._legend_labels,
                loc=loc,
                markerscale=markerscale,
                frameon=frameon,
                facecolor=facecolor,
                edgecolor=edgecolor,
                framealpha=framealpha,
                fancybox=fancybox,
                handlelength=handlelength,
                handletextpad=handletextpad,
                borderaxespad=borderaxespad,
                ncols=ncols,
                handler_map={tuple: HandlerTuple(ndivide=1)},
                **kwargs,
            )
            self.legend.get_frame().set_linewidth(edgewidth)
            for text in self.legend.get_texts():
                text.set_color(textcolor)
                text.set_fontweight(textweight)

                if textshadealpha > 0:
                    text = add_shade_to_text(
                        text,
                        alpha=textshadealpha,
                        linewidth=textshadewidth,
                        color=textshadecolor,
                    )
        return self

    def set_colorbar_tick_scale(
        self,
        multiplier: float | None = None,
        fontsize: float | str | None = None,
    ) -> "CurtainFigure":
        _cb = self.colorbar
        cb: Colorbar
        if isinstance(_cb, Colorbar):
            cb = _cb
        else:
            return self

        if fontsize is not None:
            cb.ax.tick_params(labelsize=fontsize)
            return self

        if multiplier is not None:
            tls = cb.ax.yaxis.get_ticklabels()
            if len(tls) == 0:
                tls = cb.ax.xaxis.get_ticklabels()
            if len(tls) == 0:
                return self
            _fontsize = tls[0].get_fontsize()
            if isinstance(_fontsize, str):
                from matplotlib import font_manager

                fp = font_manager.FontProperties(size=_fontsize)
                _fontsize = fp.get_size_in_points()
            cb.ax.tick_params(labelsize=_fontsize * multiplier)
        return self

    def show(self) -> None:
        import IPython
        import matplotlib.pyplot as plt
        from IPython.display import display

        if IPython.get_ipython() is not None:
            display(self.fig)
        else:
            plt.show()

    def save(
        self,
        filename: str = "",
        filepath: str | None = None,
        ds: xr.Dataset | None = None,
        ds_filepath: str | None = None,
        dpi: float | Literal["figure"] = "figure",
        orbit_and_frame: str | None = None,
        utc_timestamp: TimestampLike | None = None,
        use_utc_creation_timestamp: bool = False,
        site_name: str | None = None,
        hmax: int | float | None = None,
        radius: int | float | None = None,
        extra: str | None = None,
        transparent_outside: bool = False,
        verbose: bool = True,
        print_prefix: str = "",
        create_dirs: bool = False,
        transparent_background: bool = False,
        resolution: str | None = None,
        **kwargs,
    ) -> None:
        """
        Save a figure as an image or vector graphic to a file and optionally format the file name in a structured way using EarthCARE metadata.

        Args:
            figure (Figure | HasFigure): A figure object (`matplotlib.figure.Figure`) or objects exposing a `.fig` attribute containing a figure (e.g., `CurtainFigure`).
            filename (str, optional): The base name of the file. Can be extended based on other metadata provided. Defaults to empty string.
            filepath (str | None, optional): The path where the image is saved. Can be extended based on other metadata provided. Defaults to None.
            ds (xr.Dataset | None, optional): A EarthCARE dataset from which metadata will be taken. Defaults to None.
            ds_filepath (str | None, optional): A path to a EarthCARE product from which metadata will be taken. Defaults to None.
            pad (float, optional): Extra padding (i.e., empty space) around the image in inches. Defaults to 0.1.
            dpi (float | 'figure', optional): The resolution in dots per inch. If 'figure', use the figure's dpi value. Defaults to None.
            orbit_and_frame (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            utc_timestamp (TimestampLike | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            use_utc_creation_timestamp (bool, optional): Whether the time of image creation should be included in the file name. Defaults to False.
            site_name (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            hmax (int | float | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            radius (int | float | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            resolution (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            extra (str | None, optional): A custom string to be included in the file name. Defaults to None.
            transparent_outside (bool, optional): Whether the area outside figures should be transparent. Defaults to False.
            verbose (bool, optional): Whether the progress of image creation should be printed to the console. Defaults to True.
            print_prefix (str, optional): A prefix string to all console messages. Defaults to "".
            create_dirs (bool, optional): Whether images should be saved in a folder structure based on provided metadata. Defaults to False.
            transparent_background (bool, optional): Whether the background inside and outside of figures should be transparent. Defaults to False.
            **kwargs (dict[str, Any]): Keyword arguments passed to wrapped function call of `matplotlib.pyplot.savefig`.
        """
        save_plot(
            fig=self.fig,
            filename=filename,
            filepath=filepath,
            ds=ds,
            ds_filepath=ds_filepath,
            dpi=dpi,
            orbit_and_frame=orbit_and_frame,
            utc_timestamp=utc_timestamp,
            use_utc_creation_timestamp=use_utc_creation_timestamp,
            site_name=site_name,
            hmax=hmax,
            radius=radius,
            extra=extra,
            transparent_outside=transparent_outside,
            verbose=verbose,
            print_prefix=print_prefix,
            create_dirs=create_dirs,
            transparent_background=transparent_background,
            resolution=resolution,
            **kwargs,
        )
