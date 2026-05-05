import numpy as np


def alpha_to_hex(alpha: float) -> str:
    """Converts transparency alpha value between 0 and 1 to 2 digit hex value."""
    return hex(int(np.round(255 * alpha)))[-2::]
