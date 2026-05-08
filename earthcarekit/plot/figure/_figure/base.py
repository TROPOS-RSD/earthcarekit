from typing import Literal, Self, cast

import matplotlib.pyplot as plt
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import LogNorm, Normalize
from matplotlib.figure import Figure, SubFigure
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerTuple
from matplotlib.typing import LineStyleType

from ....color import Color, ColorLike
from ....colormap import Cmap, get_cmap
from ....typing import ValueRangeLike, validate_value_range
from ....utils.time import (
    TimestampLike,
)
from ...save import save_plot
from ...text import add_shade_to_text
from .._texture import (
    remove_arists,
    remove_axis_grid_ticks_labels,
    remove_colorbar,
    remove_legend,
    remove_white_frame_around_figure,
)
from .._validation import _validate_figsize


class BaseFigure:
    def __init__(
        self,
        ax: Axes | None = None,
        figsize: tuple[float, float] = (4.0, 4.0),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool = False,
        grid_which: Literal["major", "minor", "both"] = "major",
        grid_axis: Literal["both", "x", "y"] = "both",
        grid_color: ColorLike | None = "#CCCCCC",
        grid_alpha: float = 1.0,
        grid_linestyle: LineStyleType = "solid",
        grid_linewidth: float = 1.0,
    ):
        figsize = _validate_figsize(figsize)
        self._figsize = (figsize[0] * fig_width_scale, figsize[1] * fig_height_scale)

        if isinstance(ax, Axes):
            _fig = ax.get_figure()
            if not isinstance(_fig, (Figure, SubFigure)):
                raise ValueError("Invalid Figure")
            self._fig = cast(Figure, _fig)
            self._ax = ax
        else:
            self._fig = plt.figure(figsize=figsize, dpi=dpi)
            self._ax = self._fig.add_axes(axes_rect)

        self._ax_top: Axes | None = None
        self._ax_right: Axes | None = None

        self._title = title
        if self._title:
            self._fig.suptitle(self._title)

        self._dpi = dpi
        self._colorbar: Colorbar | None = None
        self._legend: Legend | None = self._ax.get_legend()
        self._legend_handles: list = []
        self._legend_labels: list = []

        self._show_grid: bool = show_grid
        self._grid_which: Literal["major", "minor", "both"] = grid_which
        self._grid_axis: Literal["both", "x", "y"] = grid_axis
        self._grid_color: Color | None = Color.from_optional(grid_color)
        self._grid_alpha: float = grid_alpha
        self._grid_linestyle: LineStyleType = grid_linestyle
        self._grid_linewidth: float = grid_linewidth

        self._norm: Normalize = Normalize()

    @property
    def fig(self) -> Figure:
        return self._fig

    @property
    def ax(self) -> Axes:
        return self._ax

    def _set_norm(
        self: Self,
        norm: Normalize | None = None,
        value_range: ValueRangeLike | None = None,
        log_scale: bool | None = None,
        cmap: str | Cmap | None = None,
    ) -> None:
        if cmap is not None:
            cmap = get_cmap(cmap)
            if cmap.categorical:
                norm = cmap.norm

        value_range = validate_value_range(value_range)

        if isinstance(norm, Normalize):
            if log_scale is True and not isinstance(norm, LogNorm):
                norm = LogNorm(norm.vmin, norm.vmax)
            elif log_scale is False and isinstance(norm, LogNorm):
                norm = Normalize(norm.vmin, norm.vmax)
            if value_range[0] is not None:
                norm.vmin = value_range[0]  # type: ignore
            if value_range[1] is not None:
                norm.vmax = value_range[1]  # type: ignore
        else:
            if log_scale is True:
                norm = LogNorm(value_range[0], value_range[1])  # type: ignore
            else:
                norm = Normalize(value_range[0], value_range[1])  # type: ignore

        self._norm = norm

    def set_grid(
        self: Self,
        visible: bool | None = None,
        which: Literal["major", "minor", "both"] | None = None,
        axis: Literal["both", "x", "y"] | None = None,
        color: ColorLike | None = None,
        alpha: float = 1.0,
        linestyle: LineStyleType | None = None,
        linewidth: float | None = None,
    ) -> None:
        if visible is not None:
            self._show_grid = visible
        if which is not None:
            self._grid_which = which
        if axis is not None:
            self._grid_axis = axis
        if color is not None:
            self._grid_color = Color.from_optional(color)
        if alpha is not None:
            self._grid_alpha = alpha
        if linestyle is not None:
            self._grid_linestyle = linestyle
        if linewidth is not None:
            self._grid_linewidth = float(linewidth)

        if self._show_grid:
            self._ax.grid(
                visible=self._show_grid,
                which=self._grid_which,
                axis=self._grid_axis,
                color=self._grid_color,
                alpha=self._grid_alpha,
                linestyle=self._grid_linestyle,
                linewidth=self._grid_linewidth,
            )

    def set_colorbar_tick_scale(
        self: Self,
        multiplier: float | None = None,
        fontsize: float | str | None = None,
    ) -> Self:
        if not isinstance(self._colorbar, Colorbar) or (multiplier is None and fontsize is None):
            return self

        if fontsize is None:
            ticklabels = self._colorbar.ax.yaxis.get_ticklabels()
            if len(ticklabels) == 0:
                ticklabels = self._colorbar.ax.xaxis.get_ticklabels()
            if len(ticklabels) == 0:
                return self
            fontsize = ticklabels[0].get_fontsize()

        if isinstance(fontsize, str):
            fontsize = font_manager.FontProperties(size=fontsize).get_size_in_points()

        if multiplier is not None:
            fontsize *= multiplier

        self._colorbar.ax.tick_params(labelsize=fontsize)

        return self

    def to_texture(self) -> Self:
        """Convert the figure to a texture by removing all axis ticks, labels, annotations, and text."""
        for ax in (self._ax, self._ax_top, self._ax_right):
            remove_arists(ax)
            remove_axis_grid_ticks_labels(ax)

        remove_white_frame_around_figure(self.fig)
        remove_colorbar(self._colorbar)
        remove_legend(self._legend)

        return self

    def invert_xaxis(self) -> Self:
        """Invert the x-axis."""
        self._ax.invert_xaxis()
        if self._ax_top:
            self._ax_top.invert_xaxis()
        return self

    def invert_yaxis(self) -> Self:
        """Invert the y-axis."""
        self._ax.invert_yaxis()
        if self._ax_right:
            self._ax_right.invert_yaxis()
        return self

    def show(self) -> None:
        import IPython
        from IPython.display import display

        if IPython.get_ipython() is not None:
            display(self.fig)
        else:
            plt.show()

    def show_legend(
        self: Self,
        loc: str = "upper left",
        markerscale: float = 1.5,
        frameon: bool = True,
        facecolor: ColorLike = "white",
        edgecolor: ColorLike = "black",
        framealpha: float = 0.8,
        edgewidth: float = 1.5,
        fancybox: bool = False,
        handlelength: float = 0.7,
        handletextpad: float = 0.5,
        borderaxespad: float = 0,
        ncols: int = 8,
        textcolor: ColorLike = "black",
        textweight: int | str = "normal",
        textshadealpha: float = 0.0,
        textshadewidth: float = 3.0,
        textshadecolor: ColorLike = "white",
        **kwargs,
    ) -> Self:
        facecolor = Color(facecolor)
        edgecolor = Color(edgecolor)
        textcolor = Color(textcolor)
        textshadecolor = Color(textshadecolor)

        if len(self._legend_handles) > 0:
            _ax = self._ax_right or self._ax
            self._legend = _ax.legend(
                self._legend_handles,
                self._legend_labels,
                loc=loc,
                markerscale=markerscale,
                frameon=frameon,
                facecolor=facecolor,
                edgecolor=edgecolor,
                framealpha=framealpha,
                fancybox=fancybox,
                handlelength=handlelength,
                handletextpad=handletextpad,
                borderaxespad=borderaxespad,
                ncols=ncols,
                handler_map={tuple: HandlerTuple(ndivide=1)},
                **kwargs,
            )
            self._legend.get_frame().set_linewidth(edgewidth)
            for text in self._legend.get_texts():
                text.set_color(textcolor)
                text.set_fontweight(textweight)

                if textshadealpha > 0:
                    text = add_shade_to_text(
                        text,
                        alpha=textshadealpha,
                        linewidth=textshadewidth,
                        color=textshadecolor,
                    )
        return self

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
