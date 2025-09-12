from typing import Any, Literal, Sequence, Type, TypeAlias

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from numpy.typing import NDArray

from ..color.color import Color, ColorLike

ClassIDInt: TypeAlias = int
ClassLabelStr: TypeAlias = str
import matplotlib.pyplot as plt


def plot_stacked_propabilities(
    ax: Axes,
    probabilities: NDArray,
    time: NDArray | None = None,
    colors: Sequence | NDArray | None = None,
    labels: Sequence | NDArray | None = None,
    zorder: int | float = 2,
    ax_label: str | None = None,
) -> None:
    x: NDArray = np.array(range(probabilities.shape[0]))
    if isinstance(time, (Sequence, np.ndarray)):
        x = np.array(time)

    ys = tuple(probabilities[:, i] for i in range(probabilities.shape[1]))
    sp = ax.stackplot(
        x,
        ys,
        colors=colors,
        linewidth=0,
        zorder=zorder,
    )
    ax.margins(0)

    colors = [Color(obj.get_facecolor()[0]).hex for obj in sp]  # type: ignore

    if labels is not None:
        ax.legend(
            labels=labels[::-1],
            labelcolor=colors[::-1],
            handles=[ax.plot([], [])[0] for _ in labels],
            handlelength=0,
            handleheight=0,
            handletextpad=0,
            bbox_to_anchor=(1, 0.5),
            fancybox=False,
            loc="center left",
            borderaxespad=0,
            frameon=False,
        )

    if isinstance(ax_label, str):
        ax.set_ylabel(ax_label)
