from pyteal import *

from .uint import *


@Subroutine(TealType.bytes)
def prepend_length(v: TealType.bytes) -> Expr:
    return Concat(Uint16(Len(v)).encode(), v)


@Subroutine(TealType.bytes)
def discard_length(v: TealType.bytes) -> Expr:
    return Extract(v, Int(2), Uint16.decode(v))


@Subroutine(TealType.bytes)
def tuple_get_bytes(b: TealType.bytes, idx: TealType.uint64) -> Expr:
    return Extract(b, idx + Int(2), ExtractUint16(b, idx))


@Subroutine(TealType.bytes)
def tuple_get_address(b: TealType.bytes, idx: TealType.uint64) -> Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))),  # Get the position in the byte array
        Extract(b, pos.load(), Int(32)),
    )


@Subroutine(TealType.bytes)
def tuple_get_int(
    b: TealType.bytes, size: TealType.uint64, idx: TealType.uint64
) -> Expr:
    pos = ScratchVar()
    return Seq(
        pos.store(ExtractUint16(b, idx * Int(2))),  # Get the position in the byte array
        Extract(b, pos.load(), Extract(b, pos.load(), size / Int(8))),
    )


@Subroutine(TealType.bytes)
def tuple_add_bytes(
    data: TealType.bytes, length: TealType.uint64, b: TealType.bytes
) -> Expr:
    return Seq(
        Concat(
            # Update positions to add 2, accounting for newly added position
            binary_add_list(Extract(data, Int(0), Int(2) * length), length, Int(2)),
            # Set position of new data
            Uint16.encode(Len(data) + Int(2)),
            # Add existing bytes back
            Substring(data, length * Int(2), Len(data)),
            # Prefixed bytes with length
            Uint16.encode(Len(b)),
            b,
        )
    )


@Subroutine(TealType.bytes)
def tuple_add_address(a: TealType.bytes, b: TealType.bytes):
    pass


@Subroutine(TealType.bytes)
def tuple_add_int(a: TealType.bytes, b: TealType.bytes):
    pass


@Subroutine(TealType.bytes)
def binary_add_list(
    data: TealType.bytes, len: TealType.uint64, val: TealType.uint64
) -> Expr:
    """binary_add_lists adds 2 to each element of a uint16 list (as in string array)"""
    return (
        If(len > Int(0))
        .Then(
            Concat(
                binary_add_list(Extract(data, Int(0), len * Int(2)), len - Int(1), val),
                Uint16.encode(
                    binary_add(ExtractUint16(data, (len * Int(2)) - Int(2)), val)
                ),
            )
        )
        .Else(Bytes(""))
    )


@Subroutine(TealType.uint64)
def binary_add(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return If(b == Int(0)).Then(a).Else(binary_add(a))


@Subroutine(TealType.bytes)
def encode_string_lengths(b: TealType.bytes, lengths: TealType.bytes) -> Expr:
    return (
        If(Len(b) == Int(0))
        .Then(lengths)
        .Else(
            encode_string_lengths(
                Substring(b, Uint16(b) + Int(2), Len(b)),
                Concat(lengths, Extract(b, Int(0), Int(2))),
            )
        )
    )


@Subroutine(TealType.bytes)
def encode_string_positions(
    lengths: TealType.bytes, positions: TealType.bytes, start: TealType.uint64
) -> Expr:
    return (
        If(Len(lengths) == Int(0))
        .Then(positions)
        .Else(
            encode_string_positions(
                Substring(lengths, Int(2), Len(lengths)),
                Concat(positions, Uint16.encode(start)),
                start + Uint16(lengths) + Int(2),
            )
        )
    )


@Subroutine(TealType.bytes)
def sum_string_lengths(
    lengths: TealType.bytes, idx: TealType.uint64, sum: TealType.uint64
) -> Expr:
    return (
        If(idx == Int(0))
        .Then(sum)
        .Else(
            sum_string_lengths(
                Substring(
                    lengths, Int(2), Len(lengths)
                ),  # Chop off uint16 we just read
                idx - Int(1),  # Decrement index
                sum + Uint16(lengths) + Int(2),  # Add length + 2 for uint16 length
            )
        )
    )
