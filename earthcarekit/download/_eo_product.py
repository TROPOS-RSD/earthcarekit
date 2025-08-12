import os
import shutil
import time
import urllib.parse as urlp
from dataclasses import dataclass, field
from logging import Logger
from typing import Final

import pandas as pd
import requests
import requests.cookies

from ..utils import get_product_info
from ..utils._cli import console_exclusive_info, get_counter_message
from ._auth_oads import get_oads_authentification_cookies
from ._eo_collection import EOCollection
from ._eo_parameters import STACQueryParameter, get_available_parameters
from ._request import get_request_json, validate_request_response
from ._unzip import unzip_file

SUBDIR_NAME_AUX_FILES: Final[str] = "auxiliary_files"
SUBDIR_NAME_ORB_FILES: Final[str] = "orbit_files"
SUBDIR_NAME_L0__FILES: Final[str] = "level0"
SUBDIR_NAME_L1B_FILES: Final[str] = "level1b"
SUBDIR_NAME_L1C_FILES: Final[str] = "level1c"
SUBDIR_NAME_L2A_FILES: Final[str] = "level2a"
SUBDIR_NAME_L2B_FILES: Final[str] = "level2b"
MAX_DOWNLOAD_ATTEMPTS_PER_FILE: Final[int] = 3


def ensure_single_zip_extension(filename):
    """Returns given file name with a single .ZIP extension (e.g. 'file.ZIP.zip' -> 'file.ZIP')."""
    base_name, ext = os.path.splitext(filename)
    while ext.lower() == ".zip":
        base_name, ext = os.path.splitext(base_name)
    return base_name + ".ZIP"


def get_product_sub_dirname(product_name: str) -> str:
    """Returns level subfolder name of given product name."""
    if product_name in ["AUX_JSG_1D", "AUX_MET_1D"]:
        sub_dirname = SUBDIR_NAME_AUX_FILES
    elif product_name in ["MPL_ORBSCT", "AUX_ORBPRE", "AUX_ORBRES"]:
        sub_dirname = SUBDIR_NAME_ORB_FILES
    elif "0" in product_name.lower():
        sub_dirname = SUBDIR_NAME_L0__FILES
    elif "1b" in product_name.lower():
        sub_dirname = SUBDIR_NAME_L1B_FILES
    elif "1c" in product_name.lower():
        sub_dirname = SUBDIR_NAME_L1C_FILES
    elif "2a" in product_name.lower():
        sub_dirname = SUBDIR_NAME_L2A_FILES
    elif "2b" in product_name.lower():
        sub_dirname = SUBDIR_NAME_L2B_FILES
    return sub_dirname


def get_local_product_dirpath(dirpath_local, filename, create_subdirs=True):
    """Creates local path to file."""
    if create_subdirs:
        product_info = get_product_info(filename, must_exist=False)

        product_name = product_info.file_type.value
        year = str(product_info.start_sensing_time.year).zfill(4)
        month = str(product_info.start_sensing_time.month).zfill(2)
        day = str(product_info.start_sensing_time.day).zfill(2)

        sub_dirname = get_product_sub_dirname(product_name)
        product_dirpath_local = os.path.join(
            dirpath_local, sub_dirname, product_name, year, month, day
        )
    else:
        product_dirpath_local = dirpath_local
    return product_dirpath_local


@dataclass
class _DownloadResult:
    success: bool
    downloaded: bool
    unzipped: bool
    size_mb: float
    speed_mbs: float
    time: pd.Timedelta
    filepath: str


