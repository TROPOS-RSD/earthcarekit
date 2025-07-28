from collections import defaultdict
from logging import Logger
from typing import Any

import pandas as pd

from ..utils._cli import console_exclusive_info, log_textbox
from ._eo_product import EOProduct
from ._eo_search_request import EOSearchRequest
from ._exceptions import InvalidInputError


def run_search_requets(
    search_requests: list[EOSearchRequest],
    is_debug: bool,
    is_found_files_list_to_txt: bool,
    log_heading_msg: str = f"Search products",
    selected_index_input: int | None = None,
    selected_index: int | None = None,
    logger: Logger | None = None,
) -> list[EOProduct]:
    if (
        isinstance(selected_index_input, int) and not isinstance(selected_index, int)
    ) or (
        not isinstance(selected_index_input, int) and isinstance(selected_index, int)
    ):
        raise KeyError(f"Missing selected_index_input or selected_index")

    if logger:
        console_exclusive_info()
        log_textbox(log_heading_msg, logger=logger, show_time=True)
        console_exclusive_info()

    total_count: int = len(search_requests)
    found_products: list[EOProduct] = []
    for i, sr in enumerate(search_requests):
        _counter: int = i + 1
        _products: list[EOProduct] = sr.run(
            counter=_counter,
            total_count=total_count,
            logger=logger,
        )
        found_products.extend(_products)

    # Drop duplicates
    found_products.sort()
    found_products = list({p.name: p for p in found_products}.values())
    # Ensure sorted list
    found_products.sort()

    total_results: int = len(found_products)

    if total_results == 0:
        if logger:
            logger.info(f"No files where found for your request")
        return []

    if logger:
        console_exclusive_info()
        logger.info(f"List of files found (total number {total_results}):")

    if isinstance(selected_index_input, int) and isinstance(selected_index, int):
        try:
            selected_product: EOProduct = found_products[selected_index]
        except IndexError:
            raise InvalidInputError(
                f"The index you selected exceeds the bounds of the found files list (1 - {total_results})"
            )

    if logger:
        max_idx_str_len = len(str(total_results))
        for i, file in enumerate(found_products):
            idx_str = str(i + 1)
            msg = f" [{idx_str.rjust(max_idx_str_len)}]  {file.name}"
            if isinstance(selected_index, int) and i == selected_index:
                msg = f"<[{idx_str.rjust(max_idx_str_len)}]> {file.name} <-- Select file (user input: {selected_index_input})"
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
            df["id"].to_csv("results.txt", index=False, header=False)
        else:
            logger.info(f"Note: To export this list use the option --export_results")

    if isinstance(selected_index, int):
        return [found_products[selected_index]]
    else:
        if logger:
            logger.info(
                f"Note: To select only one specific file use the option -i/--select_file_at_index"
            )
    return found_products
