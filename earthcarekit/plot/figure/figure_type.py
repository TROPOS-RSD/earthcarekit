from enum import IntEnum
from typing import TypeAlias

from .curtain import CurtainFigure
from .line import LineFigure
from .map import MapFigure
from .profile import ProfileFigure
from .swath import SwathFigure

ECKFigure: TypeAlias = MapFigure | CurtainFigure | SwathFigure | ProfileFigure | LineFigure


class FigureType(IntEnum):
    NONE = -1
    CURTAIN = 0
    CURTAIN_ZOOMED = 1
    SWATH = 2
    SWATH_ZOOMED = 3
    MAP_1_ROW = 4
    MAP_2_ROW = 5
    MAP_3_ROW = 6
    MAP_4_ROW = 7
    MAP_5_ROW = 8
    MAP_6_ROW = 9
    MAP_7_ROW = 10
    MAP_8_ROW = 11
    MAP_9_ROW = 12
    MAP_FULL_ROW = 13
    PROFILE = 14
    LINE = 15
    LINE_ZOOMED = 16
    CURTAIN_75 = 17
    CURTAIN_67 = 18
    CURTAIN_50 = 19
    CURTAIN_33 = 20
    CURTAIN_25 = 21
