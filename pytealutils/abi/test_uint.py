from pyteal import *
from pytest import *

from tests.helpers import *

from .uint import *


def test_uint512():
    pass


def test_uint256():
    pass


def test_uint128():
    expr = Log(
        Uint128.encode(
            BytesMinus(
                Uint128(Bytes("base16", "00" * 14 + "dead")),
                Uint128(Bytes("base16", "00" * 14 + "beef")),
            )
        )
    )
    output = [bytes.fromhex("00000000000000000000000000001fbe").hex()]
    assert_output(expr, output)


def test_uint64():
    expr = Log(
        Itob(
            Uint64(Bytes("base16", "00000000dead"))
            - Uint64(Bytes("base16", "00000000beef"))
        )
    )
    output = [logged_int(8126)]
    assert_output(expr, output)


def test_uint32():
    expr = Log(
        Itob(Uint32(Bytes("base16", "0000dead")) - Uint32(Bytes("base16", "0000beef")))
    )
    output = [logged_int(8126)]
    assert_output(expr, output)


def test_uint16():
    expr = Log(Itob(Uint16(Bytes("base16", "dead")) - Uint16(Bytes("base16", "beef"))))
    output = [logged_int(8126)]
    assert_output(expr, output)
