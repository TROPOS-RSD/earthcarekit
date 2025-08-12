import argparse
import datetime
import sys
from argparse import RawTextHelpFormatter
from typing import Any, Sequence, Type, TypeAlias

import numpy as np
import pandas as pd

from .. import __title__, __version__
from ..utils._cli import console_exclusive_info, create_logger, log_textbox
from ._constants import PROGRAM_DESCRIPTION, PROGRAM_NAME, PROGRAM_SETUP_INSTRUCTIONS
from ._create_search_requests import create_search_request_list
from ._eo_product import EOProduct, _DownloadResult
from ._eo_search_request import EOSearchRequest
from ._parse import (
    parse_path_to_config,
    parse_path_to_data,
    parse_search_inputs,
    parse_selected_index,
)
from ._run_downloads import run_downloads
from ._run_search_requests import run_search_requets
from ._types import Entrypoint, _SearchInputs

RadiusKMFloat: TypeAlias = float
LatFloat: TypeAlias = float
LonFloat: TypeAlias = float

LatSFloat: TypeAlias = float
LonWFloat: TypeAlias = float
LatNFloat: TypeAlias = float
LonEFloat: TypeAlias = float


def ecdownload(
    file_type: str | list[str],
    product_version: str | None = None,
    orbit_number: int | list[int] | None = None,
    start_orbit_number: int | None = None,
    end_orbit_number: int | None = None,
    frame_id: str | list[str] | None = None,
    orbit_and_frame: str | list[str] | None = None,
    start_orbit_and_frame: str | None = None,
    end_orbit_and_frame: str | None = None,
    timestamps: str | list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    radius_search: tuple[RadiusKMFloat, LatFloat, LonFloat] | list | None = None,
    bounding_box: (
        tuple[LatSFloat, LonWFloat, LatNFloat, LonEFloat] | list | None
    ) = None,
    path_to_config: str | None = None,
    path_to_data: str | None = None,
    is_log: bool = False,
    is_debug: bool = False,
    is_download: bool = True,
    is_overwrite: bool = False,
    is_unzip: bool = True,
    is_delete: bool = True,
    is_create_subdirs: bool = True,
    is_export_results: bool = False,
    idx_selected_input: int | None = None,
) -> None:
    time_start_script: pd.Timestamp = pd.Timestamp(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def _to_list(input: Any, _type: Type) -> list | None:
        if isinstance(input, _type):
            return [input]
        elif isinstance(input, list):
            return input
        else:
            return None

    _file_type: list[str] | None = _to_list(file_type, str)
    assert isinstance(_file_type, list)
    file_type = _file_type

    orbit_number = _to_list(orbit_number, int)
    frame_id = _to_list(frame_id, str)
    orbit_and_frame = _to_list(orbit_and_frame, str)
    timestamps = _to_list(timestamps, str)

    if isinstance(radius_search, tuple):
        radius_search = list(radius_search)

    if isinstance(bounding_box, tuple):
        bounding_box = list(bounding_box)

    idx_selected: int | None = parse_selected_index(idx_selected_input)

    logger = create_logger(
        logger_name=PROGRAM_NAME,
        log_to_file=is_log,
        debug=is_debug,
    )

    log_textbox(
        f"EarthCARE Download Tool\n{__title__} {__version__}",
        logger=logger,
        is_mayor=True,
    )

    if logger:
        logger.info(f"# Settings")
        logger.info(f"# - {is_download=}")
        logger.info(f"# - {is_overwrite=}")
        logger.info(f"# - {is_unzip=}")
        logger.info(f"# - {is_delete=}")
        logger.info(f"# - {is_create_subdirs=}")
        logger.info(f"# - {is_log=}")
        logger.info(f"# - {is_debug=}")
        logger.info(f"# - {is_export_results=}")
        logger.info(f"# - {idx_selected_input=}")

    config = parse_path_to_config(path_to_config, logger=logger)
    path_to_data = parse_path_to_data(path_to_data, logger=logger)
    if isinstance(path_to_data, str):
        config.path_to_data = path_to_data

    if logger:
        logger.info(f"# - config_filepath=<{config.filepath}>")
        logger.info(f"# - data_dirpath=<{config.path_to_data}>")

    search_inputs: _SearchInputs = parse_search_inputs(
        product_type=file_type,
        product_version=product_version,
        orbit_number=orbit_number,
        start_orbit_number=start_orbit_number,
        end_orbit_number=end_orbit_number,
        frame_id=frame_id,
        orbit_and_frame=orbit_and_frame,
        start_orbit_and_frame=start_orbit_and_frame,
        end_orbit_and_frame=end_orbit_and_frame,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        radius_search=radius_search,
        bounding_box=bounding_box,
        logger=logger,
    )
    if config.download_backend.lower() == "maap":
        entrypoint = Entrypoint.MAAP
    else:
        entrypoint = Entrypoint.OADS

    planned_requests: list[EOSearchRequest] = create_search_request_list(
        entrypoint=entrypoint,
        search_inputs=search_inputs,
        input_user_type=None,
        candidate_coll_names_user=[c.value for c in config.collections],
        logger=logger,
    )

    found_products: list[EOProduct] = run_search_requets(
        log_heading_msg=f"STEP 1/2 - Search products",
        search_requests=planned_requests,
        is_debug=is_debug,
        is_found_files_list_to_txt=is_export_results,
        selected_index=idx_selected,
        selected_index_input=idx_selected_input,
        logger=logger,
    )

    donwload_results: list[_DownloadResult] = run_downloads(
        log_heading_msg=f"STEP 2/2 - Download products",
        products=found_products,
        config=config,
        entrypoint=entrypoint,
        is_download=is_download,
        is_overwrite=is_overwrite,
        is_unzip=is_unzip,
        is_delete=is_delete,
        is_create_subdirs=is_create_subdirs,
        logger=logger,
    )

    if logger:
        num_downloads: int = 0
        num_unzips: int = 0
        num_errors: int = 0
        size_msg: str = "<missing size_msg>"
        avg_speed_mbs: float = 0.0
        if len(donwload_results) > 0:
            num_errors = sum([not r.success for r in donwload_results])
            num_downloads = sum([r.downloaded for r in donwload_results])
            num_unzips = sum([r.unzipped for r in donwload_results])
            total_size_mb = sum([r.size_mb for r in donwload_results])
            size_msg = f"{total_size_mb:.2f} MB"
            if total_size_mb >= 1024:
                size_msg = f"{total_size_mb / 1024:.2f} GB"
            avg_speed_mbs = float(np.mean([r.speed_mbs for r in donwload_results]))

        time_end_script: pd.Timestamp = pd.Timestamp(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        execution_time: pd.Timedelta = time_end_script - time_start_script
        execution_time_str = str(execution_time).split()[-1]

        console_exclusive_info()
        _msg = [
            f"EXECUTION SUMMARY",
            "---",
            f"Time taken          {execution_time_str}",
            f"API search requests {len(planned_requests)}",
            f"Remote files found  {len(found_products)}",
            f"Files downloaded    {num_downloads} ({size_msg} at ~{avg_speed_mbs:.2f} MB/s)",
            f"Files unzipped      {num_unzips}",
            f"Errors occured      {num_errors}",
        ]
        log_textbox("\n".join(_msg), logger=logger, show_time=True)


def cli_tool_ecdownload() -> None:
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=f"{PROGRAM_DESCRIPTION}\n\n{PROGRAM_SETUP_INSTRUCTIONS}",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "product_type",
        type=str,
        nargs="*",
        help="A list of EarthCARE product names (e.g. ANOM or ATL-NOM-1B, etc.).\nYou can also specify the product version by adding a colon and the two-letter\nprocessor baseline after the name (e.g. ANOM:AD).",
    )
    parser.add_argument(
        "-d",
        "--path_to_data",
        type=str,
        default=None,
        help="The local root directory where products will be downloaded to",
    )
    parser.add_argument(
        "-o",
        "--orbit_number",
        type=int,
        nargs="*",
        default=None,
        help="A list of EarthCARE orbit numbers (e.g. 981)",
    )
    parser.add_argument(
        "-so",
        "--start_orbit_number",
        type=int,
        default=None,
        help="Start of orbit number range (e.g. 981). Can only be used in combination with option -eo.",
    )
    parser.add_argument(
        "-eo",
        "--end_orbit_number",
        type=int,
        default=None,
        help="End of orbit number range (e.g. 986). Can only be used in combination with option -so.",
    )
    parser.add_argument(
        "-f",
        "--frame_id",
        type=str,
        nargs="*",
        default=None,
        help="A EarthCARE frame ID (i.e. single letters from A to H)",
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
        "-soaf",
        "--start_orbit_and_frame",
        type=str,
        default=None,
        help="Start orbit number and frame range (e.g. 00981E). Can only be used in combination with option -eoaf. Can not be used with separate orbit and frame options -o, -so, eo and -f.",
    )
    parser.add_argument(
        "-eoaf",
        "--end_orbit_and_frame",
        type=str,
        default=None,
        help="End orbit number and frame range (e.g. 00982B). Can only be used in combination with option -soaf. Can not be used with separate orbit and frame options -o, -so, eo and -f.",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=str,
        nargs="*",
        default=None,
        help='Search for data containing a specific timestamp (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    parser.add_argument(
        "-st",
        "--start_time",
        type=str,
        default=None,
        help='Start of sensing time (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    parser.add_argument(
        "-et",
        "--end_time",
        type=str,
        default=None,
        help='End of sensing time (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    parser.add_argument(
        "-r",
        "--radius_search",
        type=float,
        nargs=3,
        default=None,
        help="Perform search around a radius around a point (e.g. 25000 51.35 12.43, i.e. <radius[m]> <latitude> <longitude>)",
    )
    parser.add_argument(
        "-pv",
        "--product_version",
        type=str,
        default="latest",
        help='Product version, i.e. the two-letter identifier of the processor baseline (e.g. AC). Defalut ist "latest"',
    )
    parser.add_argument(
        "-bbox",
        "--bounding_box",
        type=float,
        nargs=4,
        default=None,
        help="Perform search inside a bounding box (e.g. 14.9 37.7 14.99 37.78, i.e. <latS> <lonW> <latN> <lonE>)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite local data (otherwise existing local data will not be downloaded again)",
    )
    parser.add_argument(
        "--no_download", action="store_false", help="Do not download any data"
    )
    parser.add_argument(
        "--no_unzip", action="store_false", help="Do not unzip any data"
    )
    parser.add_argument(
        "--no_delete",
        action="store_false",
        help="Do not delete zip files after unzipping them",
    )
    parser.add_argument(
        "--no_subdirs",
        action="store_false",
        help="Do not create subdirs like: data_directory/data_level/product_type/year/month/day",
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
        "--no_log", action="store_false", help="Prevents generation of log files."
    )
    parser.add_argument(
        "-i",
        "--select_file_at_index",
        type=int,
        default=None,
        help="Select only one product from the found products list by index for download. You may provide a negative index to start from the last entry (e.g. -1 downloads the last file listed).",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Shows the script's version and exit",
    )
    parser.add_argument(
        "--export_results",
        action="store_true",
        help="Writes names of found files to a txt file called 'results.txt'",
    )
    args = parser.parse_args()

    if args.version:
        print(f"earthcarekit {__version__}")
        sys.exit(0)

    path_to_config = args.path_to_config
    path_to_data = args.path_to_data

    is_overwrite: bool = args.overwrite
    is_download: bool = args.no_download
    is_unzip: bool = args.no_unzip
    is_delete: bool = args.no_delete
    is_create_subdirs: bool = args.no_subdirs
    is_log: bool = args.no_log
    is_debug: bool = args.debug
    idx_selected_input: int | None = args.select_file_at_index
    idx_selected: int | None = parse_selected_index(args.select_file_at_index)
    is_export_results: bool = args.export_results

    product_type: list[str] = args.product_type
    product_version: str = args.product_version
    orbit_number: list[int] | None = args.orbit_number
    start_orbit_number: int | None = args.start_orbit_number
    end_orbit_number: int | None = args.end_orbit_number
    frame_id: list[str] | None = args.frame_id
    orbit_and_frame: list[str] | None = args.orbit_and_frame
    start_orbit_and_frame: str | None = args.start_orbit_and_frame
    end_orbit_and_frame: str | None = args.end_orbit_and_frame
    timestamps: list[str] | None = args.time
    start_time: str | None = args.start_time
    end_time: str | None = args.end_time
    radius_search: list[float] | None = args.radius_search
    bounding_box: list[float] | None = args.bounding_box

    ecdownload(
        file_type=product_type,
        product_version=product_version,
        orbit_number=orbit_number,
        start_orbit_number=start_orbit_number,
        end_orbit_number=end_orbit_number,
        frame_id=frame_id,
        orbit_and_frame=orbit_and_frame,
        start_orbit_and_frame=start_orbit_and_frame,
        end_orbit_and_frame=end_orbit_and_frame,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        radius_search=radius_search,
        bounding_box=bounding_box,
        path_to_config=path_to_config,
        path_to_data=path_to_data,
        is_log=is_log,
        is_debug=is_debug,
        is_download=is_download,
        is_overwrite=is_overwrite,
        is_unzip=is_unzip,
        is_delete=is_delete,
        is_create_subdirs=is_create_subdirs,
        is_export_results=is_export_results,
        idx_selected_input=idx_selected_input,
    )


def main() -> None:
    cli_tool_ecdownload()


if __name__ == "__main__":
    main()
