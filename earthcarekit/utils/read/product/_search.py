import os
from typing import Any, Callable, Iterable, Type

import numpy as np
import pandas as pd

from ...config import ECKConfig, read_config
from ...time import TimestampLike, to_timestamp
from ..search import search_files_by_regex
from ._header_file import read_hdr_fixed_header
from .file_info import (
    FileAgency,
    FileInfoEnum,
    FileLatency,
    FileType,
    ProductDataFrame,
    format_frame_id,
    format_orbit_and_frame,
    format_orbit_number,
    get_product_info,
    get_product_infos,
    validate_baseline,
)


def _to_file_info_list(
    input: str | Iterable[str] | None, file_info_enum: Type[FileInfoEnum]
) -> list[FileInfoEnum]:
    """Converts input string(s) to list of `FileInfoEnum` instances."""
    if isinstance(input, str):
        return [file_info_enum.from_input(x).value for x in np.atleast_1d(input)]
    elif isinstance(input, Iterable):
        return [file_info_enum.from_input(x).value for x in input]
    return []


def _format_input(
    input: Any | None,
    file_types: list | None = None,
    default_input: str | None = None,
    format_func: Callable | None = None,
) -> list:
    """
    Applies format function to input(s) and depeding on if a list of file types
    is given checks if the number of inputs matches the number of outputs.
    """
    if input is not None:
        input = list(np.atleast_1d(input))

        if callable(format_func):
            input = [format_func(x) for x in input]

        if isinstance(file_types, list):
            if len(input) == 1:
                input = [input[0]] * len(file_types)
            elif len(input) == 0 and isinstance(default_input, str):
                input = [default_input] * len(file_types)
            elif len(input) != len(file_types):
                raise ValueError(
                    f"Number of inputs ({len(input)}: {input}) given is greater than 1 and does not match number of given file types ({len(file_types)}: {file_types})"
                )
    else:
        if isinstance(default_input, str) and isinstance(file_types, list):
            input = [default_input] * len(file_types)
        else:
            input = []
    return input


def _list_to_regex(
    input: list[str] | list[FileInfoEnum],
    default_input: str,
) -> str:
    """Joins strings in list to a regular expression string."""
    if len(input) == 0:
        return default_input
    return f"({'|'.join(input)})"


def _check_product_contains_timestamp(
    filepath: str,
    timestamp: TimestampLike,
) -> bool:
    """Checks if product may contain timestamp."""
    product_info = get_product_info(filepath)
    timestamp = to_timestamp(timestamp)
    if (
        product_info.start_sensing_time <= timestamp
        and product_info.start_sensing_time + pd.Timedelta(minutes=13) >= timestamp
    ):

        hdr_filepath = os.path.join(
            os.path.dirname(filepath), os.path.basename(filepath).split(".")[0] + ".HDR"
        )
        if os.path.exists(hdr_filepath):
            hdr = read_hdr_fixed_header(hdr_filepath)
            timestamp = to_timestamp(timestamp)
            if isinstance(hdr.validity_start, pd.Timestamp) and isinstance(
                hdr.validity_stop, pd.Timestamp
            ):
                if hdr.validity_start <= timestamp and hdr.validity_stop >= timestamp:
                    return True
        else:
            return True
    return False

def filter_time_range(
    df: ProductDataFrame,
    start_time: TimestampLike | None = None,
    end_time: TimestampLike | None = None,
    time_column: str = "start_sensing_time",
) -> ProductDataFrame:
    
    if start_time is None and end_time is None:
        return df

    df = df.sort_values(time_column).reset_index(drop=True)

    start_mask = pd.Series(True, index=df.index)
    if start_time is not None:
        start_time = to_timestamp(start_time)
        start_mask = df[time_column] >= start_time
    
    end_mask = pd.Series(True, index=df.index)
    if end_time is not None:
        end_time = to_timestamp(end_time)
        end_mask = df[time_column] <= end_time
    
    mask = np.logical_and(start_mask, end_mask)

    df_filtered = df[mask].copy()

    if df_filtered.empty:
        return df_filtered

    return df_filtered

