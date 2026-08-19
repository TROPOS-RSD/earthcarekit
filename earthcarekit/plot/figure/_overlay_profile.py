from typing import Literal

import matplotlib.dates as mdates
import numpy as np
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # type: ignore
from numpy.typing import ArrayLike, NDArray

from ...color import Color, ColorLike
from ...data import Profile
from ...typing import (
    DistanceRangeLike,
    LineStyle,
    TimeRangeLike,
    ValueRangeLike,
    validate_height_range,
)
from ...utils.time import to_timestamp, validate_time_range
from ._value_range import select_value_range
from .profile import _convert_vertical_profile_to_step_function


def _get_float_tick_formatter(max_letters: int = 5, atol: float = 1e-11) -> FuncFormatter:
    n_exp = max_letters - 2

    def fmt(x, pos):
        # Ensure round zero if close
        if np.isclose(x, 0, atol=atol):
            return "0"

        # Ensure non-scientific notation for exponents in (-n_exp, n_exp)
        exp = int(np.floor(np.log10(abs(x))))
        if -n_exp <= exp <= n_exp:
            # Ensure round values if close
            if np.isclose(x, np.round(x), atol=atol):
                return str(int(np.round(x)))
            return str(np.round(x, n_exp))

        # Use scientific notation for exponents outside (-n_exp, n_exp)
        return f"{x:.0e}"

    return FuncFormatter(fmt)


