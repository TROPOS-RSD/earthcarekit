from typing import Callable, Literal, Self, Sequence, TypeAlias, cast

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.typing import LineStyleType
from numpy.typing import NDArray

from ....color import ColorLike
from ....typing import Number, TimedeltaLike, TimeRangeNoneLike, TimestampLike, ValueRangeLike
from ....utils.time import to_timedelta, to_timestamp
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
        figsize: tuple[float, float] = (4.0, 4.0),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool = False,
        grid_which: Literal["major", "minor", "both"] = "major",
        grid_axis: Literal["both", "x", "y"] = "both",
        grid_color: ColorLike | None = "#CCCCCC",
        grid_alpha: float = 1.0,
        grid_linestyle: LineStyleType = "solid",
        grid_linewidth: float = 1.0,
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
            figsize=figsize,
            dpi=dpi,
            title=title,
            fig_height_scale=fig_height_scale,
            fig_width_scale=fig_width_scale,
            axes_rect=axes_rect,
            show_grid=show_grid,
            grid_which=grid_which,
            grid_axis=grid_axis,
            grid_color=grid_color,
            grid_alpha=grid_alpha,
            grid_linestyle=grid_linestyle,
            grid_linewidth=grid_linewidth,
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
            _t1: np.datetime64 = (t1 - self._selection_max_time_margin[-1]).to_datetime64()
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
            return (y[0], y[-1])

        return (
            float(y_range[0] or np.nanmin(y)),
            float(y_range[-1] or np.nanmax(y)),
        )
