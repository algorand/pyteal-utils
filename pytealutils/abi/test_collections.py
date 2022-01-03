import algosdk.abi as sdkabi
from pyteal import *

from tests.helpers import *

from .bytes import String
from .collections import Tuple
from .uint import Uint64

# def test_abi_dynamic_array_string():
#    StringArray = DynamicArray(String)
#    t = sdkabi.ArrayDynamicType(sdkabi.StringType())
#
#    encoded = t.encode(["this", "is", "a", "test"])
#
#    ptarray = StringArray(Bytes(encoded))
#
#    expr = Seq(ptarray.init(), Log(ptarray.encode()))
#
#    expected = [encoded.hex()]
#    assert_output(expr, expected)
#
#
# def test_abi_dynamic_array_uint():
#    UintArray = DynamicArray(Uint64)
#    t = sdkabi.ArrayDynamicType(sdkabi.UintType(64))
#
#    encoded = t.encode([10, 20, 30, 40])
#
#    print(encoded.hex())
#    return
#    ptarray = UintArray(Bytes(encoded))
#
#    expr = Seq(ptarray.init(), Log(ptarray.serialize()))
#
#    expected = [encoded.hex()]
#    assert_output(expr, expected)
#
#
# def test_abi_fixed_array_bytes():
#    t = sdkabi.ArrayStaticType(sdkabi.StringType(), 2)
#    b = t.encode(["asdf", "asdf"])
#    print(b.hex())
#


def test_abi_fixed_array_uint():
    pass


def test_abi_tuple():

    teal_tuple = Tuple([String, Uint64, String])
    print(teal_tuple)

    sdk_tuple = sdkabi.TupleType(
        [sdkabi.StringType(), sdkabi.UintType(64), sdkabi.StringType()]
    )

    input = ["A", 1, "Z"]
    idx = 0

    b = sdk_tuple.encode(input)
    t = teal_tuple.decode(Bytes(b))

    if type(input[idx]) == int:
        output = [logged_int(input[idx])]
        expr = Seq(Log(Itob(t[idx])))
    else:
        output = [logged_bytes(input[idx])]
        expr = Seq(Log(t[idx]))

    assert_output(expr, output)

    # assert_output(Log(teal_tuple(String(Bytes(input[0])), Uint64(Int(input[1])), String(Bytes(input[2]))).encode()), [b.hex()])