def search_pattern(
    file_type: str | Iterable[str] | None = None,
    agency: str | Iterable[str] | None = None,
    latency: str | Iterable[str] | None = None,
    timestamp: TimestampLike | Iterable[TimestampLike] | None = None,
    baseline: str | Iterable[str] | None = None,
    orbit_and_frame: str | Iterable[str] | None = None,
    orbit_number: int | str | Iterable[int | str] | None = None,
    frame_id: str | Iterable[str] | None = None,
):
    """
    Searches for EarthCARE product files matching given metadata filters.

    Args:
        config_filepath (str , optional): Path to a `config.toml` file. Defaults to the default configuration file.
        file_type (str or Iterable[str], optional): Product file type(s) to match.
        agency (str or Iterable[str], optional): Producing agency or agencies (e.g. "ESA" or "JAXA").
        latency (str or Iterable[str], optional): Data latency level(s).
        timestamp (TimestampLike or Iterable, optional): Timestamp(s) included in the product's time coverage.
        baseline (str or Iterable[str], optional): Baseline version(s).
        orbit_and_frame (str or Iterable[str], optional): Orbit and frame identifiers.
        orbit_number (int, str, or Iterable, optional): Orbit number(s).
        frame_id (str or Iterable[str], optional): Frame identifier(s).
        filename (str or Iterable[str], optional): Specific filename(s) or regular expression patterns to match.

    Returns:
        ProductDataFrame: Filtered list of matching product files as a `xarray.DataFrame`.

    Raises:
        FileNotFoundError: If root directory does not exist.
    """
    mission_id = "ECA"

    file_type = _to_file_info_list(file_type, FileType)
    baseline = _format_input(
        baseline,
        file_types=file_type,
        default_input="..",
        format_func=validate_baseline,
    )
    baseline_and_file_type_list = [f"{bl}_{ft}" for bl, ft in zip(baseline, file_type)]
    baseline_and_file_type = _list_to_regex(
        baseline_and_file_type_list, ".._..._..._.."
    )

    agency = _to_file_info_list(agency, FileAgency)
    agency = _list_to_regex(agency, ".")

    latency = _to_file_info_list(latency, FileLatency)
    latency = _list_to_regex(latency, ".")

    timestamp = _format_input(timestamp, format_func=to_timestamp)

    orbit_and_frame = _format_input(orbit_and_frame, format_func=format_orbit_and_frame)
    orbit_and_frame = _list_to_regex(orbit_and_frame, "." * 6)

    orbit_number = _format_input(orbit_number, format_func=format_orbit_number)
    orbit_number = _list_to_regex(orbit_number, "." * 5)

    frame_id = _format_input(frame_id, format_func=format_frame_id)
    frame_id = _list_to_regex(frame_id, ".")

    oaf_list = []
    oaf = ""
    if orbit_number != "." * 5:
        oaf_list.append(orbit_number)
    if frame_id != ".":
        oaf_list.append(frame_id)
    if orbit_number != "." * 5 or frame_id != ".":
        oaf = f"{orbit_number}{frame_id}"

    if oaf == "":
        oaf = orbit_and_frame
    elif oaf != "" and orbit_and_frame != "." * 6:
        oaf = f"(({oaf})|{orbit_and_frame})"

    pattern = f".*{mission_id}_{agency}{latency}{baseline_and_file_type}_........T......Z_........T......Z_{oaf}.h5"

    return pattern


