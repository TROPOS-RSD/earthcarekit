import re
from typing import Final

import pandas as pd

FILE_INFO_REGEX: Final[str] = (
    r".*ECA_([EJ])([XNO])([A-Z]{2})_(..._..._..)_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z_(\d{5}[ABCDEFGH])"
)


def get_file_info_from_str(s: str) -> dict:
    """Extract meta data from a EarthCARE product/file name.

    Args:
        s (str): The input string.

    Raises:
        ValueError: If the pattern of `s` does not match the EarthCARE product naming convention.

    Returns:
        dict: File meta data as a dict with the following keys:

            - `mission_id`
            - `agency`
            - `latency`
            - `baseline`
            - `file_type`
            - `start_sensing_time`
            - `start_processing_time`
            - `orbit_number`
            - `frame_id`
            - `orbit_and_frame`
            - `filename`
    """
    m = re.match(FILE_INFO_REGEX, s)
    if m is None:
        raise ValueError(f"no match found; could not get a EarthCARE file info from string '{s}'")
    fn = m.group()[-60:]  # type: ignore
    (agy, lty, bl, ft, sst, pst, oaf) = m.groups()  # type: ignore
    return dict(
        mission_id="ECA",
        agency=agy,
        latency=lty,
        baseline=bl,
        file_type=ft,
        start_sensing_time=pd.Timestamp(sst),
        start_processing_time=pd.Timestamp(pst),
        orbit_number=int(oaf[:-1]),
        frame_id=oaf[-1],
        orbit_and_frame=oaf,
        filename=fn,
    )
