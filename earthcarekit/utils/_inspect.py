import inspect
from typing import Any, Type


def has_param(cls: Type[Any], param: str) -> bool:
    """Checks if class has parameter in its signature."""
    return param in inspect.signature(cls).parameters
