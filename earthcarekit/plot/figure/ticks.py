import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from numpy.typing import NDArray

from ...utils.math_utils import get_decimal_shift
from ...utils.np_array_utils import (
    get_number_range,
    ismonotonic,
    isndarray,
    lookup_value_by_number,
)
from ...utils.time import (
    TimestampLike,
    get_time_range,
    lookup_value_by_timestamp,
    to_timestamps,
)
from ...utils.validation import validate_completeness_of_args
from .axis import AxisInput, format_label, validate_axis_input


def get_nice_ticks(
    values: NDArray,
    max_ticks: int = 10,
    ax_values: NDArray | None = None,
):
    """
    Finds nice tick values based on monotonically increasing data.

    Parameters:
        values (numpy.ndarray): Monotonically increasing data array (can be non-uniform).
        max_ticks (int, optional): Maximum number of ticks to return. Defaults to 10.
        ax_values (numpy.ndarray | None, optional): Optional array of same shape as `values`
            containing data of an axis the `values` will be displayed on. If this parameter
            is given, the 'nice' or rounded label from `values` will be displayed at the
            closest index of `ax_values`.

    Returns:
        ticks (tuple[numpy.ndarray, numpy.ndarray]):
            - tick_positions: An array containing the ticks locations.
            - ticks_labels: An array containing the respective tick labels.
    """
    values = np.asarray(values)
    if ax_values is not None:
        ax_values = np.asarray(ax_values)
    ismonotonic(values, raise_error=True)

    min_val = values[0]
    max_val = values[-1]

    is_increasing = min_val < max_val
    if not is_increasing:
        values = values[::-1]
        min_val = values[0]
        max_val = values[-1]
        if isinstance(ax_values, np.ndarray):
            ax_values = ax_values[::-1]

    raw_step_size = (max_val - min_val) / max_ticks
    decimal_shift = get_decimal_shift(raw_step_size)

    values = np.array(values) * 10**decimal_shift
    min_val, max_val = values[0], values[-1]
    raw_step_size = (max_val - min_val) / max_ticks

    magnitude = 10 ** (len(str(int(np.floor(raw_step_size)))) - 1)

    for factor in [1, 2, 3, 4, 5, 10]:
        clean_step_size = factor * magnitude
        if (max_val - min_val) // clean_step_size <= max_ticks:
            break

    first_clean_tick = (
        ((min_val // clean_step_size) + 1) * clean_step_size
        if min_val % clean_step_size != 0
        else min_val
    )
    ticks = np.arange(first_clean_tick, max_val + clean_step_size, clean_step_size)
    ticks = ticks[ticks <= max_val]

    tick_positions = ticks
    if isndarray(ax_values):
        ax_values = np.array(ax_values)
        if values.shape != ax_values.shape:
            raise ValueError(
                f"Shape mismatch: the shape of 'values' is not {values.shape} is not the same as of 'ax_values' {ax_values.shape}"
            )
        tick_positions = np.array(
            [ax_values[np.searchsorted(values, tick)] for tick in ticks]
        )
    else:
        tick_positions = ticks * 10 ** (-decimal_shift)
    ticks_labels = np.array([int(t) for t in ticks]) * 10 ** (-decimal_shift)

    return tick_positions, ticks_labels


def add_ticks(
    ax: Axes,
    ax_data: NDArray,
    tick_data: NDArray,
    axis: AxisInput = "x",
    format_function=None,
    major_tick_count=10,
    minor_tick_count=5,
    fontsize=None,
    title=None,
    show_tick_labels=True,
    in_linspace=True,
    **kwargs,
) -> None:
    """Adds ticks to a given axis."""
    if not isinstance(ax, Axes):
        raise TypeError(
            f"{add_ticks.__name__}() for `ax` expected type '{Axes.__name__}' but got '{type(ax).__name__}' instead"
        )

    axis = validate_axis_input(axis)

    ax_data = np.asarray(ax_data)
    tick_data = np.asarray(tick_data)
    if isinstance(tick_data[0], TimestampLike):
        tick_data = np.asarray(to_timestamps(tick_data))

    periods = major_tick_count
    minor_periods = minor_tick_count * (major_tick_count - 1) + 1

    if format_function is None:
        if isndarray(tick_data, dtype=np.datetime64):
            format_function = lambda t: t.strftime("%Y-%m-%d\n%H:%M:%S")
        else:
            format_function = lambda x: "${:.1f}$".format(x)
    if not in_linspace:
        ax_ticks, tick_labels = get_nice_ticks(
            tick_data,
            major_tick_count,
            ax_values=ax_data,
        )
        ax_minor_ticks: list | NDArray | pd.DatetimeIndex = []
    elif isndarray(ax_data, dtype=np.datetime64):
        ax_ticks = get_time_range(ax_data[0], ax_data[-1], periods=periods)
        ticks = np.array(
            [lookup_value_by_timestamp(t, ax_data, tick_data) for t in ax_ticks]
        )
        ax_minor_ticks = get_time_range(ax_data[0], ax_data[-1], periods=minor_periods)
        tick_labels = [format_function(tl) for tl in ticks]
    else:
        ax_ticks = get_number_range(ax_data[0], ax_data[-1], periods=periods)
        ticks = np.array(
            [lookup_value_by_number(t, ax_data, tick_data) for t in ax_ticks]
        )
        ax_minor_ticks = get_number_range(
            ax_data[0], ax_data[-1], periods=minor_periods
        )
        tick_labels = [format_function(tl) for tl in ticks]

    arg_idxs = validate_completeness_of_args(
        add_ticks.__name__, ["tick_data"], [], **kwargs
    )

    for idx in arg_idxs:
        _tick_data = kwargs[f"tick_data{idx}"]
        _format_function = (
            kwargs[f"format_function{idx}"]
            if f"format_function{idx}" in kwargs
            else lambda lon: "${:.1f}$".format(lon)
        )
        if isndarray(ax_data, dtype=np.datetime64):
            ax_ticks = get_time_range(ax_data[0], ax_data[-1], periods=periods)
            _ticks = np.array(
                [lookup_value_by_timestamp(t, ax_data, _tick_data) for t in ax_ticks]
            )
        else:
            ax_ticks = get_number_range(ax_data[0], ax_data[-1], periods=periods)
            _ticks = np.array(
                [lookup_value_by_number(t, ax_data, _tick_data) for t in ax_ticks]
            )
        _tick_labels = [_format_function(tl) for tl in _ticks]
        tick_labels = [f"{l1}\n{l2}" for l1, l2 in zip(tick_labels, _tick_labels)]

    ax_set_ticks = {"x": ax.set_xticks, "y": ax.set_yticks}[axis]
    ax_set_ticks(
        ax_ticks,
        labels=tick_labels if show_tick_labels else ["" for x in tick_labels],
        fontsize=fontsize,
    )
    ax_set_ticks(ax_minor_ticks, minor=True)

    if title is not None:
        ax_set_label = {"x": ax.set_xlabel, "y": ax.set_ylabel}[axis]  # type: ignore
        ax_set_label(title)


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
            self.axis.offsetText.set_visible(False)
            self.axis.set_label_text(self.label + " " + fmt.get_offset())

    locator = ticker.MaxNLocator(nbins="auto", min_n_ticks=4, steps=[1, 2, 2.5, 5, 10])
    _axis.set_major_locator(locator)

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((-3, 3))
    _axis.set_major_formatter(formatter)
    if show_label:
        label = format_label(label, max_line_length=max_line_length)
        lo = Labeloffset(ax, label=label, axis=axis)
    else:
        _axis.set_label_text(None)  # type: ignore

    if not show_values:
        _axis.set_ticklabels([])
