from typing import Union

from pyteal import (
    Assert,
    BitLen,
    Btoi,
    Bytes,
    BytesAdd,
    BytesDiv,
    BytesMinus,
    BytesMul,
    BytesZero,
    CompileOptions,
    Concat,
    Expr,
    GetByte,
    If,
    Int,
    Itob,
    Len,
    ScratchVar,
    Seq,
    Subroutine,
    TealType,
)
from pyteal.ast.leafexpr import LeafExpr

from ..strings import head, itoa, prefix, suffix, tail
from .math import pow10


def precision_uint8(p: int):
    return p.to_bytes(8, "big")[-1:]


@Subroutine(TealType.bytes)
def byte_precision(v: TealType.bytes):
    return Itob(pow10(GetByte(v, Int(0))))


@Subroutine(TealType.none)
def assert_fp_match(a: TealType.bytes, b: TealType.bytes):
    return Assert(head(a) == head(b))  # Check precision matches


@Subroutine(TealType.bytes)
def check_overflow(
    prec: TealType.bytes, bytelen: TealType.uint64, value: TealType.bytes
):
    """check_overflow checks to make sure we didnt overflow and sets the appropriate 0 padding if necessary

    Args:
        prec: the precision as bytes
        bytelen: the number of bytes we expect
        value: the underlying value, without the precision prefix

    Returns:
        appropriately padded bytestring or Asserts if we overflow (overflowed? overflew?)
    """
    return Seq(
        Assert(BitLen(value) / Int(8) <= bytelen),
        If(
            Len(value) > bytelen,
            Concat(
                prec, suffix(value, Len(value) - (bytelen - Int(1)))
            ),  # We can remove zeros
            Concat(
                prec, BytesZero(bytelen - Int(1) - Len(value)), value
            ),  # We need to pad with zeros
        ),
    )


class FixedPoint(LeafExpr):
    """FixedPoint represents a numeric value with a fixed number of decimal places

    From ABI: ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which

    Hold the value in memory as bytes (may be larger than a single uint64)
    Prepend the precision as a single byte (max precision 160 vs max_uint 255) the number of bits can be computed (Len(bytestring) - 1) * 8
    Every math operation asserts that the width in bytes of the result is <= to the expected width and repads with 0s if necessary
    """

    def __init__(
        self, bits: int, precision: int, value: Union[int, float, bytes, Expr]
    ):
        assert 8 <= bits <= 512, "Number of bits must be between 8 and 512"
        assert bits % 8 == 0, "Bits must be a multiple of 8"
        assert 0 < precision <= 160, "Precision must be between 0 and 160"

        self.bits = bits
        self.precision = precision

        precision_as_bytes = precision_uint8(precision)
        expected_bytes = int(self.bits / 8)

        self.raw = value

        if type(value) in [int, float]:
            self.value = Bytes(
                precision_as_bytes
                + int(value * (10 ** self.precision)).to_bytes(expected_bytes, "big")
            )
        elif type(value) == bytes:
            if len(value) != expected_bytes:
                # Should be exactly encoded except for precision
                raise ValueError
            self.value = Bytes(precision_as_bytes + value)
        elif issubclass(type(value), Expr):
            self.value = value  # Should already be in the right format
        else:
            print(type(value))
            raise ValueError

    def __teal__(self, options: "CompileOptions"):
        return self.value.__teal__(options)

    def type_of(self):
        return TealType.bytes

    def __add__(self, other: "FixedPoint"):
        return fp_add(self.value, other.value)

    def __sub__(self, other: "FixedPoint"):
        return fp_sub(self.value, other.value)

    def __mul__(self, other: "FixedPoint"):
        return fp_mul(self.value, other.value)

    def __truediv__(self, other: "FixedPoint"):
        return fp_div(self.value, other.value)

    def rescaled(self, p: int):
        return FixedPoint(self.bits, p, fp_rescale(self.value, Int(p)))

    def to_ascii(self):
        return fp_to_ascii(self.value)

    def __str__(self) -> str:
        return "FixedPoint({},{},{})".format(self.bits, self.precision, self.value)


@Subroutine(TealType.bytes)
def fp_to_ascii(v: TealType.bytes):
    val = tail(v)
    prec = GetByte(v, Int(0))

    ascii = ScratchVar()
    return Seq(
        ascii.store(itoa(Btoi(val))),
        # Combine with decimal
        Concat(
            prefix(ascii.load(), Len(ascii.load()) - prec),
            Bytes("."),
            suffix(ascii.load(), prec),
        ),
    )


@Subroutine(TealType.bytes)
def fp_rescale(v: TealType.bytes, p: TealType.uint64):
    return check_overflow(
        # Prepend new precision byte
        suffix(Itob(p), Int(1)),
        Len(v),
        # Divide off the old precision
        BytesDiv(
            # Multiply by new precision first so we dont lose precision
            BytesMul(tail(v), Itob(pow10(p))),
            byte_precision(v),
        ),
    )


@Subroutine(TealType.bytes)
def fp_add(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        check_overflow(head(a), Len(b), BytesAdd(tail(a), tail(b))),
    )


@Subroutine(TealType.bytes)
def fp_sub(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        check_overflow(head(a), Len(a), BytesMinus(tail(a), tail(b))),
    )


@Subroutine(TealType.bytes)
def fp_mul(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        check_overflow(
            head(a),
            Len(a),
            BytesDiv(
                # mul first then divide by the square of the scale
                BytesMul(tail(a), tail(b)),
                byte_precision(a),
            ),
        ),
    )


@Subroutine(TealType.bytes)
def fp_div(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        check_overflow(
            head(a),
            Len(a),
            BytesDiv(
                # Scale up the numerator so we keep the same precision
                BytesMul(tail(a), byte_precision(a)),
                tail(b),
            ),
        ),
    )
