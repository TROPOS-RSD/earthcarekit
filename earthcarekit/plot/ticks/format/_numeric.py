import re

import matplotlib.ticker as ticker
from matplotlib.axes import Axes

from ...text import format_var_label


def format_numeric_ticks(
    ax: Axes,
    axis: str = "x",
    label: str | None = None,
    max_line_length: int | None = None,
    show_label: bool = True,
    show_values: bool = True,
) -> None:
    """Format numeric tick labels on a matplotlib axis, using scientific notation if appropriate.

    This function sets up a smart tick locator and scalar formatter for either the x- or y-axis.
    It also appends the axis offset (e.g., *10^3) to the axis label instead of displaying it separately.
    Optionally, the label can be wrapped to a maximum line length.

    Args:
        ax (plt.Axes): The matplotlib Axes object.
        axis (str, optional): The axis to format, either "x" or "y". Defaults to "x".
        label (str | None, optional): The axis label to use. If None, the current label is used.
        max_line_length (int | None, optional): Maximum line length for wrapping the label. Defaults to None.

    Returns:
        None
    """
    _axis = {"y": ax.yaxis, "x": ax.xaxis}[axis]
    if label is None:
        label = _axis.get_label().get_text()

    class Labeloffset:
        def __init__(self, ax, label="", axis="y"):
            self.axis = _axis
            self.label = label
            if self.update(None) is not None:
                ax.callbacks.connect(axis + "lim_changed", self.update)
            ax.figure.canvas.draw()
            self.update(None)

        def update(self, lim):
            fmt = self.axis.get_major_formatter()
            s = fmt.get_offset()
            s = s.replace("\u2212", "-")  # Replace unicode minus with ASCII
            math_text = re.sub(
                r"\$\\times\\mathdefault\{10\^\{([^}]*)\}\}\\mathdefault\{\}\$",
                r"$\\times$10$^{\1}$",
                s,
            )
            self.axis.offsetText.set_visible(False)
            if len(math_text) > 0:
                self.axis.set_label_text(self.label + " " + math_text)
            else:
                self.axis.set_label_text(self.label)

    locator = ticker.MaxNLocator(nbins="auto", min_n_ticks=4, steps=[1, 2, 2.5, 5, 10])
    _axis.set_major_locator(locator)

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((-3, 3))
    _axis.set_major_formatter(formatter)
    if show_label:
        label = format_var_label(label, label_len=max_line_length)
        Labeloffset(ax, label=label, axis=axis)
    else:
        _axis.set_label_text(None)  # type: ignore

    if not show_values:
        _axis.set_ticklabels([])