@dataclass(order=True)
class EOProduct:
    sort_index: tuple = field(init=False, repr=False)

    name: str
    server: str
    orbit_and_frame: str
    file_type: str
    version: str
    start_processing_time: pd.Timestamp
    url_download: str
    url_quicklook: str | None
    size: int | None

    def __post_init__(self):
        self.sort_index = (
            self.server,
            self.orbit_and_frame,
            self.start_processing_time,
        )

    def download(
        self,
        download_directory: str,
        is_overwrite: bool,
        is_unzip: bool,
        is_delete: bool,
        is_create_subdirs: bool,
        maap_token: str | None = None,
        oads_username: str | None = None,
        oads_password: str | None = None,
        oads_cookies_saml: requests.cookies.RequestsCookieJar | None = None,
        proxies: dict = {},
        counter: int | None = None,
        total_count: int | None = None,
        attempts: int = 3,
        chunk_size_bytes: int = 256 * 1024,
        logger: Logger | None = None,
    ) -> _DownloadResult:
        headers_maap: dict[str, str] | None = None
        if "maap" in self.url_download:
            if isinstance(maap_token, str):
                headers_maap = {"Authorization": "Bearer " + maap_token}
            else:
                raise ValueError(f"Download failed due to missing maap token")
        else:
            if not isinstance(oads_cookies_saml, requests.cookies.RequestsCookieJar):
                if not isinstance(oads_username, str) or not isinstance(
                    oads_password, str
                ):
                    raise ValueError(
                        f"Download failed due to missing oads username or password"
                    )
                oads_cookies_saml = get_oads_authentification_cookies(
                    dissemination_server=self.server,
                    username=oads_username,
                    password=oads_password,
                )

        _downloaded: bool = False
        _unzipped: bool = False
        _size_mb: float = 0.0
        _speed_mbs: float = 0.0
        _time: pd.Timedelta = pd.Timedelta(0.0)
        _filepath: str = "none"

        count_msg, _ = get_counter_message(counter=counter, total_count=total_count)

        _success: bool = True

        # Extracting the filename from the download link
        product_info = get_product_info(self.url_download, must_exist=False)
        file_name: str = product_info.name
        product_dirpath = get_local_product_dirpath(
            download_directory, file_name, create_subdirs=is_create_subdirs
        )

        # Make sure the local download_directory exists (if not create it)
        if not os.path.exists(product_dirpath):
            os.makedirs(product_dirpath)

        # Some files may be missing zip file extension so we need to fix them
        file_name = ensure_single_zip_extension(file_name)
        zip_file_path = os.path.join(product_dirpath, file_name)
        file_path = zip_file_path[0:-4]

        file_download_url = self.url_download

        for attempt in range(attempts):
            if attempt > 0:
                if logger:
                    logger.info(
                        f" {count_msg} Restarting (starting try {attempt + 1} of max. {MAX_DOWNLOAD_ATTEMPTS_PER_FILE})."
                    )

            # Check existing files
            zip_file_exists = os.path.exists(zip_file_path)
            file_exists = os.path.exists(file_path)

            # Decide if file will be downloaded and extracted
            try_download = is_overwrite or (not zip_file_exists and not file_exists)
            try_unzip = is_unzip and (is_overwrite or not file_exists)

            if not try_download:
                if is_unzip:
                    if logger:
                        logger.info(f" {count_msg} Skip file download.")
                else:
                    if logger:
                        logger.info(
                            f" {count_msg} Skip file download. (see <{zip_file_path}>)"
                        )
            if not try_unzip:
                if logger:
                    logger.info(f" {count_msg} Skip file unzip. (see <{file_path}>)")
            if not try_download and not try_unzip:
                break

            # Delete unnessecary zip files
            if is_delete and file_exists and zip_file_exists:
                os.remove(zip_file_path)
                zip_file_exists = False

            # Overwrite files
            if zip_file_exists and is_overwrite:
                os.remove(zip_file_path)
                zip_file_exists = False
            if file_exists and is_overwrite:
                shutil.rmtree(file_path)
                # os.remove(file_path)
                file_exists = False

            # Download zip file
            if try_download:
                try:
                    # Requesting the product download
                    if logger:
                        logger.debug(f" {count_msg} Requesting: {file_download_url}")

                    file_download_response: requests.Response
                    if headers_maap:
                        file_download_response = requests.get(
                            file_download_url,
                            headers=headers_maap,
                            stream=True,
                        )
                    else:
                        file_download_response = requests.get(
                            file_download_url,
                            cookies=oads_cookies_saml,
                            proxies=proxies,
                            stream=True,
                        )
                    validate_request_response(file_download_response, logger=logger)

                    with open(zip_file_path, "wb") as f:
                        total_length_str = file_download_response.headers.get(
                            "content-length"
                        )
                        if isinstance(total_length_str, str):
                            self.size = int(total_length_str)
                        else:
                            total_length_str = file_download_response.headers.get(
                                "Content-Length"
                            )
                            if isinstance(total_length_str, str):
                                self.size = int(total_length_str)

                        # if self.size <= 0:
                        #     f.write(file_download_response.content)
                        # else:
                        current_length = 0
                        total_length = self.size
                        start_time = time.time()
                        progress_bar_length = 30
                        for data in file_download_response.iter_content(
                            chunk_size=chunk_size_bytes,
                        ):
                            current_length += len(data)
                            f.write(data)
                            done = int(
                                progress_bar_length * current_length / total_length
                            )
                            time_elapsed = time.time() - start_time
                            time_estimated = (
                                time_elapsed / current_length
                            ) * total_length
                            time_left = time.strftime(
                                "%H:%M:%S",
                                time.gmtime(int(time_estimated - time_elapsed)),
                            )
                            progress_bar = (
                                f"[{'#' * done}{'-' * (progress_bar_length - done)}]"
                            )
                            progress_percentage = f"{str(int((current_length / total_length) * 100)).rjust(3)}%"
                            elapsed_time = time.time() - start_time
                            _size_mb = current_length / 1024 / 1024
                            size_total = total_length / 1024 / 1024
                            _speed_mbs = (
                                _size_mb / elapsed_time if elapsed_time > 0 else 0
                            )  # MB/s
                            if logger:
                                if total_length > 0:
                                    console_exclusive_info(
                                        f"\r {count_msg} {progress_percentage} {progress_bar} {time_left} - {_speed_mbs:.2f} MB/s - {_size_mb:.2f}/{size_total:.2f} MB",
                                        end="\r",
                                    )
                                else:
                                    console_exclusive_info(
                                        f"\r {count_msg} Can not show progress estimate - {_speed_mbs:.2f} MB/s - {_size_mb:.2f}/? MB",
                                        end="\r",
                                    )
                        time_taken = time.strftime(
                            "%H:%M:%S",
                            time.gmtime(int(time.time() - start_time)),
                        )
                        _time = pd.Timedelta(time_taken)
                        if logger:
                            logger.info(
                                f" {count_msg} Download completed ({time_taken} - {_speed_mbs:.2f} MB/s - {_size_mb:.2f}/{size_total:.2f} MB)                   "
                            )
                except requests.exceptions.RequestException as e:
                    is_error_403_forbidden = False
                    if e.response is not None:  # Ensure response exists
                        is_error_403_forbidden = e.response.status_code == 403
                    if is_error_403_forbidden:
                        attempt = MAX_DOWNLOAD_ATTEMPTS_PER_FILE
                        if logger:
                            logger.error(f"DOWNLOAD FAILED: {e}")
                            logger.error(
                                f"Make sure that you only use OADS collections that you are allowed to access in your config.toml (see section 'Setup' in README)!"
                            )
                    else:
                        if logger:
                            logger.info(
                                f" {count_msg} DOWNLOAD FAILED for attempt {attempt + 1} of {MAX_DOWNLOAD_ATTEMPTS_PER_FILE}: {e}"
                            )
                        time.sleep(2)  # Wait for 2 seconds before retrying

                download_success = os.path.exists(zip_file_path)
                _downloaded = download_success
                _success &= download_success

            # Unzip zip file
            if try_unzip:
                _success = unzip_file(
                    zip_file_path,
                    delete=is_delete,
                    delete_on_error=True,
                    total_count=total_count,
                    counter=counter,
                    logger=logger,
                )
                unzip_success = os.path.exists(file_path)
                if unzip_success:
                    _unzipped = True
                _success &= unzip_success

            if _success:
                break

        return _DownloadResult(
            success=_success,
            downloaded=_downloaded,
            unzipped=_unzipped,
            size_mb=_size_mb,
            speed_mbs=_speed_mbs,
            time=_time,
            filepath=_filepath,
        )


