import numpy as np


def get_decimal_shift(x: float) -> int:
    """Returns the base-10 exponent needed to scale `x` into the range [1.0, 10.0).

    For example:
        - x = 0.00034 -> exponent = 4  -> x * 10**4  = 3.4
        - x = 0.564   -> exponent = 1  -> x * 10**1  = 5.64
        - x = 1234.5  -> exponent = -3 -> x * 10**-3 = 1.2345
    """
    if x == 0:
        return 0
    return -int(np.floor(np.log10(abs(x))))
