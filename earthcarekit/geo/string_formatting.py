import numpy as np


def format_latitude(lat: float | int) -> str:
    """
    Format a latitude value as a string with degree and hemisphere (N/S).

    Returns an empty string if NaN. Raises `TypeError` for invalid input type.
    """
    if isinstance(lat, (float, int)):
        if np.isnan(lat):
            return ""
        elif lat < 0:
            return r"{:.1f}$^\circ$S".format(-1 * lat)
        else:
            return r"{:.1f}$^\circ$N".format(lat)
    raise TypeError(
        f"Given value `lat` hat wrong type '{type(lat).__name__}', expecting 'float' or 'int'"
    )


def format_longitude(lon: float | int) -> str:
    """
    Format a longitude value as a string with degree and direction (E/W).

    Returns an empty string if NaN. Raises `TypeError` for invalid input type.
    """
    if isinstance(lon, (float, int)):
        if np.isnan(lon):
            return ""
        elif lon < 0:
            return r"{:.1f}$^\circ$W".format(-1 * lon)
        else:
            return r"{:.1f}$^\circ$E".format(lon)
    raise TypeError(
        f"Given value `lon` hat wrong type '{type(lon).__name__}', expecting 'float' or 'int'"
    )


def format_coords(lat: float | int, lon: float | int, precision=4) -> str:
    """
    Format a pair of latitude and longitude values as a string coordinate string.

    Raises `TypeError` for invalid input type.
    """
    if not isinstance(lat, (float, int)):
        raise TypeError(
            f"Given value `lat` hat wrong type '{type(lat).__name__}', expecting 'float' or 'int'"
        )
    if not isinstance(lon, (float, int)):
        raise TypeError(
            f"Given value `lon` hat wrong type '{type(lon).__name__}', expecting 'float' or 'int'"
        )

    fstr = f"{{:.{precision}f}}"

    return f"({fstr.format(lat)}, {fstr.format(lon)})"
