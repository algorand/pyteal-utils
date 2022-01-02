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
    TealType,
)

from ..strings import suffix
from .abi_type import ABIType


class Uint512(ABIType):
    stack_type = TealType.bytes
    byte_len = 512 // 8

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(64))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return Extract(
            Concat(BytesZero(Int(cls.byte_len) - Len(value)), value),
            Int(0),
            Int(cls.byte_len),
        )


class Uint256(ABIType):
    stack_type = TealType.bytes
    byte_len = 256 // 8

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(self.byte_len))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return Extract(
            Concat(BytesZero(Int(cls.byte_len) - Len(value)), value),
            Int(0),
            Int(cls.byte_len),
        )


class Uint128(ABIType):
    stack_type = TealType.bytes
    byte_len = 128 // 8

    def __init__(self, value: Bytes):
        self.value = Extract(value, Int(0), Int(self.byte_len))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return Extract(
            Concat(BytesZero(Int(cls.byte_len) - Len(value)), value),
            Int(0),
            Int(cls.byte_len),
        )


class Uint64(ABIType):
    stack_type = TealType.uint64
    byte_len = 64 // 8

    def __init__(self, value: Bytes):
        self.value = Btoi(Extract(value, Int(0), Int(self.byte_len)))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return Itob(value)


class Uint32(ABIType):
    stack_type = TealType.uint64
    byte_len = 32 // 8

    def __init__(self, value: Bytes):
        self.value = ExtractUint32(value, Int(0))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return suffix(Itob(value), Int(cls.byte_len))


class Uint16(ABIType):
    stack_type = TealType.uint64
    byte_len = 16 // 8

    def __init__(self, value: Bytes):
        self.value = ExtractUint16(value, Int(0))

    @classmethod
    def encode(cls, value: Int) -> Expr:
        return suffix(Itob(value), Int(cls.byte_len))
