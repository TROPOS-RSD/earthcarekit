import matplotlib.patheffects as pe
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnchoredText
from matplotlib.transforms import Bbox

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
    fig: Figure | None = None,
) -> AnchoredText:
    """Add anchored text to a matplotlib Axes with optional shading and styling.

    Args:
        ax: Target matplotlib Axes.
        text: Text string to display.
        loc: Anchor location in the Axes (e.g., "upper right").
        borderpad: Padding between text and the box border.
        pad: Padding between box and the Axes.
        fontsize: Font size of the text.
        fontweight: Font weight (e.g., "normal", "bold").
        horizontalalignment: Horizontal alignment of the text.
        color: Text color.
        is_shaded_text: If True, apply a stroke around the text.
        shade_linewidth: Width of the stroke line.
        shade_color: Color of the stroke.
        shade_alpha: Opacity of the stroke.
        is_box: If True, draw a box around the text.
        append_to: Extracts the given text string and adds the new text to it.
        zorder: Drawing order of the plot element.
        fig: Target matplotlib Figure; if given, text artists are added to the figure instead of `ax`.

    Returns:
        The text artist added to the Axes.
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
    anchored_text.set_bbox_to_anchor(Bbox.from_bounds(0, 0, 1, 1), transform=ax.transAxes)
    if fig:
        fig.add_artist(anchored_text)
    else:
        ax.add_artist(anchored_text)

    return anchored_text
