from pyteal import *

from .math import exp10

ascii_offset = Int(48)  # Magic number to convert between ascii chars and integers


@Subroutine(TealType.uint64)
def ascii_to_int(arg: TealType.uint64):
    return arg - ascii_offset


@Subroutine(TealType.bytes)
def int_to_ascii(arg: TealType.uint64):
    # return arg + ascii_offset Just returns a uint64, cant convert to bytes type
    return Substring(Bytes("0123456789"), arg, arg + Int(1))


@Subroutine(TealType.uint64)
def atoi(a: TealType.bytes):
    return If(
        Len(a) > Int(0),
        (ascii_to_int(head(a)) * exp10(Len(a) - Int(1)))
        + atoi(Substring(a, Int(1), Len(a))),
        Int(0),
    )


@Subroutine(TealType.bytes)
def itoa(i: TealType.uint64):
    return If(
        i == Int(0),
        Bytes("0"),
        Concat(
            If(i / Int(10) > Int(0), itoa(i / Int(10)), Bytes("")),
            int_to_ascii(i % Int(10)),
        ),
    )


@Subroutine(TealType.uint64)
def head(s: TealType.bytes):
    return GetByte(s, Int(0))


@Subroutine(TealType.bytes)
def tail(s: TealType.bytes):
    return Substring(s, Int(1), Len(s))


@Subroutine(TealType.bytes)
def encode_uvarint(val: TealType.uint64, b: TealType.bytes):
    buff = ScratchVar()
    return Seq(
        buff.store(b),
        Concat(
            buff.load(),
            If(
                val >= Int(128),
                encode_uvarint(
                    val >> Int(7),
                    Extract(Itob((val & Int(255)) | Int(128)), Int(7), Int(1)),
                ),
                Extract(Itob(val & Int(255)), Int(7), Int(1)),
            ),
        ),
    )
