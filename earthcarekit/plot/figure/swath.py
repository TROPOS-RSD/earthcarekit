import logging
from typing import Iterable, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.dates import date2num
from matplotlib.figure import Figure, SubFigure
from matplotlib.offsetbox import AnchoredOffsetbox, AnchoredText
from matplotlib.text import Text
from numpy.typing import ArrayLike, NDArray

from ...utils.constants import *
from ...utils.constants import FIGURE_HEIGHT_SWATH, FIGURE_WIDTH_SWATH
from ...utils.swath_data import SwathData
from ...utils.swath_data.across_track_distance import get_nadir_index
from ...utils.time import (
    TimeRangeLike,
    TimestampLike,
    to_timestamp,
    validate_time_range,
)
from ...utils.typing import DistanceRangeLike, ValueRangeLike
from ..color import Cmap, Color, ColorLike, get_cmap
from ..save import save_plot
from ._ensure_updated_msi_rgb_if_required import ensure_updated_msi_rgb_if_required
from .along_track import AlongTrackAxisStyle, format_along_track_axis
from .annotation import add_text_product_info, format_var_label
from .axis import format_label
from .colorbar import add_colorbar
from .defaults import get_default_cmap, get_default_norm, get_default_rolling_mean
from .height_ticks import format_height_ticks

logger = logging.getLogger(__name__)


