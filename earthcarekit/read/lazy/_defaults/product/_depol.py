from .....constants import DEPOL_LABEL
from ..._typing import NonEmptyTuple, _LazyDataset, _VarTransformer
from ..._variable import LazyVariable


def get_depol_transformer() -> _VarTransformer:

    def tranformer(
        lds: _LazyDataset[LazyVariable], lvar: LazyVariable
    ) -> NonEmptyTuple[LazyVariable]:
        long_name = DEPOL_LABEL
        if lvar.varname.startswith("10km"):
            long_name = f"Aer. {long_name.lower()}"
        elif lvar.varname.startswith("cloud"):
            long_name = f"Cloud {long_name.lower()}"

        if lvar.varname.endswith("10km"):
            long_name = f"{long_name} (10km)"
        elif lvar.varname.endswith("1km"):
            long_name = f"{long_name} (1km)"

        lvar.values *= 0.01
        lvar.attrs["label"] = long_name
        lvar.attrs["units"] = ""
        lvar.attrs["valid_range"] = "[0, 1]"
        lvar.attrs["earthcarekit"] = (
            "Modified by earthcarekit: Converted from percantage to decimal"
        )
        return (lvar,)

    return tranformer


def get_depol_tranformers(*vars: str) -> dict[str, _VarTransformer]:
    return {v: get_depol_transformer() for v in vars}
