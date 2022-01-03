import algosdk.abi as sdkabi
from pyteal import *
from pytest import *

from tests.helpers import *

from .uint import *


def test_uint512():
    t = sdkabi.UintType(512)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint512(BytesMinus(Uint512(Bytes(a)), Uint512(Bytes(b)))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint256():
    t = sdkabi.UintType(256)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint256((BytesMinus(Uint256(Bytes(a)), Uint256(Bytes(b))))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint128():
    t = sdkabi.UintType(128)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint128(BytesMinus(Uint128(Bytes(a)), Uint128(Bytes(b)))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint64():
    t = sdkabi.UintType(64)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint64(Uint64.decode(Bytes(a)) - Uint64.decode(Bytes(b))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint32():
    t = sdkabi.UintType(32)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint32(Uint32.decode(Bytes(a)) - Uint32.decode(Bytes(b))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint16():
    t = sdkabi.UintType(16)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint16(Uint16.decode(Bytes(a)) - Uint16.decode(Bytes(b))).encode())
    output = [t.encode(400).hex()]
    assert_output(expr, output)
