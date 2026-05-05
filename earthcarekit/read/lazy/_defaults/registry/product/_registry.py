from ._model import ProductDefaults

_REGISTRY: dict[str, ProductDefaults] = {}


def register(file_type: str, defaults: ProductDefaults) -> None:
    _REGISTRY[file_type] = defaults


def get_defaults(file_type: str) -> ProductDefaults | None:
    return _REGISTRY.get(file_type)
