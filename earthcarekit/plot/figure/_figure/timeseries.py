from typing import Any, Callable, Literal, Self, Sequence, TypeAlias, cast

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray

from ....color import Color
from ....constants import ALONG_TRACK_DIM, TIME_VAR, TRACK_LAT_VAR, TRACK_LON_VAR
from ....overpass import get_overpass_info
from ....site import Site, SiteLike, get_site
from ....typing import Number, TimedeltaLike, TimeRangeNoneLike, TimestampLike, ValueRangeLike
from ....utils.time import to_timedelta, to_timestamp, to_timestamps
from ...ticks import format_distance_ticks
from ..along_track import AlongTrackAxisStyle, format_along_track_axis
from .base import BaseFigure

_YAxisStyle: TypeAlias = Literal["height", "from_track_distance", "across_track_distance", "pixel"]
_YAxisFormatter: TypeAlias = Callable[["TimeseriesFigure"], None]
_TimeMarginLike: TypeAlias = TimedeltaLike | Sequence[TimedeltaLike]


def _format_y(tsfig: "TimeseriesFigure", label: str | None, show_units: bool = True) -> None:
    for ax, visible in [
        (tsfig.ax, tsfig._show_y_left),
        (tsfig.ax_right, tsfig._show_y_right),
    ]:
        format_distance_ticks(
            ax=ax,
            show_tick_labels=visible,
            show_units=(show_units and visible),
            label=label if visible else "",
        )


_Y_FORMATTER: dict[str, _YAxisFormatter] = {
    "height": (lambda x: _format_y(x, label="Height")),
    "pixel": (lambda x: _format_y(x, label="Pixel", show_units=False)),
    "from_track_distance": (lambda x: _format_y(x, label="Distance from track")),
    "across_track_distance": (lambda x: _format_y(x, label="Distance")),
}


