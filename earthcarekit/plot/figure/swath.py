import logging
from typing import Iterable, Literal, Self, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize
from matplotlib.offsetbox import AnchoredText
from matplotlib.typing import LineStyleType
from numpy.typing import ArrayLike, NDArray

from ...color import Color, ColorLike
from ...colormap import get_cmap
from ...constants import *
from ...constants import (
    DEFAULT_COLORBAR_WIDTH,
    FIGURE_HEIGHT_SWATH,
    FIGURE_WIDTH_SWATH,
    TIME_VAR,
)
from ...site import GroundSite
from ...swath import SwathData
from ...swath._across_track_distance import get_nadir_index
from ...typing import DistanceRangeLike, ValueRangeLike
from ...utils.time import (
    TimedeltaLike,
    TimeRangeLike,
    TimestampLike,
)
from ..annotation import add_text_product_info
from ..colorbar import add_colorbar
from ..text import format_var_label
from ._ensure_updated_msi_rgb_if_required import ensure_updated_msi_rgb_if_required
from ._figure import TimeseriesFigure
from .along_track import AlongTrackAxisStyle
from .defaults import get_default_cmap, get_default_norm

logger = logging.getLogger(__name__)


class SwathFigure(TimeseriesFigure):
    """TODO: documentation"""

    def __init__(
        self: Self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_SWATH, FIGURE_HEIGHT_SWATH),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool = True,
        grid_which: Literal["major", "minor", "both"] = "major",
        grid_axis: Literal["both", "x", "y"] = "both",
        grid_color: ColorLike | None = "#CCCCCC",
        grid_alpha: float = 1.0,
        grid_linestyle: LineStyleType = "dashed",
        grid_linewidth: float = 1.0,
        # base
        num_ticks: int = 10,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        ax_style_y: Literal[
            "from_track_distance",
            "across_track_distance",
            "pixel",
        ] = "from_track_distance",
        show_y_right: bool = False,
        show_y_left: bool = True,
        # timeseries
        colorbar_tick_scale: float | None = None,
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
            grid_which=grid_which,
            grid_axis=grid_axis,
            grid_color=grid_color,
            grid_alpha=grid_alpha,
            grid_linestyle=grid_linestyle,
            grid_linewidth=grid_linewidth,
            num_ticks=num_ticks,
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
            ax_style_y=ax_style_y,
            show_y_right=show_y_right,
            show_y_left=show_y_left,
        )

        self.colorbar_tick_scale: float | None = colorbar_tick_scale
        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None

        self.info_text: AnchoredText | None = None
        self.info_text_loc: str = "upper right"

    def _set_info_text_loc(self: Self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def plot(
        self: Self,
        swath_data: SwathData | None = None,
        *,
        values: NDArray | None = None,
        time: NDArray | None = None,
        nadir_index: int | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        # Common args for wrappers
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        from_track_range: DistanceRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        colorbar_position: str | Literal["left", "right", "top", "bottom"] = "right",
        colorbar_alignment: str | Literal["left", "center", "right"] = "center",
        colorbar_width: float = DEFAULT_COLORBAR_WIDTH,
        colorbar_spacing: float = 0.2,
        colorbar_length_ratio: float | str = "100%",
        colorbar_label_outside: bool = True,
        colorbar_ticks_outside: bool = True,
        colorbar_ticks_both: bool = False,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str = Color("white"),
        selection_highlight_alpha: float = 0.5,
        selection_max_time_margin: (TimedeltaLike | Sequence[TimedeltaLike] | None) = None,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        ax_style_y: (
            Literal["from_track_distance", "across_track_distance", "pixel"] | None
        ) = None,
        show_nadir: bool = True,
        nadir_color: ColorLike | None = "red",
        nadir_linewidth: int | float = 1.5,
        label_length: int = 25,
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

        cmap = get_cmap(cmap)
        self._set_norm(
            norm=norm,
            value_range=value_range,
            log_scale=log_scale,
            cmap=cmap,
        )

        if isinstance(swath_data, SwathData):
            values = swath_data.values
            time = swath_data.time
            nadir_index = swath_data.nadir_index
            latitude = swath_data.latitude
            longitude = swath_data.longitude
            label = swath_data.label
            units = swath_data.units
        elif (
            values is None
            or time is None
            or nadir_index is None
            or latitude is None
            or longitude is None
        ):
            raise ValueError(
                "Missing required arguments. Provide either a `SwathData` or all of `values`, `time`, `nadir_index`, `latitude` and `longitude`"
            )

        sd = SwathData(
            values=np.asarray(values),
            time=np.asarray(time),
            latitude=np.asarray(latitude),
            longitude=np.asarray(longitude),
            nadir_index=nadir_index,
            label=label,
            units=units,
        )

        tmin_original = sd.time[0]
        tmax_original = sd.time[-1]

        from_track_range = self._get_y_range(
            y=sd.from_track_distance,
            y_range=from_track_range,
        )
        self._ymin, self._ymax = from_track_range
        sd = sd.select_from_track_range(from_track_range)

        self._set_selection_max_time_margin(selection_max_time_margin)
        self._set_selection_time_range(selection_time_range)
        time_range = self._get_time_range(
            time=sd.time,
            time_range=time_range,
        )
        self._tmin, self._tmax = time_range
        sd = sd.select_time_range(time_range)

        self._ax_style_y = ax_style_y or self._ax_style_y
        if self._ax_style_y == "from_track_distance":
            ydata = sd.from_track_distance
        elif self._ax_style_y == "across_track_distance":
            ydata = sd.across_track_distance
        elif self._ax_style_y == "pixel":
            ydata = np.arange(len(sd.from_track_distance))
        ynadir = ydata[sd.nadir_index]

        if len(sd.values.shape) == 3 and sd.values.shape[2] == 3:
            mesh = self.ax.pcolormesh(
                sd.time,
                ydata,
                sd.values,
                rasterized=True,
                **kwargs,
            )
        else:
            mesh = self.ax.pcolormesh(
                sd.time,
                ydata,
                sd.values.T,
                norm=norm,
                cmap=cmap,
                rasterized=True,
                **kwargs,
            )

            if colorbar:
                cb_kwargs = dict(
                    label=format_var_label(sd.label, sd.units, label_len=label_length),
                    position=colorbar_position,
                    alignment=colorbar_alignment,
                    width=colorbar_width,
                    spacing=colorbar_spacing,
                    length_ratio=colorbar_length_ratio,
                    label_outside=colorbar_label_outside,
                    ticks_outside=colorbar_ticks_outside,
                    ticks_both=colorbar_ticks_both,
                )
                if cmap.categorical:
                    self._colorbar = add_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        cmap=cmap,
                        **cb_kwargs,  # type: ignore
                    )
                else:
                    self._colorbar = add_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        ticks=colorbar_ticks,
                        tick_labels=colorbar_tick_labels,
                        **cb_kwargs,  # type: ignore
                    )

        if show_nadir:
            nadir_color = Color.from_optional(nadir_color)
            nadir_color_shade = "white"
            if isinstance(nadir_color, Color):
                nadir_color_shade = nadir_color.get_best_bw_contrast_color()
            self.ax.axhline(
                y=ynadir,
                color=nadir_color_shade,
                linestyle="solid",
                linewidth=nadir_linewidth * 2,
                alpha=0.3,
                zorder=10,
            )
            self.ax.axhline(
                y=ynadir,
                color=Color.from_optional(nadir_color),
                linestyle="dashed",
                linewidth=nadir_linewidth,
                zorder=10,
            )

        self._set_y_axes(self._ymin, self._ymax)
        self._set_time_axes(
            tmin=self._tmin,
            tmax=self._tmax,
            time=sd.time,
            tmin_original=tmin_original,
            tmax_original=tmax_original,
            longitude=sd.longitude[:, sd.nadir_index],
            latitude=sd.latitude[:, sd.nadir_index],
            ax_style_top=ax_style_top,
            ax_style_bottom=ax_style_bottom,
        )

        self._plot_selection()
        self._plot_time_marks()

        return self

    def plot_contour(
        self: Self,
        values: NDArray,
        time: NDArray,
        latitude: NDArray,
        longitude: NDArray,
        nadir_index: int,
        label_levels: list | NDArray | None = None,
        label_format: str | None = None,
        levels: list | NDArray | None = None,
        linewidths: int | float | list | NDArray | None = 1.5,
        linestyles: str | list | NDArray | None = "solid",
        colors: Color | str | list | NDArray | None = "black",
        zorder: int | float | None = 2,
        show_labels: bool = True,
    ) -> Self:
        """Adds contour lines to the plot."""
        values = np.asarray(values)
        time = np.asarray(time)
        latitude = np.asarray(latitude)
        longitude = np.asarray(longitude)

        sd = SwathData(
            values=values,
            time=time,
            latitude=latitude,
            longitude=longitude,
            nadir_index=nadir_index,
        )

        if isinstance(colors, str):
            colors = Color.from_optional(colors)
        elif isinstance(colors, (Iterable, np.ndarray)):
            colors = [Color.from_optional(c) for c in colors]
        else:
            colors = Color.from_optional(colors)

        if self._ax_style_y == "from_track_distance":
            ydata = sd.from_track_distance
        elif self._ax_style_y == "across_track_distance":
            ydata = sd.across_track_distance
        elif self._ax_style_y == "pixel":
            ydata = np.arange(len(sd.from_track_distance))

        x = sd.time
        y = ydata
        z = sd.values.T

        if len(y.shape) == 2:
            y = y[len(y) // 2]

        cn = self.ax.contour(
            x,
            y,
            z,
            levels=levels,
            linewidths=linewidths,
            colors=colors,
            linestyles=linestyles,
            zorder=zorder,
        )

        if show_labels:
            labels: Iterable[float]
            if label_levels:
                labels = [lvl for lvl in label_levels if lvl in cn.levels]
            else:
                labels = cn.levels

            cl = self.ax.clabel(
                cn,
                labels,  # type: ignore
                inline=True,
                fmt=label_format,
                fontsize="small",
                zorder=zorder,
            )

            bold_font = font_manager.FontProperties(weight="bold")
            for text in cl:
                text.set_fontproperties(bold_font)

            for txt in cn.labelTexts:
                txt.set_rotation(0)

        return self

    def ecplot_coastline(
        self: Self,
        ds: xr.Dataset,
        var: str = "land_flag",
        *,
        time_var: str = TIME_VAR,
        lat_var: str = SWATH_LAT_VAR,
        lon_var: str = SWATH_LON_VAR,
        color: ColorLike = "#F3E490",
        linewidth: float | int = 0.5,
    ) -> Self:
        return self.plot_contour(
            values=ds[var].values,
            time=ds[time_var].values,
            latitude=ds[lat_var].values,
            longitude=ds[lon_var].values,
            nadir_index=int(ds.nadir_index.values),
            levels=[0, 1],
            colors=Color.from_optional(color),
            show_labels=False,
            linewidths=linewidth,
        )

    def ecplot(
        self: Self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        lat_var: str = SWATH_LAT_VAR,
        lon_var: str = SWATH_LON_VAR,
        track_lat_var: str = TRACK_LAT_VAR,
        track_lon_var: str = TRACK_LON_VAR,
        along_track_dim: str = ALONG_TRACK_DIM,
        site: str | GroundSite | None = None,
        radius_km: float = 100.0,
        mark_closest: bool = False,
        show_radius: bool = True,
        show_info: bool = True,
        show_info_orbit_and_frame: bool = True,
        show_info_file_type: bool = True,
        show_info_baseline: bool = True,
        info_text_orbit_and_frame: str | None = None,
        info_text_file_type: str | None = None,
        info_text_baseline: str | None = None,
        info_text_loc: str | None = None,
        # Common args for wrappers
        values: NDArray | None = None,
        time: NDArray | None = None,
        nadir_index: int | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        value_range: ValueRangeLike | Literal["default"] | None = "default",
        log_scale: bool | None = None,
        norm: Normalize | None = None,
        time_range: TimeRangeLike | None = None,
        from_track_range: DistanceRangeLike | None = None,
        label: str | None = None,
        units: str | None = None,
        cmap: str | Colormap | None = None,
        colorbar: bool = True,
        colorbar_ticks: ArrayLike | None = None,
        colorbar_tick_labels: ArrayLike | None = None,
        colorbar_position: str | Literal["left", "right", "top", "bottom"] = "right",
        colorbar_alignment: str | Literal["left", "center", "right"] = "center",
        colorbar_width: float = DEFAULT_COLORBAR_WIDTH,
        colorbar_spacing: float = 0.2,
        colorbar_length_ratio: float | str = "100%",
        colorbar_label_outside: bool = True,
        colorbar_ticks_outside: bool = True,
        colorbar_ticks_both: bool = False,
        selection_time_range: TimeRangeLike | None = None,
        selection_color: str | None = Color("ec:earthcare"),
        selection_linestyle: str | None = "dashed",
        selection_linewidth: float | int | None = 2.5,
        selection_highlight: bool = False,
        selection_highlight_inverted: bool = True,
        selection_highlight_color: str = Color("white"),
        selection_highlight_alpha: float = 0.5,
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        ax_style_y: Literal["from_track_distance", "across_track_distance", "pixel"] | None = None,
        show_nadir: bool = True,
        nadir_color: ColorLike | None = "black",
        nadir_linewidth: int | float = 1.5,
        label_length: int = 25,
        mark_time: TimestampLike | Sequence[TimestampLike] | None = None,
        mark_time_color: (str | Color | Sequence[str | Color | None] | None) = None,
        mark_time_linestyle: str | Sequence[str] = "solid",
        mark_time_linewidth: float | Sequence[float] = 2.5,
        **kwargs,
    ) -> Self:
        # Collect all common args for wrapped plot function call
        local_args = locals()
        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        del local_args["track_lat_var"]
        del local_args["track_lon_var"]
        del local_args["along_track_dim"]
        del local_args["site"]
        del local_args["radius_km"]
        del local_args["mark_closest"]
        del local_args["show_radius"]
        del local_args["show_info"]
        del local_args["show_info_orbit_and_frame"]
        del local_args["show_info_file_type"]
        del local_args["show_info_baseline"]
        del local_args["info_text_orbit_and_frame"]
        del local_args["info_text_file_type"]
        del local_args["info_text_baseline"]
        del local_args["info_text_loc"]
        # Delete kwargs to then merge it with the residual common args
        del local_args["kwargs"]
        all_args = {**local_args, **kwargs}

        if all_args["values"] is None:
            all_args["values"] = ds[var].values
        if all_args["time"] is None:
            all_args["time"] = ds[time_var].values
        if all_args["nadir_index"] is None:
            all_args["nadir_index"] = get_nadir_index(ds)
        if all_args["latitude"] is None:
            all_args["latitude"] = ds[lat_var].values
        if all_args["longitude"] is None:
            all_args["longitude"] = ds[lon_var].values

        # Set default values depending on variable name
        if label is None:
            all_args["label"] = "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
        if units is None:
            all_args["units"] = "-" if not hasattr(ds[var], "units") else ds[var].units
        if isinstance(value_range, str) and value_range == "default":
            value_range = None
            all_args["value_range"] = None
            if log_scale is None and norm is None:
                all_args["norm"] = get_default_norm(var, file_type=ds)
        if cmap is None:
            all_args["cmap"] = get_default_cmap(var, file_type=ds)

        ds = ensure_updated_msi_rgb_if_required(ds, var, time_range, time_var=time_var)

        # Handle overpass
        all_args = self._add_overpass_marks(
            all_args=all_args,
            ds=ds,
            time_var=time_var,
            lat_var=track_lat_var,
            lon_var=track_lon_var,
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
                self.ax,
                ds,
                append_to=self.info_text,
                loc=self.info_text_loc,
                show_orbit_and_frame=show_info_orbit_and_frame,
                show_file_type=show_info_file_type,
                show_baseline=show_info_baseline,
                text_orbit_and_frame=info_text_orbit_and_frame,
                text_file_type=info_text_file_type,
                text_baseline=info_text_baseline,
            )

        return self
