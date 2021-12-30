from typing import Union, Optional

from ..strings import tail, head, itoa, suffix
from pyteal import *

# From ABI: ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which


# Fixed Point Class
# Hold the value in memory as bytes (may be larger than a single uint64)
# Prepend the precision as a single byte (max precision 160 vs max_uint 255) the number of bits can be computed (Len(bytes) - 1) * 8


class FixedPoint:

    # TODO allow instantiation with other types? byte arrays?
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
                + (value * (2 ** self.precision)).to_bytes(8, "big")
            )
        elif type(value) == float:
            return Bytes(
                self.precision_as_bytes
                + int(value * (2 ** self.precision)).to_bytes(8, "big")
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
                    BytesMul(old_val, Itob(Exp(Int(2), Int(self.precision)))),
                    Itob(Exp(Int(2), old_precision)),
                ),
            ),
        )

    def to_ascii(self, value: TealType.bytes):
        val = tail(value)
        prec = Int(self.precision)

        integral = ScratchVar()
        fractional = ScratchVar()
        return Seq(
            # Integral, just divide by 2^precision as a fake "shift right" to get the integral component only
            integral.store(BytesDiv(val, Itob(Exp(Int(2), prec)))),
            # Fractional, more involvedi, handle in subroutine
            fractional.store(fractional_bits(suffix(val, prec / Int(8)))),
            # Combine with decimal
            Concat(
                itoa(Btoi(integral.load())), Bytes("."), itoa(Btoi(fractional.load()))
            ),
        )


@Subroutine(TealType.bytes)
def fractional_bits(b: TealType.bytes):
    # fractional, more involved typically this is the sum of bit[n]*2^-n from 1 to precision
    # recall algebraic identities:
    #     2^-n == 1/2^n
    #     1/x + 1/y == 1*y/x*y + 1*x/x*y == 1*x+1*y/x*y == x+y/x*y

    # Just naming it so its obvious
    num_bits = Len(b) * Int(8)
    # Just pretending here but we know what the max is
    least_common_denom = Exp(Int(2), num_bits)
    lcd = ScratchVar()  # Store lcm so we dont have to recalc
    numerator = ScratchVar()  # accumulate the numerator values

    i = ScratchVar()
    init = i.store(Int(0))
    cond = i.load() < num_bits
    iter = i.store(i.load() + Int(1))

    return Seq(
        lcd.store(least_common_denom),
        numerator.store(Int(0)),
        For(init, cond, iter).Do(
            If(
                GetBit(b, i.load()),
                Seq(
                    # Only add to numerator if the bit is set to 1
                    numerator.store(
                        numerator.load()
                        + (lcd.load() / Exp(Int(2), (i.load() + Int(1))))
                    ),
                ),
            )
        ),
        # Using  *10 to force rounding
        Itob(((numerator.load() * Int(10)) / least_common_denom) + Int(1)),
    )


@Subroutine(TealType.bytes)
def fp_unwrap(a: TealType.bytes):
    return head(a)


@Subroutine(TealType.bytes)
def fp_add(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        Assert(head(a) == head(b)),  # Check precision matches
        Concat(head(a), BytesAdd(tail(a), tail(b))),
    )
