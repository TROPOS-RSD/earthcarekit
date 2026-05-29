from matplotlib.colors import Colormap

from ._cmap import Cmap
from ._combine_mpl_cmaps import combine_mpl_cmaps
from ._get_cmap import get_cmap


def combine_cmaps(
    cmap1: str | Colormap | None,
    cmap2: str | Colormap | None,
    name: str = "combined_cmap",
    n: int = 256,
) -> Cmap:
    """Create a combined colormap from two colormaps.

    Args:
        cmap1 (str | Colormap | None): Colormap to be modified.
        cmap2 (str | Colormap | None): Colormap to be modified
        name (str): New colormap name. Defaults to "combined_cmap".
        n (int): Number of colors.

    Returns:
        Cmap: The combined colormap.
    """
    return get_cmap(
        combine_mpl_cmaps(
            cmap1=get_cmap(cmap1),
            cmap2=get_cmap(cmap2),
            name=name,
            n=n,
        ),
    )
