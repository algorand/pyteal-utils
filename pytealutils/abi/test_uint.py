from pyteal import *
from pytest import *

from tests.helpers import *

from .uint import *


def zpad(val: str, bits: int):
    # pad with 0s, since its a string, each byte is represented by 2 chars so *2
    b = val.zfill(int(bits / 8) * 2)
    return Bytes("base16", b)


def test_uint512():
    expr = Log(
        Uint512.encode(
            BytesMinus(Uint512(zpad("dead", 512)), Uint512(zpad("beef", 512)))
        )
    )
    output = [logged_int(8126, 512)]
    assert_output(expr, output)


def test_uint256():
    expr = Log(
        Uint256.encode(
            BytesMinus(Uint256(zpad("dead", 256)), Uint256(zpad("beef", 256)))
        )
    )
    output = [logged_int(8126, 256)]
    assert_output(expr, output)


def test_uint128():
    expr = Log(
        Uint128.encode(
            BytesMinus(Uint128(zpad("dead", 128)), Uint128(zpad("beef", 128)))
        )
    )
    output = [logged_int(8126, 128)]
    assert_output(expr, output)


def test_uint64():
    expr = Log(Uint64.encode(Uint64(zpad("dead", 64)) - Uint64(zpad("beef", 64))))
    output = [logged_int(8126, 64)]
    assert_output(expr, output)


def test_uint32():
    expr = Log(Uint32.encode(Uint32(zpad("dead", 32)) - Uint32(zpad("beef", 32))))
    output = [logged_int(8126, 32)]
    assert_output(expr, output)


def test_uint16():
    expr = Log(Uint16.encode(Uint16(zpad("dead", 16)) - Uint16(zpad("beef", 16))))
    output = [logged_int(8126, 16)]
    assert_output(expr, output)
