import argparse
import datetime
import sys
from argparse import RawTextHelpFormatter
from logging import Logger
from typing import Any, Sequence, Type, TypeAlias

import numpy as np
import pandas as pd

from .. import __title__, __version__
from ..utils._cli import console_exclusive_info, create_logger, log_textbox
from ..utils.read.product.file_info import ProductDataFrame, get_product_infos
from ._constants import PROGRAM_DESCRIPTION, PROGRAM_NAME, PROGRAM_SETUP_INSTRUCTIONS
from ._create_search_requests import create_search_request_list
from ._eo_product import EOProduct, _DownloadResult
from ._eo_search_request import EOSearchRequest
from ._organize_data import organize_data
from ._parse import (
    parse_path_to_config,
    parse_path_to_data,
    parse_search_inputs,
    parse_selected_index,
)
from ._remove_old_logs import remove_old_logs
from ._run_downloads import run_downloads
from ._run_search_requests import run_search_requets
from ._types import Entrypoint, _SearchInputs

RadiusMetersFloat: TypeAlias = float
LatFloat: TypeAlias = float
LonFloat: TypeAlias = float

LatSFloat: TypeAlias = float
LonWFloat: TypeAlias = float
LatNFloat: TypeAlias = float
LonEFloat: TypeAlias = float


