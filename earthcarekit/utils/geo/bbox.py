import numpy as np


def circular_lon_bbox(all_lons: np.ndarray) -> tuple[float, float]:
    """Compute smallest bounding box for longitudes, correctly handling dateline wrap."""
    lon = np.asarray(all_lons)
    lon = lon[~np.isnan(lon)]
    if lon.size == 0:
        return np.nan, np.nan

    lon360 = np.mod(lon, 360)
    lon360_sorted = np.sort(lon360)
    gaps = np.diff(np.concatenate([lon360_sorted, [lon360_sorted[0] + 360]]))
    max_gap_idx = np.argmax(gaps)

    lon_min = lon360_sorted[(max_gap_idx + 1) % len(lon360_sorted)]
    lon_max = lon360_sorted[max_gap_idx]

    # Convert back to [-180, 180]
    lon_min = ((lon_min + 180) % 360) - 180
    lon_max = ((lon_max + 180) % 360) - 180

    return lon_min, lon_max


def compute_bbox(*tracks: np.ndarray) -> list[float]:
    """
    Compute the minimal bounding box that contains all provided lat-lon tracks.

    Each track is either:
    - A tuple/list of (lat_sequence, lon_sequence)
    - Or a 2D array of shape (N, 2) where [:, 0] = lat, [:, 1] = lon

    Args:
        *tracks: One or more lat-lon coordinate sequences or 2D arrays.

    Returns:
        dict: Bounding box with lat_min, lat_max, lon_min, lon_max
    """
    all_lats = []
    all_lons = []

    for track in tracks:
        if isinstance(track, (tuple, list)) and len(track) == 2:
            lat, lon = np.asarray(track[0]), np.asarray(track[1])
        else:
            arr = np.asarray(track)
            if arr.ndim != 2 or arr.shape[1] != 2:
                raise ValueError("Each track must be (lat, lon) or Nx2 array.")
            lat, lon = arr[:, 0], arr[:, 1]

        all_lats.append(lat)
        all_lons.append(lon)

    all_lats_flat = np.concatenate(all_lats)
    all_lons_flat = np.concatenate(all_lons)

    lat_min = float(np.nanmin(all_lats_flat))
    lat_max = float(np.nanmax(all_lats_flat))
    lon_min, lon_max = circular_lon_bbox(all_lons_flat)

    extent = [
        lon_min,
        lon_max,
        lat_min,
        lat_max,
    ]
    return extent


def pad_bbox(
    extent: list[float],
    pad_lat: float | None = None,  # 2,
    pad_lon: float | None = None,  # 2,
    pad_lat_ratio: float | str | None = "1%",
    pad_lon_ratio: float | str | None = "1%",
) -> list[float]:
    lon_min = extent[0]
    lon_max = extent[1]
    lat_min = extent[2]
    lat_max = extent[3]

    _pad_lon: float = 0
    _pad_lat: float = 0

    if pad_lon is not None and pad_lon_ratio is not None:
        raise TypeError(
            f"both 'pad_lon' and 'pad_lon_ratio' are given but only one is required."
        )
    if pad_lon is not None:
        _pad_lon = pad_lon
    elif pad_lon_ratio is not None:
        lon_diff: float = float(np.abs(lon_max - lon_min))
        if isinstance(pad_lon_ratio, str):
            try:
                pad_lon_ratio = int(pad_lon_ratio[0:-1]) / 100
                if pad_lon_ratio < 0 or pad_lon_ratio > 1:
                    raise ValueError()
                _pad_lon = lon_diff * pad_lon_ratio
            except Exception as e:
                raise ValueError(
                    f"""invalid pad ratio string "{pad_lon_ratio}", expecting string like e.g. this: "75%"."""
                )
        elif isinstance(pad_lon_ratio, float):
            if pad_lon_ratio < 0 or pad_lon_ratio > 1:
                raise ValueError(
                    f"""invalid pad ratio float "{pad_lon_ratio}", expecting float between 0 and 1"""
                )
            _pad_lon = lon_diff * pad_lon_ratio

    if pad_lat is not None and pad_lat_ratio is not None:
        raise TypeError(
            f"both 'pad_lat' and 'pad_lat_ratio' are given but only one is required."
        )
    if pad_lat is not None:
        _pad_lat = pad_lat
    elif pad_lat_ratio is not None:
        lat_diff: float = float(np.abs(lat_max - lat_min))
        if isinstance(pad_lat_ratio, str):
            try:
                pad_lat_ratio = int(pad_lat_ratio[0:-1]) / 100
                if pad_lat_ratio < 0 or pad_lat_ratio > 1:
                    raise ValueError()
                _pad_lat = lat_diff * pad_lat_ratio
            except Exception as e:
                raise ValueError(
                    f"""invalid pad ratio string "{pad_lat_ratio}", expecting string like e.g. this: "75%"."""
                )
        elif isinstance(pad_lat_ratio, float):
            if pad_lat_ratio < 0 or pad_lat_ratio > 1:
                raise ValueError(
                    f"""invalid pad ratio float "{pad_lat_ratio}", expecting float between 0 and 1"""
                )
            _pad_lat = lat_diff * pad_lat_ratio

    extent = [
        lon_min - _pad_lon,
        lon_max + _pad_lon,
        lat_min - _pad_lat,
        lat_max + _pad_lat,
    ]
    return extent
