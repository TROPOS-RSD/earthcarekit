import warnings
from typing import Literal

import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnchoredText
from matplotlib.text import Text

from ...utils._parse_units import parse_units
from ...utils.constants import *
from ...utils.ground_sites import get_ground_site
from ...utils.np_array_utils import all_same
from ...utils.overpass import OverpassInfo
from ...utils.read import get_product_infos
from ...utils.read.product.file_info import FileType, ProductDataFrame
from ...utils.time import TimestampLike, format_time_range_text, to_timestamp
from ..color import Color, ColorLike
from .format_strings import wrap_label


def add_text(
    ax: Axes,
    text: str,
    loc: str = "upper right",
    borderpad: float = 0,
    pad: float = 0.4,
    fontsize: str | float | None = None,
    fontweight: str | None = None,
    horizontalalignment: str = "left",
    color: Color | ColorLike | None = "black",
    is_shaded_text: bool = True,
    shade_linewidth: float = 3,
    shade_color: str = "white",
    shade_alpha: float = 0.8,
    is_box: bool = False,
    append_to: AnchoredText | str | None = None,
    zorder: int | float | None = None,
) -> AnchoredText:
    """
    Adds anchored text to a matplotlib Axes with optional shading and styling.

    Args:
        ax (matplotlib.axes.Axes): Target matplotlib Axes.
        text (str): Text string to display.
        loc (str): Anchor location in the Axes (e.g. 'upper right').
        borderpad (float): Padding between text and the border of the box.
        pad (float): Padding between box and the Axes.
        fontsize (str or float, optional): Font size of the text.
        fontweight (str, optional): Font weight (e.g. 'normal', 'bold').
        horizontalalignment (str): Horizontal alignment of the text.
        color (Color or ColorLike, optional): Text color.
        is_shaded_text (bool): If True, apply a white stroke around the text.
        shade_linewidth (float): Width of the stroke line.
        shade_color (str): Color of the stroke.
        shade_alpha (float): Opacity of the stroke.
        is_box (bool): If True, draw a box around the text.
        append_to (AnchoredText or str, optional): Extracts the given text string and adds the new text to it.
        zorder (int | float, optional): Drawing order of the plot element.

    Returns:
        AnchoredText: The text artist added to the Axes.
    """
    old_text: str | None = None
    if isinstance(append_to, AnchoredText):
        old_text = append_to.txt.get_text()
        append_to.remove()
    elif isinstance(append_to, str):
        old_text = append_to

    if isinstance(old_text, str):
        text = f"{old_text}{text}"

    path_effects = None
    if is_shaded_text:
        path_effects = [
            pe.withStroke(
                linewidth=shade_linewidth,
                foreground=shade_color,
                alpha=shade_alpha,
            )
        ]

    text_properties = {
        "size": fontsize,
        "fontweight": fontweight,
        "horizontalalignment": horizontalalignment,
        "path_effects": path_effects,
        "color": color,
    }

    anchored_text = AnchoredText(
        text,
        loc=loc,
        borderpad=borderpad,
        pad=pad,
        prop=text_properties,
        frameon=is_box,
        zorder=zorder,
    )
    ax.add_artist(anchored_text)
    return anchored_text


def add_title(
    ax: Axes,
    title: str,
    fontsize: str = "medium",
    loc: Literal["left", "center", "right"] | None = "center",
    **kwargs,
) -> Text:
    return ax.set_title(title, loc=loc, fontsize=fontsize, **kwargs)