def ecdownload(
    file_type: str | list[str],
    baseline: str | None = None,
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
    radius_search: tuple[RadiusMetersFloat, LatFloat, LonFloat] | list | None = None,
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
    is_organize_data: bool = False,
    is_include_header: bool | None = None,
    is_reversed_order: bool = False,
    return_results: bool = False,
    verbose: bool = True,
) -> ProductDataFrame | None:
    """
    EarthCARE Download Tool: Search for and download EarthCARE products from a ESA data distribution platform (OADS or MAAP).

    The execution of this tool is divided into two parts:

    - First, based on provided arguments search request will be send via the OpenSearch API of the [ESA MAAP catalogue](https://catalog.maap.eo.esa.int/catalogue/).
    - Second, the resulting list of products is then downloaded from the configures download backend (OADS or MAAP). See:
        - MAAP: [portal.maap.eo.esa.int/earthcare](https://portal.maap.eo.esa.int/earthcare/)
        - OADS L1: [ec-pdgs-dissemination1.eo.esa.int](https://ec-pdgs-dissemination1.eo.esa.int/)
        - OADS L2: [ec-pdgs-dissemination2.eo.esa.int](https://ec-pdgs-dissemination2.eo.esa.int/)

    Args:
        file_type (str | list[str]): Name(s) of EarthCARE product(s) to search for (e.g., "ATL_NOM_1B", "ANOM", or "A-NOM").
            Note: Input string evaluation is not case sensitive. Also, product version may also be selected
            by adding a colon and the two-letter processor baseline after the name (e.g., "ANOM:BA").
        baseline (str | None, optional): Two-letter processor baseline used as default for all given `file_type`s (e.g., "BA").
            Note: A baseline specified in `file_type` with colon notation (e.g., "ANOM:BA") overwrites the default `baseline`.
            Defaults to None.
        orbit_number (int | list[int] | None, optional):
            Specific orbit number(s) to search for (e.g., 981 or [1000, 5000, ...]). Defaults to None.
        start_orbit_number (int | None, optional):
            The lower limit of orbit numbers to search for (e.g., 5000). Defaults to None.
        end_orbit_number (int | None, optional):
            The upper limit of orbit numbers to search for (e.g., 5003). Defaults to None.
        frame_id (str | list[str] | None, optional):
            Frame ID letter(s) to search for (i.e., letters A to H). Defaults to None.
        orbit_and_frame (str | list[str] | None, optional):
            Orbit and frame string(s) to search for (e.g., "01234F" or ["1000A", "5000C", ...]). Defaults to None.
        start_orbit_and_frame (str | None, optional):
            The lower limit of orbit and frames to search for (e.g., "05000D"). Defaults to None.
        end_orbit_and_frame (str | None, optional):
            The upper limit of orbit and frames to search for (e.g., "05003C"). Defaults to None.
        timestamps (str | list[str] | None, optional):
            Search for data containing specific timestamp(s) (e.g. "2024-07-31 13:45" or "20240731T134500Z"). Defaults to None.
        start_time (str | None, optional):
            The lower time limit for the search. Defaults to None.
        end_time (str | None, optional):
            The upper time limit for the search. Defaults to None.
        radius_search (tuple[RadiusMetersFloat, LatFloat, LonFloat] | list | None, optional):
            A tuple containing a radius (meters) and a lat/lon point to perform a geo radius search (e.g., 25000 51.35 12.43, i.e.,
            <radius[m]> <lat> <lon>). Latitudes must be provided as degrees north and longitudes as degrees east. Defaults to None.
        bounding_box (tuple[LatSFloat, LonWFloat, LatNFloat, LonEFloat]  |  list  |  None, optional):
            A tuple containing the extent for a bounding box geo search (e.g., [14.9, 37.7, 14.99, 37.78],
            i.e., <latS> <lonW> <latN> <lonE>). Latitudes must be provided as degrees north and longitudes as degrees east.
            Defaults to None.
        path_to_config (str | None, optional):
            If provided, uses given config file instead of the default config. Defaults to None.
        path_to_data (str | None, optional):
            If provided, downloads data to the given folder instead of the one defined in the config file. Defaults to None.
        is_log (bool, optional):
            If True, creates a log file in a `/log` folder inside the current working directory. Defaults to False.
        is_debug (bool, optional):
            If True, shows debug logs in the console. Defaults to False.
        is_download (bool, optional):
            If False, skips download part, but still performs search requests via the data dissemination platform API. Defaults to True.
        is_overwrite (bool, optional):
            If True, downloads and overwrites files that already exist in the data directory instead of skipping them. Defaults to False.
        is_unzip (bool, optional): If False, skips file extraction for downloaded archives. Defaults to True.
        is_delete (bool, optional):
            If True, deletes downloaded archives after extraction (i.e., does not delete non-extracted archives). Defaults to True.
        is_create_subdirs (bool, optional):
            If True, places downloaded files in a sub-directory structure according to the template defined in the config file.
            Defaults to True.
        is_export_results (bool, optional):
            If True, creates a text file in the current working directory listing all search results. Defaults to False.
        idx_selected_input (int | None, optional):
            A number matching an index in the list of found files. If provided, only this single file will be downloaded.
            Defaults to None.
        is_organize_data (bool, optional):
            If True, does not search or download any data. Defaults to False.
        is_include_header (bool | None, optional):
            If True, the full archive is downloaded containing both HDF5 data file (`.h5`) and header data file (`.HDR`).
            If False, only the data file will be downloaded, speeding up the download time.
            Defaults to None.

            !!! caution
                This option only applies to MAAP. OADS will always download the full archive.

        is_reversed_order (bool, optional):
            If True, downloads data products in reversed order (from the latest to the earliest). Defaults to False.
        return_results (bool, optional):
            If True, returns the search results as a `ProductDataFrame`. Defaults to False.
        verbose (bool, optional):
            If False, does not print logs to the console and does not create log file. Defaults to True.

    Returns:
        results (ProductDataFrame | None):
            If `return_results=False`, the function has no return (i.e., None).
            If `return_results=True`, the function returns the search results.
    """
    time_start_script: pd.Timestamp = pd.Timestamp(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    time_end_script: pd.Timestamp
    execution_time: pd.Timedelta

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

    logger: Logger | None = None
    if verbose:
        logger = create_logger(
            logger_name=PROGRAM_NAME,
            log_to_file=is_log,
            debug=is_debug,
        )
    if is_log:
        remove_old_logs(100, pd.Timedelta(days=30))

    log_textbox(
        f"EarthCARE Download Tool\n{__title__} {__version__}",
        logger=logger,
        is_mayor=True,
    )

    if logger and not is_organize_data:
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

    if logger and not is_organize_data:
        logger.info(f"# - config_filepath=<{config.filepath}>")
        logger.info(f"# - data_dirpath=<{config.path_to_data}>")

    if is_organize_data:
        if logger:
            logger.info(f"# Organizing local data ...")
        performed_moves = organize_data(
            config=config,
            logger=logger,
        )
        time_end_script = pd.Timestamp(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        execution_time = time_end_script - time_start_script
        execution_time_str = str(execution_time).split()[-1]
        if logger:
            console_exclusive_info()
        _moved = len([pm for pm in performed_moves if pm.get("status") == "success"])
        _failed = len([pm for pm in performed_moves if pm.get("status") == "error"])
        _msg = [
            f"EXECUTION SUMMARY",
            "---",
            f"Time taken          {execution_time_str}",
            f"Moved files         {_moved}",
            f"Failed moves        {_failed}",
        ]
        log_textbox("\n".join(_msg), logger=logger, show_time=True)
        return None

    if not isinstance(is_include_header, bool):
        is_include_header = config.maap_include_header_file

    search_inputs: _SearchInputs = parse_search_inputs(
        product_type=file_type,
        baseline=baseline,
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
        download_only_h5=not is_include_header,
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
        is_reversed_order=is_reversed_order,
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

        time_end_script = pd.Timestamp(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        execution_time = time_end_script - time_start_script
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

    if return_results:
        return get_product_infos([p.name for p in found_products], must_exist=False)
    return None


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
        "--path-to-data",
        type=str,
        default=None,
        help="The local root directory where products will be downloaded to",
    )
    parser.add_argument(
        "-o",
        "--orbit_number",
        "--orbit-number",
        type=int,
        nargs="*",
        default=None,
        help="A list of EarthCARE orbit numbers (e.g. 981)",
    )
    parser.add_argument(
        "-so",
        "--start_orbit_number",
        "--start-orbit-number",
        type=int,
        default=None,
        help="Start of orbit number range (e.g. 981). Can only be used in combination with option -eo.",
    )
    parser.add_argument(
        "-eo",
        "--end_orbit_number",
        "--end-orbit-number",
        type=int,
        default=None,
        help="End of orbit number range (e.g. 986). Can only be used in combination with option -so.",
    )
    parser.add_argument(
        "-f",
        "--frame_id",
        "--frame-id",
        type=str,
        nargs="*",
        default=None,
        help="A EarthCARE frame ID (i.e. single letters from A to H)",
    )
    parser.add_argument(
        "-oaf",
        "--orbit_and_frame",
        "--orbit-and-frame",
        type=str,
        nargs="*",
        default=None,
        help="A string describing the EarthCARE orbit number and frame (e.g. 00981E)",
    )
    parser.add_argument(
        "-soaf",
        "--start_orbit_and_frame",
        "--start-orbit-and-frame",
        type=str,
        default=None,
        help="Start orbit number and frame range (e.g. 00981E). Can only be used in combination with option -eoaf. Can not be used with separate orbit and frame options -o, -so, eo and -f.",
    )
    parser.add_argument(
        "-eoaf",
        "--end_orbit_and_frame",
        "--end-orbit-and-frame",
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
        "--start-time",
        type=str,
        default=None,
        help='Start of sensing time (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    parser.add_argument(
        "-et",
        "--end_time",
        "--end-time",
        type=str,
        default=None,
        help='End of sensing time (e.g. "2024-07-31 13:45" or 20240731T134500Z)',
    )
    parser.add_argument(
        "-r",
        "--radius_search",
        "--radius-search",
        type=float,
        nargs=3,
        default=None,
        help="Perform search around a radius around a point (e.g. 25000 51.35 12.43, i.e. <radius[m]> <latitude> <longitude>)",
    )
    parser.add_argument(
        "-pv",
        "--product_version",
        "--product-version",
        "--baseline",
        type=str,
        default="latest",
        help='Product version, i.e. the two-letter identifier of the processor baseline (e.g. AC). Defalut ist "latest"',
    )
    parser.add_argument(
        "-bbox",
        "--bounding_box",
        "--bounding-box",
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
        "--no_download",
        "--no-download",
        action="store_false",
        help="Do not download any data",
    )
    parser.add_argument(
        "--no_unzip",
        "--no-unzip",
        action="store_false",
        help="Do not unzip any data",
    )
    parser.add_argument(
        "--no_delete",
        "--no-delete",
        action="store_false",
        help="Do not delete zip files after unzipping them",
    )
    parser.add_argument(
        "--no_subdirs",
        "--no-subdirs",
        action="store_false",
        help="Do not create subdirs like: data_directory/data_level/product_type/year/month/day",
    )
    parser.add_argument(
        "-c",
        "--path_to_config",
        "--path-to-config",
        type=str,
        default=None,
        help="The path to an OADS credential TOML file (note: if not provided, a file named 'config.toml' is required in the script's folder)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Shows debug messages in console.",
    )
    parser.add_argument(
        "--no_log",
        "--no-log",
        action="store_false",
        help="Prevents generation of log files.",
    )
    parser.add_argument(
        "-i",
        "--select_file_at_index",
        "--select-file-at-index",
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
        "--export-results",
        action="store_true",
        help="Writes names of found files to a txt file called 'results.txt'",
    )
    parser.add_argument(
        "--organize_data",
        "--organize-data",
        action="store_true",
        help="Ensures that all EarthCARE data products under your data folder are located correctly in the subfolder structure. When this option is used, no data will be downloaded, only local data folders will be moved if necessary.",
    )
    parser.add_argument(
        "--include_header",
        "--include-header",
        action="store_true",
        help="Includes header file (.HDR) in product download when using MAAP",
    )
    parser.add_argument(
        "--exclude_header",
        "--exclude-header",
        action="store_true",
        help="Does not download header file (.HDR) but only the product's .h5-file when using MAAP",
    )
    parser.add_argument(
        "--reversed_order",
        "--reversed-order",
        action="store_true",
        help="Downloads data products in reversed order (from the latest to the earliest)",
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
    is_organize_data: bool = args.organize_data

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
    include_header: bool = args.include_header
    exclude_header: bool = args.exclude_header
    reversed_order: bool = args.reversed_order

    is_include_header: bool | None = None
    if include_header and exclude_header:
        print(
            f"You can't use options '--include_header' and '--exclude_header' together."
        )
        sys.exit(0)
    elif include_header:
        is_include_header = True
    elif exclude_header:
        is_include_header = False

    ecdownload(
        file_type=product_type,
        baseline=product_version,
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
        is_organize_data=is_organize_data,
        is_include_header=is_include_header,
        is_reversed_order=reversed_order,
    )


def main() -> None:
    cli_tool_ecdownload()


if __name__ == "__main__":
    main()
