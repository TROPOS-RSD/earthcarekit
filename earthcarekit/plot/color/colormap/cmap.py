from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import (
    BoundaryNorm,
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    Normalize,
)

from ..color import Color, ColorLike


def copy_extremes(cmap: Union[Colormap, "Cmap"], new_cmap: "Cmap") -> "Cmap":
    new_cmap._rgba_bad = cmap._rgba_bad  # type: ignore
    new_cmap._rgba_over = cmap._rgba_over  # type: ignore
    new_cmap._rgba_under = cmap._rgba_under  # type: ignore
    return new_cmap


def colormap_to_opaque(cmap, N=256):
    if cmap.is_categorical:
        colors = cmap.colors
    else:
        colors = cmap(np.linspace(0, 1, N))
    colors = [Color(c, is_normalized=True) for c in colors]

    colors = [c.set_alpha(1) for c in colors]
    new_cmap = Cmap(
        colors,
        name=cmap.name + "_opaque",
    ).to_categorical(dict(zip(cmap.values, cmap.labels)))
    new_cmap = copy_extremes(cmap, new_cmap)
    return new_cmap


def colormap_to_alphamap(cmap, N=256):
    if cmap.is_categorical:
        colors = cmap.colors
    else:
        colors = cmap(np.linspace(0, 1, N))
    colors = [Color(c, is_normalized=True) for c in colors]

    alpha = [c.alpha for c in colors]
    colors = [Color("black").blend(1 - a) for a in alpha]
    new_cmap = Cmap(colors, name=cmap.name + "_alphamap").to_categorical(
        dict(zip(cmap.values, cmap.labels))
    )
    new_cmap = copy_extremes(cmap, new_cmap)
    return new_cmap


def colormap_to_blended(cmap, N=256):
    if cmap.is_categorical:
        colors = cmap.colors
    else:
        colors = cmap(np.linspace(0, 1, N))
    colors = [Color(c, is_normalized=True) for c in colors]

    colors = [c.blend(c.alpha) for c in colors]
    new_cmap = Cmap(colors, name=cmap.name + "_blended").to_categorical(
        dict(zip(cmap.values, cmap.labels))
    )
    new_cmap = copy_extremes(cmap, new_cmap)
    return new_cmap


