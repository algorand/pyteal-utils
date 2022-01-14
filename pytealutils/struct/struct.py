from typing import Dict, List, TypeVar, Sequence, Tuple

from pyteal.ast.abi_collections import ABITuple
from pyteal.ast.abi_type import ABIType

T = TypeVar('T', bound=Sequence[ABIType])

class Struct(ABITuple[T]):
    value: ABITuple
    name_idx: Dict[str, int]

    def __init__(self, *fields: ABIType):
        self.fields = fields
        #self.codec = ABITuple[Tuple[([f.type for f in fields]]]
        self.name_idx = {f.name: idx for idx, f in enumerate(fields)}
        print(self.name_idx)

    def __call__(self, *values: ABIType):
        self.value = self.codec(*values)
        return self

    def get(self, name: str):
        return self.value[self.name_idx[name]]
