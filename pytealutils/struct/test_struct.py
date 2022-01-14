from pyteal import *
from dataclasses import dataclass
from pyteal.ast.abi_bytes import String
from pyteal.ast.abi_uint import Uint64

from tests.helpers import *

from .struct import Struct


@dataclass
class MyStruct(Struct):
    id: Uint64
    user: String
    options: String 


def test_struct():
    ms = MyStruct(Uint64(123), String("abc"), String("def"))

    expr = Log(Itob(ms.get("id")))
    output = [logged_int(123)]

    assert_output(expr, output)
