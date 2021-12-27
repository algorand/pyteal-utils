from algosdk.future.transaction import StateSchema
from pyteal import *

from tests.conftest import *


def test_custom_op():

    expr = Seq(Log(Bytes("hi")))

    expected = [logged_bytes("hi")]
    assert_output(expr, expected, global_schema=StateSchema(0, 64))
