import seaborn as sns

from .color import Cmap, Color, ColorLike, cmaps, get_cmap, shift_cmap
from .figure import (
    CurtainFigure,
    LineFigure,
    MapFigure,
    ProfileFigure,
    SwathFigure,
    create_column_subfigures,
    create_fig_layout_map_main_zoom_profile,
)
from .quicklook import ecquicklook, ecswath
from .save import save_plot

sns.set_style("ticks")
sns.set_context("notebook")

__all__ = [
    "Cmap",
    "Color",
    "ColorLike",
    "cmaps",
    "get_cmap",
    "shift_cmap",
    "CurtainFigure",
    "LineFigure",
    "MapFigure",
    "ProfileFigure",
    "SwathFigure",
    "create_column_subfigures",
    "create_fig_layout_map_main_zoom_profile",
    "ecquicklook",
    "ecswath",
    "save_plot",
]