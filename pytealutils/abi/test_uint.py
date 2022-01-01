from pyteal import *
from pytest import *

from tests.helpers import *

from .uint import *


def test_uint512():
    pass


def test_uint256():
    pass


def test_uint128():
    pass


def test_uint64():
    pass


def test_uint32():
    pass


def test_uint16():
    expr = Log(Itob(Uint16(Bytes("base16", "dead")) - Uint16(Bytes("base16", "beef"))))
    output = [logged_int(8126)]
    assert_output(expr, output)
