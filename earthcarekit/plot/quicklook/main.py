import argparse
import datetime
import os
import sys
from argparse import RawTextHelpFormatter
from dataclasses import dataclass
from typing import Any, Final

import numpy as np
import pandas as pd
import xarray as xr

from ... import __title__, __version__
from ...utils import FileType, GroundSite, read_product, search_product
from ...utils._cli import (
    console_exclusive_info,
    create_logger,
    get_counter_message,
    log_textbox,
)
from ...utils._cli._parse import (
    parse_path_to_config,
    parse_path_to_data,
    parse_path_to_imgs,
    parse_search_inputs,
    parse_selected_index,
)
from ...utils._cli._parse._types import _SearchInputs
from ...utils.config import ECKConfig
from ..save import create_filepath, save_plot
from ._quicklook import ecquicklook

PROGRAM_NAME: Final[str] = "ecquicklook"
PROGRAM_DESCRIPTION: Final[str] = """description is missing"""
PROGRAM_SETUP_INSTRUCTIONS: Final[str] = """setup instructions are missing"""


def add_args_product_search(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    parser.add_argument(
        "-fp",
        "--filepath",
        type=str,
        nargs="*",
        default=None,
        help="A list of paths to EarthCARE product files (.h5 files).",
    )
    parser.add_argument(
        "-p",
        "--product_type",
        type=str,
        nargs="*",
        default=None,
        help="A list of EarthCARE product names (e.g. ANOM or ATL-NOM-1B, etc.).\nNote: You can also specify the product version by adding a colon and the two-letter\nprocessor baseline after the name (e.g. ANOM:AD).",
    )
    parser.add_argument(
        "-pv",
        "--product_version",
        type=str,
        default="latest",
        help='Product version, i.e. the two-letter identifier of the processor baseline (e.g. AC). Defaults to "latest"',
    )
    parser.add_argument(
        "-o",
        "--orbit_number",
        type=int,
        nargs="*",
        default=None,
        help="A list of EarthCARE orbit numbers (e.g. 981).\nNote: Can not be used with combined orbit and frame options -soaf and -eoaf.",
    )
    parser.add_argument(
        "-f",
        "--frame_id",
        type=str,
        nargs="*",
        default=None,
        help="A EarthCARE frame ID (i.e. single letters from A to H).\nNote: Can not be used with combined orbit and frame options -soaf and -eoaf.",
    )
    parser.add_argument(
        "-oaf",
        "--orbit_and_frame",
        type=str,
        nargs="*",
        default=None,
        help="A string describing the EarthCARE orbit number and frame (e.g. 00981E)",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=str,
        nargs="*",
        default=None,
        help='Search for data containing a specific timestamp (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    return parser


def main() -> None:
    time_start_script: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=f"{PROGRAM_DESCRIPTION}\n\n{PROGRAM_SETUP_INSTRUCTIONS}",
        formatter_class=RawTextHelpFormatter,
    )
    parser = add_args_product_search(parser)
    parser.add_argument(
        "-hmin",
        "--min_height",
        type=float,
        default=0.0,
        help="The minimum height plotted in kilometers. Defaults to 0.0",
    )
    parser.add_argument(
        "-hmax",
        "--max_height",
        type=float,
        default=30.0,
        help="The maximum height plotted in kilometers. Defaults to 30.0",
    )
    parser.add_argument(
        "-rad",
        "--site_radius",
        type=float,
        default=100.0,
        help="The radius around a ground site or geo location in kilometers. Defaults to 100.0",
    )
    parser.add_argument(
        "-geo",
        "--site_geo_location",
        type=float,
        nargs=2,
        default=None,
        help="The latitude and logitude coordniates of a ground site in degrees north and east.",
    )
    parser.add_argument(
        "-site",
        "--site_name",
        type=str,
        default=None,
        help="The name of a ground site.",
    )
    parser.add_argument(
        "-d",
        "--path_to_data",
        type=str,
        default=None,
        help="The local root directory where EarthCARE products are stored.",
    )
    parser.add_argument(
        "-img",
        "--image_directory",
        type=str,
        default=None,
        help="The local directory where producted images will be saved to.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrites local data (otherwise existing files will not be processed again).",
    )
    parser.add_argument(
        "-c",
        "--path_to_config",
        type=str,
        default=None,
        help="The path to an OADS credential TOML file (note: if not provided, a file named 'config.toml' is required in the script's folder)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Shows debug messages in console."
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Shows the tools's version and exits.",
    )
    args = parser.parse_args()

    if args.version:
        print(f"earthcarekit {__version__}")
        sys.exit(0)

    is_overwrite: bool = args.overwrite
    is_debug: bool = args.debug
    hmin: float = args.min_height * 1000.0  # km to m
    hmax: float = args.max_height * 1000.0  # km to m
    radius_km: float = args.site_radius
    site_lat: float | None = (
        None
        if not isinstance(args.site_geo_location, list)
        else args.site_geo_location[0]
    )
    site_lon: float | None = (
        None
        if not isinstance(args.site_geo_location, list)
        else args.site_geo_location[1]
    )
    site_name: str | None = args.site_name

    logger = create_logger(
        logger_name=PROGRAM_NAME,
        log_to_file=False,
        debug=is_debug,
    )

    log_textbox(
        f"EarthCARE Quicklook Tool\n{__title__} {__version__}",
        logger=logger,
        is_mayor=True,
    )

    config = parse_path_to_config(args.path_to_config, logger=logger)
    path_to_data = parse_path_to_data(args.path_to_data, logger=logger)
    if isinstance(path_to_data, str):
        config.path_to_data = path_to_data
    path_to_imgs = parse_path_to_imgs(args.image_directory, logger=logger)
    if isinstance(path_to_imgs, str):
        config.path_to_images = path_to_imgs

    logger.info(f"# Settings")
    logger.info(f"# - config_filepath=<{config.filepath}>")
    logger.info(f"# - data_directory=<{config.path_to_data}>")
    logger.info(f"# - image_directory=<{config.path_to_images}>")
    logger.info(f"# - height_range: {args.min_height} to {args.max_height} km")
    logger.info(f"# - {site_name=}")
    logger.info(f"# - {radius_km=}")
    logger.info(f"# - site_coords=({site_lat}, {site_lon})")
    logger.info(f"# - {is_debug=}")
    logger.info(f"# - {is_overwrite=}")
    console_exclusive_info()

    file_type: list[str]
    baseline: list[str]
    if args.product_type:
        search_inputs: _SearchInputs = parse_search_inputs(
            product_type=args.product_type,
            product_version=args.product_version,
            logger=logger,
        )
        file_type = [p.type for p in search_inputs.products]
        baseline = [p.version for p in search_inputs.products]
    else:
        file_type = []
        baseline = []

    df = search_product(
        root_dirpath=config.path_to_data,
        config=config,
        file_type=file_type,
        baseline=baseline,
        timestamp=args.time,
        orbit_and_frame=args.orbit_and_frame,
        orbit_number=args.orbit_number,
        frame_id=args.frame_id,
        filename=args.filepath,
    )

    num_plots: int = 0
    for i, (_, row) in enumerate(df.iterrows()):
        count_msg, _ = get_counter_message(counter=i + 1, total_count=len(df))

        logger.info(f"*{count_msg} {row['name']}")

        site: GroundSite | str | None = site_name
        _site_name: str | None = site_name
        if isinstance(site_lat, float) and isinstance(site_lon, float):
            site = GroundSite(
                latitude=site_lat,
                longitude=site_lon,
                name=site_name or "X",
                long_name=site_name or "X",
            )
            _lat_str = f"{site_lat}N" if site_lat >= 0 else f"{-site_lat}S"
            _lon_str = f"{site_lon}E" if site_lon >= 0 else f"{-site_lon}W"
            _site_name = site_name or f"{_lat_str}{_lon_str}"
            _site_name = _site_name.replace(".", "d")

        ds2: xr.Dataset | str | None = None
        if row["file_type"] == FileType.ATL_CTH_2A:
            for _bg_file_type in ["anom", "aebd"]:
                _df = search_product(
                    root_dirpath=config.path_to_data,
                    config=config,
                    file_type=_bg_file_type,
                    orbit_and_frame=row["orbit_and_frame"],
                )
                if len(_df) > 0:
                    ds2 = _df.filepath[-1]
            if ds2 is None:
                logger.info(
                    f" {count_msg} Skipping since no matching A-NOM or A-EBD frame was found to use as the curtain background"
                )
                continue

        with read_product(row["filepath"]) as ds:
            img_filepath = create_filepath(
                filename="quicklook.png",
                ds=ds,
                hmax=hmax,
                site_name=_site_name,
                radius=radius_km if site else None,
            )
            if os.path.exists(img_filepath) and not is_overwrite:
                logger.info(
                    f" {count_msg} Skipping since image already exits at <{img_filepath}>"
                )
                continue
            gl = ecquicklook(
                ds=ds,
                ds2=ds2,
                logger=logger,
                log_msg_prefix=f" {count_msg} ",
                height_range=(hmin, hmax),
                site=site,
                radius_km=radius_km,
            )
            save_plot(
                fig=gl.fig,
                filepath=img_filepath,
                verbose=True,
                print_prefix=f" {count_msg} ",
            )
            num_plots += 1

    time_end_script: str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    execution_time: pd.Timedelta = pd.Timestamp(time_end_script) - pd.Timestamp(
        time_start_script
    )
    execution_time_str = str(execution_time).split()[-1]

    console_exclusive_info()
    _msg = [
        f"EXECUTION SUMMARY",
        "---",
        f"Time taken          {execution_time_str}",
        f"Files found         {len(df)}",
        f"Quicklooks created  {num_plots}",
        # f"Errors occured      {num_errors}",
    ]
    log_textbox("\n".join(_msg), logger=logger, show_time=True)


if __name__ == "__main__":
    main()
