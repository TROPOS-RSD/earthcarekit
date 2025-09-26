from typing import Any, Literal, Sequence, TypeAlias

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.patches import ConnectionPatch

from ...utils.time import TimestampLike, to_timestamp
from ...utils.typing import Number
from ..color import Color, ColorLike

_NumberTimeOrTuple: TypeAlias = (
    int
    | float
    | TimestampLike
    | tuple[int | float | TimestampLike, int | float | TimestampLike]
)


def _convert_to_matplotlib_axis_value(input: Any | TimestampLike) -> float:
    if isinstance(input, TimestampLike):
        t = to_timestamp(input)
        return mdates.date2num(t)
    return float(input)


def _get_point(
    ax: Axes,
    idx: Literal[1, 2],
    point: _NumberTimeOrTuple,
) -> tuple[float, float]:
    p: tuple[float, float]
    if isinstance(point, Sequence) and not isinstance(point, str):
        p = (
            _convert_to_matplotlib_axis_value(point[0]),
            _convert_to_matplotlib_axis_value(point[1]),
        )
    elif isinstance(point, (Number | TimestampLike)):
        p = (
            _convert_to_matplotlib_axis_value(point),
            ax.get_ylim()[idx - 1],
        )
    else:
        raise TypeError(f"Invalid type {type(point).__name__} for point{idx}")
    return p


def plot_line_between_figures(
    ax1: Axes,
    ax2: Axes,
    point1: _NumberTimeOrTuple,
    point2: _NumberTimeOrTuple | None = None,
    color: ColorLike | None = "ec:red",
    linestyle: str = "dashed",
    linewidth: int | float = 2,
    alpha: int | float = 0.3,
    capstyle: str = "butt",
    zorder: int | float = -20,
    **kwargs,
) -> None:
    """Draws a line connecting a point in one subfigure (ax1) to a point in another (ax2)."""
    p1: tuple[float, float] = _get_point(ax1, 1, point1)
    if point2 is None:
        point2 = point1
    p2: tuple[float, float] = _get_point(ax2, 2, point2)

    con = ConnectionPatch(
        xyA=p1,
        coordsA=ax1.transData,
        xyB=p2,
        coordsB=ax2.transData,
        axesA=ax1,
        axesB=ax2,
        color=Color.from_optional(color),
        linestyle=linestyle,
        linewidth=linewidth,
        alpha=alpha,
        capstyle=capstyle,
        zorder=zorder,
        **kwargs,
    )
    ax1.figure.add_artist(con)
