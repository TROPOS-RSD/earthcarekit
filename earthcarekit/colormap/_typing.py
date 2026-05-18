from typing import Callable, Sequence, TypeAlias

from matplotlib.colors import Colormap
from numpy.typing import ArrayLike

from ._cmap import Cmap

CmapFn: TypeAlias = Callable[..., Cmap]
CmapLike: TypeAlias = str | Colormap | Sequence | ArrayLike
