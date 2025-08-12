from enum import IntEnum
from typing import TypeAlias

from .curtain import CurtainFigure
from .map import MapFigure
from .profile import ProfileFigure
from .swath import SwathFigure

ECKFigure: TypeAlias = MapFigure | CurtainFigure | SwathFigure | ProfileFigure


class FigureType(IntEnum):
    NONE = -1
    CURTAIN = 0
    CURTAIN_ZOOMED = 1
    SWATH = 2
    SWATH_ZOOMED = 3
    MAP_1_ROW = 4
    MAP_2_ROW = 5
    PROFILE = 6
    LINE = 7
    LINE_ZOOMED = 8
