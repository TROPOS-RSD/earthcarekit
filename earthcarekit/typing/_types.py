import datetime
from typing import Protocol, Sequence, TypeAlias

import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray

Number: TypeAlias = float | int | np.number
NumericPairLike: TypeAlias = (
    tuple[Number, Number] | list[Number] | Sequence[Number] | npt.NDArray[np.number]
)
NumericPairNoneLike: TypeAlias = (
    tuple[Number | None, Number | None]
    | list[Number | None]
    | Sequence[Number | None]
    | npt.NDArray[np.number]
)
ValueRangeLike: TypeAlias = NumericPairLike | NumericPairNoneLike
DistanceRangeLike: TypeAlias = NumericPairLike
DistanceRangeNoneLike: TypeAlias = NumericPairLike | NumericPairNoneLike
LatLonCoordsLike: TypeAlias = NumericPairLike
ColorLike: TypeAlias = str | Sequence[int | float]
TimestampLike: TypeAlias = str | np.str_ | pd.Timestamp | np.datetime64 | datetime.datetime
TimedeltaLike: TypeAlias = str | np.str_ | pd.Timedelta | np.timedelta64 | datetime.timedelta
TimeRangeLike: TypeAlias = (
    tuple[TimestampLike, TimestampLike] | list[TimestampLike] | NDArray[np.datetime64]
)


class HasFigure(Protocol):
    """Protocol for objects exposing a `.fig` attribute of type `matplotlib.figure.Figure`."""

    fig: Figure


class HasAxes(Protocol):
    """Protocol for objects exposing a `.ax` attribute of type `matplotlib.axes.Axes`."""

    ax: Axes
