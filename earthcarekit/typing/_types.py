from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final, Literal, Protocol, Sequence, Tuple, TypeAlias

import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray

_TypeTuple: TypeAlias = tuple[type[Any], ...]

Number: TypeAlias = float | int | np.number
NumberPairLike: TypeAlias = Sequence[Number] | npt.NDArray[np.number]
NumberPairNoneLike: TypeAlias = Sequence[Number | None] | npt.NDArray[np.number]

ValueRangeLike: TypeAlias = NumberPairLike | NumberPairNoneLike
DistanceRangeLike: TypeAlias = NumberPairLike
DistanceRangeNoneLike: TypeAlias = NumberPairLike | NumberPairNoneLike
LatLonCoordsLike: TypeAlias = NumberPairLike

TimestampLike: TypeAlias = str | np.str_ | pd.Timestamp | np.datetime64 | datetime
TIMESTAMP_TYPES: Final[_TypeTuple] = (str, np.str_, pd.Timestamp, np.datetime64, datetime)

TimedeltaLike: TypeAlias = str | np.str_ | pd.Timedelta | np.timedelta64 | timedelta
TIMEDELTA_TYPES: Final[_TypeTuple] = (str, np.str_, pd.Timedelta, np.timedelta64, timedelta)

TimeRangeLike: TypeAlias = Sequence[TimestampLike] | NDArray[np.datetime64]
TimeRangeNoneLike: TypeAlias = Sequence[TimestampLike | None] | NDArray[np.datetime64]

ColorLike: TypeAlias = str | Sequence[int | float]
PathLike: TypeAlias = str | Path

_Offset: TypeAlias = float | int
_OnOffSeq: TypeAlias = Tuple[float | int, float | int]
LineStyle: TypeAlias = (
    str
    | Literal[
        "-",
        "solid",
        "--",
        "dashed",
        "-.",
        "dashdot",
        ":",
        "dotted",
        "",
        "none",
    ]
    | Tuple[_Offset, _OnOffSeq]
)


class HasFigure(Protocol):
    """Protocol for objects exposing a `.fig` attribute of type `matplotlib.figure.Figure`."""

    fig: Figure


class HasAxes(Protocol):
    """Protocol for objects exposing a `.ax` attribute of type `matplotlib.axes.Axes`."""

    ax: Axes
