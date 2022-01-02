import algosdk.abi as sdkabi
from pyteal import *

from tests.helpers import *

from .bytes import String
from .collections import DynamicArray


def test_abi_fixed_array_string():
    StringArray = DynamicArray(String)
    t = sdkabi.ArrayDynamicType(sdkabi.StringType())

    encoded = t.encode(["this", "is", "a", "test"])

    ptarray = StringArray(Bytes(encoded))

    expr = Seq(ptarray.init(), Log(ptarray.serialize()))

    expected = [encoded.hex()]
    assert_output(expr, expected)


def test_abi_fixed_array_uint():
    pass


def test_abi_dynamic_array_bytes():
    pass


def test_abi_dynamic_array_uint():
    pass


def test_tuple():
    pass
