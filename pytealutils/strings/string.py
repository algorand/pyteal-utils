from pyteal import (
    Assert,
    Bytes,
    Concat,
    Extract,
    GetByte,
    If,
    Int,
    Itob,
    Len,
    ScratchVar,
    Seq,
    Subroutine,
    Substring,
    TealType,
)

from pytealutils.math import exp10

# Magic number to convert between ascii chars and integers
_ascii_zero = 48
_ascii_nine = _ascii_zero + 9
ascii_zero = Int(_ascii_zero)
ascii_nine = Int(_ascii_nine)


@Subroutine(TealType.uint64)
def ascii_to_int(arg: TealType.uint64):
    """Convert the integer representing a character in ascii to the actual integer it represents"""
    return Seq(Assert(arg >= ascii_zero), Assert(arg <= ascii_nine), arg - ascii_zero)


@Subroutine(TealType.bytes)
def int_to_ascii(arg: TealType.uint64):
    """Convert an integer to the ascii byte that represents it"""
    return Extract(Bytes("0123456789"), arg, Int(1))


@Subroutine(TealType.uint64)
def atoi(a: TealType.bytes):
    """Convert a byte string representing a number to the integer value it represents"""
    return If(
        Len(a) > Int(0),
        (ascii_to_int(GetByte(a, Int(0))) * exp10(Len(a) - Int(1)))
        + atoi(Substring(a, Int(1), Len(a))),
        Int(0),
    )


@Subroutine(TealType.bytes)
def itoa(i: TealType.uint64):
    """Convert an integer to the ascii byte string it represents"""
    return If(
        i == Int(0),
        Bytes("0"),
        Concat(
            If(i / Int(10) > Int(0), itoa(i / Int(10)), Bytes("")),
            int_to_ascii(i % Int(10)),
        ),
    )


@Subroutine(TealType.bytes)
def head(s: TealType.bytes):
    """Get the first byte from a bytestring, returns a uint64"""
    return Extract(s, Int(0), Int(1))


@Subroutine(TealType.bytes)
def tail(s: TealType.bytes):
    """Return the string with the first character removed"""
    return Substring(s, Int(1), Len(s))


@Subroutine(TealType.bytes)
def encode_uvarint(val: TealType.uint64, b: TealType.bytes):
    """
    Returns the uvarint encoding of an integer

    Useful in the case that the bytecode for a contract is being populated, since
    integers in a contract are uvarint encoded

    This subroutine is recursive, the first call should include
    the integer to be encoded and an empty bytestring

    """
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
