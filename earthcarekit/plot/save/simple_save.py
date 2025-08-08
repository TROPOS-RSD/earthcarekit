import os
from typing import TypeAlias

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.figure import Figure

from ...utils.config import read_config
from ...utils.ground_sites import get_ground_site
from ...utils.read.product.file_info import ProductDataFrame, get_product_infos
from ...utils.time import TimestampLike, time_to_iso, to_timestamp


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
            utc_timestamp = time_to_iso(utc_timestamp, format="%Y%m%dT%H%M%SZ")
            filename_components.append(utc_timestamp)

        if use_utc_creation_timestamp == True:
            creation_timestamp = time_to_iso(
                pd.Timestamp.now().utcnow(), format="%Y%m%dT%H%M%SZ"
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
        filename_components.append(basename)

        new_basename = "_".join(filename_components)

        dirname = os.path.dirname(filepath)
        if create_dirs and not os.path.exists(dirname):
            os.makedirs(dirname)

        new_filepath = os.path.join(dirname, new_basename)
        new_filepath = os.path.abspath(new_filepath)
        return new_filepath
    else:
        raise ValueError("missing filepath inputs")


def save_plot(
    fig: Figure,
    filename: str = "",
    filepath: str | None = None,
    ds: xr.Dataset | None = None,
    ds_filepath: str | None = None,
    dpi: int | None = None,
    pad_inches: int = 0,
    orbit_and_frame: str | None = None,
    utc_timestamp: TimestampLike | None = None,
    use_utc_creation_timestamp: bool = False,
    site_name: str | None = None,
    hmax: int | float | None = None,
    radius: int | float | None = None,
    extra: str | None = None,
    transparent_outside: bool = False,
    bbox_inches: str = "tight",
    verbose: bool = True,
    print_prefix: str = "",
    create_dirs: bool = False,
    transparent_background: bool = False,
    resolution: str | None = None,
    **kwargs,
):
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
            fig.get_axes()[0].patch.set_alpha(0)
        if verbose:
            print(f"{print_prefix}Saving plot ...", end="\r")
        fig.savefig(
            new_filepath,
            bbox_inches=bbox_inches,
            dpi=dpi,
            pad_inches=pad_inches,
            **kwargs,
        )
        _etime: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        _dtime: str = str(pd.Timestamp(_etime) - pd.Timestamp(_stime)).split()[-1]
        if verbose:
            print(f"{print_prefix}Plot saved (time taken {_dtime}): <{new_filepath}>")
    except ValueError as e:
        if verbose:
            print(f"{print_prefix}Did not create plot since no filepath was provided")
