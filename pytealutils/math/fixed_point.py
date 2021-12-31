from typing import Optional, Union

from pyteal import (
    Assert,
    Btoi,
    Bytes,
    BytesAdd,
    BytesDiv,
    BytesMinus,
    BytesMul,
    BytesZero,
    Concat,
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

# Fixed Point Class
# From ABI: ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which

# Hold the value in memory as bytes (may be larger than a single uint64)
# Prepend the precision as a single byte (max precision 160 vs max_uint 255) the number of bits can be computed (Len(bytes) - 1) * 8
# Every math operation asserts that the result is <= to the expected width and repads with 0s if necessary
class FixedPoint:
    def __init__(self, bits: int, precision: int):
        assert 8 <= bits <= 512, "Number of bits must be between 8 and 512"
        assert bits % 8 == 0, "Bits must be a multiple of 8"
        assert 0 < precision <= 160, "Precision must be between 0 and 160"

        self.bits = bits
        self.precision = precision
        self.precision_as_bytes = precision.to_bytes(8, "big")[-1:]

    def wrap(self, value: Optional[Union[int, float, bytes]]):
        expected_bytes = int(self.bits / 8)
        if type(value) in [int, float]:
            intbytes = int(value * (10 ** self.precision)).to_bytes(
                expected_bytes, "big"
            )
            return Bytes(
                self.precision_as_bytes
                + b"00" * (len(intbytes) - expected_bytes)
                + intbytes
            )
        elif type(value) == bytes:
            if len(value) != expected_bytes:
                # Should be exactly encoded except for precision
                raise ValueError
            return Bytes(self.precision_as_bytes + value)
        else:
            raise ValueError

    def rescale(self, value: TealType.bytes):
        old_precision = byte_precision(value)
        old_val = tail(value)
        return Seq(
            Concat(
                # Prepend precision byte
                Bytes(self.precision_as_bytes),
                # Divide off the old precision
                BytesDiv(
                    # Multiply by new precision first so we dont lose precision
                    BytesMul(old_val, Itob(pow10(Int(self.precision)))),
                    old_precision,
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

    def __str__(self) -> str:
        return "FixedPoint({},{})".format(self.bits, self.precision)


@Subroutine(TealType.bytes)
def byte_precision(v: TealType.bytes):
    return Itob(pow10(GetByte(v, Int(0))))


@Subroutine(TealType.none)
def assert_fp_match(a: TealType.bytes, b: TealType.bytes):
    return Assert(head(a) == head(b))  # Check precision matches


@Subroutine(TealType.bytes)
def pad_assert_overflow(prec: TealType.bytes, len: TealType.uint64, a: TealType.bytes):
    return Seq(
        Assert(Len(a) <= len),  # Make sure we didn't overflow
        Concat(prec, BytesZero(len - Int(1) - Len(a)), a),
    )


@Subroutine(TealType.bytes)
def fp_add(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        pad_assert_overflow(head(a), Len(a), BytesAdd(tail(a), tail(b))),
    )


@Subroutine(TealType.bytes)
def fp_sub(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        pad_assert_overflow(head(a), Len(a), BytesMinus(tail(a), tail(b))),
    )


@Subroutine(TealType.bytes)
def fp_mul(a: TealType.bytes, b: TealType.bytes):
    return Seq(
        assert_fp_match(a, b),
        pad_assert_overflow(
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
        pad_assert_overflow(
            head(a),
            Len(a),
            BytesDiv(
                # Scale up the numerator so we keep the same precision
                BytesMul(tail(a), byte_precision(a)),
                tail(b),
            ),
        ),
    )
