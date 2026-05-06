from ...typing import NumberPairLike


def _validate_figsize(figsize: NumberPairLike) -> tuple[float, float]:
    return (float(figsize[0]), float(figsize[1]))
