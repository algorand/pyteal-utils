import math

from pyteal import (
    BitLen,
    BytesAdd,
    BytesDiv,
    BytesMinus,
    BytesMul,
    BytesZero,
    Concat,
    Exp,
    Expr,
    ExtractUint64,
    If,
    Int,
    Itob,
    Len,
    Not,
    ScratchSlot,
    Seq,
    Subroutine,
    TealType,
)

from ..inline.inline_asm import InlineAssembly

_scale = 1000000
_log2_10 = math.log2(10)
_log2_e = math.log2(math.e)

_max_uint = (2 ** 64) - 1
_half_uint = (2 ** 32) - 1

log2_10 = Int(int(_log2_10 * _scale))
log2_e = Int(int(_log2_e * _scale))
scale = Int(_scale)

max_uint = Int(_max_uint)
half_uint = Int(_half_uint)


@Subroutine(TealType.uint64)
def odd(x: TealType.uint64):
    """odd returns 1 if x is odd"""
    return x & Int(1)


@Subroutine(TealType.uint64)
def even(x: TealType.uint64):
    """even returns 1 if x is even"""
    return Not(odd(x))


@Subroutine(TealType.uint64)
def factorial(x: TealType.uint64):
    """factorial returns x! = x * x-1 * x-2 * ...,
    for a 64bit integer, the max possible value is maxes out at 20
    """
    return If(x == Int(1), x, x * factorial(x - Int(1)))


@Subroutine(TealType.bytes)
def wide_factorial(x: TealType.bytes):
    """factorial returns x! = x * x-1 * x-2 * ...,"""
    return If(
        BitLen(x) == Int(1), x, BytesMul(x, wide_factorial(BytesMinus(x, Itob(Int(1)))))
    )


# @Subroutine(TealType.bytes)
# def negative_power(x: TealType.uint64, n: TealType.uint64):
#    """negative power returns x^-n"""
#    return BytesDiv(Itob(Int(1)), wide_power(x, n))
#


@Subroutine(TealType.bytes)
def wide_power(x: TealType.uint64, n: TealType.uint64):
    return Seq(InlineAssembly("expw", x, n), stack_to_wide())


def exponential(x: TealType.uint64, n: TealType.uint64):
    """exponential approximates e**x for n iterations

    Args:
        x: The exponent to apply
        n: The number of iterations, more is better appx but costs ops

    """
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

    return bytes_to_int(BytesDiv(_impl(Itob(x), wide_factorial(Itob(n)), n), _scale))


@Subroutine(TealType.uint64)
def log2(x: TealType.uint64):
    return BitLen(x)  # Only returns integral component


@Subroutine(TealType.uint64)
def ln(x: TealType.uint64):
    """Returns natural log of x for integer passed"""
    return (log2(x) * scale) / log2_e


@Subroutine(TealType.uint64)
def log10(x: TealType.uint64):
    """Returns log base 10 of the integer passed

    uses log10(x) = log2(x)/log2(10) identity
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


@Subroutine(TealType.uint64)
def bytes_to_int(x: TealType.bytes):
    return If(
        Len(x) < Int(8),
        ExtractUint64(Concat(BytesZero(Int(8) - Len(x)), x), Int(0)),
        ExtractUint64(x, Len(x) - Int(8)),
    )


@Subroutine(TealType.bytes)
def stack_to_wide():
    h = ScratchSlot()
    l = ScratchSlot()
    return Seq(
        l.store(),
        h.store(),  # Take the low and high ints off the stack and combine them
        Concat(Itob(h.load()), Itob(l.load())),
    )
