from logging import Logger

from ._exceptions import InvalidInputError


def parse_selected_index(
    selected_index: int | None, logger: Logger | None = None
) -> int | None:
    """Converts 1-indexed selected_index to 0-indexed and raises InvalidInputError if it is 0"""
    try:
        if selected_index is None:
            return None
        else:
            if selected_index >= 1:
                selected_index = selected_index - 1
            elif selected_index == 0:
                raise InvalidInputError(
                    "The indices in the found files list start at 1."
                )
            return selected_index
    except InvalidInputError as e:
        if logger:
            logger.exception(e)
        raise
