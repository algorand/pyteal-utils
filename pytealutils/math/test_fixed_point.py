from pyteal import *

from tests.helpers import assert_output, logged_bytes

from .fixed_point import *


def test_fixed_point():
    fp = FixedPoint(64, 8)
    FixedPoint(64, 16)

    fp1 = fp.wrap(2.3)
    fp2 = fp.wrap(3.3)

    s = ScratchVar()
    expr = Seq(s.store(fp_add(fp1, fp2)), Log(fp.to_ascii(s.load())))

    output = [logged_bytes("5.6")]

    assert_output(expr, output, pad_budget=2)
