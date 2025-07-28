from typing import Final

EC_LATITUDE_FRAME_BOUNDS: Final[dict[str, list[float]]] = {
    "A": [-22.5, 22.5],
    "B": [22.5, 67.5],
    "C": [67.5, 67.5],
    "D": [67.5, 22.5],
    "E": [22.5, -22.5],
    "F": [-22.5, -67.5],
    "G": [-67.5, -67.5],
    "H": [-67.5, -22.5],
}
