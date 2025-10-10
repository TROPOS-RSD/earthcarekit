from ...utils.typing import DistanceRangeLike


def set_none_height_range_to_default(
    height_range: DistanceRangeLike | None, hmin: float, hmax: float
) -> tuple[float, float]:
    if height_range is None:
        return (hmin, hmax)

    new_height_range: tuple
    new_height_range = (height_range[0], height_range[1])
    if new_height_range[0] is None:
        new_height_range = (hmin, new_height_range[1])

    if new_height_range[1] is None:
        new_height_range = (new_height_range[0], hmax)

    return (float(new_height_range[0]), float(new_height_range[1]))
