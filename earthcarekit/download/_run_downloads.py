from logging import Logger

import requests

from ..utils._cli import console_exclusive_info, get_counter_message, log_textbox
from ..utils.config import ECKConfig
from ._auth_oads import get_oads_authentification_cookies
from ._eo_product import EOProduct, _DownloadResult
from ._eo_search_request import EOSearchRequest
from ._types import Entrypoint


def run_downloads(
    products: list[EOProduct],
    config: ECKConfig,
    entrypoint: Entrypoint,
    is_download: bool,
    is_overwrite: bool,
    is_unzip: bool,
    is_delete: bool,
    is_create_subdirs: bool,
    log_heading_msg: str = f"Download products",
    logger: Logger | None = None,
) -> list[_DownloadResult]:
    if logger:
        console_exclusive_info()
        log_textbox(log_heading_msg, logger=logger, show_time=True)
        console_exclusive_info()

    if not is_download:
        if logger:
            logger.info(f"Skipped since option --no_download was used")
        return []

    _current_server: str = ""
    _num_products: int = len(products)
    _download_results: list[_DownloadResult] = []
    oads_cookies_saml: requests.cookies.RequestsCookieJar | None = None
    for i, p in enumerate(products):
        count_msg, _ = get_counter_message(i + 1, _num_products)
        if logger:
            if logger:
                logger.info(f"*{count_msg} Starting: {p.name}")
        if entrypoint == Entrypoint.OADS:
            if p.server != _current_server:
                if logger:
                    logger.info(
                        f" {count_msg} Authenticate at dissemination service: {p.server}"
                    )
                if len(config.oads_username) == 0 or len(config.oads_password) == 0:
                    msg = f"Authentication failed due to missing oads username or password"
                    raise ValueError(msg)
                oads_cookies_saml = get_oads_authentification_cookies(
                    dissemination_server=p.server,
                    username=config.oads_username,
                    password=config.oads_password,
                )
                _current_server = p.server
            _dlr = p.download(
                download_directory=config.path_to_data,
                is_overwrite=is_overwrite,
                is_unzip=is_unzip,
                is_delete=is_delete,
                is_create_subdirs=is_create_subdirs,
                oads_cookies_saml=oads_cookies_saml,
                total_count=_num_products,
                counter=i + 1,
                logger=logger,
            )
            _download_results.append(_dlr)
        elif entrypoint == Entrypoint.MAAP:
            _dlr = p.download(
                download_directory=config.path_to_data,
                is_overwrite=is_overwrite,
                is_unzip=is_unzip,
                is_delete=is_delete,
                is_create_subdirs=is_create_subdirs,
                maap_token=config.maap_token,
                total_count=_num_products,
                counter=i + 1,
                logger=logger,
            )
            _download_results.append(_dlr)
        else:
            raise ValueError(f"invalid value for entrypoint: {entrypoint}")
    return _download_results
