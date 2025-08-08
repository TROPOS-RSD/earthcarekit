import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class _ParsedColumnName:
    old_name: str
    name: str
    long_name: str
    units: str


def _parse_units(units: str) -> str:

    pattern = re.compile(
        r"(?i)^((mm|msr)(\^?-1)\s*(m|sr)(\^?-1)|(m|sr)(\^?-1)\s*(mm|msr)(\^?-1))$"
    )
    match = pattern.match(units)
    if match:
        return "Mm-1 sr-1"

    pattern = re.compile(r"(?i)^((m)(\^?-1)\s*(sr)(\^?-1)|(sr)(\^?-1)\s*(m)(\^?-1))$")
    match = pattern.match(units)
    if match:
        return "m-1 sr-1"

    pattern = re.compile(r"(?i)^mm(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "Mm-1"

    pattern = re.compile(r"(?i)^m(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "m-1"

    pattern = re.compile(r"(?i)^msr(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "Msr-1"

    pattern = re.compile(r"(?i)^sr(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "sr-1"

    return units


def _parse_column_name(column_name: str) -> _ParsedColumnName:
    old_name: str = column_name
    name: str
    long_name: str
    units: str

    def _clean_string(s: str) -> str:
        s = re.sub(r"[^A-Za-z0-9]", "_", s.strip().lower())
        return re.sub(r"_+", "_", s)

    pattern = re.compile(r"^(.*?)\s*(?:\((.*?)\))?\:?$")
    match = pattern.match(column_name)
    if match:
        name = _clean_string(match.group(1))
        long_name = match.group(1).strip()
        units = match.group(2) if match.group(2) else ""
    else:
        name = _clean_string(column_name)
        long_name = column_name
        units = ""

    return _ParsedColumnName(
        old_name=old_name,
        name=name,
        long_name=long_name,
        units=_parse_units(units),
    )


def _make_column_names_unique(columns: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    unique_columns: list[str] = []
    for col in columns:
        if col not in seen:
            seen[col] = 1
            unique_columns.append(col)
        else:
            count = seen[col]
            new_col = f"{col}_{count}"
            while new_col in seen:
                count += 1
                new_col = f"{col}_{count}"
            seen[col] = count + 1
            seen[new_col] = 1
            unique_columns.append(new_col)
    return unique_columns


def read_polly(input: str | xr.Dataset) -> xr.Dataset:
    """Reads manually processed PollyXT output text files as `xarray.Dataset` or returns an already open one."""

    if isinstance(input, xr.Dataset):
        return input

    with open(input, "r", encoding="utf-8", errors="ignore") as f:
        df = pd.read_csv(f, sep="\t")

    new_columns = [_parse_column_name(c) for c in df.columns]
    new_column_names = [c.name for c in new_columns]
    new_column_names = _make_column_names_unique(new_column_names)
    df.columns = pd.Index(new_column_names)

    ds = xr.Dataset.from_dataframe(df)
    ds = ds.assign_coords(index=ds.height.values)
    ds = ds.rename({"index": "vertical"})
    if "time" not in ds:
        ds = ds.assign({"time": np.datetime64("1970-01-01T00:00:00.000", "ms")})

    vars_order = ["time"] + [v for v in ds.data_vars if v != "time"]
    ds = ds[vars_order]

    for c in new_columns:
        if c.units == "km":
            ds[c.name].values = ds[c.name].values * 1e3
            c.units = c.units.replace("k", "")
        elif c.units in ["Mm-1 sr-1", "Mm-1", "Msr-1"]:
            ds[c.name].values = ds[c.name].values / 1e6
            c.units = c.units.replace("M", "")

        ds[c.name] = ds[c.name].assign_attrs(
            dict(
                long_name=c.long_name,
                units=c.units,
            )
        )
    return ds
