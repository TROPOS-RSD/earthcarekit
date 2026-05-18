import matplotlib.patheffects as pe
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnchoredText

from ...color import Color, ColorLike


def add_text(
    ax: Axes,
    text: str,
    loc: str = "upper right",
    borderpad: float = 0,
    pad: float = 0.4,
    fontsize: str | float | None = None,
    fontweight: str | None = None,
    horizontalalignment: str = "left",
    color: Color | ColorLike | None = "black",
    is_shaded_text: bool = True,
    shade_linewidth: float = 3,
    shade_color: str = "white",
    shade_alpha: float = 0.8,
    is_box: bool = False,
    append_to: AnchoredText | str | None = None,
    zorder: int | float | None = None,
) -> AnchoredText:
    """
    Adds anchored text to a matplotlib Axes with optional shading and styling.

    Args:
        ax (matplotlib.axes.Axes): Target matplotlib Axes.
        text (str): Text string to display.
        loc (str): Anchor location in the Axes (e.g. 'upper right').
        borderpad (float): Padding between text and the border of the box.
        pad (float): Padding between box and the Axes.
        fontsize (str or float, optional): Font size of the text.
        fontweight (str, optional): Font weight (e.g. 'normal', 'bold').
        horizontalalignment (str): Horizontal alignment of the text.
        color (Color or ColorLike, optional): Text color.
        is_shaded_text (bool): If True, apply a white stroke around the text.
        shade_linewidth (float): Width of the stroke line.
        shade_color (str): Color of the stroke.
        shade_alpha (float): Opacity of the stroke.
        is_box (bool): If True, draw a box around the text.
        append_to (AnchoredText or str, optional): Extracts the given text string and adds the new text to it.
        zorder (int | float, optional): Drawing order of the plot element.

    Returns:
        AnchoredText: The text artist added to the Axes.
    """
    old_text: str | None = None
    if isinstance(append_to, AnchoredText):
        old_text = append_to.txt.get_text()
        append_to.remove()
    elif isinstance(append_to, str):
        old_text = append_to

    if isinstance(old_text, str):
        text = f"{old_text}{text}"

    path_effects = None
    if is_shaded_text:
        path_effects = [
            pe.withStroke(
                linewidth=shade_linewidth,
                foreground=shade_color,
                alpha=shade_alpha,
            )
        ]

    text_properties = {
        "size": fontsize,
        "fontweight": fontweight,
        "horizontalalignment": horizontalalignment,
        "path_effects": path_effects,
        "color": color,
    }

    anchored_text = AnchoredText(
        text,
        loc=loc,
        borderpad=borderpad,
        pad=pad,
        prop=text_properties,
        frameon=is_box,
        zorder=zorder,
    )
    ax.add_artist(anchored_text)
    return anchored_text
