from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AlongTrackAxisData(StrEnum):
    TIME = "time"
    TIME_UTC = "utc"
    TIME_LST = "lst"
    GEO = "geo"
    LAT = "lat"
    LON = "lon"
    DISTANCE = "distance"
    COUNT = "count"
    NONE = "none"

    @staticmethod
    def from_str(label: str) -> "AlongTrackAxisData":
        label = label.lower()
        # Convert plural to singular
        if len(label) > 0 and label[-1] == "s":
            label = label[0:-1]
        if label in (
            "latlon",
            "lonlat",
            "coord",
            "coords",
            "coordinates",
            "geo",
            "geoloc",
            "geolocation",
            "loc",
            "location",
        ):
            return AlongTrackAxisData.GEO
        elif label in ("lat", "latitude"):
            return AlongTrackAxisData.LAT
        elif label in ("lon", "longitude"):
            return AlongTrackAxisData.LON
        elif label in ("distance", "dist", "grounddist", "grounddistance"):
            return AlongTrackAxisData.DISTANCE
        elif label in ("time", "utclst", "lstutc", "timeutclst", "timelstutc"):
            return AlongTrackAxisData.TIME
        elif label in ("utc", "timeutc", "utctime"):
            return AlongTrackAxisData.TIME_UTC
        elif label in ("lst", "timelst", "lsttime"):
            return AlongTrackAxisData.TIME_LST
        elif label in ("count", "sample", "number", "num", "index", "idx"):
            return AlongTrackAxisData.COUNT
        elif label in ("none", "no", "not", "empty", "nothing", "-", ""):
            return AlongTrackAxisData.NONE
        else:
            try:
                return AlongTrackAxisData(label)
            except:
                raise ValueError(f"Can not find any match for label '{label}'")


@dataclass
class AlongTrackAxisStyle:
    data: AlongTrackAxisData
    units: bool | None = None
    title: bool | None = None
    labels: bool | None = None

    def __post_init__(self):
        self.data = AlongTrackAxisData.from_str(self.data)

    @classmethod
    def from_input(cls, input: "AlongTrackAxisStyle | str") -> "AlongTrackAxisStyle":
        if isinstance(input, cls):
            return input
        if isinstance(input, str):
            return cls(input)  # type: ignore
        raise TypeError(
            f"invalid type '{type(input).__name__}', expecting '{cls.__name__}' or 'str'"
        )
