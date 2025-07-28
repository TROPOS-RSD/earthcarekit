import re
from typing import Final

_LATEST: Final[str] = "latest"


def parse_product_version(product_version: str | None) -> str:
    if product_version is None:
        return _LATEST

    product_version_pattern = "[a-zA-Z]{2}"
    match = re.fullmatch(product_version_pattern, product_version)
    if match:
        return product_version.upper()
    elif product_version.lower() == _LATEST.lower():
        return _LATEST
    else:
        raise ValueError(
            f'bad product_version string "{product_version}". expected 2 alphabetical letters (A-Z) or "latest"'
        )
