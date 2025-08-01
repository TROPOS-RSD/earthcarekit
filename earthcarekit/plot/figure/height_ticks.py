from typing import Literal, TypeAlias

import matplotlib.ticker as ticker
import numpy as np
from matplotlib.axes import Axes

from .axis import AxisInput, validate_axis_input


def _smart_format(x, n=5):
    """Format with n decimals, then strip trailing 0 if present"""
    s = f"{x:.{n}f}"
    if s.endswith("0" * n):
        return s[: -n + 1]
    for i in range(n - 1, 0, -1):
        if s.endswith("0" * i):
            return s[:-i]
    return s


def format_height_ticks(
    ax: Axes,
    axis: AxisInput = "y",
    label: str | None = "Height",
    show_tick_labels: bool = True,
    show_units: bool = True,
):
    if not isinstance(ax, Axes):
        raise TypeError(
            f"{format_height_ticks.__name__}() for `ax` expected type '{Axes.__name__}' but got '{type(ax).__name__}' instead"
        )

    axis = validate_axis_input(axis)

    locator = ticker.MaxNLocator(nbins="auto", min_n_ticks=4, steps=[1, 2, 2.5, 5, 10])
    _ax = {"y": ax.yaxis, "x": ax.xaxis}[axis]
    _ax.set_major_locator(locator)

    height_ticks = ax.get_yticks() if axis == "y" else ax.get_xticks()
    height_lim = ax.get_ylim() if axis == "y" else ax.get_xlim()
    height_ticks = np.array(
        [h for h in height_ticks if h >= height_lim[0] and h <= height_lim[1]]
    )
    height_distance = height_ticks[-1] - height_ticks[0]
    units = ""
    _max_height_distance = 2.3e3

    if show_units and label != "none" and label is not None:
        units = " [km]" if height_distance >= _max_height_distance else " [m]"

    new_height_ticks = height_ticks
    if height_distance >= _max_height_distance:
        new_height_ticks = np.array([h / 1000 for h in height_ticks])

    all_ticks_are_integers = np.array([t.is_integer() for t in new_height_ticks]).all()
    if all_ticks_are_integers:
        new_height_ticks = np.array([int(t) for t in new_height_ticks])

    if not show_tick_labels:
        new_height_ticks = np.array(["" for t in new_height_ticks])

    if np.issubdtype(new_height_ticks.dtype, np.floating):
        new_height_ticks = np.array([_smart_format(t) for t in new_height_ticks])

    if axis == "y":
        ax.set_yticks(height_ticks, labels=new_height_ticks)
    else:
        ax.set_xticks(height_ticks, labels=new_height_ticks)

    if label == "none" or label is None:
        label = ""

    if axis == "y":
        ax.set_ylabel(f"{label}{units}")
    else:
        ax.set_xlabel(f"{label}{units}")
