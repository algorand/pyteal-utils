import algosdk.abi as sdkabi
from pyteal import *

from tests.helpers import *

from .bytes import String
from .collections import DynamicArray, FixedArray, Tuple
from .uint import Uint64


def test_abi_collection_dynamic_array_string():
    StringArray = DynamicArray(String)
    t = sdkabi.ArrayDynamicType(sdkabi.StringType())

    arr = ["dead", "beef", "dead", "beef"]
    encoded = t.encode(arr)

    ptarray = StringArray([String(Bytes(s)) for s in arr])

    expr = Seq(Log(ptarray.encode()))

    expected = [encoded.hex()]
    assert_output(expr, expected, pad_budget=15)


def test_abi_collection_fixed_array_string():
    fixedarr = FixedArray(String, 3)
    sdk_tuple = sdkabi.ArrayStaticType(sdkabi.StringType(), 3)

    input = ["dead", "beef", "dead"]
    b = sdk_tuple.encode(input)
    t = fixedarr.decode(Bytes(b))
    idx = 2

    if type(input[idx]) == int:
        output = [logged_int(input[idx])]
        expr = Seq(Log(Itob(t[idx])))
    else:
        output = [logged_bytes(input[idx])]
        expr = Seq(Log(t[idx]))

    assert_output(expr, output)

    assert_output(
        Log(
            fixedarr(
                String(Bytes(input[0])),
                String(Bytes(input[1])),
                String(Bytes(input[2])),
            )
        ),
        [b.hex()],
    )


def test_abi_collection_tuple():
    teal_tuple = Tuple([String, Uint64, String, String, String, String])
    sdk_tuple = sdkabi.TupleType(
        [
            sdkabi.StringType(),
            sdkabi.UintType(64),
            sdkabi.StringType(),
            sdkabi.StringType(),
            sdkabi.StringType(),
            sdkabi.StringType(),
        ]
    )

    input = ["A", 234231, "Z", "B", "C", "Dadsf"]
    idx = 4
    b = sdk_tuple.encode(input)
    t = teal_tuple.decode(Bytes(b))

    if type(input[idx]) == int:
        output = [logged_int(input[idx])]
        expr = Seq(Log(Itob(t[idx])))
    else:
        output = [logged_bytes(input[idx])]
        expr = Seq(Log(t[idx]))

    assert_output(expr, output)

    assert_output(
        Log(
            teal_tuple(
                String(Bytes(input[0])),
                Uint64(Int(input[1])),
                String(Bytes(input[2])),
                String(Bytes(input[3])),
                String(Bytes(input[4])),
                String(Bytes(input[5])),
            )
        ),
        [b.hex()],
    )