def get_earthcare_frame_string(data: xr.Dataset | ProductDataFrame) -> str:
    text: str = ""

    if isinstance(data, xr.Dataset):
        if "concat_dim" in data.dims:
            if "frame_id" in data and "orbit_number" in data:
                orbit_start = str(data["orbit_number"].values[0]).zfill(5)
                orbit_end = str(data["orbit_number"].values[-1]).zfill(5)
                frame_start = str(data["frame_id"].values[0])
                frame_end = str(data["frame_id"].values[-1])

                if orbit_start == orbit_end:
                    text = (
                        f"{orbit_start}{frame_start}"
                        if frame_start == frame_end
                        else f"{orbit_start}{frame_start}-{frame_end}"
                    )
                else:
                    text = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"
                return text
        elif "orbit_and_frame" in data:
            return str(data["orbit_and_frame"].values)
        elif "frame_id" in data and "orbit_number" in data:
            o = str(data["orbit_number"].values).zfill(5)
            f = str(data["frame_id"].values)
            return f"{o}{f}"

    try:
        df: ProductDataFrame = get_product_infos(data)
    except ValueError as e:
        return text

    if len(df.shape) == 2 and df.shape[0] == 1:
        text = str(df["orbit_and_frame"][0])
    elif len(df.shape) == 2 and df.shape[0] > 1:
        orbit_start = str(df["orbit_number"].iloc[0]).zfill(5)
        orbit_end = str(df["orbit_number"].iloc[-1]).zfill(5)
        frame_start = df["frame_id"].iloc[0]
        frame_end = df["frame_id"].iloc[-1]

        if orbit_start == orbit_end:
            text = (
                f"{orbit_start}{frame_start}"
                if frame_start == frame_end
                else f"{orbit_start}{frame_start}-{frame_end}"
            )
        else:
            text = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"

    return text


def get_earthcare_file_type_baseline_string(data: xr.Dataset | ProductDataFrame) -> str:
    text: str = ""

    if isinstance(data, xr.Dataset):
        if "file_type" in data and "baseline" in data:
            ft = np.atleast_1d(data["file_type"].values)[0]
            ft = FileType.from_input(ft).to_shorthand()
            bl = np.atleast_1d(data["baseline"].values)[0]
            return f"{ft}:{bl}"

    try:
        df: ProductDataFrame = get_product_infos(data)
    except ValueError as e:
        return text

    file_types = df["file_type"]
    baselines = df["baseline"]

    if not all_same(baselines):
        warnings.warn(f"The data contains multiple baselines: {baselines}")

    file_type: str = FileType.from_input(file_types[0]).to_shorthand()
    baseline: str = baselines[0]

    text = f"{file_type}:{baseline}"

    return text


def add_title_earthcare_frame(
    ax: Axes,
    ds: xr.Dataset,
    fontsize: str = "medium",
    loc: Literal["left", "center", "right"] | None = "right",
    color: Color | ColorLike | None = "black",
) -> Text:
    color = Color.from_optional(color)
    text = get_earthcare_frame_string(ds)
    return add_title(ax, text, fontsize=fontsize, loc=loc, color=color)
    # plt.title(text, loc=loc, fontsize=fontsize, color=color)


def add_title_earthcare_time(
    ax: Axes,
    ds: xr.Dataset | None = None,
    time_var: str = TIME_VAR,
    tmin: TimestampLike | None = None,
    tmax: TimestampLike | None = None,
    fontsize: str = "medium",
    loc: Literal["left", "center", "right"] | None = "left",
    color: Color | ColorLike | None = "black",
) -> Text:
    color = Color.from_optional(color)

    _tmin: TimestampLike | None = None
    _tmax: TimestampLike | None = None

    if isinstance(ds, xr.Dataset):
        _tmin = ds[time_var].values[0]
        _tmax = ds[time_var].values[-1]

    if isinstance(tmin, TimestampLike):
        _tmin = to_timestamp(tmin)

    if isinstance(tmax, TimestampLike):
        _tmax = to_timestamp(tmax)

    if isinstance(_tmin, TimestampLike) and isinstance(_tmax, TimestampLike):
        text = format_time_range_text(_tmin, _tmax)
    else:
        raise ValueError(
            f"Missing arguments. At least 'ds' or 'tmin' and 'tmax' must be given."
        )

    return add_title(ax, text, fontsize=fontsize, loc=loc, color=color)