class TimeseriesFigure(BaseFigure):
    def __init__(
        self: Self,
        ax: Axes | None = None,
        fig: Figure | None = None,
        figsize: tuple[float, float] = (4.0, 4.0),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool | None = None,
        grid_kwargs: dict[str, Any] = {},
        title_kwargs: dict[str, Any] = {},
        # base
        num_ticks: int = 10,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        ax_style_y: _YAxisStyle | None = None,
        show_y_right: bool = False,
        show_y_left: bool = True,
        # timeseries
    ) -> None:
        super().__init__(
            ax=ax,
            fig=fig,
            figsize=figsize,
            dpi=dpi,
            title=title,
            fig_height_scale=fig_height_scale,
            fig_width_scale=fig_width_scale,
            axes_rect=axes_rect,
            show_grid=show_grid,
            grid_kwargs=grid_kwargs,
            title_kwargs=title_kwargs,
        )

        self._ax_top: Axes = self._ax.twiny()
        self._ax_top.set_xlim(self._ax.get_xlim())

        self._ax_right: Axes = self._ax.twinx()
        self._ax_right.set_ylim(self._ax.get_ylim())

        self._num_ticks: int = num_ticks
        self._ax_style_top: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(ax_style_top)
        self._ax_style_bottom: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(ax_style_bottom)

        self._ax_style_y: _YAxisStyle | None = ax_style_y
        self._show_y_right: bool = show_y_right
        self._show_y_left: bool = show_y_left

        self._selection_time_range: tuple[pd.Timestamp | None, pd.Timestamp | None] | None = None
        self._selection_max_time_margin: tuple[pd.Timedelta, pd.Timedelta] | None = None

        self._tmin: np.datetime64 | None = None
        self._tmax: np.datetime64 | None = None
        self._ymin: float | None = None
        self._ymax: float | None = None

        self._selection_color: Color | None = Color("ec:earthcare")
        self._selection_linestyle: str | None = "dashed"
        self._selection_linewidth: float | int | None = 2.5
        self._selection_highlight: bool = False
        self._selection_highlight_inverted: bool = True
        self._selection_highlight_color: Color | None = Color("white")
        self._selection_highlight_alpha: float = 0.5

        self._mark_time: list[TimestampLike] | None = None
        self._mark_time_color: Color | list[Color | None] | None = None
        self._mark_time_linestyle: str | list[str] = "solid"
        self._mark_time_linewidth: float | list[float] = 2.5

    @property
    def ax_top(self) -> Axes:
        return self._ax_top

    @property
    def ax_right(self) -> Axes:
        return self._ax_right

    def _set_y_axes(
        self: Self,
        ymin: Number | None = None,
        ymax: Number | None = None,
    ) -> None:
        if ymin is not None and not np.isfinite(ymin):
            ymin = None
        if ymax is not None and not np.isfinite(ymax):
            ymax = None

        self._ax.set_ylim(
            bottom=cast(float, ymin),
            top=cast(float, ymax),
        )
        self._ax_right.set_ylim(self._ax.get_ylim())

        _format_y_ticks: _YAxisFormatter | None = None
        if isinstance(self._ax_style_y, str):
            _format_y_ticks = _Y_FORMATTER.get(self._ax_style_y)

        if _format_y_ticks is not None:
            _format_y_ticks(self)

    def _set_time_axes(
        self: Self,
        tmin: TimestampLike,
        tmax: TimestampLike,
        time: NDArray,
        tmin_original: TimestampLike | None = None,
        tmax_original: TimestampLike | None = None,
        longitude: NDArray | None = None,
        latitude: NDArray | None = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
    ) -> None:
        if not isinstance(tmin, np.datetime64):
            tmin = to_timestamp(tmin).to_datetime64()
        if not isinstance(tmax, np.datetime64):
            tmax = to_timestamp(tmax).to_datetime64()

        if tmin_original is None:
            tmin_original = tmin
        elif not isinstance(tmin_original, np.datetime64):
            tmin_original = to_timestamp(tmin_original).to_datetime64()

        if tmax_original is None:
            tmax_original = tmax
        elif not isinstance(tmax_original, np.datetime64):
            tmax_original = to_timestamp(tmax_original).to_datetime64()

        if ax_style_top is not None:
            self._ax_style_top = AlongTrackAxisStyle.from_input(ax_style_top)
        if ax_style_bottom is not None:
            self._ax_style_bottom = AlongTrackAxisStyle.from_input(ax_style_bottom)

        self._ax.set_xlim(
            left=cast(float, tmin),
            right=cast(float, tmax),
        )
        self._ax_top.set_xlim(self._ax.get_xlim())

        for ax, style in [
            (self._ax, self._ax_style_bottom),
            (self._ax_top, self._ax_style_top),
        ]:
            format_along_track_axis(
                ax=ax,
                ax_style=style,
                time=time,
                tmin=tmin,
                tmax=tmax,
                tmin_original=tmin_original,
                tmax_original=tmax_original,
                lon=longitude,
                lat=latitude,
                num_ticks=self._num_ticks,
            )

    def _set_selection_max_time_margin(
        self: Self,
        margin: _TimeMarginLike | None,
    ) -> None:
        if margin is None:
            return

        if isinstance(margin, TimedeltaLike):
            margin = (margin, margin)

        self._selection_max_time_margin = (
            to_timedelta(margin[0]),  # type: ignore
            to_timedelta(margin[-1]),  # type: ignore
        )

    def _set_selection_time_range(
        self: Self,
        selection_time_range: TimeRangeNoneLike | None,
    ) -> None:
        if selection_time_range is None:
            return

        if selection_time_range == (None, None):
            self._selection_time_range = (None, None)
            return

        if not isinstance(selection_time_range, (Sequence, np.ndarray)) or isinstance(
            selection_time_range, str
        ):
            TypeError(f"invalid type '{type(selection_time_range).__name__}' for time_range")

        t0 = selection_time_range[0]
        t1 = selection_time_range[-1]

        if t0 is not None:
            t0 = to_timestamp(t0)

        if t1 is not None:
            t1 = to_timestamp(t1)

        self._selection_time_range = (t0, t1)

    def _update(
        self: Self,
        selection_color: str | None = None,
        selection_linestyle: str | None = None,
        selection_linewidth: float | int | None = None,
        selection_highlight: bool | None = None,
        selection_highlight_inverted: bool | None = None,
        selection_highlight_color: str | None = None,
        selection_highlight_alpha: float | None = None,
        mark_time: TimestampLike | Sequence[TimestampLike] | None = None,
        mark_time_color: (str | Color | Sequence[str | Color | None] | None) = None,
        mark_time_linestyle: str | Sequence[str] = "solid",
        mark_time_linewidth: float | Sequence[float] = 2.5,
    ) -> None:
        if selection_color is not None:
            self._selection_color = Color.from_optional(selection_color)
        if selection_linestyle is not None:
            self._selection_linestyle = selection_linestyle
        if selection_linewidth is not None:
            self._selection_linewidth = selection_linewidth
        if selection_highlight is not None:
            self._selection_highlight = selection_highlight
        if selection_highlight_inverted is not None:
            self._selection_highlight_inverted = selection_highlight_inverted
        if selection_highlight_color is not None:
            self._selection_highlight_color = Color.from_optional(selection_highlight_color)
        if selection_highlight_alpha is not None:
            self._selection_highlight_alpha = selection_highlight_alpha
        if mark_time is not None:
            if isinstance(mark_time, np.ndarray):
                self._mark_time = mark_time.tolist()
            elif isinstance(mark_time, TimestampLike):
                self._mark_time = [to_timestamp(mark_time)]
            else:
                self._mark_time = list(mark_time)
        if mark_time_color is not None:
            if isinstance(mark_time_color, str):
                self._mark_time_color = Color.from_optional(mark_time_color)
            else:
                self._mark_time_color = [Color.from_optional(mtc) for mtc in mark_time_color]
        if mark_time_linestyle is not None:
            if isinstance(mark_time_linestyle, str):
                self._mark_time_linestyle = mark_time_linestyle
            elif isinstance(mark_time_linestyle, np.ndarray):
                self._mark_time_linestyle = mark_time_linestyle.tolist()
            else:
                self._mark_time_linestyle = list(mark_time_linestyle)
        if mark_time_linewidth is not None:
            if isinstance(mark_time_linewidth, (int, float)):
                self._mark_time_linewidth = mark_time_linewidth
            elif isinstance(mark_time_linewidth, np.ndarray):
                self._mark_time_linewidth = mark_time_linewidth.tolist()
            else:
                self._mark_time_linewidth = list(mark_time_linewidth)

    def _plot_selection(self: Self) -> None:
        if self._selection_time_range is None:
            return

        _tmin = cast(float | None, self._tmin)
        _tmax = cast(float | None, self._tmax)
        _selection_time_range = cast(tuple[float | None, float | None], self._selection_time_range)

        if self._selection_highlight:
            if self._selection_highlight_inverted:
                if _tmin is not None and _selection_time_range[0] is not None:
                    self._ax.axvspan(
                        _tmin,
                        _selection_time_range[0],
                        color=self._selection_highlight_color,
                        alpha=self._selection_highlight_alpha,
                        zorder=3,
                    )
                if _tmax is not None and _selection_time_range[1] is not None:
                    self._ax.axvspan(
                        _selection_time_range[1],
                        _tmax,
                        color=self._selection_highlight_color,
                        alpha=self._selection_highlight_alpha,
                        zorder=3,
                    )
            elif _selection_time_range[0] is not None and _selection_time_range[1] is not None:
                self._ax.axvspan(
                    _selection_time_range[0],
                    _selection_time_range[1],
                    color=self._selection_highlight_color,
                    alpha=self._selection_highlight_alpha,
                    zorder=3,
                )

        for t in _selection_time_range:
            if t is not None:
                self._ax.axvline(
                    x=t,
                    color=self._selection_color,
                    linestyle=self._selection_linestyle,
                    linewidth=self._selection_linewidth,
                    zorder=3,
                )

    def _plot_time_marks(self: Self) -> None:
        if self._mark_time is not None:
            params: list[list] = [[], [], []]
            for i, x in enumerate(
                (
                    self._mark_time_color,
                    self._mark_time_linestyle,
                    self._mark_time_linewidth,
                )
            ):
                if isinstance(x, list):
                    params[i] = x
                else:
                    params[i] = [x] * len(self._mark_time)

            color = params[0]
            linestyle = params[1]
            linewidth = params[2]

            for i, t in enumerate(to_timestamps(self._mark_time)):
                self._ax.axvline(
                    t,  # type: ignore
                    color=color[i],
                    linestyle=linestyle[i],
                    linewidth=linewidth[i],
                    zorder=20,
                )  # type: ignore

    def _get_time_range(
        self: Self,
        time: NDArray[np.datetime64],
        time_range: TimeRangeNoneLike | None,
    ) -> tuple[np.datetime64, np.datetime64]:
        if self._selection_max_time_margin is None:
            if time_range is None:
                return (time[0], time[-1])
            return (
                to_timestamp(time_range[0] or time[0]).to_datetime64(),
                to_timestamp(time_range[-1] or time[-1]).to_datetime64(),
            )

        selection_time_range: tuple[pd.Timestamp | None, pd.Timestamp | None]
        if self._selection_time_range is None:
            selection_time_range = (None, None)
        else:
            selection_time_range = self._selection_time_range

        t0: pd.Timestamp = selection_time_range[0] or to_timestamp(time[0])
        t1: pd.Timestamp = selection_time_range[-1] or to_timestamp(time[-1])

        if self._selection_max_time_margin is not None:
            _t0: np.datetime64 = (t0 - self._selection_max_time_margin[0]).to_datetime64()
            _t1: np.datetime64 = (t1 + self._selection_max_time_margin[-1]).to_datetime64()
            _t0 = np.max([time[0], _t0])
            _t1 = np.min([time[-1], _t1])
            return (_t0, _t1)

        return (t0.to_datetime64(), t1.to_datetime64())

    def _get_y_range(
        self: Self,
        y: NDArray[np.floating],
        y_range: ValueRangeLike | None,
    ) -> tuple[float, float]:
        if y_range is None:
            return (np.nanmin(y), np.nanmax(y))

        return (
            float(y_range[0] or np.nanmin(y)),
            float(y_range[-1] or np.nanmax(y)),
        )

    @property
    def value_range(self) -> tuple[float | None, float | None]:
        return (self._norm.vmin, self._norm.vmax)

    def _add_overpass_marks(
        self: Self,
        all_args: dict[str, Any],
        ds: xr.Dataset,
        time_var: str = TIME_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        site: SiteLike | None = None,
        radius_km: float = 100.0,
        mark_closest: bool = False,
        show_radius: bool = True,
    ) -> dict[str, Any]:
        _site: Site | None = None
        if isinstance(site, Site):
            _site = site
        elif isinstance(site, str):
            _site = get_site(site)

        if isinstance(_site, Site):
            info_overpass = get_overpass_info(
                ds,
                radius_km=radius_km,
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
                mark_closest = True

            if mark_closest:
                _mark_time = all_args["mark_time"]
                _mark_time_color = all_args["mark_time_color"]
                _mark_time_linestyle = all_args["mark_time_linestyle"]
                _mark_time_linewidth = all_args["mark_time_linewidth"]
                if isinstance(_mark_time, (Sequence, np.ndarray)):
                    _mark_time = list(_mark_time)
                    _mark_time.append(info_overpass.closest_time)
                    all_args["mark_time"] = _mark_time
                else:
                    all_args["mark_time"] = [info_overpass.closest_time]

                if not isinstance(_mark_time_color, str) and isinstance(
                    _mark_time_color, (Sequence, np.ndarray)
                ):
                    _mark_time_color = list(_mark_time_color)
                    _mark_time_color.append("ec:earthcare")
                    all_args["mark_time_color"] = _mark_time_color

                if not isinstance(_mark_time_linestyle, str) and isinstance(
                    _mark_time_linestyle, (Sequence, np.ndarray)
                ):
                    _mark_time_linestyle = list(_mark_time_linestyle)
                    _mark_time_linestyle.append("solid")
                    all_args["mark_time_linestyle"] = _mark_time_linestyle

                if isinstance(_mark_time_linewidth, (Sequence, np.ndarray)):
                    _mark_time_linewidth = list(_mark_time_linewidth)
                    _mark_time_linewidth.append(2.5)
                    all_args["mark_time_linewidth"] = _mark_time_linewidth

                all_args["selection_linestyle"] = "none"
                all_args["selection_linewidth"] = 0.1

        return all_args
