import re
import textwrap

import numpy as np


def format_float(f: float | int) -> str:
    """
    Format a float or integer to a string with one decimal place.

    Raises `TypeError` for invalid input type.
    """
    if isinstance(f, (float, int)):
        return "{:.1f}".format(f)
    raise TypeError(
        f"Given value `f` hat wrong type '{type(f).__name__}', expecting 'float' or 'int'"
    )


def wrap_label(label: str, width: int = 40) -> str:
    wrapped_label = label
    match = re.match(r"([^\[]+)(\[[^\]]+\])?(.*)", label)
    if match:
        var_name = match.group(1).strip()
        units = match.group(2) or ""
        extra = match.group(3).strip()

        _width = width
        while len(var_name) % _width < _width / 2 and _width > 10:
            _width -= 1

        wrapped_var_name = textwrap.fill(var_name, width=_width)
        current = len(wrapped_var_name) % width

        if current + len(units) + len(extra) <= width:
            wrapped_label = f"{wrapped_var_name} {units} {extra}".strip()
        else:
            wrapped_label = f"{wrapped_var_name}\n{units} {extra}".strip()
    else:
        while len(label) % width < width / 2 and width > 10:
            width -= 1

        wrapped_label = textwrap.fill(label, width=width)
    return wrapped_label
