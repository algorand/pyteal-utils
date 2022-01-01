from typing import Generic, List, Tuple, TypeVar, Union

from pyteal import *

from .abi_type import ABIType
from .bytes import *
from .codec_util import *
from .uint import *

T = TypeVar("T", bound=ABIType)


class FixedArray(Generic[T]):
    stack_type = TealType.bytes

    @staticmethod
    @Subroutine(TealType.bytes)
    def decode(value: Bytes) -> Expr:
        return value

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Bytes) -> Expr:
        return value


class DynamicArray(Generic[T]):

    stack_type = TealType.bytes

    def __init__(self, data: Bytes):
        self.size = ScratchVar(TealType.uint64)
        self.bytes = ScratchVar(TealType.bytes)
        self.lengths = ScratchVar(TealType.bytes)

        self.value = data

    def init(self) -> Expr:
        return (
            If(Len(self.value) == Int(0))
            .Then(
                Seq(
                    self.size.store(Int(0)),
                    self.bytes.store(Bytes("")),
                    self.lengths.store(Bytes("")),
                )
            )
            .Else(
                Seq(
                    self.size.store(ExtractUint16(self.value, Int(0))),
                    self.bytes.store(
                        Substring(
                            self.value,
                            (Int(2) * self.size.load()) + Int(2),
                            Len(self.value),
                        )
                    ),
                    self.lengths.store(
                        encode_string_lengths(self.bytes.load(), Bytes(""))
                    ),
                )
            )
        )

    def __getitem__(self, idx: Union[Int, int]) -> T:
        if isinstance(idx, int):
            idx = Int(idx)

        if self.__orig_class__.__args__[0] is String:
            return tuple_get_bytes(
                self.bytes.load(), sum_string_lengths(self.lengths.load(), idx, Int(0))
            )

        elif self.__orig_class__.__args__[0] is Address:
            return tuple_get_address(self.bytes.load(), idx)

        else:
            return tuple_get_int(self.bytes.load(), Int(64), idx)

    def append(self, b: TealType.bytes):
        if self.__orig_class__.__args__[0] is String:
            return Seq(
                self.bytes.store(Concat(self.bytes.load(), Uint16.encode(Len(b)), b)),
                self.lengths.store(Concat(self.lengths.load(), Uint16.encode(Len(b)))),
                self.size.store(self.size.load() + Int(1)),
            )

        elif self.__orig_class__.__args__[0] is Address:
            return Assert(Int(0))
        else:
            return Assert(Int(0))

    def serialize(self) -> Bytes:
        return Concat(
            Uint16.encode(self.size.load()),
            encode_string_positions(
                self.lengths.load(), Bytes(""), self.size.load() * Int(2)
            ),
            self.bytes.load(),
        )

    def __teal__(self, options: CompileOptions):
        return self.value.__teal__(options)

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: TealType.bytes) -> Expr:
        return value


class Tuple(Generic[T]):
    stack_type = TealType.bytes

    def __init__(self, types: List[ABIType]):
        pass

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Bytes) -> Expr:
        pass
