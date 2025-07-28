import numpy as np
from matplotlib.axes import Axes
from numpy.typing import NDArray

from ....utils.geo import get_cumulative_distances
from ....utils.geo.string_formatting import format_latitude, format_longitude
from ...figure.format_strings import format_float
from ...figure.ticks import add_ticks
from .style import AlongTrackAxisData, AlongTrackAxisStyle
from .time_ticks import format_time_ticks


def format_along_track_axis(
    ax: Axes,
    ax_style: AlongTrackAxisStyle,
    time: NDArray,
    tmin: np.datetime64,
    tmax: np.datetime64,
    tmin_original: np.datetime64,
    tmax_original: np.datetime64,
    lon: NDArray | None = None,
    lat: NDArray | None = None,
    num_ticks: int = 10,
) -> None:
    show_title = ax_style.title
    show_units = ax_style.units
    show_labels = ax_style.labels

    if ax_style.data in [
        AlongTrackAxisData.TIME,
        AlongTrackAxisData.TIME_UTC,
        AlongTrackAxisData.TIME_LST,
    ]:
        show_title = False if show_title == False else True
        show_labels = False if show_labels == False else True

        show_utc = True
        show_lst = True
        if ax_style.data == AlongTrackAxisData.TIME_UTC:
            show_lst = False
        elif ax_style.data == AlongTrackAxisData.TIME_LST:
            show_lst = True

        format_time_ticks(
            ax=ax,
            time=time,
            tmin=tmin,
            tmax=tmax,
            lon=lon,
            show_title=show_title,
            show_utc=show_utc,
            show_lst=show_lst,
            show_tick_labels=show_labels,
            max_ticks=num_ticks,
        )
        return

    show_units = False if show_units == False else True
    show_labels = False if show_labels == False else True

    if (
        ax_style.data == AlongTrackAxisData.GEO
        and isinstance(lat, np.ndarray)
        and isinstance(lon, np.ndarray)
    ):
        show_title = True if show_title == True else False
        time_data = time
        lat_data = lat
        lon_data = lon
        if tmin < tmin_original:
            time_data = np.concatenate(([tmin], time_data))
            lat_data = np.concatenate(([np.nan], lat_data))
            lon_data = np.concatenate(([np.nan], lon_data))
        if tmax_original < tmax:
            time_data = np.concatenate((time_data, [tmax]))
            lat_data = np.concatenate((lat_data, [np.nan]))
            lon_data = np.concatenate((lon_data, [np.nan]))
        if show_title:
            if not show_units:
                title = r"Latitude/Logitude [$^\circ$N/$^\circ$E]"
            else:
                title = r"Latitude/Logitude"
        else:
            title = ""
        add_ticks(
            ax=ax,
            ax_data=time_data,
            major_tick_count=num_ticks,
            fontsize="small",
            title=title,
            show_tick_labels=show_labels,
            tick_data=lat_data,
            format_function=format_latitude,
            tick_data2=lon_data,
            format_function2=format_longitude,
        )
    elif ax_style.data == AlongTrackAxisData.LAT and isinstance(lat, np.ndarray):
        show_title = True if show_title == True else False
        time_data = time
        lat_data = lat
        if tmin < tmin_original:
            time_data = np.concatenate(([tmin], time_data))
            lat_data = np.concatenate(([np.nan], lat_data))
        if tmax_original < tmax:
            time_data = np.concatenate((time_data, [tmax]))
            lat_data = np.concatenate((lat_data, [np.nan]))
        if show_title:
            if not show_units:
                title = r"Latitude [$^\circ$N]"
            else:
                title = r"Latitude"
        else:
            title = ""
        add_ticks(
            ax=ax,
            ax_data=time_data,
            major_tick_count=num_ticks,
            fontsize="small",
            title=title,
            show_tick_labels=show_labels,
            tick_data=lat_data,
            format_function=format_latitude,
        )
    elif ax_style.data == AlongTrackAxisData.LON and isinstance(lon, np.ndarray):
        show_title = True if show_title == True else False
        time_data = time
        lon_data = lon
        if tmin < tmin_original:
            time_data = np.concatenate(([tmin], time_data))
            lon_data = np.concatenate(([np.nan], lon_data))
        if tmax_original < tmax:
            time_data = np.concatenate((time_data, [tmax]))
            lon_data = np.concatenate((lon_data, [np.nan]))
        if show_title:
            if not show_units:
                title = r"Logitude [$^\circ$E]"
            else:
                title = r"Logitude"
        else:
            title = ""
        add_ticks(
            ax=ax,
            ax_data=time_data,
            major_tick_count=num_ticks,
            fontsize="small",
            title=title,
            show_tick_labels=show_labels,
            tick_data=lon_data,
            format_function=format_longitude,
        )
    elif (
        ax_style.data == AlongTrackAxisData.DISTANCE
        and isinstance(lat, np.ndarray)
        and isinstance(lon, np.ndarray)
    ):
        show_title = False if show_title == False else True
        distances = get_cumulative_distances(lat, lon, units="km")
        title = r"Distance [km]"
        add_ticks(
            ax=ax,
            ax_data=time,
            major_tick_count=num_ticks,
            fontsize="small",
            title=title,
            tick_data=distances,
            format_function=format_float,
            show_tick_labels=show_labels,
            in_linspace=False,
        )
    elif ax_style.data == AlongTrackAxisData.COUNT:
        show_title = False if show_title == False else True
        title = r"Samples"
        add_ticks(
            ax=ax,
            ax_data=time,
            major_tick_count=num_ticks,
            fontsize="small",
            title=title,
            tick_data=np.arange(len(time)),
            format_function=format_float,
            show_tick_labels=show_labels,
            in_linspace=False,
        )
    else:
        ax.set_xticks([], [])
