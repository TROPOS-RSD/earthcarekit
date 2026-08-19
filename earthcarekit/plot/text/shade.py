import matplotlib.patheffects as pe
from matplotlib.text import Text

from ...color import Color, ColorLike


def add_shade_to_text(
    t: Text,
    alpha: float = 0.8,
    linewidth: float = 3,
    color: ColorLike | None = None,
) -> Text:
    """Applies a shaded stroke effect around a Matplotlib text object.

    Args:
        t: Text object to modify.
        alpha: Stroke opacity; defaults to 0.8.
        linewidth: Stroke width; defaults to 3.
        color: Stroke color; defaults to "white".

    Returns:
        The text object with the stroke effect applied.
    """

    if color is None:
        c = Color.from_optional(t.get_color())  # type: ignore
        color = c.get_best_bw_contrast_color()  # type: ignore
    else:
        color = Color.from_optional(color)

    t.set_path_effects([pe.withStroke(linewidth=linewidth, foreground=color, alpha=alpha)])
    return t
