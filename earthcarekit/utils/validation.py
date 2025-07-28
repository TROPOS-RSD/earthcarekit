import re
from typing import Any, Iterable, List

import numpy as np

from .typing import DistanceRangeLike


def validate_completeness_of_args(
    function_name: str,
    required_names: Iterable[str],
    positional_values: Iterable[Any] | None = None,
    **kwargs,
) -> List[str]:
    """
    Validates that required positional and optional argument groups are complete.

    For example, if `required_names = ['x', 'y']`, this function will:
    - Check if `x` and `y` are both provided in positional arguments (if used).
    - Check if optional arguments like `x1`, `x2`, ..., `y1`, `y2`, ... are all matched
      across the required names (e.g., if `x2` is given, `y2` must also be present).

    Parameters:
        function_name (str): Name of the function (used in error messages).
        required_names (Iterable[str]): Base names of required argument groups (e.g. ['x', 'y']).
        positional_values (Iterable[Any], optional): Positional argument values to validate.
        **kwargs: Optional keyword arguments to validate for matching suffixes.

    Returns:
        List[str]: List of suffixes (as strings) used in optional arguments for the first group.

    Raises:
        TypeError: If any required arguments are missing.
    """
    # Check required positional arguments
    if positional_values is not None:
        missing = [
            required_names[i] for i, v in enumerate(positional_values) if v is None
        ]
        if missing:
            msg = f"{function_name}() missing {len(missing)} required positional argument{'s' if len(missing) > 1 else ''}: "
            msg += ", ".join(f"'{name}'" for name in missing)
            raise TypeError(msg)

    # Check completeness of optional argument groups (e.g., x1/y1, x2/y2, ...)
    suffixes_by_name = [[] for _ in required_names]
    for key in kwargs:
        for i, name in enumerate(required_names):
            match = re.fullmatch(f"{name}(\\d*)", key)
            if match:
                suffix = match.group(1)
                suffixes_by_name[i].append(suffix)

    # Find mismatched suffixes between argument groups
    missing = []
    for i in range(len(suffixes_by_name) - 1):
        for j in range(i + 1, len(suffixes_by_name)):
            suffixes_i = np.array(suffixes_by_name[i])
            suffixes_j = np.array(suffixes_by_name[j])
            missing_from_j = np.setdiff1d(suffixes_i, suffixes_j)
            missing_from_i = np.setdiff1d(suffixes_j, suffixes_i)
            missing += [f"'{required_names[j]}{s}'" for s in missing_from_j]
            missing += [f"'{required_names[i]}{s}'" for s in missing_from_i]

    # Raise error if mismatches were found
    if missing:
        unique_missing = sorted(set(missing))
        msg = f"{function_name}() missing {len(unique_missing)} required argument{'s' if len(unique_missing) > 1 else ''}: "
        msg += ", ".join(unique_missing)
        raise TypeError(msg)

    return suffixes_by_name[0]


def validate_height_range(height_range: DistanceRangeLike) -> tuple[float, float]:
    """Returns validated height range and raises `ValueError` if invalid."""
    if isinstance(height_range, Iterable):
        if len(height_range) == 2:
            if all([isinstance(x, (int, float)) for x in height_range]):
                return float(height_range[0]), float(height_range[1])
    raise ValueError(f"invalid height range: {height_range}")
