from typing import Literal

from matplotlib.axes import Axes
from matplotlib.text import Text


def add_title(
    ax: Axes,
    title: str,
    fontsize: str = "medium",
    loc: Literal["left", "center", "right"] | None = "center",
    **kwargs,
) -> Text:
    return ax.set_title(title, loc=loc, fontsize=fontsize, **kwargs)
