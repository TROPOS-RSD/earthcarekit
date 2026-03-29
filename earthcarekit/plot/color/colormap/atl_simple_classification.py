
from ..color import Color
from .cmap import Cmap

cmap_data = [
    [-3, "#E6E6E6", "Missing"],
    [-2, "#000000", "Surface"],
    [-1, "#999999", "Attenuated"],
    [0, "#FFFFFF", "Clear"],
    [1, "#0000FF", "Liquid cloud"],
    [2, "#00FFFF", "Ice cloud"],
    [3, "#DEB887", "Aerosol"],
    [4, "#800080", "Strat. cloud"],
    [5, "#FF00FF", "Strat. aerosol"],
]


def apply_alpha(t, kw):
    """apply cmap_data tupel t from the keyword arg dict"""
    if any([t[2].lower() in s for s in kw.keys()]):
        return Color(t[1]).set_alpha(kw[f"alpha_{t[2].lower()}"])
    else:
        return Color(t[1]).set_alpha(kw["alpha"])


def get_cmap(
    alpha_clear: float = 1.0,
    alpha_missing: float = 1.0,
    alpha_attenuated: float = 1.0,
    alpha: float = 1.0,
):
    kw = locals()
    colors = [apply_alpha(t, kw) for t in cmap_data]
    definitions: dict = {k: label for k, _, label in cmap_data}
    cmap = Cmap(colors=colors, name="atl_simple_classification").to_categorical(
        definitions
    )
    return cmap
