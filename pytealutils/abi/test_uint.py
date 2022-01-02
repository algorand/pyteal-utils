import algosdk.abi as sdkabi
from pyteal import *
from pytest import *

from tests.helpers import *

from .uint import *


def test_uint512():
    t = sdkabi.UintType(512)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint512.encode(BytesMinus(Uint512(Bytes(a)), Uint512(Bytes(b)))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint256():
    t = sdkabi.UintType(256)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint256.encode(BytesMinus(Uint256(Bytes(a)), Uint256(Bytes(b)))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint128():
    t = sdkabi.UintType(128)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint128.encode(BytesMinus(Uint128(Bytes(a)), Uint128(Bytes(b)))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint64():
    t = sdkabi.UintType(64)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint64.encode(Uint64(Bytes(a)) - Uint64(Bytes(b))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint32():
    t = sdkabi.UintType(32)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint32.encode(Uint32(Bytes(a)) - Uint32(Bytes(b))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)


def test_uint16():
    t = sdkabi.UintType(16)
    a, b = t.encode(500), t.encode(100)
    expr = Log(Uint16.encode(Uint16(Bytes(a)) - Uint16(Bytes(b))))
    output = [t.encode(400).hex()]
    assert_output(expr, output)