def overlay_profile(
    ax: Axes,
    values: ArrayLike | Profile,
    time_range: TimeRangeLike | None = None,
    height_range: DistanceRangeLike | None = None,
    value_range: ValueRangeLike | None = None,
    height: ArrayLike | Profile | None = None,
    time: ArrayLike | Profile | None = None,
    background_color: ColorLike = "white",
    background_edgecolor: ColorLike | None = None,
    background_linewidth: float | None = None,
    background_alpha: float = 0.6,
    axis_loc: Literal["top", "bottom", "both", "none"] = "top",
    show_ticklabels: bool = True,
    show_ticks: bool = True,
    color: ColorLike = "ec:earthcare",
    linewidth: float = 2.5,
    linestyle: LineStyle = "solid",
    tick_color: ColorLike = "ec:darkred",
    tick_linewidth: float = 1.5,
    tick_linestyle: LineStyle = "dotted",
    tick_vlines: Literal["zero", "all", "none"] | bool = "zero",
    ticklabel_color: ColorLike | None = None,
    ticklabel_facecolor: ColorLike | None = None,
    ticklabel_edgecolor: ColorLike | None = None,
    ticklabel_linewidth: float = 1.5,
    ticklabel_size: float | None = None,
    ticklabel_rotation: float | None = None,
    ticklabel_boxstyle: str = "round,pad=0.3",
    ticklabel_boxalpha: float = 1.0,
    ticklabel_fontweight: str | None = None,
    log_scale: bool = False,
    show_steps: bool = True,
    **kwargs,
) -> Axes:
    """Overlays a mean vertical profile on a time/height (curtain) axes.

    Args:
        ax: Target axes for the inset profile plot.
        values: Profile values (2D array or `Profile`).
        time_range: Time range filter; uses full range if None.
        height_range: Height range filter in meters; uses full range if None.
        value_range: X-axis limits for the profile; auto-scaled if None.
        height: Height bins (1D/2D array or `Profile`); extracted from `values` if None.
        time: Time bins (1D array or `Profile`); extracted from `values` if None.
        background_color: Inset axes facecolor; defaults to "white".
        background_edgecolor: Inset axes spine color; defaults to parent axes.
        background_linewidth: Inset axes spine width; defaults to parent axes.
        background_alpha: Inset axes transparency; defaults to 0.6.
        axis_loc: Tick position ("top", "bottom", "both", "none"); defaults to "top".
        show_ticklabels: Display tick labels if True.
        show_ticks: Display ticks if True.
        color: Profile line color; defaults to "ec:earthcare".
        linewidth: Profile line width; defaults to 2.5.
        linestyle: Profile line style; defaults to "solid".
        tick_color: Tick and vline color; defaults to "ec:darkred".
        tick_linewidth: Tick and vline width; defaults to 1.5.
        tick_linestyle: Vline style; defaults to "dotted".
        tick_vlines: Vline mode ("zero", "all", "none"); True→"all", False→"none".
        ticklabel_color: Tick label text color.
        ticklabel_facecolor: Tick label box facecolor.
        ticklabel_edgecolor: Tick label box edgecolor.
        ticklabel_linewidth: Tick label box edge width.
        ticklabel_size: Tick label font size.
        ticklabel_rotation: Tick label rotation in degrees.
        ticklabel_boxstyle: Tick label box style.
        ticklabel_boxalpha: Tick label box transparency.
        ticklabel_fontweight: Tick label font weight.
        log_scale: Use logarithmic scale if True.

    Returns:
        The inset axes hosting the overlayed profile plot.
    """
    # Validate color inputs
    color = Color(color)
    background_color = Color(background_color)
    background_edgecolor = Color.from_optional(background_edgecolor)
    tick_color = Color(tick_color)
    ticklabel_color = Color.from_optional(ticklabel_color) or tick_color.blend(0.2, "black")
    ticklabel_facecolor = Color.from_optional(ticklabel_facecolor) or tick_color.blend(0.2)
    ticklabel_edgecolor = Color.from_optional(ticklabel_edgecolor) or tick_color

    # Validate profile data inputs
    _p: Profile | None = None
    _values: NDArray
    _height: NDArray | None = None
    _time: NDArray | None = None
    if isinstance(values, Profile):
        _p = values
        _values = _p.values
        _height = _p.height
        _time = _p.time
    else:
        _values = np.asarray(values)

    if height is not None:
        if isinstance(height, Profile):
            _height = height.height
        else:
            _height = np.asarray(height)

    if time is not None:
        if isinstance(time, Profile):
            _time = time.time
        else:
            _time = np.asarray(time)

    if _height is None:
        raise ValueError(
            f"{overlay_profile.__name__}() missing 1 argument: 'height' (or use a 'earthcarekit.Profile' in 'values' instead of an array-like)"
        )
    if _time is None:
        raise ValueError(
            f"{overlay_profile.__name__}() missing 1 argument: 'time' (or use a 'earthcarekit.Profile' in 'values' instead of an array-like)"
        )

    _p = Profile(values=_values, height=_height, time=_time)

    # Get mean profile within time range
    if time_range:
        time_range = validate_time_range(time_range)
        _p = _p.select_time_range(time_range)
    else:
        time_range = (to_timestamp(_p.time[0]), to_timestamp(_p.time[-1]))
    _p = _p.mean()

    # Cut mean profile to height range
    if height_range:
        height_range = validate_height_range(height_range)
        _p = _p.select_height_range(height_range)
    else:
        _height = _p.height.flatten()
        height_range = (float(_height[0]), float(_height[-1]))

    # Position overlay/inset axes
    xmin, xmax = ax.get_xlim()
    tmin = np.datetime64(mdates.num2date(xmin).replace(tzinfo=None))
    tmax = np.datetime64(mdates.num2date(xmax).replace(tzinfo=None))
    t0 = np.datetime64(time_range[0])
    t1 = np.datetime64(time_range[-1])
    left = (t0 - tmin) / (tmax - tmin)  # type: ignore
    right = (t1 - tmin) / (tmax - tmin)  # type: ignore
    width = right - left
    _ax = inset_axes(
        parent_axes=ax,
        width="100%",
        height="100%",
        bbox_to_anchor=(left, 0, width, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )

    # Set appearance of the overlay/inset axes
    _ax.patch.set_facecolor(background_color)
    _ax.patch.set_alpha(background_alpha)
    _ax.spines["top"].set_edgecolor(background_edgecolor or ax.spines["top"].get_edgecolor())
    _ax.spines["top"].set_linewidth(
        background_linewidth
        if background_linewidth is not None
        else ax.spines["top"].get_linewidth()
    )
    _ax.spines["bottom"].set_edgecolor(background_edgecolor or ax.spines["bottom"].get_edgecolor())
    _ax.spines["bottom"].set_linewidth(
        background_linewidth
        if background_linewidth is not None
        else ax.spines["bottom"].get_linewidth()
    )
    _ax.spines["left"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.xaxis.set_major_formatter(_get_float_tick_formatter())
    is_top = axis_loc in ["top", "both"]
    is_bottom = axis_loc in ["bottom", "both"]
    _ax.tick_params(
        axis="both",
        left=False,
        labelleft=False,
        right=False,
        labelright=False,
        top=is_top and show_ticks,
        labeltop=is_top and show_ticklabels,
        bottom=is_bottom and show_ticks,
        labelbottom=is_bottom and show_ticklabels,
        which="major",
        labelsize=ticklabel_size,
        direction="out",
        color=tick_color,
        labelcolor=ticklabel_color,
        rotation=ticklabel_rotation,
    )

    # Plot the profile
    x = _p.values
    y = _p.height
    if show_steps:
        x, y = _convert_vertical_profile_to_step_function(x, y)
    _ax.plot(
        x.flatten(),
        y.flatten(),
        color=color,
        linestyle=linestyle,
        linewidth=linewidth,
        **kwargs,
    )

    # Update axes limits to fit the plotted profile
    _ax.set_ylim(ax.get_ylim())
    if log_scale:
        _ax.set_xscale("log")
        # Update ticks: keep only min and max major ticks
        _ticks = _ax.xaxis.get_major_locator()()
        _xmin, _xmax = _ax.get_xlim()
        value_range = select_value_range(
            np.abs(np.concat((x, _ticks))), value_range=value_range, use_min_max=True
        )
        _ax.set_xlim(value_range)
        _xmin, _xmax = _ax.get_xlim()
        _ticks = _ticks[(_ticks >= _xmin) & (_ticks <= _xmax)]
        _new_ticks = [_ticks[0], _ticks[-1]]
        _ax.set_xticks(_new_ticks)
    else:
        value_range = select_value_range(
            np.append(x, 0.0), value_range=value_range, use_min_max=True
        )
        _ax.set_xlim(value_range)

        # Update ticks: keep only up to 3 major ticks
        _ticks = _ax.xaxis.get_major_locator()()
        _xmin, _xmax = _ax.get_xlim()
        _ticks = _ticks[(_ticks >= _xmin) & (_ticks <= _xmax)]
        # -> Keep zero tick
        _new_ticks = [0]
        # -> Keep most negative tick
        _neg_ticks = _ticks[_ticks < 0]
        if len(_neg_ticks):
            _new_ticks.insert(0, _neg_ticks[0])
        # -> Keep most positive tick
        _pos_ticks = _ticks[_ticks > 0]
        if len(_pos_ticks):
            _new_ticks.append(_pos_ticks[-1])

        # Add optional vlines per tick
        _ax.set_xticks(_new_ticks)
        if tick_vlines == "all" or tick_vlines is True:
            for x in _new_ticks:
                _ax.axvline(x, color=tick_color, linestyle=tick_linestyle, linewidth=tick_linewidth)
        elif tick_vlines == "zero":
            _ax.axvline(0, color=tick_color, linestyle=tick_linestyle, linewidth=tick_linewidth)
        elif tick_vlines != "none" and tick_vlines is not False and tick_vlines is not None:
            raise ValueError(
                f"""Invalid tick_vinles '{tick_vlines}'; expected "zero", "all" or True, "none" or False"""
            )

    # Style tick labels
    for label in _ax.get_xticklabels():
        label.set_fontweight(ticklabel_fontweight)
        label.set_bbox(
            dict(
                facecolor=ticklabel_facecolor,
                edgecolor=ticklabel_edgecolor,
                linewidth=ticklabel_linewidth,
                boxstyle=ticklabel_boxstyle,
                alpha=ticklabel_boxalpha,
            )
        )

    return _ax
