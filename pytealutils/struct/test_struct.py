from pyteal import *
from pyteal.ast.abi_bytes import String
from pyteal.ast.abi_uint import Uint64

from tests.helpers import *

from .struct import Struct, StructField


def test_struct():

    my_struct_codec = Struct(
        StructField("id", Uint64),
        StructField("user", String),
        StructField("options", String)
    )
    instance = my_struct_codec(Uint64(123), String(Bytes("abc")), String(Bytes("def")))

    expr = Log(Itob(instance.get("id")))
    output = [logged_int(123)]

    assert_output(expr, output)
