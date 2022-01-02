import algosdk.abi as sdkabi
from pyteal import *
from pytest import *

from tests.helpers import *

from .bytes import *


def test_abi_string():
    b = sdkabi.StringType().encode("stringvar")
    expr = Log(String.encode(String(Bytes(b))))
    output = [b.hex()]
    assert_output(expr, output)


def test_abi_address():
    b = sdkabi.AddressType().encode(
        "DCIPMQ3SDOVBX5IUY65LR7BZ2R63JCULO72J7IS3W2PUNW7JTAGYEHBRRA"
    )
    expr = Log(Address.encode(Address(Bytes(b))))
    output = [b.hex()]
    assert_output(expr, output)