def _create_search_url(
    collection: EOCollection,
    user_inputs: dict[str, str],
    logger: Logger | None = None,
) -> str:
    """Substitutes parameters given by the user into a search URL string if they match available parameters (else ignored)."""
    url_items = collection.url_items
    if not isinstance(url_items, str):
        return ""

    available_parameters = get_available_parameters(
        collection=collection,
        logger=logger,
    )

    available_parameter_dict = {eop.name: eop for eop in available_parameters}
    url_search = f"{url_items}?"
    for uik, uiv in user_inputs.items():
        p = available_parameter_dict.get(uik, None)
        if not isinstance(p, STACQueryParameter):
            continue

        if isinstance(p.enum, list) and uiv.lower() not in [e.lower() for e in p.enum]:
            continue

        url_search = f"{url_search}&{p.name}={uiv}"
    return url_search


def get_available_products(
    collection: EOCollection,
    params: dict[str, str],
    logger: Logger | None = None,
) -> list[EOProduct]:
    """Returns products matching user inputs from the specified collection."""
    url_search = _create_search_url(
        collection=collection,
        user_inputs=params,
        logger=logger,
    )

    if len(url_search) == 0:
        return []

    data = get_request_json(url=url_search, logger=logger)

    server: str
    url_download: str | None = None
    url_quicklook: str | None = None
    eo_products: list[EOProduct] = []
    for feature in data.get("features", []):
        assets = feature.get("assets")
        has_assets = isinstance(assets, dict)

        # eo-cat
        if has_assets:
            enclosure = assets.get("enclosure")
            if not isinstance(enclosure, dict):
                continue

            url_download = enclosure.get("href")
            if not isinstance(url_download, str):
                continue

            size = enclosure.get("file:size")

            server = str(urlp.urlparse(url_download).netloc)

            quicklook = assets.get("quicklook")
            if quicklook:
                url_quicklook = quicklook.get("href")
            else:
                url_quicklook = ""

            product_info = get_product_info(url_download, must_exist=False)

            eop = EOProduct(
                name=product_info.name.split(".")[0],
                server=server,
                orbit_and_frame=product_info.orbit_and_frame,
                file_type=product_info.file_type,
                version=product_info.baseline,
                start_processing_time=product_info.start_processing_time,
                url_download=url_download,
                url_quicklook=url_quicklook,
                size=size,
            )
            eo_products.append(eop)
            continue

        # maap
        size = (
            feature.get("properties", {}).get("productInformation", {}).get("size", -1)
        )
        for link in feature.get("links", []):
            server = ""
            url_download = None
            url_quicklook = ""

            _rel = link.get("rel")
            _type = link.get("type")

            if _rel in ["enclosure", "archives"] and _type == "application/zip":
                url_download = link.get("href", None)
                if not isinstance(url_download, str):
                    server = str(urlp.urlparse(url_download).netloc)
                    continue

            # TODO: Figure out where to find quicklooks on MAAP
            if _rel == "preview":
                url_quicklook = link.get("href", "")
            # url_quicklook = ""

            if isinstance(url_download, str) and isinstance(url_quicklook, str):
                product_info = get_product_info(url_download, must_exist=False)

                eop = EOProduct(
                    name=product_info.name,
                    server=server,
                    orbit_and_frame=product_info.orbit_and_frame,
                    file_type=product_info.file_type,
                    version=product_info.baseline,
                    start_processing_time=product_info.start_processing_time,
                    url_download=url_download,
                    url_quicklook="",
                    size=size,
                )
                eo_products.append(eop)
                break

    return eo_products


def remove_duplicates_keeping_latest(products: list[EOProduct]) -> list[EOProduct]:
    unique: dict[tuple[str, str], EOProduct] = {}

    for p in products:
        key = (p.file_type, p.orbit_and_frame)
        if (
            key not in unique
            or p.start_processing_time > unique[key].start_processing_time
        ):
            unique[key] = p

    return sorted(list(unique.values()))
