from ..._lazy_variable import LazyVariable
from ..._typing import _LazyDataset, _VarTransformer


def _edit_attrs(attrs: dict[str, str]) -> _VarTransformer:
    def transformer(lds: _LazyDataset[LazyVariable], lvar: LazyVariable) -> tuple[LazyVariable]:
        lvar.attrs = {**lvar.attrs, **attrs}

        return (lvar,)

    return transformer
