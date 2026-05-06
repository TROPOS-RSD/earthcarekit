from typing import Literal, Self, cast

import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure, SubFigure
from matplotlib.legend import Legend

from ....utils.time import (
    TimestampLike,
)
from ...save import save_plot
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
    ):
        figsize = _validate_figsize(figsize)
        figsize = (figsize[0] * fig_width_scale, figsize[1] * fig_height_scale)

        if isinstance(ax, Axes):
            _fig = ax.get_figure()
            if not isinstance(_fig, (Figure, SubFigure)):
                raise ValueError("Invalid Figure")
            self.fig = cast(Figure, _fig)
            self.ax = ax
        else:
            self.fig = plt.figure(figsize=figsize, dpi=dpi)
            self.ax = self.fig.add_axes(axes_rect)

        self.ax_top: Axes | None = None
        self.ax_right: Axes | None = None

        self.title = title
        if self.title:
            self.fig.suptitle(self.title)

        self.dpi = dpi
        self.colorbar: Colorbar | None = None
        self.legend: Legend | None = self.ax.get_legend()
        self._legend_handles: list = []
        self._legend_labels: list = []

    def to_texture(self) -> Self:
        """Convert the figure to a texture by removing all axis ticks, labels, annotations, and text."""
        for ax in (self.ax, self.ax_top, self.ax_right):
            remove_arists(ax)
            remove_axis_grid_ticks_labels(ax)

        remove_white_frame_around_figure(self.fig)
        remove_colorbar(self.colorbar)
        remove_legend(self.legend)

        return self

    def invert_xaxis(self) -> Self:
        """Invert the x-axis."""
        self.ax.invert_xaxis()
        if self.ax_top:
            self.ax_top.invert_xaxis()
        return self

    def invert_yaxis(self) -> Self:
        """Invert the y-axis."""
        self.ax.invert_yaxis()
        if self.ax_right:
            self.ax_right.invert_yaxis()
        return self

    def show(self) -> None:
        import IPython
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
