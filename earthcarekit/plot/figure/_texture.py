from cartopy.mpl.feature_artist import FeatureArtist  # type: ignore
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.offsetbox import AnchoredOffsetbox
from matplotlib.patches import Rectangle
from matplotlib.text import Text


def remove_rectangles(fig: Figure) -> None:
    for c in fig.get_children():
        if isinstance(c, Rectangle):
            c.set_alpha(0)


def remove_images(ax: Axes | None) -> None:
    if not ax:
        return
    for img in ax.get_images():
        img.remove()


def remove_features(ax: Axes | None) -> None:
    if not ax:
        return
    for c in ax.get_children():
        if isinstance(c, FeatureArtist):
            c.remove()


def remove_arists(ax: Axes | None) -> None:
    if not ax:
        return
    for artist in reversed(ax.artists):
        if isinstance(artist, (Text, AnchoredOffsetbox)):
            artist.remove()


def remove_axis_grid_ticks_labels(ax: Axes | None) -> None:
    if ax:
        ax.axis("off")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        ax.grid(False)
        ax.set_facecolor("none")


def remove_white_frame_around_figure(fig: Figure) -> None:
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)


def remove_colorbar(colorbar: Colorbar | None) -> None:
    if colorbar:
        colorbar.remove()


def remove_legend(legend: Legend | None) -> None:
    if legend:
        legend.remove()
