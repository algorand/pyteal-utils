from typing import Optional, Union

from pyteal import (
    Assert,
    Btoi,
    Bytes,
    BytesAdd,
    BytesDiv,
    BytesMinus,
    BytesMul,
    Concat,
    Exp,
    Expr,
    GetByte,
    Int,
    Itob,
    Len,
    ScratchVar,
    Seq,
    Subroutine,
    Substring,
    TealType,
)

from ..strings import head, itoa, tail
from .math import pow10

# From ABI: ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which


# Fixed Point Class
# Hold the value in memory as bytes (may be larger than a single uint64)
# Prepend the precision as a single byte (max precision 160 vs max_uint 255) the number of bits can be computed (Len(bytes) - 1) * 8


class FixedPoint:
    def __init__(self, bits: int, precision: int):
        assert 8 <= bits <= 512, "Number of bits must be between 8 and 512"
        assert bits % 8 == 0, "Bits must be a multiple of 8"
        assert 0 < precision <= 160, "Precision must be between 0 and 160"

        self.bits = bits
        self.precision = precision
        self.precision_as_bytes = precision.to_bytes(8, "big")[-1:]

    def wrap(self, value: Optional[Union[int, float, bytes, Expr]]):
        if type(value) == int:
            return Bytes(
                self.precision_as_bytes
                + (value * (10 ** self.precision)).to_bytes(8, "big")
            )
        elif type(value) == float:
            return Bytes(
                self.precision_as_bytes
                + int(value * (10 ** self.precision)).to_bytes(8, "big")
            )
        elif type(value) == bytes:
            return Bytes(self.precision_as_bytes + value)
        else:
            raise ValueError

    def rescale(self, value: TealType.bytes):
        old_precision = GetByte(value, Int(0))
        old_val = tail(value)
        return Seq(
            Concat(
                # Prepend precision byte
                Bytes(self.precision_as_bytes),
                # Divide off the old precision
                BytesDiv(
                    # Multiply by new precision first so we dont lose precision
                    BytesMul(old_val, Itob(Exp(Int(10), Int(self.precision)))),
                    Itob(Exp(Int(10), old_precision)),
                ),
            )
        )

    def to_ascii(self, value: TealType.bytes):
        val = tail(value)
        prec = Int(self.precision)

        ascii = ScratchVar()
        return Seq(
            ascii.store(itoa(Btoi(val))),
            # Combine with decimal
            Concat(
                Substring(ascii.load(), Int(0), Len(ascii.load()) - prec),
                Bytes("."),
                Substring(ascii.load(), Len(ascii.load()) - prec, Len(ascii.load())),
            ),
        )


@Subroutine(TealType.none)
def assert_fp_match(a: TealType.bytes, b: TealType.bytes):
    return Assert(head(a) == head(b))  # Check precision matches


@Subroutine(TealType.bytes)
def fp_add(a: TealType.bytes, b: TealType.bytes):
    return Seq(assert_fp_match(a, b), Concat(head(a), BytesAdd(tail(a), tail(b))))


@Subroutine(TealType.bytes)
def fp_sub(a: TealType.bytes, b: TealType.bytes):
    return Seq(assert_fp_match(a, b), Concat(head(a), BytesMinus(tail(a), tail(b))))


@Subroutine(TealType.bytes)
def fp_mul(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        Concat(
            head(a),
            BytesDiv(
                BytesMul(
                    tail(a), tail(b)
                ),  # mul first then divide by the square of the scale
                Itob(Exp(Int(10), GetByte(a, Int(0)))),
            ),
        ),
    )


@Subroutine(TealType.bytes)
def fp_div(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        Concat(
            head(a),
            BytesDiv(
                # Scale up the numerator so we keep the same precision
                BytesMul(tail(a), Itob(pow10(GetByte(a, Int(0))))),
                tail(b),
            ),
        ),
    )


# @Subroutine(TealType.bytes)
# def binary_fractional_bits(b: TealType.bytes):
#    # fractional, more involved typically this is the sum of bit[n]*2^-n from 1 to precision
#    # recall algebraic identities:
#    #     2^-n == 1/2^n
#    #     1/x + 1/y == 1*y/x*y + 1*x/x*y == 1*x+1*y/x*y == x+y/x*y
#
#    # Just naming it so its obvious
#    num_bits = Len(b) * Int(8)
#    # We know what the max is
#    least_common_denom = Exp(Int(2), num_bits)
#    lcd = ScratchVar()          # Store lcd so we dont have to recalc
#    numerator = ScratchVar()    # accumulate the numerator values
#
#    i = ScratchVar()
#    init = i.store(Int(0))
#    cond = i.load() < num_bits
#    iter = i.store(i.load() + Int(1))
#
#    return Seq(
#        lcd.store(least_common_denom),
#        numerator.store(Int(0)),
#        For(init, cond, iter).Do(
#            If(
#                GetBit(b, i.load()),
#                Seq(
#                    # Only add to numerator if the bit is set to 1
#                    numerator.store(
#                        numerator.load()
#                        + (lcd.load() / Exp(Int(2), (i.load() + Int(1))))
#                    )
#                ),
#            )
#        ),
#        # Using  *10 to force rounding to 1 decimal
#        Itob(((numerator.load() * Int(10)) / least_common_denom) + Int(1)),
#    )
