from typing import Final

# Dataset dimension names
ALONG_TRACK_DIM: Final[str] = "along_track"
ACROSS_TRACK_DIM: Final[str] = "across_track"
VERTICAL_DIM: Final[str] = "vertical"

# Dataset variable names
TIME_VAR: Final[str] = "time"
HEIGHT_VAR: Final[str] = "height"

TRACK_LAT_VAR: Final[str] = "latitude"
TRACK_LON_VAR: Final[str] = "longitude"

SWATH_LAT_VAR: Final[str] = "latitude_swath"
SWATH_LON_VAR: Final[str] = "longitude_swath"

ELEVATION_VAR: Final[str] = "elevation"
TROPOPAUSE_VAR: Final[str] = "tropopause_height"
TEMP_CELSIUS_VAR: Final[str] = "temperature_celsius"
TEMP_KELVIN_VAR: Final[str] = "temperature_kelvin"

ACROSS_TRACK_DISTANCE: Final[str] = "across_track_distance"
FROM_TRACK_DISTANCE: Final[str] = "from_track_distance"

# Dataset variable labels (i.e. long_name attributes)
BSC_LABEL: Final[str] = "Bsc. coeff."
EXT_LABEL: Final[str] = "Ext. coeff."
LR_LABEL: Final[str] = "Lidar ratio"
DEPOL_LABEL: Final[str] = "Depol. ratio"
