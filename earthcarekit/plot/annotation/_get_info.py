import warnings

import numpy as np
import xarray as xr

from ...constants import TIME_VAR
from ...read import get_product_infos
from ...read.info import FileType, ProductDataFrame
from ...read.lazy import LazyDataset
from ...utils.numpy import all_same
from ...utils.time import TimestampLike, format_time_range_text, to_timestamp


def get_earthcare_frame_string(data: xr.Dataset | ProductDataFrame) -> str:
    text: str = ""

    if isinstance(data, (xr.Dataset, LazyDataset)):
        if "orbit_and_frame" in data:
            oaf = data["orbit_and_frame"].values
            if len(oaf.shape) == 0:
                return str(oaf)
            else:
                if oaf[0] == oaf[-1]:
                    return str(oaf[0])
                else:
                    orbit_start = str(oaf[0])[:-1].zfill(5)
                    orbit_end = str(oaf[1])[:-1].zfill(5)
                    frame_start = str(oaf[0])[-1]
                    frame_end = str(oaf[1])[-1]
                    if orbit_start == orbit_end:
                        text = (
                            f"{orbit_start}{frame_start}"
                            if frame_start == frame_end
                            else f"{orbit_start}{frame_start}-{frame_end}"
                        )
                    else:
                        text = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"
                    return text

        elif "frame_id" in data and "orbit_number" in data:
            o = np.atleast_1d(data["orbit_number"].values)
            f = np.atleast_1d(data["frame_id"].values)

            orbit_start = str(o[0]).zfill(5)
            orbit_end = str(o[-1]).zfill(5)
            frame_start = str(f[0])
            frame_end = str(f[-1])
            if orbit_start == orbit_end:
                text = (
                    f"{orbit_start}{frame_start}"
                    if frame_start == frame_end
                    else f"{orbit_start}{frame_start}-{frame_end}"
                )
            else:
                text = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"
            return text

    try:
        df: ProductDataFrame = get_product_infos(data)
    except ValueError:
        return text

    if len(df.shape) == 2 and df.shape[0] == 1:
        text = str(df["orbit_and_frame"][0])
    elif len(df.shape) == 2 and df.shape[0] > 1:
        orbit_start = str(df["orbit_number"].iloc[0]).zfill(5)
        orbit_end = str(df["orbit_number"].iloc[-1]).zfill(5)
        frame_start = df["frame_id"].iloc[0]
        frame_end = df["frame_id"].iloc[-1]

        if orbit_start == orbit_end:
            text = (
                f"{orbit_start}{frame_start}"
                if frame_start == frame_end
                else f"{orbit_start}{frame_start}-{frame_end}"
            )
        else:
            text = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"

    return text


def get_earthcare_file_type_baseline_string(
    data: xr.Dataset | ProductDataFrame,
    show_file_type: bool = True,
    show_baseline: bool = True,
    text_file_type: str | None = None,
    text_baseline: str | None = None,
) -> str:

    def _format_ft_bl(ft: str | None, bl: str | None) -> str:
        if isinstance(ft, str) and isinstance(bl, str) and show_file_type and show_baseline:
            return f"{ft}:{bl}"
        elif isinstance(ft, str) and show_file_type:
            return f"{ft}"
        elif isinstance(bl, str) and show_baseline:
            return f"{bl}"
        return ""

    text: str = ""

    if (
        show_file_type
        and show_baseline
        and isinstance(text_file_type, str)
        and isinstance(text_baseline, str)
    ):
        return _format_ft_bl(text_file_type, text_baseline)
    elif show_file_type and not show_baseline and isinstance(text_file_type, str):
        return _format_ft_bl(text_file_type, None)
    elif text_baseline and not show_file_type and isinstance(text_baseline, str):
        return _format_ft_bl(None, text_baseline)

    if (not isinstance(text_file_type, str) or not isinstance(text_file_type, str)) and isinstance(
        data, (xr.Dataset, LazyDataset)
    ):
        if "file_type" in data and "baseline" in data:
            fts = np.atleast_1d(data["file_type"].values)
            bls = np.atleast_1d(data["baseline"].values)

            texts: list[str] = []
            for i, ft in enumerate(fts):
                _ft: str
                if isinstance(text_file_type, str):
                    _ft = text_file_type
                else:
                    _ft = FileType.from_input(ft).to_shorthand()

                bl: str = "??"
                if isinstance(text_baseline, str):
                    bl = text_baseline
                elif bls.shape[0] > i:
                    bl = bls[i]

                ft_bl = _format_ft_bl(_ft, bl)

                if len(ft_bl) > 0 and ft_bl not in texts:
                    texts.append(ft_bl)

            text = "\n".join(texts)

            return text

    try:
        df: ProductDataFrame = get_product_infos(data)
    except ValueError:
        return text

    file_types = df["file_type"]
    baselines = df["baseline"]

    if not all_same(baselines):
        warnings.warn(f"The data contains multiple baselines: {baselines}")

    file_type: str
    if isinstance(text_file_type, str):
        file_type = text_file_type
    else:
        file_type = FileType.from_input(file_types[0]).to_shorthand()

    baseline: str
    if isinstance(text_baseline, str):
        baseline = text_baseline
    else:
        baseline = baselines[0]

    text = _format_ft_bl(file_type, baseline)

    return text


def get_earthcare_overpass_string(
    ds: xr.Dataset | None = None,
    time_var: str = TIME_VAR,
    tmin: TimestampLike | None = None,
    tmax: TimestampLike | None = None,
) -> str:
    _tmin: TimestampLike | None = None
    _tmax: TimestampLike | None = None

    if isinstance(ds, (xr.Dataset, LazyDataset)):
        _tmin = ds[time_var].values[0]
        _tmax = ds[time_var].values[-1]

    if isinstance(tmin, TimestampLike):
        _tmin = to_timestamp(tmin)

    if isinstance(tmax, TimestampLike):
        _tmax = to_timestamp(tmax)

    if isinstance(_tmin, TimestampLike) and isinstance(_tmax, TimestampLike):
        return format_time_range_text(_tmin, _tmax)

    raise ValueError("Missing arguments. At least 'ds' or 'tmin' and 'tmax' must be given.")
