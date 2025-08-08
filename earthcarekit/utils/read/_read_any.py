import os

import xarray as xr

from ._read_nc import read_nc
from ._read_polly import read_polly
from .product import read_product
from .product.file_info import is_earthcare_product


def read_any(input: str | xr.Dataset, **kwargs) -> xr.Dataset:
    """Reads various input types and returns an `xarray.Dataset`.

    This function can read:
        - EarthCARE product files (`.h5`)
        - NetCDF files (`.nc`)
        - Manually processed PollyXT output files (`.txt`)

    Args:
        input (str | xr.Dataset): File path or existing Dataset.
        **kwargs: Additional keyword arguments for specific readers.

    Returns:
        xr.Dataset: Opened dataset.

    Raises:
        ValueError: If the file type is not supported.
        TypeError: If the input type is invalid.
    """
    if isinstance(input, xr.Dataset):
        return input
    elif isinstance(input, str):
        filepath = input

        if is_earthcare_product(filepath=filepath):
            return read_product(filepath, **kwargs)

        filename = os.path.basename(filepath)
        _, ext = os.path.splitext(filename)
        if ext.lower() == ".txt":
            return read_polly(filepath)
        elif ext.lower() == ".nc":
            return read_nc(filepath, **kwargs)

        raise ValueError(f"Reading of file not supported: <{input}>")
    raise TypeError(f"Invalid type '{type(input).__name__}' for input.")