def search_product(
    root_dirpath: str | None = None,
    config: str | ECKConfig | None = None,
    file_type: str | Iterable[str] | None = None,
    agency: str | Iterable[str] | None = None,
    latency: str | Iterable[str] | None = None,
    timestamp: TimestampLike | Iterable[TimestampLike] | None = None,
    baseline: str | Iterable[str] | None = None,
    orbit_and_frame: str | Iterable[str] | None = None,
    orbit_number: int | str | Iterable[int | str] | None = None,
    frame_id: str | Iterable[str] | None = None,
    filename: str | Iterable[str] | None = None,
    start_time: TimestampLike | None = None,
    end_time: TimestampLike | None = None,
) -> ProductDataFrame:
    """
    Searches for EarthCARE product files matching given metadata filters.

    Args:
        root_dirpath (str, optional): Root directory to search. Defaults to directory given in a configuration file.
        config (str | ECKConfig | None , optional): Path to a `config.toml` file or a ECKConfig instance. Defaults to the default configuration file path.
        file_type (str | Iterable[str], optional): Product file type(s) to match.
        agency (str | Iterable[str], optional): Producing agency or agencies (e.g. "ESA" or "JAXA").
        latency (str | Iterable[str], optional): Data latency level(s).
        timestamp (TimestampLike | Iterable, optional): Timestamp(s) included in the product's time coverage.
        baseline (str | Iterable[str], optional): Baseline version(s).
        orbit_and_frame (str | Iterable[str], optional): Orbit and frame identifiers.
        orbit_number (int, str, | Iterable, optional): Orbit number(s).
        frame_id (str | Iterable[str], optional): Frame identifier(s).
        filename (str | Iterable[str], optional): Specific filename(s) or regular expression patterns to match.
        start_time (TimestampLike, optional): First timestamp included in the product's time coverage.
        end_time (TimestampLike, optional): Last timestamp included in the product's time coverage.

    Returns:
        ProductDataFrame: Filtered list of matching product files as a `pandas.DataFrame`-based object.

    Raises:
        FileNotFoundError: If root directory does not exist.
    """
    if not isinstance(root_dirpath, str):
        if isinstance(config, ECKConfig):
            root_dirpath = config.path_to_data
        else:
            root_dirpath = read_config(config).path_to_data

    if not os.path.exists(root_dirpath):
        raise FileNotFoundError(f"Given root directory does not exist: {root_dirpath}")

    mission_id = "ECA"

    file_type = _to_file_info_list(file_type, FileType)
    baseline = _format_input(
        baseline,
        file_types=file_type,
        default_input="..",
        format_func=validate_baseline,
    )
    baseline_and_file_type_list = [f"{bl}_{ft}" for bl, ft in zip(baseline, file_type)]
    baseline_and_file_type = _list_to_regex(
        baseline_and_file_type_list, ".._..._..._.."
    )

    agency = _to_file_info_list(agency, FileAgency)
    agency = _list_to_regex(agency, ".")

    latency = _to_file_info_list(latency, FileLatency)
    latency = _list_to_regex(latency, ".")

    timestamp = _format_input(timestamp, format_func=to_timestamp)
    _start_time =  [] if start_time is None else [to_timestamp(start_time)]
    _end_time =  [] if end_time is None else [to_timestamp(end_time)]
    timestamp = timestamp + _start_time + _end_time

    orbit_and_frame = _format_input(orbit_and_frame, format_func=format_orbit_and_frame)
    orbit_and_frame = _list_to_regex(orbit_and_frame, "." * 6)

    orbit_number = _format_input(orbit_number, format_func=format_orbit_number)
    orbit_number = _list_to_regex(orbit_number, "." * 5)

    frame_id = _format_input(frame_id, format_func=format_frame_id)
    frame_id = _list_to_regex(frame_id, ".")

    oaf_list = []
    oaf = ""
    if orbit_number != "." * 5:
        oaf_list.append(orbit_number)
    if frame_id != ".":
        oaf_list.append(frame_id)
    if orbit_number != "." * 5 or frame_id != ".":
        oaf = f"{orbit_number}{frame_id}"

    if oaf == "":
        oaf = orbit_and_frame
    elif oaf != "" and orbit_and_frame != "." * 6:
        oaf = f"(({oaf})|{orbit_and_frame})"

    pattern = f".*{mission_id}_{agency}{latency}{baseline_and_file_type}_........T......Z_........T......Z_{oaf}.h5"

    # pattern = search_pattern(
    #     file_type=file_type,
    #     agency=agency,
    #     latency=latency,
    #     timestamp=timestamp,
    #     baseline=baseline,
    #     orbit_and_frame=orbit_and_frame,
    #     orbit_number=orbit_number,
    #     frame_id=frame_id,
    # )

    if pattern == ".*ECA_...._..._..._.._........T......Z_........T......Z_.......h5":
        files = []
    else:
        files = search_files_by_regex(root_dirpath, pattern)

    if isinstance(filename, str) or isinstance(filename, Iterable):
        if isinstance(filename, str):
            filename = np.atleast_1d(filename)
        _get_pattern = lambda fn: f".*{os.path.basename(fn).replace('.h5', '')}.*.h5"
        filename = [_get_pattern(fn) for fn in filename]
    elif filename is None:
        filename = []
    else:
        raise TypeError(
            f"Given filename has invalid type ({type(filename)}: {filename})"
        )

    for fn in filename:
        new_files = search_files_by_regex(root_dirpath, fn)
        files.extend(new_files)

    # Remove duplicates
    files = list(set(files))

    old_files = files.copy()
    if len(timestamp) > 0:
        files = []
        for t in timestamp:
            new_files = [
                f for f in old_files if _check_product_contains_timestamp(f, t)
            ]
            if len(new_files) > 0:
                files.extend(new_files)

    d = []
    df = get_product_infos(files)
    for f in files:
        try:
            d.append(get_product_info(f).to_dict())
        except ValueError as e:
            continue

    df = ProductDataFrame(d)

    if start_time is not None or end_time is not None:
        _d = []
        _df = get_product_infos(old_files)
        for _f in old_files:
            try:
                _d.append(get_product_info(_f).to_dict())
            except ValueError as _e:
                continue

        _df = ProductDataFrame(_d)

        _df = filter_time_range(_df, start_time=start_time, end_time=end_time)

        if not df.empty and not _df.empty:
            df = pd.concat([df, _df], ignore_index=True)
        elif not _df.empty:
            df = _df

    df = df.sort_values(by=["orbit_and_frame", "file_type", "start_processing_time"])
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    return df
