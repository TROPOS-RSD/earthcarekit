from matplotlib.colors import LinearSegmentedColormap


def get_cmap():
    name = "labview"
    colors = ["#0043DC", "#00AAC7", "#4FEE25", "#FEF900", "#FF7F00", "#FF1200"]
    positions = [0.0, 0.19929453, 0.3633157, 0.6031746, 0.7707231, 1.0]
    color_dict = list(zip(positions, colors))
    cmap = LinearSegmentedColormap.from_list(name, color_dict).with_extremes(
        under="#000000", bad="#000000"
    )
    return cmap
