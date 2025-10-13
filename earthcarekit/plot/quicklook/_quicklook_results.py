from dataclasses import dataclass
from logging import Logger
from typing import Literal, Sequence

import numpy as np
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ...utils.time import TimestampLike
from ..figure import ECKFigure
from ..save import save_plot


@dataclass
class QuicklookFigure:
    """Container for quicklook figure results.

    Attributes:
        fig (Figure): The main figure object (`matplotlib.figure.Figure`) that contains all subfigures (`matplotlib.figure.SubFigure`).
        subfigs (list[list[ECKFigure]]):
            Nested list of earthcarekik figure objects, where each inner list groups
            subfigures belonging to a particular panel, section, or layout element.
    """

    fig: Figure
    subfigs: list[list[ECKFigure]]

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
