import importlib
import pkgutil

from . import product as product_module


def import_all() -> None:
    """Ensure discovery and registration of all product-specific sub-modules."""
    for _, sub_module_name, _ in pkgutil.iter_modules(product_module.__path__):
        importlib.import_module(f"{product_module.__name__}.{sub_module_name}")
