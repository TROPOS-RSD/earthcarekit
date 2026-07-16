from logging import Logger
from pathlib import Path

import pandas as pd

from ..utils._cli import console_exclusive_info, log_textbox
from . import maap
from ._eo_product import EOProduct
from ._exceptions import InvalidInputError
from .maap.search import Params
from .maap.search.items import item_to_eo_product


def run_search_requets(
    search_requests: list[Params],
    user_collections: list[str],
    is_debug: bool,
    is_found_files_list_to_txt: bool,
    log_heading_msg: str = "Search products",
    selected_index_input: int | None = None,
    selected_index: int | None = None,
    logger: Logger | None = None,
    download_only_h5: bool = False,
    download_only_hdr: bool = False,
    clear_cache: bool = False,
) -> list[EOProduct]:
    if (isinstance(selected_index_input, int) and not isinstance(selected_index, int)) or (
        not isinstance(selected_index_input, int) and isinstance(selected_index, int)
    ):
        raise KeyError("Missing selected_index_input or selected_index")

    if logger:
        console_exclusive_info()
        log_textbox(log_heading_msg, logger=logger, show_time=True)
        console_exclusive_info()

    searcher = maap.Searcher()
    if clear_cache:
        searcher.clear_cache()
    items = searcher.search(search_requests, user_collections, logger=logger)
    found_products: list[EOProduct] = item_to_eo_product(
        items,
        download_only_h5=download_only_h5,
        download_only_hdr=download_only_hdr,
    )

    # Drop duplicates
    found_products.sort()
    found_products = list({p.name: p for p in found_products}.values())
    # Ensure sorted list
    found_products.sort()

    total_results: int = len(found_products)

    if total_results == 0:
        if logger:
            logger.info("No files where found for your request")
        return []

    if logger:
        console_exclusive_info()
        logger.info("File list:")

    if isinstance(selected_index_input, int) and isinstance(selected_index, int):
        try:
            found_products[selected_index]
        except IndexError:
            raise InvalidInputError(
                f"The index you selected exceeds the bounds of the file list (1 - {total_results})"
            )

    if logger:
        max_idx_str_len = len(str(total_results))
        for i, file in enumerate(found_products):
            idx_str = str(i + 1)
            msg = f" [{idx_str.rjust(max_idx_str_len)}]  {file.name}"
            if isinstance(selected_index, int) and i == selected_index:
                msg = f"<[{idx_str.rjust(max_idx_str_len)}]> {file.name} <-- Select file"
            if total_results > 41:
                if i == 20:
                    console_exclusive_info(f" ... {total_results - 40} more files ...")
                if i < 20 or total_results - i <= 20:
                    if not is_debug:
                        console_exclusive_info(msg)
            else:
                if not is_debug:
                    console_exclusive_info(msg)
            logger.debug(msg)

        if is_found_files_list_to_txt:
            df = pd.DataFrame({"id": [p.name for p in found_products]})
            export_file_path = Path("results.txt").resolve()
            df["id"].to_csv(export_file_path, index=False, header=False)
            logger.info(f"==> File list exported to <{export_file_path}>")
        else:
            logger.info("Note: To export this list use the option --export_results")

    if isinstance(selected_index, int):
        if logger:
            logger.info(f"==> Selected file at index {selected_index_input}")
        return [found_products[selected_index]]
    else:
        if logger:
            logger.info(
                "Note: To select only one specific file use the option -i/--select_file_at_index"
            )
    return found_products
