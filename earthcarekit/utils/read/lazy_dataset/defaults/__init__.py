# Import common module and all product submodules to ensure registrations (i.e., populate registries)
from . import common
from ._product_importer import import_all

# Core imports
from .registry.common import get_common_var_transformer
from .registry.nadir_index import DEFAULT_NADIR_INDEX
from .registry.product import ProductDefaults, get_defaults, register

# Import all product submodules
import_all()
