from pathlib import Path

from .chiljet2 import get_cmap as get_cmap_chiljet2


def get_cmap():
    cmap = get_cmap_chiljet2()
    cmap.name = Path(__file__).stem
    return cmap
