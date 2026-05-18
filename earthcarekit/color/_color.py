import re
from dataclasses import dataclass
from typing import Sequence, Tuple, Union

import matplotlib.colors as mcolors
import numpy as np

from ._contrast import get_best_bw_contrast_color
from ._registry import EC_COLORS
from ._typing import ColorLike


@dataclass(frozen=True)
class Color(str):
    """Represents a color with convenient conversion, blending, and alpha support.

    Extends `str` to store a color as a hex string while providing methods
    to access RGB/RGBA, set transparency, blend with other colors, and
    normalize input from various formats.

    Attributes:
        input (ColorLike): Original input used to create the color.
        name (str | None): Optional name of the color.
        is_normalized (bool): Whether the color values are normalized (0-1).
    """

    input: ColorLike
    name: str | None = None
    is_normalized: bool = False

    def __new__(
        cls,
        color_input: "Color" | ColorLike,
        name: str | None = None,
        is_normalized: bool = False,
    ):
        """Create a Color instance from a color-like input."""
        hex_color = cls._to_hex(color_input, is_normalized=is_normalized)
        return str.__new__(cls, hex_color)

    def __init__(
        self,
        color_input: "Color" | ColorLike,
        name: str | None = None,
        is_normalized: bool = False,
    ):
        """Initialize Color attributes."""
        object.__setattr__(self, "input", color_input)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "is_normalized", is_normalized)

    def __hash__(self):
        """Return the hash of the color string."""
        return hash(str(self))

    @classmethod
    def _rgb_str_to_hex(
        cls,
        rgb_string: str,
        is_normalized: bool = False,
    ) -> str:
        """Convert an 'rgb(...)' string to a hex color."""
        if (not is_normalized and re.match(r"^rgb\(\d*,\d*,\d*\)$", rgb_string)) or (
            is_normalized and re.match(r"^rgb\(\d*\.?\d*,\d*\.?\d*,\d*\.?\d*\)$", rgb_string)
        ):
            rgb_str_list = rgb_string[4:-1].split(",")
            if is_normalized:
                rgb_tuple = tuple(float(v) for v in rgb_str_list)
            else:
                rgb_tuple = tuple(int(v) for v in rgb_str_list)
            return cls._rgb_tuple_to_hex(rgb_tuple, is_normalized=is_normalized)
        raise ValueError(f"Invalid rgb color: '{rgb_string}'")

    @classmethod
    def _rgba_str_to_hex(
        cls,
        rgba_string: str,
        is_normalized: bool = False,
    ) -> str:
        """Convert an 'rgba(...)' string to a hex color."""
        if (not is_normalized and re.match(r"^rgba\(\d*,\d*,\d*,\d*\.?\d*\)$", rgba_string)) or (
            is_normalized
            and re.match(r"^rgba\(\d*\.?\d*,\d*\.?\d*,\d*\.?\d*,\d*\.?\d*\)$", rgba_string)
        ):
            rgba_str_list = rgba_string[5:-1].split(",")
            if float(rgba_str_list[-1]) > 1:
                raise ValueError(
                    f"Invalid alpha value (must be float between 0 and 1): '{rgba_string}'"
                )
            if is_normalized:
                rgba_tuple = tuple(float(v) for v in rgba_str_list)
            else:
                rgba_tuple = tuple(
                    int(v) if i < 3 else float(v) for i, v in enumerate(rgba_str_list)
                )
            return cls._rgba_tuple_to_hex(rgba_tuple, is_normalized=is_normalized)
        raise ValueError(f"Invalid rgba color: '{rgba_string}'")

    @classmethod
    def _rgb_tuple_to_hex(
        cls,
        rgb_tuple: Tuple[int, ...] | Tuple[float, ...],
        is_normalized: bool = False,
    ) -> str:
        """Convert an RGB tuple to a hex color string."""
        if is_normalized:
            rgb_tuple = tuple(int(v * 255) for v in rgb_tuple)
        is_all_int = all(isinstance(v, int | np.integer) for v in rgb_tuple)
        is_all_in_range = all(0 <= v <= 255 for v in rgb_tuple)
        if is_all_int and is_all_in_range:
            return "#{:02X}{:02X}{:02X}".format(*rgb_tuple)
        raise ValueError(f"Invalid rgb tuple: '{rgb_tuple}'")

    @classmethod
    def _rgba_tuple_to_hex(
        cls,
        rgba_tuple: Tuple[int | float, ...],
        is_normalized: bool = False,
    ) -> str:
        """Convert an RGBA tuple to a hex color string."""
        if is_normalized:
            rgba_tuple = tuple(int(v * 255) if i < 3 else v for i, v in enumerate(rgba_tuple))
        is_all_int = all(isinstance(v, int | np.integer | float | np.floating) for v in rgba_tuple)
        is_all_in_range = all(
            0 <= v <= 255 if i < 3 else 0 <= v <= 1 for i, v in enumerate(rgba_tuple)
        )
        if is_all_int and is_all_in_range:
            rgba_tuple = tuple(int(v) if i < 3 else float(v) for i, v in enumerate(rgba_tuple))
            rgba_int_tuple = tuple(
                int(v) if i < 3 else int(float(v) * 255) for i, v in enumerate(rgba_tuple)
            )
            return "#{:02X}{:02X}{:02X}{:02X}".format(*rgba_int_tuple)
        raise ValueError(f"Invalid rgba tuple: '{rgba_tuple}'")

    @classmethod
    def _hex_str_to_hex(
        cls,
        hex_string: str,
    ) -> str:
        """Normalize a hex string to standard 6- or 8-character format."""
        c = hex_string.upper()
        if re.match(r"^#[A-F0-9]{3}$", c):
            c = f"#{c[1] * 2}{c[2] * 2}{c[3] * 2}"
        elif re.match(r"^#[A-F0-9]{4}$", c):
            c = f"#{c[1] * 2}{c[2] * 2}{c[3] * 2}{c[4] * 2}"
        if not re.match(r"^#[A-F0-9]{6}$", c) and not re.match(r"^#[A-F0-9]{8}$", c):
            raise ValueError(f"Invalid hex color: '{hex_string}'")
        return c

    @classmethod
    def _to_hex(
        cls,
        color: str | Sequence,
        is_normalized: bool = False,
    ) -> str:
        """Convert a color input of various formats to a hex string."""
        if isinstance(color, str):
            c_str = color.strip().replace(" ", "").lower()
            if c_str.startswith("#"):
                return cls._hex_str_to_hex(c_str)
            elif c_str.startswith("rgb("):
                return cls._rgb_str_to_hex(c_str)
            elif c_str.startswith("rgba("):
                return cls._rgba_str_to_hex(c_str)
            elif c_str.startswith("rgb255("):
                return cls._rgb_str_to_hex(c_str.replace("rgb255(", "rgb("))
            elif c_str.startswith("rgba255("):
                return cls._rgba_str_to_hex(c_str.replace("rgba255(", "rgba("))
            elif c_str.startswith("rgb01("):
                return cls._rgb_str_to_hex(c_str.replace("rgb01(", "rgb("), is_normalized=True)
            elif c_str.startswith("rgba01("):
                return cls._rgba_str_to_hex(c_str.replace("rgba01(", "rgba("), is_normalized=True)
            else:
                try:
                    return EC_COLORS[color].upper()
                except KeyError:
                    pass
                return mcolors.to_hex(color).upper()
        elif isinstance(color, (Sequence, np.ndarray)):
            if len(color) > 0:
                if isinstance(color[0], float):
                    is_normalized = True
                else:
                    is_normalized = False
            c_tup = tuple(float(v) for v in color)
            if len(c_tup) == 3:
                if is_normalized:
                    c_tup = tuple(float(v) for v in color)
                else:
                    c_tup = tuple(int(v) for v in color)
                return cls._rgb_tuple_to_hex(c_tup, is_normalized=is_normalized)
            elif len(c_tup) == 4:
                return cls._rgba_tuple_to_hex(c_tup, is_normalized=is_normalized)
        raise TypeError(f"Invalid type for input color ({type(color)}: {color})")

    @property
    def hex(self) -> str:
        """Returns the hex color string."""
        return str(self).upper()

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Returns the RGB tuple with values in the 0-255 range."""
        hex_str = self.lstrip("#")
        return (
            int(hex_str[0:2], 16),
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
        )

    @property
    def alpha(self) -> float:
        """Returns the transparency alpha value in the 0-1 range."""
        if len(self) == 9:
            return int(str(self).upper()[7::], 16) / 255
        return 1.0

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        """Returns the RGBA tuple with values in the 0-1 range."""
        hex_str = self.lstrip("#")
        return (
            int(hex_str[0:2], 16) / 255,
            int(hex_str[2:4], 16) / 255,
            int(hex_str[4:6], 16) / 255,
            self.alpha,
        )

    def set_alpha(self, value: float) -> "Color":
        """Returns the same color with the given transparency alpha value applied."""
        if not 0 <= value <= 1:
            raise ValueError(f"Invalid alpha value: '{value}' (must be in the 0-1 range)")
        return Color(self.hex[0:7] + "{:02X}".format(int(value * 255)), name=self.name)

    def blend(self, value: float, blend_color: "Color" | ColorLike = "white") -> "Color":
        """Returns the same color blended with a second color."""
        original_color = self.rgb
        blend_color = Color(blend_color).rgb
        new_color = Color(
            tuple(
                int(round((1 - value) * bc + value * oc))
                for oc, bc in zip(original_color, blend_color)
            )
        )
        return new_color

    @classmethod
    def from_optional(
        cls,
        color_input: "Color" | ColorLike | None,
        alpha: float | None = None,
    ) -> Union["Color", None]:
        """Parses optional color input and returns a `Color` instance or `None`."""
        if color_input is None:
            return None
        elif isinstance(alpha, float):
            return cls(color_input).set_alpha(alpha)
        elif color_input == "none":
            return None
        return cls(color_input)

    def is_close_to_white(self, threshold: float = 0.1) -> bool:
        """Check if the color is close to white."""
        rgb01 = 1 - (np.array(self.rgb) / 255)
        return bool(np.all(rgb01 < threshold))

    def get_best_bw_contrast_color(self) -> "Color":
        """
        Return black or white color depending on best contrast according to WCAG 2.0.

        See https://www.w3.org/TR/WCAG20/
        """
        return Color(get_best_bw_contrast_color(self.rgb))
