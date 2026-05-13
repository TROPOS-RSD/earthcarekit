from typing import Any, Literal, Self, cast

import matplotlib.pyplot as plt
import xarray as xr
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import LogNorm, Normalize
from matplotlib.figure import Figure, SubFigure
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerTuple
from matplotlib.typing import LineStyleType
from numpy.typing import ArrayLike

from ....color import Color, ColorLike
from ....colormap import Cmap, get_cmap
from ....typing import ValueRangeLike, validate_value_range
from ....utils.dict import update_if_not_none
from ....utils.time import (
    TimestampLike,
)
from ...colorbar import add_colorbar
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
        fig: Figure | None = None,
        figsize: tuple[float, float] = (4.0, 4.0),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] | None = None,
        show_grid: bool | None = None,
        grid_kwargs: dict[str, Any] | None = None,
        title_kwargs: dict[str, Any] | None = None,
        legend_kwargs: dict[str, Any] | None = None,
        colorbar_kwargs: dict[str, Any] | None = None,
    ):
        figsize = _validate_figsize(figsize)
        self._figsize = (figsize[0] * fig_width_scale, figsize[1] * fig_height_scale)

        if isinstance(fig, (Figure | SubFigure)):
            self._fig = fig
        elif isinstance(ax, Axes):
            _fig = ax.get_figure()
            if not isinstance(_fig, (Figure, SubFigure)):
                raise ValueError("Invalid Figure")
            self._fig = cast(Figure, _fig)
        else:
            self._fig = plt.figure(figsize=figsize, dpi=dpi)

        if isinstance(ax, Axes):
            self._ax = ax
        elif axes_rect is not None:
            self._ax = self._fig.add_axes(axes_rect)
        else:
            self._ax = self._fig.add_subplot()

        self._ax_top: Axes | None = None
        self._ax_right: Axes | None = None

        self._title = title
        if self._title:
            self._fig.suptitle(self._title, **(title_kwargs or {}))

        self._dpi = dpi
        self._colorbar: Colorbar | None = None
        self._legend: Legend | None = self._ax.get_legend()
        self._legend_handles: list = []
        self._legend_labels: list = []
        self._show_legend: bool = False

        self._grid_kwargs: dict[str, Any] = {
            "visible": show_grid or False,
            "which": "major",
            "axis": "both",
            "color": "#CCCCCC",
            "alpha": 1.0,
            "linestyle": "solid",
            "linewidth": 1.0,
        }
        if grid_kwargs:
            self._grid_kwargs.update(grid_kwargs)

        self._legend_kwargs: dict[str, Any] = {
            "loc": "upper left",
            "markerscale": 1.5,
            "frameon": True,
            "facecolor": "white",
            "edgecolor": "black",
            "framealpha": 0.8,
            "fancybox": False,
            "handlelength": 0.7,
            "handletextpad": 0.5,
            "borderaxespad": 0,
            "ncols": 8,
        }
        if legend_kwargs:
            self._legend_kwargs.update(legend_kwargs)

        self._legend_style_kwargs: dict[str, Any] = {
            "textcolor": "black",
            "textweight": "normal",
            "textshadealpha": 0.0,
            "textshadewidth": 3.0,
            "textshadecolor": "white",
            "edgewidth": 1.5,
        }

        self._colorbar_kwargs: dict[str, Any] = {}
        if colorbar_kwargs:
            self._colorbar_kwargs.update(colorbar_kwargs)

        self._norm: Normalize = Normalize()
        self._cmap_source: ScalarMappable | None = None

    @property
    def _show_grid(self) -> bool:
        return self._grid_kwargs.get("visible", False)

    @property
    def fig(self) -> Figure:
        """The underlying matplotlib figure."""
        return self._fig

    @property
    def ax(self) -> Axes:
        """The main matplotlib axis of the figure."""
        return self._ax

    @property
    def ax_top(self) -> Axes | None:
        """The top-side matplotlib x-axis, if present."""
        return self._ax_top

    @property
    def ax_right(self) -> Axes | None:
        """The right-side matplotlib y-axis, if present."""
        return self._ax_right

    @property
    def colorbar(self) -> Colorbar | None:
        """The matplotlib colorbar, if present."""
        return self._colorbar

    @property
    def legend(self) -> Legend | None:
        """The matplotlib legend, if present."""
        return self._legend

    def remove_colorbar(self) -> None:
        """Remove the colorbar from the figure, if present."""
        if self._colorbar:
            self._colorbar.remove()
            self._colorbar = None

    def remove_legend(self) -> None:
        """Remove the legend from the figure, if present."""
        if self._legend:
            self._legend.remove()
            self._legend = None

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
        **kwargs,
    ) -> Self:
        """Configure the grid lines of the main matplotlib axis."""
        update_if_not_none(
            d=self._grid_kwargs,
            updates=dict(
                visible=visible,
                which=which,
                axis=axis,
                color=Color.from_optional(color),
                alpha=alpha,
                linestyle=linestyle,
                linewidth=linewidth,
                **kwargs,
            ),
        )

        self._ax.grid(**self._grid_kwargs)

        return self

    def set_colorbar_tick_scale(
        self: Self,
        multiplier: float | None = None,
        fontsize: float | str | None = None,
    ) -> Self:
        """Configure the scale of the colorbar tick lables, if present."""
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
        """Convert the figure to a texture
        (i.e., remove all axis ticks, labels, annotations, and text).
        """
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
        """Display figure in interactive frontends (e.g., `IPython`/`jupyter` notebooks)."""
        import IPython
        from IPython.display import display

        if IPython.get_ipython() is not None:
            display(self.fig)
        else:
            plt.show()

    def set_legend(
        self: Self,
        ax: Axes | None = None,
        loc: str | None = None,
        markerscale: float | None = None,
        frameon: bool | None = None,
        facecolor: ColorLike | None = None,
        edgecolor: ColorLike | None = None,
        framealpha: float | None = None,
        fancybox: bool | None = None,
        handlelength: float | None = None,
        handletextpad: float | None = None,
        borderaxespad: float | None = None,
        ncols: int | None = None,
        edgewidth: float | None = None,
        textcolor: ColorLike | None = None,
        textweight: int | str | None = None,
        textshadealpha: float | None = None,
        textshadewidth: float | None = None,
        textshadecolor: ColorLike | None = None,
        **kwargs,
    ) -> Self:
        """Configure the legend.

        If no axis is given and a right-side axis is present (`ax_right`), the legend is attached
        to it so that it renders above all plot elements; otherwise, the main axis is used (`ax`).
        """
        self.remove_legend()

        update_if_not_none(
            d=self._legend_kwargs,
            updates=dict(
                loc=loc,
                markerscale=markerscale,
                frameon=frameon,
                facecolor=Color.from_optional(facecolor),
                edgecolor=Color.from_optional(edgecolor),
                framealpha=framealpha,
                fancybox=fancybox,
                handlelength=handlelength,
                handletextpad=handletextpad,
                borderaxespad=borderaxespad,
                ncols=ncols,
                **kwargs,
            ),
        )
        update_if_not_none(
            d=self._legend_style_kwargs,
            updates=dict(
                textcolor=Color.from_optional(textcolor),
                textweight=textweight,
                textshadealpha=textshadealpha,
                textshadewidth=textshadewidth,
                textshadecolor=Color.from_optional(textshadecolor),
                edgewidth=edgewidth,
            ),
        )

        _textcolor = self._legend_style_kwargs.get("textcolor", "black")
        _textweight = self._legend_style_kwargs.get("textweight", "normal")
        _textshadealpha = self._legend_style_kwargs.get("textshadealpha", 0.0)
        _textshadewidth = self._legend_style_kwargs.get("textshadewidth", 3.0)
        _textshadecolor = self._legend_style_kwargs.get("textshadecolor", "white")
        _edgewidth = self._legend_style_kwargs.get("edgewidth", 1.5)

        if len(self._legend_handles) > 0:
            _ax = ax or self._ax_right or self._ax
            self._legend = _ax.legend(
                self._legend_handles,
                self._legend_labels,
                **self._legend_kwargs,
                handler_map={tuple: HandlerTuple(ndivide=1)},
            )
            self._legend.get_frame().set_linewidth(_edgewidth)
            for text in self._legend.get_texts():
                text.set_color(_textcolor)
                text.set_fontweight(_textweight)

                if _textshadealpha > 0:
                    text = add_shade_to_text(
                        text,
                        alpha=_textshadealpha,
                        linewidth=_textshadewidth,
                        color=_textshadecolor,
                    )
        return self

    def show_legend(self: Self, *args, **kwargs) -> Self:
        """Configure the legend.

        Deprecated:
            Use `set_legend()` instead.
        """
        import warnings

        warnings.warn(
            "'show_legend()' is deprecated; use 'set_legend()' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_legend(*args, **kwargs)

    def set_colorbar(
        self: Self,
        fig: Figure | SubFigure | None = None,
        ax: Axes | None = None,
        data: ScalarMappable | None = None,
        label: str | None = None,
        ticks: ArrayLike | None = None,
        tick_labels: ArrayLike | None = None,
        cmap: Cmap | None = None,
        position: str | Literal["left", "right", "top", "bottom"] | None = None,
        alignment: str | Literal["left", "center", "right"] | None = None,
        width: float | None = None,
        spacing: float | None = None,
        length_ratio: float | str | None = None,
        label_outside: bool | None = None,
        ticks_outside: bool | None = None,
        ticks_both: bool | None = None,
    ) -> Self:
        update_if_not_none(
            d=self._colorbar_kwargs,
            updates=dict(
                fig=fig or self._fig,
                ax=ax or self._ax,
                data=data or self._cmap_source,
                label=label,
                ticks=ticks,
                tick_labels=tick_labels,
                cmap=None if cmap is None else get_cmap(cmap),
                position=position,
                alignment=alignment,
                width=width,
                spacing=spacing,
                length_ratio=length_ratio,
                label_outside=label_outside,
                ticks_outside=ticks_outside,
                ticks_both=ticks_both,
            ),
        )
        if all(v in self._colorbar_kwargs for v in ("fig", "ax", "data")):
            self.remove_colorbar()
            self._colorbar = add_colorbar(**self._colorbar_kwargs)

        return self

    def set_cmap(
        self: Self,
        cmap: Cmap,
    ) -> Self:
        if isinstance(self._cmap_source, ScalarMappable):
            self._cmap_source.set_cmap(get_cmap(cmap))
            self._colorbar_kwargs["cmap"] = cmap

        return self

    def save(
        self: Self,
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
        """Save a figure as an image or vector graphic to a file and optionally
        format the file name in a structured way using EarthCARE metadata.

        Args:
            figure (Figure | HasFigure):
                A figure object (`matplotlib.figure.Figure`) or objects exposing a `.fig` attribute
                containing a figure (e.g., `CurtainFigure`).
            filename (str, optional):
                The base name of the file. Can be extended based on other metadata provided.
                Defaults to empty string.
            filepath (str | None, optional):
                The path where the image is saved. Can be extended based on other metadata
                provided. Defaults to None.
            ds (xr.Dataset | None, optional):
                A EarthCARE dataset from which metadata will be taken. Defaults to None.
            ds_filepath (str | None, optional):
                A path to a EarthCARE product from which metadata will be taken. Defaults to None.
            pad (float, optional):
                Extra padding (i.e., empty space) around the image in inches. Defaults to 0.1.
            dpi (float | 'figure', optional):
                The resolution in dots per inch. If 'figure', use the figure's dpi value.
                Defaults to None.
            orbit_and_frame (str | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            utc_timestamp (TimestampLike | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            use_utc_creation_timestamp (bool, optional):
                Whether the time of image creation should be included in the file name.
                Defaults to False.
            site_name (str | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            hmax (int | float | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            radius (int | float | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            resolution (str | None, optional):
                Metadata used in the formatting of the file name. Defaults to None.
            extra (str | None, optional):
                A custom string to be included in the file name. Defaults to None.
            transparent_outside (bool, optional):
                Whether the area outside figures should be transparent. Defaults to False.
            verbose (bool, optional):
                Whether the progress of image creation should be printed to the console.
                Defaults to True.
            print_prefix (str, optional):
                A prefix string to all console messages. Defaults to "".
            create_dirs (bool, optional):
                Whether images should be saved in a folder structure based on provided metadata.
                Defaults to False.
            transparent_background (bool, optional):
                Whether the background inside and outside of figures should be transparent.
                Defaults to False.
            **kwargs (dict[str, Any]):
                Keyword arguments passed to wrapped function call of `matplotlib.pyplot.savefig`.
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
