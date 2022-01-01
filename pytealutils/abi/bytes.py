from pyteal import Bytes, Expr, Subroutine, TealType

from .abi_type import ABIType
from .codec_util import discard_length, prepend_length


class String(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = discard_length(value)

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: bytes) -> Expr:
        return prepend_length(value)


class Address(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = value

    @staticmethod
    @Subroutine(TealType.bytes)
    def encode(value: bytes) -> Expr:
        return value
