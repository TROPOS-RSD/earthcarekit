from functools import wraps

from ...._typing import (
    _CommonVarTransformer,
    _CommonVarTransformRegistry,
    _LazyDataset,
    _LazyVariable,
)

_REGISTRY: _CommonVarTransformRegistry = {}


def get_common_var_transformers() -> _CommonVarTransformRegistry:
    return _REGISTRY.copy()


def register_common_var_transformer(var: str):
    def decorator(func: _CommonVarTransformer):
        @wraps(func)
        def wrapper(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
            return func(common_var, lds, lvar)

        _REGISTRY[var] = wrapper
        return wrapper

    return decorator


def get_common_var_transformer(common_var: str) -> _CommonVarTransformer | None:
    return None if common_var is None else _REGISTRY.get(common_var)