class SwathFigure:
    """TODO: documentation"""

    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (FIGURE_WIDTH_SWATH, FIGURE_HEIGHT_SWATH),
        dpi: int | None = None,
        title: str | None = None,
        ax_style_top: AlongTrackAxisStyle | str = "geo",
        ax_style_bottom: AlongTrackAxisStyle | str = "time",
        num_ticks: int = 10,
        colorbar_tick_scale: float | None = None,
        ax_style_y: Literal[
            "from_track_distance",
            "across_track_distance",
            "pixel",
        ] = "from_track_distance",
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
    ):
        figsize = (figsize[0] * fig_width_scale, figsize[1] * fig_height_scale)
        self.fig: Figure
        if isinstance(ax, Axes):
            tmp = ax.get_figure()
            if not isinstance(tmp, (Figure, SubFigure)):
                raise ValueError(f"Invalid Figure")
            self.fig = tmp  # type: ignore
            self.ax = ax
        else:
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))

        self.title = title
        if self.title:
            self.fig.suptitle(self.title)

        self.ax_top: Axes | None = None
        self.ax_right: Axes | None = None
        self.colorbar: Colorbar | None = None
        self.colorbar_tick_scale: float | None = colorbar_tick_scale
        self.selection_time_range: tuple[pd.Timestamp, pd.Timestamp] | None = None
        self.ax_style_top: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(
            ax_style_top
        )
        self.ax_style_bottom: AlongTrackAxisStyle = AlongTrackAxisStyle.from_input(
            ax_style_bottom
        )
        self.ax_style_y: Literal[
            "from_track_distance",
            "across_track_distance",
            "pixel",
        ] = ax_style_y

        self.info_text: AnchoredText | None = None
        self.info_text_loc: str = "upper right"
        self.num_ticks = num_ticks

    def _set_info_text_loc(self, info_text_loc: str | None) -> None:
        if isinstance(info_text_loc, str):
            self.info_text_loc = info_text_loc

    def plot(
        self,
        swath: SwathData | None = None,
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
        ax_style_top: AlongTrackAxisStyle | str | None = None,
        ax_style_bottom: AlongTrackAxisStyle | str | None = None,
        ax_style_y: (
            Literal["from_track_distance", "across_track_distance", "pixel"] | None
        ) = None,
        show_nadir: bool = True,
        nadir_color: ColorLike | None = "red",
        nadir_linewidth: int | float = 1.5,
        label_length: int = 25,
        **kwargs,
    ) -> "SwathFigure":
        if isinstance(value_range, Iterable):
            if len(value_range) != 2:
                raise ValueError(
                    f"invalid `value_range`: {value_range}, expecting (vmin, vmax)"
                )
        else:
            value_range = (None, None)

        cmap = get_cmap(cmap)

        if isinstance(cmap, Cmap) and cmap.categorical == True:
            norm = cmap.norm
        elif isinstance(norm, Normalize):
            if log_scale == True and not isinstance(norm, LogNorm):
                norm = LogNorm(norm.vmin, norm.vmax)
            elif log_scale == False and isinstance(norm, LogNorm):
                norm = Normalize(norm.vmin, norm.vmax)
            if value_range[0] is not None:
                norm.vmin = value_range[0]  # type: ignore
            if value_range[1] is not None:
                norm.vmax = value_range[1]  # type: ignore
        else:
            if log_scale == True:
                norm = LogNorm(value_range[0], value_range[1])  # type: ignore
            else:
                norm = Normalize(value_range[0], value_range[1])  # type: ignore

        assert isinstance(norm, Normalize)
        value_range = (norm.vmin, norm.vmax)

        if isinstance(swath, SwathData):
            values = swath.values
            time = swath.time
            nadir_index = swath.nadir_index
            latitude = swath.latitude
            longitude = swath.longitude
            label = swath.label
            units = swath.units
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

        values = np.asarray(values)
        time = np.asarray(time)
        latitude = np.asarray(latitude)
        longitude = np.asarray(longitude)

        swath_data = SwathData(
            values=values,
            time=time,
            latitude=latitude,
            longitude=longitude,
            nadir_index=nadir_index,
            label=label,
            units=units,
        )

        tmin_original = swath_data.time[0]
        tmax_original = swath_data.time[-1]

        if from_track_range is not None:
            if isinstance(from_track_range, Iterable) and len(from_track_range) == 2:
                from_track_range = list(from_track_range)
                for i in [0, -1]:
                    if from_track_range[i] is None:
                        from_track_range[i] = swath_data.across_track_distance[i]
            swath_data = swath_data.select_from_track_range(from_track_range)
        else:
            from_track_range = (
                swath_data.across_track_distance[0],
                swath_data.across_track_distance[-1],
            )

        if time_range is not None:
            if isinstance(time_range, Iterable) and len(time_range) == 2:
                time_range = list(time_range)
                for i in [0, -1]:
                    if time_range[i] is None:
                        time_range[i] = to_timestamp(swath_data.time[i])
                    else:
                        time_range[i] = to_timestamp(time_range[i])
            swath_data = swath_data.select_time_range(time_range)
        else:
            time_range = (swath_data.time[0], swath_data.time[-1])

        values = swath_data.values
        time = swath_data.time
        latitude = swath_data.latitude
        longitude = swath_data.longitude
        across_track_distance = swath_data.across_track_distance
        from_track_distance = swath_data.from_track_distance
        label = swath_data.label
        units = swath_data.units
        nadir_index = swath_data.nadir_index

        self.ax_style_y = ax_style_y or self.ax_style_y
        if self.ax_style_y == "from_track_distance":
            ydata = from_track_distance
            ylabel = "Distance from track"
        elif self.ax_style_y == "across_track_distance":
            ydata = across_track_distance
            ylabel = "Distance"
        elif self.ax_style_y == "pixel":
            ydata = np.arange(len(from_track_distance))
            ylabel = "Pixel"
        ynadir = ydata[nadir_index]

        tmin = np.datetime64(time_range[0])
        tmax = np.datetime64(time_range[1])

        if len(values.shape) == 3 and values.shape[2] == 3:
            mesh = self.ax.pcolormesh(
                time,
                ydata,
                values,
                rasterized=True,
                **kwargs,
            )
        else:
            mesh = self.ax.pcolormesh(
                time,
                ydata,
                values.T,
                norm=norm,
                cmap=cmap,
                rasterized=True,
                **kwargs,
            )

            if colorbar:
                cb_kwargs = dict(
                    label=format_var_label(label, units, label_len=label_length),
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
                    self.colorbar = add_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        cmap=cmap,
                        **cb_kwargs,  # type: ignore
                    )
                else:
                    self.colorbar = add_colorbar(
                        fig=self.fig,
                        ax=self.ax,
                        data=mesh,
                        ticks=colorbar_ticks,
                        tick_labels=colorbar_tick_labels,
                        **cb_kwargs,  # type: ignore
                    )

        if selection_time_range is not None:
            self.selection_time_range = validate_time_range(selection_time_range)

            if selection_highlight:
                if selection_highlight_inverted:
                    self.ax.axvspan(  # type: ignore
                        tmin,  # type: ignore
                        self.selection_time_range[0],  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore
                    self.ax.axvspan(  # type: ignore
                        self.selection_time_range[1],  # type: ignore
                        tmax,  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore
                else:
                    self.ax.axvspan(  # type: ignore
                        self.selection_time_range[0],  # type: ignore
                        self.selection_time_range[1],  # type: ignore
                        color=selection_highlight_color,  # type: ignore
                        alpha=selection_highlight_alpha,  # type: ignore
                    )  # type: ignore

            for t in self.selection_time_range:
                self.ax.axvline(  # type: ignore
                    x=t,  # type: ignore
                    color=selection_color,  # type: ignore
                    linestyle=selection_linestyle,  # type: ignore
                    linewidth=selection_linewidth,  # type: ignore
                )  # type: ignore

        if show_nadir:
            nadir_color = Color.from_optional(nadir_color)
            nadir_color_shade = "white"
            if isinstance(nadir_color, Color):
                nadir_color_shade = nadir_color.get_best_bw_contrast_color()
            nadir_line_shade = self.ax.axhline(
                y=ynadir,
                color=nadir_color_shade,
                linestyle="solid",
                linewidth=nadir_linewidth * 2,
                alpha=0.3,
                zorder=10,
            )
            nadir_line = self.ax.axhline(
                y=ynadir,
                color=Color.from_optional(nadir_color),
                linestyle="dashed",
                linewidth=nadir_linewidth,
                zorder=10,
            )

        self.ax.set_xlim((tmin, tmax))  # type: ignore
        # self.ax.set_ylim((hmin, hmax))

        self.ax_right = self.ax.twinx()
        self.ax_right.set_ylim(self.ax.get_ylim())

        self.ax_top = self.ax.twiny()
        self.ax_top.set_xlim(self.ax.get_xlim())

        if self.ax_style_y == "pixel":
            format_height_ticks(self.ax, label=ylabel, show_units=False)
        else:
            format_height_ticks(self.ax, label=ylabel)
        format_height_ticks(
            self.ax_right, show_tick_labels=False, show_units=False, label=""
        )

        if ax_style_top is not None:
            self.ax_style_top = AlongTrackAxisStyle.from_input(self.ax_style_top)
        if ax_style_bottom is not None:
            self.ax_style_bottom = AlongTrackAxisStyle.from_input(self.ax_style_bottom)

        format_along_track_axis(
            self.ax,
            self.ax_style_bottom,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude[:, nadir_index],
            latitude[:, nadir_index],
            num_ticks=self.num_ticks,
        )
        format_along_track_axis(
            self.ax_top,
            self.ax_style_top,
            time,
            tmin,
            tmax,
            tmin_original,
            tmax_original,
            longitude[:, nadir_index],
            latitude[:, nadir_index],
            num_ticks=self.num_ticks,
        )

        return self

    def plot_contour(
        self,
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
    ) -> "SwathFigure":
        """Adds contour lines to the plot."""
        values = np.asarray(values)
        time = np.asarray(time)
        latitude = np.asarray(latitude)
        longitude = np.asarray(longitude)

        swath_data = SwathData(
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

        values = swath_data.values
        time = swath_data.time
        latitude = swath_data.latitude
        longitude = swath_data.longitude
        across_track_distance = swath_data.across_track_distance
        from_track_distance = swath_data.from_track_distance
        # label = swath_data.label
        # units = swath_data.units
        nadir_index = swath_data.nadir_index

        if self.ax_style_y == "from_track_distance":
            ydata = from_track_distance
        elif self.ax_style_y == "across_track_distance":
            ydata = across_track_distance
        elif self.ax_style_y == "pixel":
            ydata = np.arange(len(from_track_distance))

        x = time
        y = ydata
        z = values.T

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
                labels = [l for l in label_levels if l in cn.levels]
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

            for l in cn.labelTexts:
                l.set_rotation(0)

        return self

    def ecplot_coastline(
        self,
        ds: xr.Dataset,
        var: str = "land_flag",
        *,
        time_var: str = TIME_VAR,
        lat_var: str = SWATH_LAT_VAR,
        lon_var: str = SWATH_LON_VAR,
        color: ColorLike = "#F3E490",
        linewidth: float | int = 0.5,
    ):
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
        self,
        ds: xr.Dataset,
        var: str,
        *,
        time_var: str = TIME_VAR,
        lat_var: str = SWATH_LAT_VAR,
        lon_var: str = SWATH_LON_VAR,
        values: NDArray | None = None,
        time: NDArray | None = None,
        nadir_index: int | None = None,
        latitude: NDArray | None = None,
        longitude: NDArray | None = None,
        show_info: bool = True,
        info_text_loc: str | None = None,
        # Common args for wrappers
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
        ax_style_y: Literal[
            "from_track_distance", "across_track_distance", "pixel"
        ] = "from_track_distance",
        show_nadir: bool = True,
        nadir_color: ColorLike | None = "black",
        nadir_linewidth: int | float = 1.5,
        label_length: int = 25,
        **kwargs,
    ) -> "SwathFigure":
        # Collect all common args for wrapped plot function call
        local_args = locals()
        # Delete all args specific to this wrapper function
        del local_args["self"]
        del local_args["ds"]
        del local_args["var"]
        del local_args["time_var"]
        del local_args["lat_var"]
        del local_args["lon_var"]
        del local_args["show_info"]
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
            all_args["label"] = (
                "Values" if not hasattr(ds[var], "long_name") else ds[var].long_name
            )
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

        self.plot(**all_args)

        self._set_info_text_loc(info_text_loc)
        if show_info:
            self.info_text = add_text_product_info(
                self.ax, ds, append_to=self.info_text, loc=self.info_text_loc
            )

        return self

    def to_texture(self) -> "SwathFigure":
        """Convert the figure to a texture by removing all axis ticks, labels, annotations, and text."""
        # Remove anchored text and other artist text objects
        for artist in reversed(self.ax.artists):
            if isinstance(artist, (Text, AnchoredOffsetbox)):
                artist.remove()

        # Completely remove axis ticks and labels
        self.ax.axis("off")

        if self.ax_top:
            self.ax_top.axis("off")

        if self.ax_right:
            self.ax_right.axis("off")

        # Remove white frame around figure
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        # Remove colorbar
        if self.colorbar:
            self.colorbar.remove()

        return self

    def invert_xaxis(self) -> "SwathFigure":
        """Invert the x-axis."""
        self.ax.invert_xaxis()
        if self.ax_top:
            self.ax_top.invert_xaxis()
        return self

    def invert_yaxis(self) -> "SwathFigure":
        """Invert the y-axis."""
        self.ax.invert_yaxis()
        if self.ax_right:
            self.ax_right.invert_yaxis()
        return self

    def set_colorbar_tick_scale(
        self,
        multiplier: float | None = None,
        fontsize: float | str | None = None,
    ) -> "SwathFigure":
        _cb = self.colorbar
        cb: Colorbar
        if isinstance(_cb, Colorbar):
            cb = _cb
        else:
            return self

        if fontsize is not None:
            cb.ax.tick_params(labelsize=fontsize)
            return self

        if multiplier is not None:
            _fontsize = cb.ax.yaxis.get_ticklabels()[0].get_fontsize()
            if isinstance(_fontsize, str):
                fp = font_manager.FontProperties(size=_fontsize)
                _fontsize = fp.get_size_in_points()
            cb.ax.tick_params(labelsize=_fontsize * multiplier)
        return self

    def show(self) -> None:
        import IPython
        import matplotlib.pyplot as plt
        from IPython.display import display

        if IPython.get_ipython() is not None:
            display(self.fig)
        else:
            plt.show()

    def save(
        self,
        filename: str = "",
        filepath: str | None = None,
        ds: xr.Dataset | None = None,
        ds_filepath: str | None = None,
        dpi: float | Literal["figure"] = "figure",
        orbit_and_frame: str | None = None,
        utc_timestamp: TimestampLike | None = None,
        use_utc_creation_timestamp: bool = False,
        site_name: str | None = None,
        hmax: int | float | None = None,
        radius: int | float | None = None,
        extra: str | None = None,
        transparent_outside: bool = False,
        verbose: bool = True,
        print_prefix: str = "",
        create_dirs: bool = False,
        transparent_background: bool = False,
        resolution: str | None = None,
        **kwargs,
    ) -> None:
        """
        Save a figure as an image or vector graphic to a file and optionally format the file name in a structured way using EarthCARE metadata.

        Args:
            figure (Figure | HasFigure): A figure object (`matplotlib.figure.Figure`) or objects exposing a `.fig` attribute containing a figure (e.g., `CurtainFigure`).
            filename (str, optional): The base name of the file. Can be extended based on other metadata provided. Defaults to empty string.
            filepath (str | None, optional): The path where the image is saved. Can be extended based on other metadata provided. Defaults to None.
            ds (xr.Dataset | None, optional): A EarthCARE dataset from which metadata will be taken. Defaults to None.
            ds_filepath (str | None, optional): A path to a EarthCARE product from which metadata will be taken. Defaults to None.
            pad (float, optional): Extra padding (i.e., empty space) around the image in inches. Defaults to 0.1.
            dpi (float | 'figure', optional): The resolution in dots per inch. If 'figure', use the figure's dpi value. Defaults to None.
            orbit_and_frame (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            utc_timestamp (TimestampLike | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            use_utc_creation_timestamp (bool, optional): Whether the time of image creation should be included in the file name. Defaults to False.
            site_name (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            hmax (int | float | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            radius (int | float | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            resolution (str | None, optional): Metadata used in the formatting of the file name. Defaults to None.
            extra (str | None, optional): A custom string to be included in the file name. Defaults to None.
            transparent_outside (bool, optional): Whether the area outside figures should be transparent. Defaults to False.
            verbose (bool, optional): Whether the progress of image creation should be printed to the console. Defaults to True.
            print_prefix (str, optional): A prefix string to all console messages. Defaults to "".
            create_dirs (bool, optional): Whether images should be saved in a folder structure based on provided metadata. Defaults to False.
            transparent_background (bool, optional): Whether the background inside and outside of figures should be transparent. Defaults to False.
            **kwargs (dict[str, Any]): Keyword arguments passed to wrapped function call of `matplotlib.pyplot.savefig`.
        """
        save_plot(
            fig=self.fig,
            filename=filename,
            filepath=filepath,
            ds=ds,
            ds_filepath=ds_filepath,
            dpi=dpi,
            orbit_and_frame=orbit_and_frame,
            utc_timestamp=utc_timestamp,
            use_utc_creation_timestamp=use_utc_creation_timestamp,
            site_name=site_name,
            hmax=hmax,
            radius=radius,
            extra=extra,
            transparent_outside=transparent_outside,
            verbose=verbose,
            print_prefix=print_prefix,
            create_dirs=create_dirs,
            transparent_background=transparent_background,
            resolution=resolution,
            **kwargs,
        )
