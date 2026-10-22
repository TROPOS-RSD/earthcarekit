from ..._typing import NonEmptyTuple, _LazyDataset, _VarTransformer
from ..._variable import LazyVariable


def combine(
    trans1: _VarTransformer[LazyVariable],
    trans2: _VarTransformer[LazyVariable],
) -> _VarTransformer[LazyVariable]:
    def transformer(
        lds: _LazyDataset[LazyVariable], lvar: LazyVariable
    ) -> NonEmptyTuple[LazyVariable]:
        lvar = trans1(lds, lvar)[0]
        return trans2(lds, lvar)

    return transformer


def combine_dicts(
    dict1: dict[str, _VarTransformer], dict2: dict[str, _VarTransformer]
) -> dict[str, _VarTransformer]:
    for var, trans in dict1.items():
        if var in dict2:
            dict2[var] = combine(trans, dict2[var])
        else:
            dict2[var] = trans
    return dict2
