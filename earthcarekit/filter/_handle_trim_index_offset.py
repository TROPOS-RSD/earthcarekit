import numpy as np
from xarray import Dataset

from ..constants import TRIM_INDEX_OFFSET_VAR
from ..utils.xarray import insert_var


def update_trim_index_offset(ds: Dataset, offset: int, var: str = TRIM_INDEX_OFFSET_VAR) -> Dataset:
    if var in ds:
        if len(ds[var].values.shape) != 0:
            ds[var] = ([], ds[var].values[0])
        ds[var].values = np.asarray(int(ds[var].values) + offset)
    else:
        ds = insert_var(
            ds=ds,
            var=var,
            data=offset,
            index=0,
            after_var="processing_start_time",
        )
        ds[var] = ds[var].assign_attrs(
            {
                "earthcarekit": "Added by earthcarekit: Used to calculate the index in the original, untrimmed dataset, i.e. by addition."
            }
        )
    return ds
