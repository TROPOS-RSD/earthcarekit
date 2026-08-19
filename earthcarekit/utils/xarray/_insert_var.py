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
    """Inserts a new variable into an `xarray.Dataset` at a specified position.

    Args:
        ds: Original dataset.
        var: Name of the new variable.
        data: Data for the new variable.
        index: Insertion index; ignored if `before_var` or `after_var` is valid.
        before_var: Insert before this variable.
        after_var: Insert after this variable; ignored if `before_var` is valid.

    Returns:
        The dataset with the new variable inserted.
    """
    if var in ds.data_vars:
        ds = ds.drop_vars(var)

    if isinstance(index, int) or isinstance(before_var, str) or isinstance(after_var, str):
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