def add_text_overpass_info(
    ax: Axes,
    info: OverpassInfo,
    zorder: int | float | None = 100,
) -> list[AnchoredText]:

    site = get_ground_site(info.site)
    site_name = site.name
    site_altitude = site.altitude
    site_coords = site.coordinates
    radius = info.site_radius_km
    samples = info.samples
    along_track_distance = info.along_track_distance_km
    closest_distance = info.closest_distance_km
    closest_time = info.closest_time

    _site_name = f" ({site_name})" if site_name != "" else ""
    _alt = f" {int(site_altitude)}m" if site_altitude is not None else ""
    _lat = "{:.3f}".format(site_coords[0]) + r"$^\circ\text{N}$"
    _lon = "{:.3f}".format(site_coords[1]) + r"$^\circ\text{E}$"
    _radius = f"Radius: {'{:.0f}'.format(radius)}km"
    _samples = f"Samples: {samples}"
    _along_track_distance = (
        ""
        if along_track_distance is None
        else f"\nAlong-track: {np.round(along_track_distance, decimals=3)}km"
    )
    _closest_distance = (
        ""
        if closest_distance is None
        else f"\nClosest: {np.round(closest_distance, decimals=3)}km at {pd.Timestamp(closest_time).strftime('%H:%M:%S')} UTC"
    )
    info_string = f"{_lat} {_lon}{_alt}{_site_name}\n{_radius}"
    add_text(
        ax,
        info_string,
        loc="upper left",
        horizontalalignment="left",
        fontsize="small",
        zorder=zorder,
    )
    info_string2 = f"{_samples}{_along_track_distance}{_closest_distance}"
    add_text(
        ax,
        info_string2,
        loc="lower left",
        horizontalalignment="left",
        fontsize="small",
        zorder=zorder,
    )
    text = f""

    t1 = add_text(
        ax,
        text,
        zorder=zorder,
    )

    return [t1]


def add_text_product_info(
    ax: Axes,
    ds: xr.Dataset,
    fontsize: str | float = "medium",
    loc: str = "upper right",
    color: Color | ColorLike | None = "black",
    append_to: AnchoredText | str | None = None,
    zorder: int | float | None = 100,
) -> AnchoredText:
    color = Color.from_optional(color)
    text_frame = get_earthcare_frame_string(ds)
    text_type_baseline = get_earthcare_file_type_baseline_string(ds)
    text = f"{text_frame}\n{text_type_baseline}"

    old_text: str | None = None
    if isinstance(append_to, AnchoredText):
        old_text = append_to.txt.get_text()
        append_to.remove()
    elif isinstance(append_to, str):
        old_text = append_to
    if isinstance(old_text, str):
        text = old_text
        if text_frame not in text:
            text = f"{text}\n{text_frame}"
        if text_type_baseline not in text:
            text = f"{text}\n{text_type_baseline}"

    horizontalalignment: str = "center"
    if "left" in loc:
        horizontalalignment = "left"
    elif "right" in loc:
        horizontalalignment = "right"

    return add_text(
        ax=ax,
        text=text,
        fontsize=fontsize,
        loc=loc,
        horizontalalignment=horizontalalignment,
        color=color,
        fontweight="bold",
        zorder=zorder,
    )


def format_var_label(
    name: str | None = None,
    units: str | None = None,
    da: xr.DataArray | None = None,
    label_len: int | None = 40,
) -> str:
    """Format a label with optional units and wrap it to a specified maximum line length.

    Args:
        name (str | None): The base name of the label.
        units (str | None, optional): The units to include in the label. Defaults to None.
        da (xr.DataArray | None, optional): A `xarray.DataArray` from which the label and units
            will be taken, if it has the attributes 'long_name' and 'units'. Defaults to None.
        label_len (int | None, optional): The maximum length of each line. Defaults to 40.

    Returns:
        str: The formatted and wrapped label string.
    """

    if label_len is None:
        label_len = 40

    label: str

    if isinstance(da, xr.DataArray):
        if name is None and hasattr(da, "long_name"):
            name = da.long_name
        if units is None and hasattr(da, "units"):
            units = da.units

    if name is None:
        name = ""
    elif not isinstance(name, str):
        raise TypeError(
            f"Invalid type '{type(name).__name__}' for variable name: {name}. Expected type 'str'."
        )

    label = name

    if isinstance(units, str):
        if units == "":
            pass
        elif units.lower() not in ["-", "none"]:
            label = f"{name} [{parse_units(units, use_latex=True)}]"

    label = wrap_label(label, label_len)

    return label
