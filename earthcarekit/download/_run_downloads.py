from logging import Logger

from ..utils._cli import console_exclusive_info, get_counter_message, log_textbox
from ..utils._config import ECKConfig
from ._eo_product import EOProduct, _DownloadResult


def run_downloads(
    products: list[EOProduct],
    config: ECKConfig,
    is_download: bool,
    is_overwrite: bool,
    is_unzip: bool,
    is_delete: bool,
    is_create_subdirs: bool,
    log_heading_msg: str = "Download products",
    logger: Logger | None = None,
    is_reversed_order: bool = False,
) -> list[_DownloadResult]:
    if logger:
        console_exclusive_info()
        log_textbox(log_heading_msg, logger=logger, show_time=True)
        console_exclusive_info()

    if not is_download:
        if logger:
            logger.info("Skipped since option --no_download was used")
        return []

    if is_reversed_order:
        products.reverse()

    _num_products: int = len(products)
    _download_results: list[_DownloadResult] = []
    for i, p in enumerate(products):
        if is_reversed_order:
            counter = _num_products - i
        else:
            counter = i + 1

        count_msg, _ = get_counter_message(counter, _num_products)

        if logger:
            if logger:
                logger.info(f"*{count_msg} Starting: {p.name}")

            _dlr = p.download(
                download_directory=config.path_to_data,
                is_overwrite=is_overwrite,
                is_unzip=is_unzip,
                is_delete=is_delete,
                is_create_subdirs=is_create_subdirs,
                maap_token=config.maap_token,
                total_count=_num_products,
                counter=counter,
                config=config,
                logger=logger,
            )
            _download_results.append(_dlr)

    return _download_results
