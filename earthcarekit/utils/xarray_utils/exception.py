import numpy as np


class EmptyFilterResultError(Exception):
    min_distance: float

    def __init__(self, *args: object, min_distance: int | float | np.number) -> None:
        if not isinstance(min_distance, (int | float)):
            raise TypeError(
                f"`min_distance` must be numerical, but got type '{type(min_distance).__name__}'"
            )
        super().__init__(*args, f"Min. distance = {min_distance}")
        self.min_distance = float(min_distance)
