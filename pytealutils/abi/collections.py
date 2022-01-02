from typing import List, Tuple, TypeVar, Union

from pyteal import *

from ..strings import prefix, rest
from .abi_type import ABIType
from .bytes import *
from .codec_util import *
from .uint import *


class DynamicArray(ABIType):

    stack_type = TealType.bytes

    element_type: TypeVar
    size: ScratchVar
    bytes: ScratchVar
    lengths: ScratchVar
    value: Expr

    def __init__(self, type: ABIType):
        self.element_type = type
        self.size = ScratchVar(TealType.uint64)
        self.bytes = ScratchVar(TealType.bytes)
        self.lengths = ScratchVar(TealType.bytes)

    def __call__(self, data: Bytes) -> "DynamicArray":
        da = DynamicArray(self.element_type)
        da.value = data
        return da

    def init(self) -> Expr:
        if self.element_type == String:
            ops = [
                self.size.store(ExtractUint16(self.value, Int(0))),
                self.bytes.store(
                    Substring(
                        self.value,
                        (Int(2) * self.size.load()) + Int(2),
                        Len(self.value),
                    )
                ),
                self.lengths.store(encode_string_lengths(self.bytes.load(), Bytes(""))),
            ]

        return (
            If(Len(self.value) == Int(0))
            .Then(
                Seq(
                    self.size.store(Int(0)),
                    self.bytes.store(Bytes("")),
                    self.lengths.store(Bytes("")),
                )
            )
            .Else(Seq(*ops))
        )

    def __getitem__(self, idx: Union[Int, int]) -> ABIType:
        if isinstance(idx, int):
            idx = Int(idx)

        if self.element_type is String:
            return tuple_get_bytes(
                self.bytes.load(), sum_string_lengths(self.lengths.load(), idx, Int(0))
            )
        elif self.element_type is Address:
            return tuple_get_address(self.bytes.load(), idx)
        else:
            return tuple_get_int(self.bytes.load(), Int(64), idx)

    def append(self, b: TealType.bytes):
        if self.element_type is String:
            return Seq(
                self.bytes.store(Concat(self.bytes.load(), Uint16.encode(Len(b)), b)),
                self.lengths.store(Concat(self.lengths.load(), Uint16.encode(Len(b)))),
                self.size.store(self.size.load() + Int(1)),
            )
        elif self.element_type is Address:
            return Seq(
                self.bytes.store(Concat(self.bytes.load(), Uint16.encode(Int(32)), b)),
                self.lengths.store(Concat(self.lengths.load(), Uint16.encode(Int(32)))),
                self.size.store(self.size.load() + Int(1)),
            )
        else:
            return Assert(Int(0))

    def __teal__(self, options: CompileOptions):
        return self.value.__teal__(options)

    def encode(self) -> Expr:
        return Concat(
            Uint16.encode(self.size.load()),
            encode_string_positions(
                self.lengths.load(), Bytes(""), self.size.load() * Int(2)
            ),
            self.bytes.load(),
        )


class FixedArray(ABIType):
    stack_type = TealType.bytes

    value: Expr

    def __init__(self, type: ABIType):
        self.type = type

    def __call__(self, value: Bytes) -> "FixedArray":
        pass

    def __getitem__(self, i: int) -> Expr:
        pass

    def encode(value: Bytes) -> Expr:
        return value


class Tuple(ABIType):
    stack_type = TealType.bytes

    types: List[ABIType]
    value: Expr

    def __init__(self, types: List[ABIType]):
        self.types = types

    def __call__(self, value: Bytes) -> "Tuple":
        clone = Tuple(self.types)
        clone.value = value
        return clone

    def __getitem__(self, i: int) -> Expr:
        target_type = self.types[i]
        return target_type(rest(self.value, self.element_position(i)))

    def __setitem__(self, i: int, e: Expr):
        # TODO: Rewrite all the lengths for dynamic elements _after_ the one we're updating

        position_update_ops = []
        for t in self.types[i:]:
            if t.dynamic:
                position_update_ops.append()
            else:
                position_update_ops.append()

        elem_pos = ScratchVar()
        return Seq(
            elem_pos.store(self.element_position(i)),
            Concat(
                prefix(self.value, elem_pos.load()),
                String.encode(e),
                rest(
                    self.value,
                    elem_pos.load() + ExtractUint16(elem_pos.load() + Int(2)),
                ),
            ),
        )

    def element_position(self, i: int) -> Expr:
        pos = ScratchVar()
        ops = [pos.store(Int(0))]

        for t in self.types[:i]:
            if t.dynamic:
                # Just add uint16 length
                ops.append(pos.store(pos.load() + Int(2)))
            else:
                # Add length of static type
                ops.append(pos.store(pos.load() + Int(t.byte_len)))

        if self.types[i].dynamic:
            ops.append(pos.store(ExtractUint16(self.value, pos.load())))

        return Seq(*ops, pos.load())

    def encode(self) -> Expr:
        return self.value
