from typing import Dict, Tuple

from pyteal import ABITuple, CompileOptions, Expr, TealBlock, TealSimpleBlock, TealType


class Struct(Expr):
    value: ABITuple
    name_idx: Dict[str, int]

    def __post_init__(self):

        type_list = [v.__class__ for v in self.__dict__.values()]
        self.value = ABITuple[type_list](self.__dict__.values())

        self.name_idx = {f.name: idx for idx, f in enumerate(self.__dict__.keys())}

    def __teal__(self, options: "CompileOptions") -> Tuple[TealBlock, TealSimpleBlock]:
        return self.value.__teal__(options)

    def has_return(self) -> bool:
        return self.value.has_return()

    def type_of(self) -> TealType:
        return self.value.type_of()

    def __str__(self):
        return ""

    def get(self, name: str):
        return self.value[self.name_idx[name]]
