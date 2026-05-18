from matplotlib.colors import Colormap


def rename_cmap(cmap: Colormap, name: str) -> Colormap:
    """Returns the given `cmap` with the new `name`."""
    result_cmap = cmap.copy()
    result_cmap.name = name
    return result_cmap
