import os
from typing import Literal, TypeAlias

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.figure import Figure

from ...utils.config import read_config
from ...utils.ground_sites import get_ground_site
from ...utils.read.product.file_info import ProductDataFrame, get_product_infos
from ...utils.time import TimestampLike, time_to_iso, to_timestamp
from ...utils.typing import HasFigure
from .save_figure_with_auto_margins import save_figure_with_auto_margins


def create_filepath(
    filename: str = "",
    filepath: str | None = None,
    ds: xr.Dataset | None = None,
    ds_filepath: str | None = None,
    orbit_and_frame: str | None = None,
    utc_timestamp: TimestampLike | None = None,
    use_utc_creation_timestamp: bool = False,
    site_name: str | None = None,
    hmax: int | float | None = None,
    radius: int | float | None = None,
    extra: str | None = None,
    create_dirs: bool = False,
    resolution: str | None = None,
) -> str:
    if not isinstance(filepath, str):
        config = read_config()
        filepath = os.path.join(config.path_to_images, filename)
    else:
        filepath = os.path.join(filepath, filename)

    df: ProductDataFrame | None = None
    if isinstance(ds, xr.Dataset):
        df = get_product_infos(ds)
    elif isinstance(ds_filepath, str):
        df = get_product_infos(ds_filepath)

    _file_type: str | None = None
    if df is not None:
        orbit_and_frame = df.orbit_and_frame[0]
        utc_timestamp = df.start_sensing_time[0]
        _file_type = df.file_type[0]

    if filepath:
        filename_components = []
        if orbit_and_frame is not None:
            filename_components.append(orbit_and_frame)

        if _file_type is not None:
            filename_components.append(_file_type)

        if utc_timestamp is not None:
            utc_timestamp = time_to_iso(utc_timestamp, format="%Y%m%dT%H%M%S")
            filename_components.append(utc_timestamp)

        if use_utc_creation_timestamp == True:
            creation_timestamp = time_to_iso(
                pd.Timestamp.now().utcnow(), format="%Y%m%dT%H%M%S"
            )
            filename_components.append(creation_timestamp)

        if site_name is not None:
            try:
                site_name = get_ground_site(site_name).name
            except ValueError as e:
                pass
            filename_components.append(f"site{site_name}")

        if radius is not None:
            radius_string = "rad" + str(int(np.round(radius))) + "m"
            filename_components.append(radius_string)

        if hmax is not None:
            hmax_string = "upto" + str(int(np.round(hmax / 1000))) + "km"
            filename_components.append(hmax_string)

        if resolution is not None:
            if resolution == "" or "high" in resolution.lower():
                filename_components.append("HiRes")
            elif "medium" in resolution.lower():
                filename_components.append("MedRes")
            elif "low" in resolution.lower():
                filename_components.append("LowRes")
            else:
                filename_components.append(resolution)

        if extra is not None:
            filename_components.append(extra)

        basename = os.path.basename(filepath)
        if len(basename) > 0 and basename[0] != ".":
            filename_components.append(basename)
        new_basename = "_".join(filename_components)

        dirname = os.path.dirname(filepath)

        if create_dirs and not os.path.exists(dirname):
            os.makedirs(dirname)

        new_filepath = os.path.join(dirname, new_basename)
        new_filepath = os.path.abspath(new_filepath)

        filepath = os.path.abspath(filepath)
        new_filepath = os.path.abspath(new_filepath)

        if os.path.isdir(new_filepath):
            new_filepath = os.path.join(new_filepath, ".png")
        return new_filepath
    else:
        raise ValueError("missing filepath inputs")


def save_plot(
    fig: Figure | HasFigure,
    filename: str = "",
    filepath: str | None = None,
    ds: xr.Dataset | None = None,
    ds_filepath: str | None = None,
    pad: float = 0.1,
    dpi: float | Literal["figure"] = "figure",
    orbit_and_frame: str | None = None,
    utc_timestamp: TimestampLike | None = None,
    use_utc_creation_timestamp: bool = False,
    site_name: str | None = None,
    hmax: int | float | None = None,
    radius: int | float | None = None,
    resolution: str | None = None,
    extra: str | None = None,
    transparent_outside: bool = False,
    verbose: bool = True,
    print_prefix: str = "",
    create_dirs: bool = False,
    transparent_background: bool = False,
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
    if not isinstance(fig, Figure):
        fig = fig.fig

    _stime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if transparent_background:
            transparent_outside = True

        new_filepath = create_filepath(
            filename,
            filepath,
            ds,
            ds_filepath,
            orbit_and_frame,
            utc_timestamp,
            use_utc_creation_timestamp,
            site_name,
            hmax,
            radius,
            extra,
            create_dirs,
            resolution,
        )

        if transparent_outside:
            fig.patch.set_alpha(0)
        if transparent_background:
            for ax in fig.get_axes():
                ax.patch.set_alpha(0)

        if verbose:
            print(f"{print_prefix}Saving plot ...", end="\r")
        save_figure_with_auto_margins(
            fig,
            new_filepath,
            pad=pad,
            dpi=dpi,
            **kwargs,
        )

        # Restore original settings
        if transparent_outside:
            fig.patch.set_alpha(1)
        if transparent_background:
            for ax in fig.get_axes():
                ax.patch.set_alpha(1)

        _etime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        _dtime: str = str(pd.Timestamp(_etime) - pd.Timestamp(_stime)).split()[-1]
        if verbose:
            print(f"{print_prefix}Plot saved (time taken {_dtime}): <{new_filepath}>")

        # raise ValueError(f"hi")
    except ValueError as e:
        if verbose:
            print(f"{print_prefix}Did not create plot since an error occured: {e}")
