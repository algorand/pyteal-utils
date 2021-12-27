from algosdk.future.transaction import StateSchema
from pyteal import *

from tests.conftest import *

from .inline_asm import InlineAssembly


def test_inline_assembly():
    get_uint8 = """
extract 7 1
"""
    s = ScratchSlot()
    expr = Seq(InlineAssembly(get_uint8, Itob(Int(255))), s.store(), Log(s.load()))

    expected = [logged_int(255)[-2:]]
    assert_output(expr, expected, global_schema=StateSchema(0, 64))
