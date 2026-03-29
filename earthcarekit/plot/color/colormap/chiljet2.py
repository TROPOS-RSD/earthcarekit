from matplotlib.colors import LinearSegmentedColormap


def get_cmap():
    """
    Based on color index values from the chiljet2 colormap in the 'ectools' project by Shannon Mason (ECMWF):
    https://bitbucket.org/smason/workspace/projects/EC
    Original under Apache 2.0 license.
    """
    name = "chiljet2"
    colors = [
        "#e6e6e6",
        "#0000ff",
        "#008000",
        "#ffff00",
        "#ff0000",
        "#000000",
    ]
    positions = [0.0, 0.2, 0.35, 0.67, 0.9, 1.0]
    color_dict = list(zip(positions, colors))
    cmap = LinearSegmentedColormap.from_list(name, color_dict)
    return cmap
