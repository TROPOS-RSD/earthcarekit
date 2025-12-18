from typing import Any

from xarray import Dataset


def insert_var(
    ds: Dataset,
    var: str,
    data: Any,
    index: int | None = None,
    before_var: str | None = None,
    after_var: str | None = None,
) -> Dataset:
    """
    Inserts a new variable in a `xarray.Dataset` before or after a given variable or at a given index.

    Args:
        ds (Dataset):
            The original dataset to which the variable will be added.
        var (str):
            Name of the new variable to be added.
        data (Any):
            Data stored in the new variable.
        index (int | None, optional):
            Index at which the new variable will be added. Will be ignored when either `before_var` or
            `after_var` are given and valid. Defaults to None.
        before_var (str | None, optional):
            Name of the variable before which the new variable should be inserted. Defaults to None.
        after_var (str | None, optional):
            Name of the variable after which the new variable should be inserted. Will be ignored
            when `before_var` is given and valid. Defaults to None.

    Returns:
        Dataset: The original dataset with the new variable inserted.
    """
    if var in ds.data_vars:
        ds = ds.drop_vars(var)

    if (
        isinstance(index, int)
        or isinstance(before_var, str)
        or isinstance(after_var, str)
    ):
        vars = list(ds.data_vars)

        if isinstance(before_var, str) and before_var in vars:
            index = vars.index(before_var)
        elif isinstance(after_var, str) and after_var in vars:
            index = vars.index(after_var) + 1
        elif not isinstance(index, int):
            index = len(vars)

        vars.insert(index, var)

        ds[var] = data
        ds = ds[vars]
    else:
        ds[var] = data

    return ds
