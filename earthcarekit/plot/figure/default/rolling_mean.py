import xarray as xr

from ....read import FileType


def get_default_rolling_mean(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> int | None:

    if file_type is not None and not isinstance(file_type, FileType):
        try:
            file_type = FileType.from_input(file_type)
        except ValueError:
            pass

    if var in [
        "mie_attenuated_backscatter",
        "rayleigh_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
        "crosspolar_attenuated_backscatter_10km",
        "crosspolar_attenuated_backscatter_1km",
    ]:
        return 20
    if var in [
        "mie_total_attenuated_backscatter_355nm",
        "attenuated_backscatter_10km",
        "attenuated_backscatter_1km",
    ]:
        return 1
    return None
