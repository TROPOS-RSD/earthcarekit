from typing import Literal

import numpy as np
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import BoundaryNorm
from matplotlib.figure import Figure, SubFigure
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # type: ignore
from numpy.typing import ArrayLike

from ..color import Cmap


def add_vertical_colorbar(
    fig: Figure | SubFigure,
    ax: Axes,
    data: ScalarMappable,
    label: str | None = None,
    ticks: ArrayLike | None = None,
    tick_labels: ArrayLike | None = None,
    position: Literal["left", "right"] = "right",
    horz_buffer: float = 0.025,
    width_ratio: float | str = "1.25%",
    height_ratio: float | str = "100%",
    cmap: Cmap | None = None,
) -> Colorbar:
    """Creates a vertical colorbar that streches to the height of the plot and keeps a set horizontal padding and width."""
    valid_fig_types = (Figure, SubFigure)
    if not isinstance(fig, valid_fig_types):
        raise TypeError(
            f"{add_vertical_colorbar.__name__}() for `fig` expected type '{Figure.__name__}' or '{SubFigure.__name__}' but got '{type(fig).__name__}' instead"
        )
    if not isinstance(ax, Axes):
        raise TypeError(
            f"{add_vertical_colorbar.__name__}() for `ax` expected type '{Axes.__name__}' but got '{type(ax).__name__}' instead"
        )
    if not isinstance(data, ScalarMappable):
        raise TypeError(
            f"{add_vertical_colorbar.__name__}() for `data` expected type '{ScalarMappable.__name__}' but got '{type(data).__name__}' instead"
        )
    if not isinstance(position, str):
        raise TypeError(
            f"{add_vertical_colorbar.__name__}() for `position` expected type '{str.__name__}' but got '{type(position).__name__}' instead"
        )

    if position == "right":
        bbox_left = 1 + horz_buffer
    elif position == "left":
        bbox_left = 0 - horz_buffer
    else:
        raise ValueError(
            f"Invald colorbar position: '{position}'. Set it to either 'left' or 'right'."
        )

    cax = inset_axes(
        ax,
        width=width_ratio,
        height=height_ratio,
        loc="center left",
        bbox_to_anchor=(bbox_left, 0, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )

    if isinstance(cmap, Cmap) and cmap.categorical:
        cbar_bounds = np.arange(cmap.N + 1)
        cbar_norm = BoundaryNorm(cbar_bounds, cmap.N)
        sm = ScalarMappable(cmap=cmap, norm=cbar_norm)
        sm.set_array([])
        data = sm
        ticks = cmap.ticks
        tick_labels = cmap.labels

    cb = fig.colorbar(data, cax=cax, label=label, ticks=ticks, spacing="proportional")

    if tick_labels is not None:
        tick_labels = [str(l) for l in np.asarray(tick_labels)]
        cb.set_ticklabels(tick_labels)
        if (
            isinstance(data, ScalarMappable)
            and isinstance(cmap, Cmap)
            and cmap.categorical
        ):
            cb.solids.set_edgecolor("face")  # type: ignore
            cb.ax.tick_params(which="minor", size=0)
    else:
        if isinstance(cb.locator, ticker.AutoLocator):
            tick_locator = ticker.MaxNLocator(nbins="auto", steps=[1, 2, 2.5, 3, 5, 10])
            cb.locator = tick_locator
        if hasattr(cb.formatter, "set_useMathText"):
            cb.formatter.set_useMathText(True)
        cb.ax.yaxis.set_offset_position("left")
        cb.update_ticks()
        if hasattr(cb.formatter, "set_powerlimits"):
            cb.formatter.set_powerlimits((-2, 5))

    return cb


def add_colorbar(
    fig: Figure | SubFigure,
    ax: Axes,
    data: ScalarMappable,
    label: str | None = None,
    ticks: ArrayLike | None = None,
    tick_labels: ArrayLike | None = None,
    orientation: str | Literal["vertical", "horizontal"] = "vertical",
    position: str | Literal["left", "right", "top", "bottom"] = "right",
    alignment: str | Literal["left", "center", "right"] = "center",
    buffer: float = 0.025,
    width_ratio: float | str = "1.25%",
    height_ratio: float | str = "100%",
    cmap: Cmap | None = None,
) -> Colorbar:
    """
    Creates a colorbar (vertical or horizontal) alongside an axis with fixed placement and size.

    Args:
        fig (Figure | SubFigure): The parent figure.
        ax (Axes): The axis to which the colorbar is attached.
        data (ScalarMappable): The data for the colorbar.
        label (str, optional): Label for the colorbar.
        ticks (ArrayLike, optional): Tick positions.
        tick_labels (ArrayLike, optional): Tick labels.
        orientation (str): 'vertical' or 'horizontal'.
        position (str): Position relative to the axis ('left', 'right', 'top', 'bottom').
        alignment (str): Alignment of the colorbar ('left', 'center', 'right').
        buffer (float): Padding between axis and colorbar.
        width_ratio (float | str): Width (for vertical) or height (for horizontal) of the colorbar.
        height_ratio (float | str): Height (for vertical) or width (for horizontal) of the colorbar.
        cmap (Cmap, optional): A custom Cmap with categorical info.
    """
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
    elif alignment not in ["left", "center", "right"]:
        raise ValueError(
            f"""invalid value "{alignment}" for aligment, valid values are: "left", "center", "right"."""
        )

    bbox_anchor: tuple[float, float, float, float]
    if orientation == "vertical":
        if position == "right":
            bbox_anchor = (1 + buffer, 0, 1, 1)
            loc = f"left {alignment}"
        elif position == "left":
            bbox_anchor = (0 - buffer, 0, 1, 1)
            loc = f"right {alignment}"
        else:
            raise ValueError(
                "For vertical colorbars, position must be 'left' or 'right'."
            )
        cax = inset_axes(
            ax,
            width=width_ratio,
            height=height_ratio,
            loc=loc,
            bbox_to_anchor=bbox_anchor,
            bbox_transform=ax.transAxes,
            borderpad=0,
        )
    elif orientation == "horizontal":
        if position == "bottom":
            bbox_anchor = (0, -buffer, 1, 1)
            loc = f"upper {alignment}"
        elif position == "top":
            bbox_anchor = (0, 1 + buffer, 1, 1)
            loc = f"lower {alignment}"
        else:
            raise ValueError(
                "For horizontal colorbars, position must be 'top' or 'bottom'."
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
    else:
        raise ValueError("Orientation must be either 'vertical' or 'horizontal'.")

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
        if orientation == "vertical":
            cb.ax.yaxis.set_offset_position("left")
        cb.update_ticks()
        if hasattr(cb.formatter, "set_powerlimits"):
            cb.formatter.set_powerlimits((-2, 5))

    return cb
