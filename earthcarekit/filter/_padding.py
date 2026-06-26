from typing import Sequence

import numpy as np
import xarray as xr
from numpy.typing import NDArray

from ..constants import TIME_VAR
from ..utils.numpy import pad_true_sequence, shift_true_sequence
from ..utils.time import TimedeltaLike, to_timedelta, to_timestamp


def _pad_mask(
    ds: xr.Dataset,
    mask: NDArray[np.bool_],
    pad_idxs: int = 0,
    shift_idxs: int = 0,
    pad_time: TimedeltaLike | tuple[TimedeltaLike, TimedeltaLike] | None = None,
    time_var: str = TIME_VAR,
) -> NDArray[np.bool_]:
    if pad_time is not None:
        if not isinstance(pad_time, str) and isinstance(pad_time, (Sequence, np.ndarray)):
            pad1 = to_timedelta(pad_time[0])
            pad2 = to_timedelta(pad_time[-1])
        else:
            pad1 = to_timedelta(pad_time)
            pad2 = pad1
        times = ds[time_var].values
        time_range = (
            (to_timestamp(times[mask][0]) - pad1).to_datetime64(),
            (to_timestamp(times[mask][-1]) + pad2).to_datetime64(),
        )
        mask = (times >= np.min([time_range[0], time_range[1]])) & (
            times <= np.max([time_range[0], time_range[1]])
        )

    mask = pad_true_sequence(mask, pad_idxs)
    mask = shift_true_sequence(mask, shift_idxs)

    return mask
