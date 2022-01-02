from pyteal import (
    Btoi,
    Bytes,
    BytesZero,
    Concat,
    Expr,
    Extract,
    ExtractUint16,
    ExtractUint32,
    Int,
    Itob,
    Len,
    Subroutine,
    TealType,
)

from .abi_type import ABIType


class Uint512(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(64))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(value, Int(0), Int(64))


class Uint256(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(32))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(value, Int(0), Int(32))


class Uint128(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(16))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(Concat(BytesZero(Int(16) - Len(value)), value), Int(0), Int(16))


class Uint64(ABIType):
    stack_type = TealType.uint64

    def __init__(self, value: Bytes):
        self.value = Btoi(value)

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Itob(value)


class Uint32(ABIType):
    stack_type = TealType.uint64

    def __init__(self, value: Bytes):
        self.value = ExtractUint32(value, Int(0))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(Itob(value), Int(4), Int(4))


class Uint16(ABIType):
    stack_type = TealType.uint64

    def __init__(self, value: Bytes):
        self.value = ExtractUint16(value, Int(0))

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: Int) -> Expr:
        return Extract(Itob(value), Int(6), Int(2))
