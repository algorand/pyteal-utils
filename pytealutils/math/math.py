import math

from pyteal.ast.scratch import ScratchSlot
from ..inline.inline_asm import InlineAssembly
from pyteal import (
    Concat,
    Log,
    Len,
    ExtractUint64,
    Btoi,
    Itob,
    GetByte,
    BytesAdd,
    BytesDiv,
    BytesMinus,
    BytesMul,
    Exp,
    Expr,
    If,
    Int,
    Subroutine,
    TealType,
    BitLen,
    WideRatio,
    ScratchVar,
    Seq,
)
from pyteal.ast.binaryexpr import ExtractUint64


# TODO: Wide math?

_scale = 10000
_log2_10 = math.log2(10)
scale = Int(_scale)
log2_10 = Int(int(_log2_10 * _scale))


@Subroutine(TealType.uint64)
def factorial(x: TealType.uint64):
    """factorial returns x! = x * x-1 * x-2 * ...,
    for a 64bit integer, the max possible value is maxes out at 20
    """
    return If(x > Int(1), x * factorial(x - Int(1)), x)


@Subroutine(TealType.bytes)
def wide_factorial(x: TealType.bytes):
    """factorial returns x! = x * x-1 * x-2 * ...,"""
    return If(
        BitLen(x) > Int(1), BytesMul(x, wide_factorial(BytesMinus(x, Itob(Int(1))))), x
    )


@Subroutine(TealType.uint64)
def bytes_to_int(x: TealType.bytes):
    return ExtractUint64(x, Len(x) - Int(8))


@Subroutine(TealType.bytes)
def wide_power(x: TealType.uint64, n: TealType.uint64):
    h = ScratchSlot()
    l = ScratchSlot()
    return Seq(
        InlineAssembly("expw", x, n),
        l.store(),
        h.store(),
        Concat(Itob(h.load()), Itob(l.load())),
    )


def exponential(x: TealType.uint64, n: TealType.uint64):
    """exponential approximates e**x for n iterations"""

    _scale = Itob(Int(1000))

    @Subroutine(TealType.bytes)
    def _impl(x: TealType.bytes, f: TealType.bytes, n: TealType.uint64):
        return If(
            n == Int(1),
            BytesAdd(_scale, BytesMul(x, _scale)),
            BytesAdd(
                _impl(x, BytesDiv(f, Itob(n)), n - Int(1)),
                BytesDiv(BytesMul(_scale, wide_power(bytes_to_int(x), n)), f),
            ),
        )

    return BytesDiv(_impl(Itob(x), wide_factorial(Itob(n)), n), _scale)


@Subroutine(TealType.uint64)
def ln(x: TealType.uint64):
    pass


def log2(x: TealType.uint64):
    """Returns the integral part of log2(x)"""
    # return BitLen(x/Int(2)) * Int(1000)
    # return BitLen(x/Int(4)) * Int(1000)
    return BitLen(x / Int(8)) * Int(1000)


@Subroutine(TealType.uint64)
def log10(x: TealType.uint64):
    """Returns log base 10 of the integer passed

    uses log10(x) = log2(x)/log2(10) equality
    """
    return (log2(x) * scale) / log2_10


@Subroutine(TealType.uint64)
def pow10(x: TealType.uint64) -> Expr:
    """Returns 10^x, useful for things like total supply of an asset"""
    return Exp(Int(10), x)


@Subroutine(TealType.uint64)
def max(a: TealType.uint64, b: TealType.uint64) -> Expr:
    """Returns the max of 2 integers"""
    return If(a > b, a, b)


@Subroutine(TealType.uint64)
def min(a: TealType.uint64, b: TealType.uint64) -> Expr:
    """Returns the min of 2 integers"""
    return If(a < b, a, b)


@Subroutine(TealType.uint64)
def div_ceil(a: TealType.uint64, b: TealType.uint64) -> Expr:
    """Returns the result of division rounded up to the next integer"""
    q = a / b
    return If(a % b > Int(0), q + Int(1), q)
