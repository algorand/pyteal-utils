from pyteal import *

from .uint import *


@Subroutine(TealType.bytes)
def prepend_length(v: TealType.bytes) -> Expr:
    return Concat(Uint16.encode(Len(v)), v)


@Subroutine(TealType.bytes)
def discard_length(v: TealType.bytes) -> Expr:
    return Extract(v, Int(2), Uint16(v))
