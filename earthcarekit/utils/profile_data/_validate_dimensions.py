import numpy as np
from numpy.typing import NDArray


def validate_profile_data_dimensions(
    values: NDArray,
    time: NDArray | None = None,
    height: NDArray | None = None,
    latitude: NDArray | None = None,
    longitude: NDArray | None = None,
) -> None:
    if len(values.shape) != 2:
        raise ValueError(
            f"Values must be either 2D, but has {len(values.shape)} dimensions (shape={values.shape})"
        )

    if isinstance(height, np.ndarray):
        is_height_1d = len(height.shape) == 1
        is_height_2d = len(height.shape) == 2
        if not is_height_1d and not is_height_2d:
            raise ValueError(
                f"Height must be either 1D or 2D, but has {len(height.shape)} dimensions (shape={height.shape})"
            )

        if is_height_1d:
            if height.shape[0] != values.shape[1]:
                raise ValueError(
                    f"Since height given is 1D it must have the same length as the second (i.e. vertical) dimension of values [height{height.shape[0]} != values{values.shape[1]}]"
                )
        elif is_height_2d:
            if height.shape != values.shape:
                raise ValueError(
                    f"Since height given is 2D it must have the same shape as values [height{height.shape} != values{values.shape}]"
                )

    if isinstance(time, np.ndarray):
        if time.shape[0] != values.shape[0]:
            raise ValueError(
                f"Time must have the same length as the first (i.e. temporal) dimension of values [time{time.shape} != values{values.shape}]"
            )

    if isinstance(latitude, np.ndarray):
        if len(latitude.shape) != 0 and latitude.shape[0] != values.shape[0]:
            raise ValueError(
                f"Latitude must have the same length as the first (i.e. temporal) dimension of values [latitude{latitude.shape} != values{values.shape}]"
            )

    if isinstance(longitude, np.ndarray):
        if len(longitude.shape) != 0 and longitude.shape[0] != values.shape[0]:
            raise ValueError(
                f"Longitude must have the same length as the first (i.e. temporal) dimension of values [longitude{longitude.shape} != values{values.shape}]"
            )


def ensure_vertical_2d(values: NDArray, vertical_dim_length: int) -> NDArray:
    if len(values.shape) == 1:
        values = np.repeat(values[np.newaxis, :], vertical_dim_length, axis=0)
    return values


def ensure_along_track_2d(values: NDArray, along_track_dim_length: int) -> NDArray:
    if len(values.shape) == 1:
        values = np.repeat(values[:, np.newaxis], along_track_dim_length, axis=1)
    return values
