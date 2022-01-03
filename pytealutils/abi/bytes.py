from pyteal import Bytes, Expr, Int, Len, Seq, TealType

from .abi_type import ABIType
from .codec_util import discard_length, prepend_length


class String(ABIType):
    stack_type = TealType.bytes
    dynamic = True

    def __init__(self, value: Bytes):
        self.value = value
        self.byte_len = Seq(Len(value) + Int(2))

    @staticmethod
    def decode(value: Bytes) -> "String":
        return String(discard_length(value))

    def encode(self) -> Expr:
        return prepend_length(self.value)


class Address(ABIType):
    stack_type = TealType.bytes
    byte_len = Int(32)

    def __init__(self, value: Bytes):
        self.value = value

    def decode(self, value: Bytes):
        self.value = discard_length(value)

    def encode(self) -> Expr:
        return self.value
