from dataclasses import dataclass
from logging import Logger
from typing import Literal, Sequence

import numpy as np
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..figure import ECKFigure


@dataclass
class _QuicklookResults:
    fig: Figure
    subfigs: list[list[ECKFigure]]
