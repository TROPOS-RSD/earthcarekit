import logging
import re
from typing import Any, Literal

from xarray import Dataset

from ...download import ecdownload
from ...read import LazyDataset, read_product, search_product
from ...read.info import FileType
from ...typing import PathLike
from ...utils.time import TimestampLike, time_to_str


def _load_product(
    is_lazy: bool,
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None,
    baseline: str | None = None,
    path_to_data: str | None = None,
    mode: Literal["exhaustive", "fast"] = "exhaustive",
    download: bool = True,
    verbose: bool = False,
    logger: logging.Logger | None = None,
    return_path: bool = False,
    **kwargs,
) -> Dataset | LazyDataset | str:
    if verbose:
        logger = logger or logging.getLogger()

    _kwargs: dict[str, Any] = {"in_memory": True}
    _kwargs.update(kwargs)

    if isinstance(type_or_path, str) and len(type_or_path.split(":")[-1]) == 2:
        baseline = type_or_path.split(":")[-1]
        type_or_path = type_or_path[:-3]

    if isinstance(type_or_path, str) and len(type_or_path) <= 10:
        file_type = FileType.from_input(type_or_path).value

        if frame_or_time is None:
            raise ValueError("Missing 'frame_or_time' input")

        orbit_and_frame: str | None = None
        timestamp: str | None = None
        if isinstance(frame_or_time, str) and re.compile(r"^\d{1,5}[AaBbCcDdEeFfGgHh]$").match(
            frame_or_time
        ):
            orbit_and_frame = frame_or_time
        else:
            timestamp = time_to_str(frame_or_time)

        if logger:
            msg = f"Searching '{file_type}'"
            if orbit_and_frame is not None:
                msg = f"{msg} frame {orbit_and_frame}"
            if timestamp is not None:
                msg = f"{msg} at {timestamp}"
            logger.info(f"{msg} ...")

        df = search_product(
            path_to_data=path_to_data,
            file_type=file_type,
            orbit_and_frame=orbit_and_frame,
            timestamp=timestamp,
            baseline=baseline,
            mode=mode,
        ).filter_latest()

        if df.size == 0:
            if not download:
                if logger:
                    logger.error(
                        "File not found locally. Use 'download' option to automatically donwload requested file from ESA MAAP."
                    )
            elif download:
                if logger:
                    logger.info("File not found locally. Starting download ...")
                ecdownload(
                    path_to_data=path_to_data,
                    file_type=file_type,
                    orbit_and_frame=orbit_and_frame,
                    timestamp=timestamp,
                    baseline=baseline,
                    verbose=verbose,
                )

                if logger:
                    logger.info("Download complete. Searching file locally ...")
                df = search_product(
                    path_to_data=path_to_data,
                    file_type=file_type,
                    orbit_and_frame=orbit_and_frame,
                    timestamp=timestamp,
                    baseline=baseline,
                    mode=mode,
                ).filter_latest()

        if df.size == 0:
            raise ValueError(
                f"Can't find frame for inputs: {file_type=}, {orbit_and_frame=}, {baseline=}, "
            )

        fp = str(df.filepath[-1])
    else:
        fp = str(type_or_path)

    if return_path:
        return fp

    if logger:
        logger.info("Reading file ...")

    if is_lazy:
        return LazyDataset(fp, **_kwargs)
    return read_product(fp, **_kwargs)
