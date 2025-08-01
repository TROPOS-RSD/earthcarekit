from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def create_column_subfigures(
    ncols: int,
    single_figsize: tuple[float, float] = (3, 8),
    margin: float = 0.0,
) -> tuple[Figure, list[Axes]]:
    """
    Creates a figure with multiple subfigures arranged as columns in a single row, each containing one Axes.

    Args:
        ncols (int): Number of subfigures (columns) to create.
        single_figsize (tuple[float, float], optional): Size (width, height) of each individual subfigure.
            Defaults to (3, 8).

    Returns:
        tuple[Figure, list[Axes]]: The parent figure and a list of Axes objects, one for each subfigure.
    """
    fig: Figure = plt.figure(
        figsize=(single_figsize[0] * ncols + (ncols - 1) * margin, single_figsize[1])
    )
    figs: np.ndarray
    if ncols == 1:
        figs = np.array([fig])
    else:
        width_ratios = [single_figsize[0]]
        for c in range(ncols - 1):
            width_ratios.extend([margin, single_figsize[0]])

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

    return fig, axs
