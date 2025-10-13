import seaborn as sns

from .color import Cmap, Color, ColorLike, cmaps, get_cmap, shift_cmap
from .figure import (
    CurtainFigure,
    FigureType,
    LineFigure,
    MapFigure,
    ProfileFigure,
    SwathFigure,
    create_column_figure_layout,
    create_multi_figure_layout,
    plot_line_between_figures,
)
from .quicklook import ecquicklook, ecquicklook_deep_convection, ecswath
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
    "create_column_figure_layout",
    "create_multi_figure_layout",
    "ecquicklook",
    "ecswath",
    "ecquicklook_deep_convection",
    "save_plot",
    "plot_line_between_figures",
]
