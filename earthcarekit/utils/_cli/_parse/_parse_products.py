from logging import Logger

from ._parse_product_type import parse_product_type_and_version
from ._parse_product_version import parse_product_version
from ._types import ProductTypeVersion


def parse_products(
    product_type: list[str],
    product_version: str | None,
    logger: Logger | None = None,
) -> list[ProductTypeVersion]:
    v = parse_product_version(product_version)
    return [
        parse_product_type_and_version(p, default_version=v, logger=logger)
        for p in product_type
    ]
