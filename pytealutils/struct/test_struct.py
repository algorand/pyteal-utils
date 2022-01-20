from dataclasses import dataclass

from pyteal import *

from tests.helpers import *

from .struct import Struct


@dataclass
class MyStruct(Struct):
    id: Uint64
    user: String
    options: String


def test_struct():
    ms = MyStruct(Uint64(123), String("abc"), String("def"))

    print(ms)
    # print(ms.get("id"))
    # expr = Log(Itob(ms.get("id")))
    # output = [logged_int(123)]

    # assert_output(expr, output)
