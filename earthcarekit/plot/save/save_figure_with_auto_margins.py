import os

from matplotlib.figure import Figure

from ...utils.typing import HasFigure


def save_figure_with_auto_margins(
    figure: Figure | HasFigure,
    filename: str,
    pad: float = 0.0,
    dpi: float | None = None,
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

    if dpi is None:
        dpi = fig.dpi

    _, extension = os.path.splitext(filename)
    if extension.lower() in [".pdf", ".svg", ".eps"]:
        dpi = 72

    kwargs["bbox_inches"] = "tight"

    fig.savefig(filename, pad_inches=pad, dpi=dpi, **kwargs)
