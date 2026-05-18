from typing import Any, Literal

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnchoredText
from matplotlib.text import Text

from ...color import Color, ColorLike
from ...constants import TIME_VAR
from ...overpass import OverpassInfo
from ...site import get_site
from ...typing import HasAxes
from ...utils.time import TimestampLike
from ._get_info import (
    get_earthcare_file_type_baseline_string,
    get_earthcare_frame_string,
    get_earthcare_overpass_string,
)
from ._text import add_text
from ._title import add_title


def add_text_overpass_info(
    ax: Axes,
    info: OverpassInfo,
    zorder: int | float | None = 100,
) -> list[AnchoredText]:

    site = get_site(info.site)
    site_altitude = site.altitude
    site_coords = site.coordinates
    radius = info.site_radius_km
    samples = info.samples
    along_track_distance = info.along_track_distance_km
    closest_distance = info.closest_distance_km
    closest_time = info.closest_time

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
    info_string = f"{_lat} {_lon}{_alt}\n{_radius}"
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
    text = ""

    t1 = add_text(
        ax,
        text,
        zorder=zorder,
    )

    return [t1]


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
    text = get_earthcare_overpass_string(ds, time_var, tmin, tmax)
    return add_title(ax, text, fontsize=fontsize, loc=loc, color=color)


def add_text_product_info(
    ax: Axes,
    ds: xr.Dataset,
    fontsize: str | float = "medium",
    loc: str = "upper right",
    color: Color | ColorLike | None = "black",
    append_to: AnchoredText | str | None = None,
    zorder: int | float | None = 100,
    show_orbit_and_frame: bool = True,
    show_file_type: bool = True,
    show_baseline: bool = True,
    text_orbit_and_frame: str | None = None,
    text_file_type: str | None = None,
    text_baseline: str | None = None,
) -> AnchoredText:
    color = Color.from_optional(color)
    text_frame = ""
    if show_orbit_and_frame:
        if isinstance(text_orbit_and_frame, str):
            text_frame = text_orbit_and_frame
        else:
            text_frame = get_earthcare_frame_string(ds)
    text_type_baseline = get_earthcare_file_type_baseline_string(
        ds,
        show_file_type=show_file_type,
        show_baseline=show_baseline,
        text_file_type=text_file_type,
        text_baseline=text_baseline,
    )
    texts = [t for t in [text_frame, text_type_baseline] if t != ""]
    text = "\n".join(texts)

    old_text: str | None = None
    if isinstance(append_to, AnchoredText):
        old_text = append_to.txt.get_text()
        append_to.remove()
    elif isinstance(append_to, str):
        old_text = append_to
    if isinstance(old_text, str):
        text = old_text
        if text_frame != "" and text_frame not in text:
            text = f"{text}\n{text_frame}"
        for ttb in text_type_baseline.split("\n"):
            if ttb != "" and ttb not in text:
                text = f"{text}\n{ttb}"

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


def add_image_source_label(
    ax: Axes | HasAxes,
    data: (Literal["osm", "nasa", "nasagibs", "eumetsat", "mtg", "msg", "esa"] | str | None) = None,
    text: str | None = None,
    loc: str = "lower right",
    fontsize: str = "x-small",
    box_alpha: float = 0.6,
    box_color: str = "white",
    pad: float = 0.2,
    borderpad: float = 0.1,
    change_anchor: bool = False,
    bbox_to_anchor: tuple[float, float] = (1.01, -0.08),
) -> AnchoredText | None:
    """
    Adds a small text label to a plot, intended to display background images sources in map plots.

    Args:
        ax (Axes): The image axes.
        data (Literal[&quot;osm&quot;, &quot;nasa&quot;, &quot;nasagibs&quot;, &quot;eumetsat&quot;, &quot;mtg&quot;, &quot;msg&quot;, &quot;esa&quot;] | None, optional): A tag name used to select a predefiened attribution text. Defaults to None.
        text (str | None, optional): The (manual) attribution text. Defaults to None.
        loc (str, optional): Positioning string for the label in the plot. Defaults to "lower right".
        fontsize (str, optional): Text size. Defaults to "x-small".
        box_alpha (float, optional): Transparency of the label box. Defaults to 0.6.
        box_color (str, optional): Color of the label box. Defaults to "white".
        pad (float, optional): Inside padding between text and box edges. Defaults to 0.2.
        borderpad (float, optional): Outside padding around box. Defaults to 0.1.

    Returns:
        AnchoredText | None: The text object or nothing, if invalid inputs.
    """
    _ax: Axes
    if hasattr(ax, "ax") and isinstance(ax.ax, Axes):
        _ax = ax.ax
    elif isinstance(ax, Axes):
        _ax = ax
    else:
        raise TypeError("invalid ax")

    if not isinstance(text, str):
        if not isinstance(data, str):
            return None

        data = str(data).lower()
        data = data.replace(" ", "").replace("-", "").replace("_", "")

        if data == "osm":
            text = "© OSM contributors"
        elif data == "nasa":
            text = "© NASA"
        elif data in ["nasagibs"]:
            text = "© NASA GIBS"
        elif data in ["bluemarble"]:
            text = "Blue Marble © NASA"
        elif data in ["eumetsat"]:
            text = f"© EUMETSAT {pd.Timestamp.now().year}"
        elif data in ["mtg"]:
            text = "MTG GeoColour\n© EUMETSAT / NASA"
        elif data in ["msg"]:
            text = f"Natural Colour Enhanced RGB\n© EUMETSAT {pd.Timestamp.now().year}"
        elif data == "esa":
            text = "© ESA"
        elif data == "ecmwf":
            text = "© ECMWF"
        else:
            return None

    kwargs: dict[str, Any] = {}
    if change_anchor:
        kwargs["bbox_to_anchor"] = bbox_to_anchor
        kwargs["bbox_transform"] = _ax.transAxes

    at = AnchoredText(
        text,
        loc=loc,
        frameon=True,
        pad=pad,
        borderpad=borderpad,
        prop={"fontsize": fontsize},
        **kwargs,
    )
    at.patch.set_facecolor(box_color)
    at.patch.set_alpha(box_alpha)
    at.patch.set_edgecolor("none")
    _ax.add_artist(at)

    return at
