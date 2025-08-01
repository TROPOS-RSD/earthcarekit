import logging

import xarray as xr


def read_nc(
    filepath: str,
    modify: bool = True,
    **kwargs,
) -> xr.Dataset:
    """Wrapper function for `xr.open_dataset()`."""

    logger = logging.getLogger()

    ds = xr.open_dataset(filepath, **kwargs)

    if modify:
        for var in ds.variables:
            units_attr: str | None = None
            if hasattr(ds[var], "units"):
                units_attr = "units"
            elif hasattr(ds[var], "unit"):
                units_attr = "unit"

            if isinstance(units_attr, str):
                units = ds[var].attrs[units_attr].lower()
                if "seconds" in units and "since" in units and "1970-01-01" in units:
                    ds[var].values = ds[var].values.astype("datetime64[s]")
                    ds[var].attrs[units_attr] = ""

        if (
            "altitude" in ds
            and "height" in ds
            and ds["altitude"].values.size == 1
            and ds["height"].values.size > 1
        ):
            logger.info(f"Convert height above ground level to height above ellipsoid.")
            ds["height"] = ds["height"] + ds["altitude"].values
            ds = ds.reset_index("height")
            ds = ds.reset_coords("height")
            ds = ds.drop_vars("altitude")

    return ds
