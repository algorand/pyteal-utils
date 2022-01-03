from pyteal import Bytes, Expr, TealType

from .abi_type import ABIType
from .codec_util import discard_length, prepend_length


class String(ABIType):
    stack_type = TealType.bytes
    dynamic = True

    def __init__(self, value: Bytes):
        self.decode(value)

    def decode(self, value: Bytes):
        self.value = discard_length(value)

    def encode(self) -> Expr:
        return prepend_length(self.value)


class Address(ABIType):
    stack_type = TealType.bytes

    def __init__(self, value: Bytes):
        self.value = value

    def decode(self, value: Bytes):
        self.value = discard_length(value)

    def encode(self) -> Expr:
        return self.value
