# Working With Profiles

This tutorial gives a short introduction to the [`ProfileData`][earthcarekit.ProfileData] class and it's use in `earthcarekit`.

Begin by importing the following modules:

```python
import earthcarekit as eck
import numpy as np
import pandas as pd
```

The class [`ProfileData`][earthcarekit.ProfileData] is a container for atmospheric profile data.
It stores profile values together with their time/height bins and, optionally, their coordinates and metadata in a consistent structure, making profiles easier to handle, compare and visualise.

## Initialisation

[`ProfileData`][earthcarekit.ProfileData] requires at least three inputs:

- **values** - the profile data, either of a single vertical profile or a time series of profiles (2D array with time as the first dimension and height as the second).
- **height** - an array or time series of arrays of ascending height bin centers.
- **time** - an array of ascending timestamps corresponding to the profiles.

```python
p = eck.ProfileData(
    values=[[0, 0.4, 1, 1, 0.6, 0]],
    height=[0e3, 5e3, 10e3, 15e3, 20e3, 25e3],
    time=["2025-01-01T00:00"],
)
print(p)
```

Output:
```
ProfileData(values=array([[0. , 0.4, 1. , 1. , 0.6, 0. ]]), height=array([    0.,  5000., 10000., 15000., 20000., 25000.]), time=array(['2025-01-01T00:00:00.000000000'], dtype='datetime64[ns]'), latitude=None, longitude=None, color=None, label=None, units=None, platform=None, error=None)
```