import warnings
from typing import Any, Final, Iterable, Literal, Self, Sequence, cast

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize
from matplotlib.dates import date2num
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Patch
from numpy.typing import ArrayLike, NDArray

from ...color import Color, ColorLike
from ...colormap import get_cmap
from ...constants import (
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
from ...data.profile import Profile, ensure_along_track_2d, ensure_vertical_2d
from ...site import GroundSite
from ...typing import DistanceRangeLike, ValueRangeLike
from ...utils.numpy import asarray_or_none
from ...utils.time import TimedeltaLike, TimeRangeLike, TimestampLike
from ..annotation import add_text_product_info
from ..colorbar import add_colorbar
from ..text import add_shade_to_text, format_var_label
from ._figure import TimeseriesFigure
from .along_track import AlongTrackAxisStyle
from .default import get_default_cmap, get_default_norm, get_default_rolling_mean

_MIN_NUM_PROFILES: Final[int] = 5000


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
    height_edges = np.concatenate([height[:, [0]] - dh[:, [0]] / 2, height + dh / 2], axis=1)

    # Compute height edge rows (M+1, N+1) by copying last row
    last_row = height_edges[[-1], :]
    height_grid = np.vstack([height_edges, last_row])

    return height_grid


def fill_height(height: NDArray) -> NDArray:
    return pd.DataFrame(height).ffill(axis=1).fillna(0).values


def create_time_height_grids(
    values: NDArray,
    time: NDArray,
    height: NDArray,
) -> tuple[NDArray, NDArray]:
    M, N = values.shape

    time_grid = create_time_grid(time, N)

    _height = fill_height(np.atleast_2d(height))
    height_grid = create_height_grid(_height, M)
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


class CurtainFigure(TimeseriesFigure):
    """Figure object for displaying EarthCARE curtain data (e.g., ATLID and CPR L1/L2 profiles) along the satellite track.

    This class sets up a horizontal-along-track or time vs. vertical-height plot (a "curtain" view), for profiling
    atmospheric quantities retrieved from ground-based or nadir-viewing air/space-bourne instruments (like EarthCARE).
    It displays dual top/bottom x-axes (e.g., geolocation and time), and left/right y-axes for height labels.

    Attributes:
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
        min_num_profiles (int, optional): Minimum number of profiles to keep when using "fast" mode. Defaults to 5000.
    """

    def __init__(
        self: Self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_CURTAIN, FIGURE_HEIGHT_CURTAIN),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool | None = False,
        grid_kwargs: dict[str, Any] = {},
        title_kwargs: dict[str, Any] = {},
        # base
        num_ticks: int = 10,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        ax_style_y: Literal["height"] | None = "height",
        show_y_right: bool = False,
        show_y_left: bool = True,
        # timeseries
        show_height_left: bool = True,
        show_height_right: bool = False,
        mode: Literal["exact", "fast"] = "fast",
        min_num_profiles: int = _MIN_NUM_PROFILES,
        colorbar_tick_scale: float | None = None,
    ) -> None:
        super().__init__(
            ax=ax,
            figsize=figsize,
            dpi=dpi,
            title=title,
            fig_height_scale=fig_height_scale,
            fig_width_scale=fig_width_scale,
            axes_rect=axes_rect,
            show_grid=show_grid,
            grid_kwargs=grid_kwargs,
            title_kwargs=title_kwargs,
            num_ticks=num_ticks,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
            ax_style_y=ax_style_y,
            show_y_right=show_y_right,
            show_y_left=show_y_left,
        )

        self.colorbar_tick_scale: float | None = colorbar_tick_scale

        self.info_text: AnchoredText | None = None
        self.info_text_loc: str = "upper right"
        self.show_height_left = show_height_left
        self.show_height_right = show_height_right

        if mode in ["exact", "fast"]:
            self.mode = mode
        else:
            self.mode = "fast"

        if isinstance(min_num_profiles, int):
            self.min_num_profiles = min_num_profiles
        else:
            self.min_num_profiles = _MIN_NUM_PROFILES

    def _set_info_text_loc(self: Self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def _set_axes(
        self: Self,
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
    ) -> Self:

        self.set_colorbar_tick_scale(multiplier=self.colorbar_tick_scale)

        self._set_y_axes(hmin, hmax)

        self._set_time_axes(
            tmin=tmin,
            tmax=tmax,
            time=time,
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            longitude=longitude,
            latitude=latitude,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        return self

    def plot(
        self: Self,
        profiles: Profile | None = None,
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
        selection_max_time_margin: (TimedeltaLike | Sequence[TimedeltaLike] | None) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        show_temperature: bool = False,
        mode: Literal["exact", "fast"] | None = None,
        min_num_profiles: int = _MIN_NUM_PROFILES,
        mark_time: TimestampLike | Sequence[TimestampLike] | None = None,
        mark_time_color: (str | Color | Sequence[str | Color | None] | None) = None,
        mark_time_linestyle: str | Sequence[str] = "solid",
        mark_time_linewidth: float | Sequence[float] = 2.5,
        label_length: int = 40,
        **kwargs,
    ) -> Self:
        self._update(
            selection_color=selection_color,
            selection_linestyle=selection_linestyle,
            selection_linewidth=selection_linewidth,
            selection_highlight=selection_highlight,
            selection_highlight_inverted=selection_highlight_inverted,
            selection_highlight_color=selection_highlight_color,
            selection_highlight_alpha=selection_highlight_alpha,
            mark_time=mark_time,
            mark_time_color=mark_time_color,
            mark_time_linestyle=mark_time_linestyle,
            mark_time_linewidth=mark_time_linewidth,
        )

        if mode in ["exact", "fast"]:
            self.mode = mode

        if isinstance(min_num_profiles, int):
            self.min_num_profiles = min_num_profiles

        cmap = get_cmap(cmap)
        self._set_norm(
            norm=norm,
            value_range=value_range,
            log_scale=log_scale,
            cmap=cmap,
        )

        if isinstance(profiles, Profile):
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
        latitude = asarray_or_none(latitude)
        longitude = asarray_or_none(longitude)

        vp = Profile(
            values=values,
            time=time,
            height=height,
            latitude=latitude,
            longitude=longitude,
            label=label,
            units=units,
        )

        tmin_original: np.datetime64 = vp.time[0]
        tmax_original: np.datetime64 = vp.time[-1]

        if isinstance(rolling_mean, int):
            vp = vp.rolling_mean(rolling_mean)

        self._set_selection_max_time_margin(selection_max_time_margin)
        self._set_selection_time_range(selection_time_range)
        time_range = self._get_time_range(time=vp.time, time_range=time_range)
        height_range = self._get_y_range(y=vp.height, y_range=height_range)

        vp = vp.select_height_range(height_range=height_range, pad_idx=1)
        vp = vp.select_time_range(time_range=time_range, pad_idxs=rolling_mean or 0)
        time_range = cast(tuple[np.datetime64, np.datetime64], (vp.time[0], vp.time[-1]))

        self._tmin, self._tmax = time_range
        self._ymin, self._ymax = height_range

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

        mesh = self._ax.pcolormesh(
            time_grid,
            height_grid[:, ::-1],
            vp.values[:, ::-1],
            cmap=cmap,
            norm=self._norm,
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
                self._colorbar = add_colorbar(
                    fig=self.fig,
                    ax=self._ax,
                    data=mesh,
                    cmap=cmap,
                    **cb_kwargs,  # type: ignore
                )
            else:
                self._colorbar = add_colorbar(
                    fig=self.fig,
                    ax=self._ax,
                    data=mesh,
                    ticks=colorbar_ticks,
                    tick_labels=colorbar_tick_labels,
                    **cb_kwargs,  # type: ignore
                )

        _latitude = None
        if isinstance(vp.latitude, (np.ndarray)) and isinstance(lat_non_coarsened, (np.ndarray)):
            _latitude = np.concatenate(
                ([lat_non_coarsened[0]], vp.latitude, [lat_non_coarsened[-1]])
            )

        _longitude = None
        if isinstance(vp.longitude, (np.ndarray)) and isinstance(lon_non_coarsened, (np.ndarray)):
            _longitude = np.concatenate(
                ([lon_non_coarsened[0]], vp.longitude, [lon_non_coarsened[-1]])
            )

        self._set_axes(
            tmin=self._tmin,
            tmax=self._tmax,
            hmin=self._ymin,
            hmax=self._ymax,
            time=np.concatenate(([time_non_coarsened[0]], vp.time, [time_non_coarsened[-1]])),
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

        self._plot_selection()
        self._plot_time_marks()

        return self

    def ecplot(
        self: Self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        temperature_var: str = TEMP_CELSIUS_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        mark_closest: bool = False,
        show_radius: bool = True,
        show_info: bool = True,
        show_info_orbit_and_frame: bool = True,
        show_info_file_type: bool = True,
        show_info_baseline: bool = True,
        info_text_orbit_and_frame: str | None = None,
        info_text_file_type: str | None = None,
        info_text_baseline: str | None = None,
        info_text_loc: str | None = None,
        # Common args for wrappers
        values: NDArray | None = None,
        time: NDArray | None = None,
        height: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        values_temperature: NDArray | None = None,
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
        selection_max_time_margin: (TimedeltaLike | Sequence[TimedeltaLike] | None) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        show_temperature: bool = False,
        mode: Literal["exact", "fast"] | None = None,
        min_num_profiles: int = _MIN_NUM_PROFILES,
        mark_time: TimestampLike | Sequence[TimestampLike] | None = None,
        mark_time_color: (str | Color | Sequence[str | Color | None] | None) = None,
        mark_time_linestyle: str | Sequence[str] = "solid",
        mark_time_linewidth: float | Sequence[float] = 2.5,
        label_length: int = 40,
        **kwargs,
    ) -> Self:
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
            mark_closest (bool, optional): Mark the closest profile to the ground site in the plot; ignored if `site` not set. Defaults to False.
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
            min_num_profiles (int, optional): Overwrites the minimum number of profiles to keep when using "fast" mode. Defaults to 5000.
            mark_time (Sequence[TimestampLike] | None, optional): Timestamps at which to mark vertical profiles. Defaults to None.

        Returns:
            CurtainFigure: The figure object containing the curtain plot.

        Example:
            ```python
            import earthcarekit as eck

            filepath = (
                "path/to/mydata/ECA_EXAE_ATL_NOM_1B_20250606T132535Z_20250606T150730Z_05813D.h5"
            )
            with eck.read_product(filepath) as ds:
                cf = eck.CurtainFigure()
                cf = cf.ecplot(ds, "mie_attenuated_backscatter", height_range=(0, 20e3))
            ```
        """

        # Collect all common args for wrapped plot function call
        local_args = locals()

        # Handle deprecated arguments
        def _get_depr_arg(old_name: str, new_name: str) -> Any:
            if old_name in kwargs:
                msg = f"'{old_name}' is deprecated and will be removed in future versions; use '{new_name}' instead."
                warnings.warn(msg, FutureWarning, stacklevel=2)
                out = kwargs.get(old_name, local_args[new_name])
                del kwargs[old_name]
                return out
            return local_args[new_name]

        mark_closest = _get_depr_arg("mark_closest_profile", "mark_closest")
        kwargs["mark_time"] = _get_depr_arg("mark_profiles_at", "mark_time")
        kwargs["mark_time_color"] = _get_depr_arg("mark_profiles_at_color", "mark_time_color")
        kwargs["mark_time_linestyle"] = _get_depr_arg(
            "mark_profiles_at_linestyle", "mark_time_linestyle"
        )
        kwargs["mark_time_linewidth"] = _get_depr_arg(
            "mark_profiles_at_linewidth", "mark_time_linewidth"
        )

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
        del local_args["show_info_orbit_and_frame"]
        del local_args["show_info_file_type"]
        del local_args["show_info_baseline"]
        del local_args["info_text_orbit_and_frame"]
        del local_args["info_text_file_type"]
        del local_args["info_text_baseline"]
        del local_args["show_radius"]
        del local_args["info_text_loc"]
        del local_args["mark_closest"]

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
            if not show_temperature:
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
            all_args["label"] = "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
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
        all_args = self._add_overpass_marks(
            all_args=all_args,
            ds=ds,
            time_var=time_var,
            lat_var=lat_var,
            lon_var=lon_var,
            along_track_dim=along_track_dim,
            site=site,
            radius_km=radius_km,
            mark_closest=mark_closest,
            show_radius=show_radius,
        )

        self.plot(**all_args)

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self._ax,
                ds,
                append_to=self.info_text,
                loc=self.info_text_loc,
                show_orbit_and_frame=show_info_orbit_and_frame,
                show_file_type=show_info_file_type,
                show_baseline=show_info_baseline,
                text_orbit_and_frame=info_text_orbit_and_frame,
                text_file_type=info_text_file_type,
                text_baseline=info_text_baseline,
            )

        return self

    def plot_height(
        self: Self,
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
    ) -> Self:
        """Adds height line to the plot."""
        color = Color.from_optional(color)

        height = np.asarray(height)
        time = np.asarray(time)

        hnew, tnew = _convert_height_line_to_time_bin_step_function(height, time)

        fb: list = []
        if fill:
            _fb1 = self._ax.fill_between(
                tnew,
                hnew,
                y2=-5e3,
                color=color,
                alpha=alpha,
                zorder=zorder,
            )

            # Proxy for the legend
            _fb2 = Patch(facecolor=color, alpha=alpha, linewidth=0.0)
            fb = [_fb1, _fb2]

        hl = self._ax.plot(
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
        self: Self,
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
    ) -> Self:
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
                self._ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self

    def plot_contour(
        self: Self,
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
    ) -> Self:
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

        self._ax.contour(
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

        cn = self._ax.contour(
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
            labels = [lvl for lvl in label_levels if lvl in cn.levels]
        else:
            labels = cn.levels

        self._ax.clabel(
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
        self: Self,
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
    ) -> Self:
        """Adds hatched/filled areas to the plot."""
        values = np.asarray(values)
        time = np.asarray(time)
        height = np.asarray(height)

        if len(height.shape) == 2:
            height = height[0]

        color = Color.from_optional(color)
        color_border = Color.from_optional(color_border)

        cnf = self._ax.contourf(
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
        self: Self,
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
    ) -> Self:
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
        self: Self,
        ds: xr.Dataset,
        var: str = "simple_classification",
        value_range: tuple[float, float] = (-1.5, -0.5),
        **kwargs,
    ) -> Self:
        """Adds hatched area where ATLID "simple_classification" shows "attenuated" (-1)."""
        return self.ecplot_hatch(
            ds=ds,
            var=var,
            value_range=value_range,
            **kwargs,
        )

    def ecplot_contour(
        self: Self,
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
    ) -> Self:
        """Adds contour lines to the plot."""
        values = ds[var].values
        time = ds[time_var].values
        height = ds[height_var].values
        tp = Profile(values=values, time=time, height=height)
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
        self: Self,
        ds: xr.Dataset,
        var: str = TEMP_CELSIUS_VAR,
        label_format: str | None = r"$%.0f^{\circ}$C",
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
    ) -> Self:
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
        self: Self,
        ds: xr.Dataset,
        var: str = PRESSURE_VAR,
        time_var: str = TIME_VAR,
        height_var: str = HEIGHT_VAR,
        label_format: str | None = r"%d hPa",
        **kwargs,
    ) -> Self:
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
        self: Self,
        ds: xr.Dataset,
        var: str = ELEVATION_VAR,
        time_var: str = TIME_VAR,
        land_flag_var: str = LAND_FLAG_VAR,
        color: Color | str | None = "ec:land",
        color_water: Color | str | None = "ec:water",
        legend_label: str | None = None,
        legend_label_water: str | None = None,
    ) -> Self:
        """Adds filled elevation/surface area to the plot."""
        height = ds[var].copy().values
        time = ds[time_var].copy().values

        kwargs = dict(
            linewidth=0,
            linestyle="none",
            marker="none",
            markersize=0,
            fill=True,
            zorder=2.5,
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
        self: Self,
        ds: xr.Dataset,
        var: str = TROPOPAUSE_VAR,
        time_var: str = TIME_VAR,
        color: Color | str | None = "ec:tropopause",
        linewidth: float = 2,
        linestyle: str = "solid",
        legend_label: str | None = None,
    ) -> Self:
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
            zorder=2.5,
            legend_label=legend_label,
        )

        return self
