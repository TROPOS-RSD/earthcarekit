from matplotlib.figure import Figure

from ...utils.typing import HasFigure


def save_figure_with_auto_margins(
    figure: Figure | HasFigure,
    filename: str,
    pad: float = 0.1,
    **kwargs,
) -> None:
    """
    Save a figure as an image or vector graphic to a file.

    Args:
        figure (Figure | HasFigure): A figure object (`matplotlib.figure.Figure`) or objects exposing a `.fig` attribute containing a figure (e.g., `CurtainFigure`).
        filename (str): The path where the image is saved.
        pad (float): Extra padding (i.e., empty space) around the image in inches. Defaults to 0.1.
        **kwargs (dict[str, Any]): Keyword arguments passed to wrapped function call of `matplotlib.pyplot.savefig`.
    """
    if isinstance(figure, Figure):
        fig = figure
    else:
        fig = figure.fig

    # Get original sizes
    original_size: tuple[float, float] = tuple(fig.get_size_inches())
    original_positions = {}
    for ax in fig.get_axes():
        original_positions[ax] = ax.get_position()

    fig.canvas.draw()

    # Get the bounding box of all figure elements in inches
    bbox = fig.get_tightbbox(fig.canvas.get_renderer())  # type: ignore

    # Calculate required padding on each side in inches
    pad_left = max(0, -bbox.x0)
    pad_right = max(0, bbox.x1 - original_size[0])
    pad_bottom = max(0, -bbox.y0)
    pad_top = max(0, bbox.y1 - original_size[1])

    # Add extra outside padding
    pad_left += pad
    pad_right += pad
    pad_bottom += pad
    pad_top += pad

    # Calculate new figure size
    new_width = original_size[0] + pad_left + pad_right
    new_height = original_size[1] + pad_bottom + pad_top

    # Resize figure
    fig.set_size_inches(new_width, new_height)

    # Reposition all axes to account for padding
    for ax in fig.get_axes():
        old_pos = original_positions[ax]
        ax.set_position(
            (
                (old_pos.x0 * original_size[0] + pad_left) / new_width,
                (old_pos.y0 * original_size[1] + pad_bottom) / new_height,
                (old_pos.width * original_size[0]) / new_width,
                (old_pos.height * original_size[1]) / new_height,
            )
        )

    # Save figure as an image
    fig.savefig(filename, **kwargs)

    # Restore original settings
    for ax in fig.get_axes():
        ax.set_position(original_positions[ax])
    fig.set_size_inches(original_size)
