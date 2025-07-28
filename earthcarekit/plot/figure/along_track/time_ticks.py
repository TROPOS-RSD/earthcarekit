import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from numpy.typing import NDArray

from ....utils.time import (
    TimestampLike,
    check_if_same_timestamp,
    format_time_range_text,
    get_time_range,
    lookup_value_by_timestamp,
    to_timestamp,
)


def format_time_ticks(
    ax: Axes,
    time: NDArray,
    lon: NDArray | None = None,
    tmin: TimestampLike | None = None,
    tmax: TimestampLike | None = None,
    show_lst: bool = True,
    show_utc: bool = True,
    show_major: bool = True,
    show_minor: bool = True,
    show_title: bool = True,
    show_tick_labels: bool = True,
    major_frequency: str | None = None,
    minor_frequency: str | None = None,
    xlabel_prefix: str = "",
    max_ticks: int = 12,
    fontsize_ticks: str = "small",
    fontsize_label: str = "small",
):
    if not isinstance(ax, Axes):
        raise TypeError(
            f"{format_time_ticks.__name__}() for `ax` expected type '{Axes.__name__}' but got '{type(ax).__name__}' instead"
        )

    utc_time = xr.DataArray(time)
    if not isinstance(tmin, TimestampLike):
        tmin = utc_time.values[0]
    if not isinstance(tmax, TimestampLike):
        tmax = utc_time.values[-1]

    start_time = to_timestamp(tmin)
    end_time = to_timestamp(tmax)

    duration = end_time - start_time

    divisors = {
        ("1s", "250ms"): 1,  # 1 sec
        ("2s", "1s"): 2,  # 2 sec
        ("3s", "1s"): 3,  # 3 sec
        ("4s", "1s"): 4,  # 4 sec
        ("5s", "1s"): 5,  # 5 sec
        ("10s", "2s"): 10,  # 10 sec
        ("15s", "3s"): 15,  # 15 sec
        ("20s", "5s"): 20,  # 20 sec
        ("30s", "10s"): 30,  # 30 sec
        ("1min", "15s"): 60 * 1,  # 1 min
        ("2min", "30s"): 60 * 2,  # 2 min
        ("3min", "1min"): 60 * 3,  # 3 min
        ("4min", "1min"): 60 * 4,  # 4 min
        ("5min", "1min"): 60 * 5,  # 5 min
        ("10min", "2min"): 60 * 10,  # 10 min
        ("15min", "3min"): 60 * 15,  # 15 min
        ("20min", "5min"): 60 * 20,  # 20 min
        ("30min", "10min"): 60 * 30,  # 30 min
        ("1h", "15min"): 60 * 60 * 1,  # 1 hour
        ("2h", "30min"): 60 * 60 * 2,  # 2 hours
        ("3h", "1h"): 60 * 60 * 3,  # 3 hours
        ("4h", "1h"): 60 * 60 * 4,  # 4 hours
        ("6h", "2h"): 60 * 60 * 6,  # 6 hours
        ("12h", "3h"): 60 * 60 * 12,  # 12 hours
        ("1D", "6h"): 60 * 60 * 24 * 1,  # 1 day
        ("2D", "12h"): 60 * 60 * 24 * 2,  # 2 days
        ("3D", "1D"): 60 * 60 * 24 * 3,  # 3 days
        ("4D", "1D"): 60 * 60 * 24 * 4,  # 4 days
        ("5D", "1D"): 60 * 60 * 24 * 5,  # 5 days
        ("1W", "1D"): 60 * 60 * 24 * 7,  # 7 days
        ("2W", "1W"): 60 * 60 * 24 * 14,  # 14 days
        ("MS", "SMS"): 60 * 60 * 24 * 30,  # 1 month
        ("QS", "MS"): 60 * 60 * 24 * 30 * 2,  # 2 months
        ("QS", "MS"): 60 * 60 * 24 * 30 * 6,  # 6 months
        ("1YS", "QS"): 60 * 60 * 24 * 356,  # 1 year
        ("2YS", "1YS"): 60 * 60 * 24 * 356 * 2,  # 2 years
    }

    for key, value in divisors.items():
        if (duration.days * 24 * 60 * 60 + duration.seconds) / value <= max_ticks:
            major_frequency = key[0]
            minor_frequency = key[1]
            break

    format_time = lambda t: t.strftime("%H:%M:%S")
    if "s" in major_frequency:
        format_time = lambda t: f"{t:%H:%M:%S}"
    elif "min" in major_frequency:
        format_time = lambda t: f"{t:%H:%M}"
    elif "h" in major_frequency:
        format_time = lambda t: f"{t:%m-%d %H}"
        if f"{start_time:%Y-%m-%d}" == f"{end_time:%Y-%m-%d}":
            format_time = lambda t: f"{t:%H:%M}"
    elif "D" in major_frequency or "W" in major_frequency:
        format_time = lambda t: f"{t:%Y-%m-%d}"
    elif "MS" in major_frequency or "SMS" in major_frequency or "QS" in major_frequency:
        format_time = lambda t: f"{t:%Y-%m-%d}"
    elif "Y" in major_frequency:
        format_time = lambda t: f"{t:%Y-%m-%d}"

    utc_ticks = get_time_range(start_time, end_time, freq=major_frequency)
    if len(utc_ticks) == 0:
        raise ValueError(f"invalid time range: ({start_time}, {end_time})")
    lst_time = None
    if lon is not None:
        lon = xr.DataArray(lon)
        lons = [
            lookup_value_by_timestamp(_t, utc_time.values, lon.to_numpy())
            for _t in utc_ticks
        ]
        lst_time = xr.DataArray(utc_ticks) + [
            pd.Timedelta(l / 15, "h").to_numpy() for l in lons
        ]
    utc_tick_labels = [format_time(t) for t in utc_ticks]

    time_idx = [np.argmin(np.abs(pd.DatetimeIndex(utc_ticks) - t)) for t in utc_ticks]
    if lst_time is not None:
        lst_ticks = pd.DatetimeIndex(lst_time[time_idx])
        lst_tick_labels = [format_time(t) for t in lst_ticks]
    else:
        show_lst = False

    tick_labels = ["" for utc in utc_tick_labels]
    if show_utc and show_lst:
        tick_labels = [
            f"{utc}\n{lst}" for utc, lst in zip(utc_tick_labels, lst_tick_labels)
        ]
        last_tick_label = tick_labels[-1].split("\n")
        tick_labels[-1] = (
            f"          {last_tick_label[0]} (UTC)\n         {last_tick_label[1]} (LST)"
        )
    elif show_utc:
        tick_labels = [f"{utc}" for utc in utc_tick_labels]
        last_tick_label = tick_labels[-1]
        tick_labels[-1] = f"{last_tick_label}"
    elif show_lst:
        tick_labels = [f"{lst}" for lst in lst_tick_labels]
        last_tick_label = tick_labels[-1]
        tick_labels[-1] = f"{last_tick_label}"

    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_xlabel("")

    if show_major:
        ax.set_xticks(
            utc_ticks,
            labels=tick_labels if show_tick_labels else ["" for x in tick_labels],
            fontsize=fontsize_ticks,
        )

    if show_minor:
        utc_ticks_minor = get_time_range(start_time, end_time, freq=minor_frequency)
        ax.set_xticks(utc_ticks_minor, minor=True)

    if show_title and show_tick_labels:
        label = f"{xlabel_prefix}{pd.to_datetime(utc_ticks[0]):%d %b %Y}"
        if not check_if_same_timestamp(start_time, end_time).is_same:
            label = f"{xlabel_prefix}{format_time_range_text(start_time, end_time, show_date=True, show_time=False)}"
        if show_utc and not show_lst:
            label = label + " (UTC)"
        elif not show_utc and show_lst:
            label = label + " (LST)"
        ax.set_xlabel(label, loc="center", fontsize=fontsize_label)