class Cmap(ListedColormap):
    def __init__(
        self,
        colors,
        name: str = "colormap",
        N: int | None = None,
        categorical: bool = False,
        ticks: List[float] | None = None,
        labels: List[str] | None = None,
        norm: Normalize | None = None,
        values: List | None = None,
        gradient: bool = False,
        circular: bool = False,
    ):
        colors = [Color(c) if isinstance(c, str) else c for c in colors]

        if gradient:
            tmp_cmap = LinearSegmentedColormap.from_list("tmp_cmap", colors, N=256)
            colors = [tmp_cmap(i) for i in range(256)]

        super().__init__(colors, name=name, N=N or len(colors))
        self.categorical = categorical
        self.gradient = gradient
        self.circular = circular
        self.ticks = ticks or []
        self.labels = labels or []
        self.norm = norm
        self.values = values or []

    @classmethod
    def from_colormap(cls, cmap: Colormap, N: int = 256) -> "Cmap":
        if isinstance(cmap, cls):
            return cmap
        elif isinstance(cmap, ListedColormap):
            colors = cmap.colors
            if isinstance(colors, np.ndarray) and colors.ndim == 2:
                N = len(colors)
            else:
                N = cmap.N
        else:
            colors = [cmap(x) for x in np.linspace(0, 1, N)]

        new_cmap = cls(colors, name=cmap.name, N=N)
        new_cmap = copy_extremes(cmap, new_cmap)
        return new_cmap

    def to_categorical(
        self,
        values_to_labels: Dict[Any, str] | int,
        endpoint: bool | None = None,
        use_discrete: bool | None = None,
    ) -> "Cmap":
        if isinstance(values_to_labels, int):
            values_to_labels = {i: str(i) for i in range(values_to_labels)}
        keys = list(values_to_labels.keys())
        labels = list(values_to_labels.values())
        sorted_values = sorted(keys)

        n_classes = len(sorted_values)
        bounds = np.array(sorted_values + [sorted_values[-1] + 1]) - 0.5
        norm = BoundaryNorm(bounds, n_classes)

        ticks = [t for t in np.arange(0.5, n_classes)]

        if use_discrete:
            colors = [self(i) for i in range(n_classes)]
        else:
            if not isinstance(endpoint, bool):
                endpoint = not self.circular
            offset = -1 if endpoint else 0
            colors = [self(i / max(n_classes + offset, 1)) for i in range(n_classes)]

        return Cmap(
            colors=colors,
            name=self.name,
            N=n_classes,
            categorical=True,
            gradient=False,
            circular=self.circular,
            ticks=ticks,
            labels=labels,
            norm=norm,
            values=sorted_values,
        )

    def set_alpha(self, value: float) -> "Cmap":
        """Returns the same colormap with the given transparency alpha value applied."""
        if not 0 <= value <= 1:
            raise ValueError(
                f"Invalid alpha value: '{value}' (must be in the 0-1 range)"
            )

        new_cmap = Cmap(
            colors=[Color(c).set_alpha(value) for c in np.asarray(self.colors)],
            name=self.name,
            N=self.N,
            categorical=self.categorical,
            gradient=self.gradient,
            circular=self.circular,
            ticks=self.ticks,
            labels=self.labels,
            norm=self.norm,
        )

        if self._rgba_bad is not None:  # type: ignore
            new_cmap._rgba_bad = Color(self._rgba_bad, is_normalized=True).set_alpha(value).rgba  # type: ignore
        if self._rgba_over is not None:  # type: ignore
            new_cmap._rgba_over = Color(self._rgba_over, is_normalized=True).set_alpha(value).rgba  # type: ignore
        if self._rgba_under is not None:  # type: ignore
            new_cmap._rgba_under = Color(self._rgba_under, is_normalized=True).set_alpha(value).rgba  # type: ignore

        return new_cmap

    def blend(self, value: float, blend_color: Color | ColorLike = "white") -> "Cmap":
        """Returns the same colormap beldned with a second color."""
        if not 0 <= value <= 1:
            raise ValueError(
                f"Invalid blend value: '{value}' (must be in the 0-1 range)"
            )

        new_cmap = Cmap(
            colors=[
                Color(c).blend(value, blend_color) for c in np.asarray(self.colors)
            ],
            name=self.name,
            N=self.N,
            categorical=self.categorical,
            gradient=self.gradient,
            circular=self.circular,
            ticks=self.ticks,
            labels=self.labels,
            norm=self.norm,
        )

        if self._rgba_bad is not None:  # type: ignore
            new_cmap._rgba_bad = Color(self._rgba_bad, is_normalized=True).blend(value, blend_color).rgba  # type: ignore
        if self._rgba_over is not None:  # type: ignore
            new_cmap._rgba_over = Color(self._rgba_over, is_normalized=True).blend(value, blend_color).rgba  # type: ignore
        if self._rgba_under is not None:  # type: ignore
            new_cmap._rgba_under = Color(self._rgba_under, is_normalized=True).blend(value, blend_color).rgba  # type: ignore

        return new_cmap

    @property
    def rgba_list(self) -> list[tuple[float, ...]]:
        return [Color(c, is_normalized=True).rgba for c in np.array(self.colors)]

    # def set_alpha_gradient(self, alpha_input: list) -> "Cmap":
    #     from matplotlib.colors import ListedColormap
    #     from scipy.interpolate import interp1d

    #     # Interpolate to 256 values
    #     n_colors = 256
    #     x_old = np.linspace(0, 1, len(alpha_input))
    #     x_new = np.linspace(0, 1, n_colors)
    #     alpha_interp = interp1d(x_old, alpha_input, kind="linear")(x_new)

    #     # Get base colormap and apply interpolated alpha
    #     colors = self(np.linspace(0, 1, n_colors))
    #     colors[:, 3] = alpha_interp  # Replace alpha channel

    #     # Create transparent colormap
    #     new_cmap = Cmap(colors, name=self.name)

    @property
    def opaque(self) -> "Cmap":
        return colormap_to_opaque(self)

    @property
    def alphamap(self) -> "Cmap":
        return colormap_to_alphamap(self)

    @property
    def blended(self) -> "Cmap":
        return colormap_to_blended(self)

    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], Colormap):
            return cls.from_colormap(args[0])
        return super().__new__(cls)
