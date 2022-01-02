from typing import Generic, List, Tuple, TypeVar, Union

from pyteal import *

from .abi_type import ABIType
from .bytes import *
from .uint import *

T = TypeVar("T", bound=ABIType)


@Subroutine(TealType.bytes)
def tuple_get_bytes(b: TealType.bytes, idx: TealType.uint64) -> Expr:
    return Extract(b, idx + Int(2), ExtractUint16(b, idx))


@Subroutine(TealType.bytes)
def tuple_get_address(b: TealType.bytes, idx: TealType.uint64) -> Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))),  # Get the position in the byte array
        Extract(b, pos.load(), Int(32)),
    )


@Subroutine(TealType.bytes)
def tuple_get_int(
    b: TealType.bytes, size: TealType.uint64, idx: TealType.uint64
) -> Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))),  # Get the position in the byte array
        Extract(b, pos.load(), Extract(b, pos.load(), size / Int(8))),
    )


@Subroutine(TealType.bytes)
def tuple_add_bytes(
    data: TealType.bytes, length: TealType.uint64, b: TealType.bytes
) -> Expr:
    return Seq(
        Concat(
            # Update positions to add 2, accounting for newly added position
            binary_add_list(Extract(data, Int(0), Int(2) * length), length, Int(2)),
            # Set position of new data
            Uint16.encode(Len(data) + Int(2)),
            # Add existing bytes back
            Substring(data, length * Int(2), Len(data)),
            # Prefixed bytes with length
            Uint16.encode(Len(b)),
            b,
        )
    )


@Subroutine(TealType.bytes)
def tuple_add_address(a: TealType.bytes, b: TealType.bytes):
    pass


@Subroutine(TealType.bytes)
def tuple_add_int(a: TealType.bytes, b: TealType.bytes):
    pass


@Subroutine(TealType.bytes)
def binary_add_list(
    data: TealType.bytes, len: TealType.uint64, val: TealType.uint64
) -> Expr:
    return (
        If(len > Int(0))
        .Then(
            Concat(
                binary_add_list(Extract(data, Int(0), len * Int(2)), len - Int(1), val),
                Uint16.encode(
                    binary_add(ExtractUint16(data, (len * Int(2)) - Int(2)), val)
                ),
            )
        )
        .Else(Bytes(""))
    )


@Subroutine(TealType.uint64)
def binary_add(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return If(b == Int(0)).Then(a).Else(binary_add(a))


@Subroutine(TealType.bytes)
def encode_string_lengths(b: TealType.bytes, lengths: TealType.bytes) -> Expr:
    return (
        If(Len(b) == Int(0))
        .Then(lengths)
        .Else(
            encode_string_lengths(
                Substring(b, Uint16(b) + Int(2), Len(b)),
                Concat(lengths, Extract(b, Int(0), Int(2))),
            )
        )
    )


@Subroutine(TealType.bytes)
def encode_string_positions(
    lengths: TealType.bytes, positions: TealType.bytes, start: TealType.uint64
) -> Expr:
    return (
        If(Len(lengths) == Int(0))
        .Then(positions)
        .Else(
            encode_string_positions(
                Substring(lengths, Int(2), Len(lengths)),
                Concat(positions, Uint16.encode(start)),
                start + Uint16(lengths) + Int(2),
            )
        )
    )


@Subroutine(TealType.bytes)
def sum_string_lengths(
    lengths: TealType.bytes, idx: TealType.uint64, sum: TealType.uint64
) -> Expr:
    return (
        If(idx == Int(0))
        .Then(sum)
        .Else(
            sum_string_lengths(
                Substring(
                    lengths, Int(2), Len(lengths)
                ),  # Chop off uint16 we just read
                idx - Int(1),  # Decrement index
                sum + Uint16(lengths) + Int(2),  # Add length + 2 for uint16 length
            )
        )
    )


class DynamicArray(Generic[T]):

    stack_type = TealType.bytes

    element_type: TypeVar
    size: ScratchVar
    bytes: ScratchVar
    lengths: ScratchVar
    value: Expr

    def __init__(self, type: T):
        self.element_type = type
        self.size = ScratchVar(TealType.uint64)
        self.bytes = ScratchVar(TealType.bytes)
        self.lengths = ScratchVar(TealType.bytes)
        self.value = None

    def __call__(self, data: Bytes) -> "DynamicArray":
        da = DynamicArray(self.element_type)
        da.value = data
        return da

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


class Tuple(Generic[T]):
    stack_type = TealType.bytes

    def __init__(self, types: List[ABIType]):
        pass

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Bytes) -> Expr:
        pass
