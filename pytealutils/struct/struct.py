from typing import Dict, List

from pyteal.ast.abi_collections import ABITuple
from pyteal.ast.abi_type import ABIType


class StructField:
    def __init__(self, name: str, type: ABIType):
        self.name = name
        self.type = type


class Struct(ABITuple):
    fields: List[StructField]
    value: ABITuple
    name_idx: Dict[str, int]

    def __init__(self, *fields: StructField):
        self.fields = fields
        self.codec = ABITuple([f.type for f in fields])
        self.name_idx = {f.name: idx for idx, f in enumerate(fields)}
        print(self.name_idx)

    def __call__(self, *values: ABIType):
        self.value = self.codec(*values)
        return self

    def get(self, name: str):
        return self.value[self.name_idx[name]]
