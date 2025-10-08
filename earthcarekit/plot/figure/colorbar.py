from typing import Literal, Tuple, cast

import matplotlib.figure as mf
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import BoundaryNorm
from matplotlib.figure import Figure, SubFigure
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # type: ignore
from numpy.typing import ArrayLike

from ...utils.constants import CM_AS_INCH, DEFAULT_COLORBAR_WIDTH
from ..color import Cmap


def get_size_inches(ax: Axes) -> Tuple[float, float]:
    fig_h = ax.bbox.height
    fig_w = ax.bbox.width
    size = (fig_w / ax.figure.dpi, fig_h / ax.figure.dpi)
    return size


def add_colorbar(
    fig: Figure | SubFigure,
    ax: Axes,
    data: ScalarMappable,
    label: str | None = None,
    ticks: ArrayLike | None = None,
    tick_labels: ArrayLike | None = None,
    cmap: Cmap | None = None,
    position: str | Literal["left", "right", "top", "bottom"] = "right",
    alignment: str | Literal["left", "center", "right"] = "center",
    width: float = DEFAULT_COLORBAR_WIDTH,
    spacing: float = 0.2,
    length_ratio: float | str = "100%",
    label_outside: bool = True,
    ticks_outside: bool = True,
    ticks_both: bool = False,
) -> Colorbar:
    if not isinstance(fig, (Figure, SubFigure)):
        raise TypeError(
            f"{add_colorbar.__name__}() expected `fig` to be a Figure or SubFigure"
        )
    if not isinstance(ax, Axes):
        raise TypeError(f"{add_colorbar.__name__}() expected `ax` to be an Axes")
    if not isinstance(data, ScalarMappable):
        raise TypeError(
            f"{add_colorbar.__name__}() expected `data` to be a ScalarMappable"
        )

    if not isinstance(alignment, str):
        raise TypeError(
            f"""alignment has invalid type '{type(alignment).__name__}', expected 'str' ("left", "center", "right")"""
        )
    elif alignment in ["l", "c", "r"]:
        if alignment == "l":
            alignment = "left"
        elif alignment == "c":
            alignment = "center"
        elif alignment == "r":
            alignment = "right"
    elif alignment not in ["left", "center", "right"]:
        raise ValueError(
            f"""invalid value "{alignment}" for aligment, valid values are: "left", "center", "right"."""
        )

    if position == "l":
        position = "left"
    elif position == "r":
        position = "right"
    elif position == "t":
        position = "top"
    elif position == "b":
        position = "bottom"

    if isinstance(length_ratio, (float, int)):
        length_ratio = f"{length_ratio * 100.0}%"

    figsize = get_size_inches(ax)
    # figsize = fig.get_size_inches()  # type: ignore
    buffer: float
    width_ratio: float | str
    height_ratio: float | str
    orientation: Literal["vertical", "horizontal"]
    bbox_anchor: tuple[float, float, float, float]
    ytick_pos: Literal["left", "right"] = "right"
    xtick_pos: Literal["bottom", "top"] = "bottom"
    if position in ["left", "right"]:
        orientation = "vertical"
        buffer = spacing / figsize[0]
        width_ratio = length_ratio
        height_ratio = f"{(width / figsize[0]) * 100.0}%"
        if position in ["right"]:
            bbox_anchor = (1 + buffer, 0, 1, 1)
            if alignment == "left":
                alignment = "lower"
            elif alignment == "right":
                alignment = "upper"
            loc = f"{alignment} left"
        elif position in ["left"]:
            bbox_anchor = (-1 - buffer, 0, 1, 1)
            ytick_pos = "left"
            if alignment == "left":
                alignment = "lower"
            elif alignment == "right":
                alignment = "upper"
            loc = f"{alignment} right"
        else:
            raise ValueError(
                "For vertical colorbars, position must be 'left' or 'right'."
            )
    elif position in ["top", "bottom"]:
        orientation = "horizontal"
        buffer = spacing / figsize[1]
        width_ratio = f"{(width / figsize[1]) * 100.0}%"
        height_ratio = length_ratio
        if position in ["bottom"]:
            bbox_anchor = (0, -1 - buffer, 1, 1)
            loc = f"upper {alignment}"
        elif position in ["top"]:
            bbox_anchor = (0, 1 + buffer, 1, 1)
            xtick_pos = "top"
            loc = f"lower {alignment}"
        else:
            raise ValueError(
                "For horizontal colorbars, position must be 'top' or 'bottom'."
            )
    else:
        raise ValueError(
            'Invalid value given for position. Valid values are: "left", "right", "l", "r"'
        )
    cax = inset_axes(
        ax,
        width=height_ratio,
        height=width_ratio,
        loc=loc,
        bbox_to_anchor=bbox_anchor,
        bbox_transform=ax.transAxes,
        borderpad=0,
    )

    # Handle categorical colormap
    if isinstance(cmap, Cmap) and cmap.categorical:
        cbar_bounds = np.arange(cmap.N + 1)
        cbar_norm = BoundaryNorm(cbar_bounds, cmap.N)
        sm = ScalarMappable(cmap=cmap, norm=cbar_norm)
        sm.set_array([])
        data = sm
        ticks = cmap.ticks
        tick_labels = cmap.labels

    cb = fig.colorbar(
        data,
        cax=cax,
        orientation=orientation,
        label=label,
        ticks=ticks,
        spacing="proportional",
    )
    cb.ax.set_zorder(1)

    if tick_labels is not None:
        cb.set_ticklabels([str(l) for l in np.asarray(tick_labels)])
        if (
            isinstance(data, ScalarMappable)
            and isinstance(cmap, Cmap)
            and cmap.categorical
        ):
            cb.solids.set_edgecolor("face")  # type: ignore
            cb.ax.tick_params(which="minor", size=0)
    else:
        if hasattr(cb.formatter, "set_useMathText"):
            cb.formatter.set_useMathText(True)
        cb.update_ticks()
        if hasattr(cb.formatter, "set_powerlimits"):
            cb.formatter.set_powerlimits((-3, 5))

    ytick_pos_label = ytick_pos
    xtick_pos_label = xtick_pos
    if not label_outside:
        ytick_pos_label = "left" if ytick_pos == "right" else "right"
        xtick_pos_label = "top" if xtick_pos == "bottom" else "bottom"
    cb.ax.yaxis.set_label_position(ytick_pos_label)
    cb.ax.xaxis.set_label_position(xtick_pos_label)

    ytick_pos_ticks: Literal["left", "right", "both", "default", "none"] = ytick_pos
    xtick_pos_ticks: Literal["top", "bottom", "both", "default", "none"] = xtick_pos
    if ticks_both:
        ytick_pos_ticks = "both"
        xtick_pos_ticks = "both"
    elif not ticks_outside:
        ytick_pos_ticks = "left" if ytick_pos == "right" else "right"
        xtick_pos_ticks = "top" if xtick_pos == "bottom" else "bottom"
    cb.ax.yaxis.set_ticks_position(ytick_pos_ticks)
    cb.ax.xaxis.set_ticks_position(xtick_pos_ticks)

    if position in ["right", "left"]:
        cb.ax.yaxis.set_offset_position("left")

    return cb
