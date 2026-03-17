import re
from typing import Final

import pandas as pd

FILE_INFO_REGEX: Final[str] = (
    r".*ECA_([EJ])([XNO])([A-Z]{2})_(..._..._..)_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z_(\d{5}[ABCDEFGH])"
)


def get_file_info_from_str(s: str) -> dict:
    m = re.match(FILE_INFO_REGEX, s)
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
