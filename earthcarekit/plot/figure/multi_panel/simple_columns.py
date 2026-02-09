from dataclasses import dataclass
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


@dataclass(frozen=True)
class FigureLayoutColumns:
    fig: Figure
    axs: list[Axes]


def create_column_figure_layout(
    ncols: int,
    single_figsize: tuple[float, float] = (3, 8),
    margin: float = 0.0,
    height_scale: float = 1.0,
    width_scale: float | list[float] = 1.0,
) -> FigureLayoutColumns:
    """
    Creates a figure with multiple subfigures arranged as columns in a single row, each containing one Axes.

    Args:
        ncols (int): Number of subfigures (columns) to create.
        single_figsize (tuple[float, float], optional): Size (width, height) of each individual subfigure.
            Defaults to (3, 8).

    Returns:
        tuple[Figure, list[Axes]]: The parent figure and a list of Axes objects, one for each subfigure.
    """
    if not isinstance(width_scale, list):
        width_scale = [width_scale] * ncols

    if not isinstance(width_scale, list) or len(width_scale) != ncols:
        raise ValueError(
            f"length of list width_scale ({len(width_scale)}) must match 'ncols' ({ncols}) or be scalar float"
        )

    fig: Figure = plt.figure(
        figsize=(
            np.sum(single_figsize[0] * np.array(width_scale)) + (ncols - 1) * margin,
            single_figsize[1] * height_scale,
        )
    )
    figs: np.ndarray
    if ncols == 1:
        figs = np.array([fig])
    else:
        width_ratios = [single_figsize[0]]
        for i in range(ncols - 1):
            width_ratios.extend([margin, single_figsize[0] * width_scale[i + 1]])

        figs = fig.subfigures(
            1,
            ncols + (ncols - 1),
            wspace=0.0,
            hspace=0.0,
            width_ratios=width_ratios,
        )
    axs: list[Axes] = [
        f.add_subplot([0, 0, 1, 1]) for i, f in enumerate(figs) if i % 2 == 0
    ]

    return FigureLayoutColumns(fig=fig, axs=axs)
