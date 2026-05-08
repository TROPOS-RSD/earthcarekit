import warnings
from typing import Any, Literal, Self, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.offsetbox import AnchoredText
from numpy.typing import NDArray

from ...color import Color, ColorLike
from ...constants import (
    ALONG_TRACK_DIM,
    FIGURE_HEIGHT_LINE,
    FIGURE_WIDTH_LINE,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
)
from ...site import GroundSite
from ...typing import ValueRangeLike
from ...utils.numpy import asarray_or_none
from ...utils.time import (
    TimedeltaLike,
    TimeRangeLike,
    TimestampLike,
)
from ..annotation import add_text_product_info
from ..text import format_var_label
from ..ticks import format_numeric_ticks
from ._figure import TimeseriesFigure
from ._plot_1d_integer_flag import plot_1d_integer_flag
from ._plot_stacked_propabilities import plot_stacked_propabilities
from .along_track import AlongTrackAxisStyle
from .defaults import get_default_norm


class LineFigure(TimeseriesFigure):
    """TODO: documentation"""

    def __init__(
        self: Self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_LINE, FIGURE_HEIGHT_LINE),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool | None = True,
        grid_kwargs: dict[str, Any] = {},
        title_kwargs: dict[str, Any] = {},
        # base
        num_ticks: int = 10,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        show_y_right: bool = False,
        show_y_left: bool = True,
        # timeseries
        show_value_left: bool = True,
        show_value_right: bool = False,
        mode: str | Literal["line", "scatter", "area"] = "line",
    ) -> None:
        super().__init__(
            ax=ax,
            figsize=figsize,
            dpi=dpi,
            title=title,
            fig_height_scale=fig_height_scale,
            fig_width_scale=fig_width_scale,
            axes_rect=axes_rect,
            show_grid=show_grid,
            grid_kwargs=grid_kwargs,
            title_kwargs=title_kwargs,
            num_ticks=num_ticks,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
            ax_style_y=None,
            show_y_right=show_y_right,
            show_y_left=show_y_left,
        )
        self.ax_right.set_yticks([])

        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None

        self.info_text: AnchoredText | None = None
        self.info_text_loc: str = "upper right"
        self.show_value_left: bool = show_value_left
        self.show_value_right: bool = show_value_right
        self.mode: str | Literal["line", "scatter", "area"] = mode

        self.tmin: np.datetime64 | None = None
        self.tmax: np.datetime64 | None = None

    def _set_info_text_loc(self: Self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def _set_axes(
        self: Self,
        tmin: np.datetime64,
        tmax: np.datetime64,
        vmin: float | None,
        vmax: float | None,
        time: NDArray,
        tmin_original: np.datetime64 | None = None,
        tmax_original: np.datetime64 | None = None,
        longitude: NDArray | None = None,
        latitude: NDArray | None = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
    ) -> Self:
        if vmin is not None and not np.isfinite(vmin):
            vmin = None
        if vmax is not None and not np.isfinite(vmax):
            vmax = None
        self.ax.set_ylim((vmin, vmax))  # type: ignore
        self.ax_right.set_ylim(self.ax.get_ylim())

        self.set_grid()

        self._set_time_axes(
            tmin=tmin,
            tmax=tmax,
            time=time,
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            longitude=longitude,
            latitude=latitude,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        return self

    def plot(
        self: Self,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        mode: str | Literal["line", "scatter", "area"] | None = None,
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        color: str | None = Color("ec:blue"),
        alpha: float = 1.0,
        linestyle: str | None = "solid",
        linewidth: float | int | None = 2.0,
        marker: str | None = "s",
        markersize: float | int | None = 2.0,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str | None = Color("white"),
        selection_highlight_alpha: float = 0.5,
        selection_max_time_margin: (TimedeltaLike | Sequence[TimedeltaLike] | None) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        classes: Sequence[int] | dict[int, str] | None = None,
        classes_kwargs: dict[str, Any] = {},
        is_prob: bool = False,
        prob_labels: list[str] | None = None,
        prob_colors: list[ColorLike] | None = None,
        zorder: int | float | None = None,
        label_length: int = 20,
        mark_time: TimestampLike | Sequence[TimestampLike] | None = None,
        mark_time_color: (str | Color | Sequence[str | Color | None] | None) = None,
        mark_time_linestyle: str | Sequence[str] = "solid",
        mark_time_linewidth: float | Sequence[float] = 2.5,
        **kwargs,
    ) -> Self:
        self._update(
            selection_color=selection_color,
            selection_linestyle=selection_linestyle,
            selection_linewidth=selection_linewidth,
            selection_highlight=selection_highlight,
            selection_highlight_inverted=selection_highlight_inverted,
            selection_highlight_color=selection_highlight_color,
            selection_highlight_alpha=selection_highlight_alpha,
            mark_time=mark_time,
            mark_time_color=mark_time_color,
            mark_time_linestyle=mark_time_linestyle,
            mark_time_linewidth=mark_time_linewidth,
        )

        _zorder: float = 2.0
        if isinstance(zorder, (int, float)):
            _zorder = float(zorder)

        if isinstance(mode, str):
            if mode in ["line", "scatter", "area"]:
                self.mode = mode
            else:
                raise ValueError(
                    f'invalid `mode` "{mode}", expected either "line", "scatter" or "area"'
                )

        values = np.asarray(values)
        time = np.asarray(time)
        latitude = asarray_or_none(latitude)
        longitude = asarray_or_none(longitude)

        # Validate inputs
        if is_prob:
            if len(values.shape) != 2:
                raise ValueError(
                    f"Since {is_prob=} values must be 2D, but has shape={values.shape}"
                )
        elif len(values.shape) != 1:
            raise ValueError(f"Since {is_prob=} values must be 1D, but has shape={values.shape}")

        tmin_original: np.datetime64 = time[0]
        tmax_original: np.datetime64 = time[-1]

        self._set_norm(
            norm=norm,
            value_range=value_range,
            log_scale=log_scale,
        )
        self._set_selection_max_time_margin(selection_max_time_margin)
        self._set_selection_time_range(selection_time_range)
        time_range = self._get_time_range(time=time, time_range=time_range)
        y_range = self._get_y_range(y=values, y_range=self.value_range)

        self._tmin, self._tmax = time_range
        self._ymin, self._ymax = y_range

        x: NDArray = time
        y: NDArray = values

        if is_prob:
            if label is None:
                label = "Probability"
            plot_stacked_propabilities(
                ax=self._ax,
                probabilities=values,
                time=time,
                labels=prob_labels,
                colors=prob_colors,
                zorder=_zorder,
                ax_label=label,
            )
            self._ymin = 0
            self._ymax = 1
        elif classes is not None:
            _yaxis_position = classes_kwargs.get("yaxis_position", "left")
            _is_left = _yaxis_position == "left"
            _label = format_var_label(label, units, label_len=label_length)

            plot_1d_integer_flag(
                ax=self._ax if _is_left else self._ax_right,
                ax2=self._ax_right if _is_left else self._ax,
                data=y,
                x=x,
                classes=classes,
                ax_label=_label,
                zorder=_zorder,
                **classes_kwargs,
            )
        else:
            color = Color.from_optional(color)
            if "line" in self.mode:
                self._ax.plot(
                    x,
                    y,
                    marker="none",
                    linewidth=linewidth,
                    linestyle=linestyle,
                    color=color,
                    alpha=alpha,
                    zorder=_zorder,
                )
            elif "scatter" in self.mode:
                self._ax.scatter(
                    x,
                    y,
                    marker=marker,
                    s=markersize,
                    color=color,
                    alpha=alpha,
                    zorder=_zorder,
                )
            elif "area" in self.mode:
                self._ax.fill_between(
                    x,
                    [0] * x.shape[0],
                    y,
                    color=color,
                    alpha=alpha,
                    zorder=zorder or 0.0,
                )
            else:
                raise ValueError(f"invalid `mode` {self.mode}")

        self._set_axes(
            tmin=self._tmin,
            tmax=self._tmax,
            vmin=self._ymin,
            vmax=self._ymax,
            time=time,
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            latitude=latitude,
            longitude=longitude,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        if not is_prob and classes is None:
            format_numeric_ticks(
                ax=self._ax,
                axis="y",
                label=format_var_label(label, units, label_len=label_length),
                max_line_length=label_length,
                show_label=self.show_value_left,
                show_values=self.show_value_left,
            )
            format_numeric_ticks(
                ax=self._ax_right,
                axis="y",
                label=format_var_label(label, units, label_len=label_length),
                max_line_length=label_length,
                show_label=self.show_value_right,
                show_values=self.show_value_right,
            )

        self._plot_selection()
        self._plot_time_marks()

        return self

    def ecplot(
        self: Self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        mark_closest: bool = False,
        show_radius: bool = True,
        show_info: bool = True,
        info_text_loc: str | None = None,
        # Common args for wrappers
        values: NDArray | None = None,
        time: NDArray | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        mode: str | Literal["line", "scatter", "area"] | None = None,
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        color: str | None = Color("ec:blue"),
        alpha: float = 1.0,
        linestyle: str | None = "solid",
        linewidth: float | int | None = 2.0,
        marker: str | None = "s",
        markersize: float | int | None = 2.0,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str | None = Color("white"),
        selection_highlight_alpha: float = 0.5,
        selection_max_time_margin: (TimedeltaLike | Sequence[TimedeltaLike] | None) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        mark_time: Sequence[TimestampLike] | None = None,
        classes: Sequence[int] | dict[int, str] | None = None,
        classes_kwargs: dict[str, Any] = {},
        is_prob: bool = False,
        prob_labels: list[str] | None = None,
        prob_colors: list[ColorLike] | None = None,
        zorder: int | float | None = None,
        label_length: int = 20,
        **kwargs,
    ) -> Self:
        # Collect all common args for wrapped plot function call
        local_args = locals()

        # Handle deprecated arguments
        def _get_depr_arg(old_name: str, new_name: str) -> Any:
            if old_name in kwargs:
                msg = f"'{old_name}' is deprecated and will be removed in future versions; use '{new_name}' instead."
                warnings.warn(msg, FutureWarning, stacklevel=2)
                out = kwargs.get(old_name, local_args[new_name])
                del kwargs[old_name]
                return out
            return local_args[new_name]

        mark_closest = _get_depr_arg("mark_closest_profile", "mark_closest")
        kwargs["mark_time"] = _get_depr_arg("mark_profiles_at", "mark_time")

        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        del local_args["along_track_dim"]
        del local_args["site"]
        del local_args["radius_km"]
        del local_args["show_info"]
        del local_args["info_text_loc"]
        del local_args["mark_closest"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        if all_args["values"] is None:
            all_args["values"] = ds[var].values
        if all_args["time"] is None:
            all_args["time"] = ds[time_var].values
        if all_args["latitude"] is None:
            all_args["latitude"] = ds[lat_var].values
        if all_args["longitude"] is None:
            all_args["longitude"] = ds[lon_var].values

        # Set default values depending on variable name
        if label is None:
            all_args["label"] = "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
        if units is None:
            all_args["units"] = "-" if not hasattr(ds[var], "units") else ds[var].units
        if classes is not None and len(classes) > 0:
            all_args["value_range"] = (-0.5, len(classes) - 0.5)
        elif value_range is None and log_scale is None and norm is None:
            all_args["norm"] = get_default_norm(var, file_type=ds)

        # Handle overpass
        all_args = self._add_overpass_marks(
            all_args=all_args,
            ds=ds,
            time_var=time_var,
            lat_var=lat_var,
            lon_var=lon_var,
            along_track_dim=along_track_dim,
            site=site,
            radius_km=radius_km,
            mark_closest=mark_closest,
            show_radius=show_radius,
        )

        self.plot(**all_args)

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self._ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self
