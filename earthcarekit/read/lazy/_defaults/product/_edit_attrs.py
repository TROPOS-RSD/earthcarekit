from ..._typing import _LazyDataset, _VarTransformer
from ..._variable import LazyVariable


def _edit_attrs(attrs: dict[str, str]) -> _VarTransformer:
    def transformer(lds: _LazyDataset[LazyVariable], lvar: LazyVariable) -> tuple[LazyVariable]:
        lvar.attrs = {**lvar.attrs, **attrs}

        return (lvar,)

    return transformer
