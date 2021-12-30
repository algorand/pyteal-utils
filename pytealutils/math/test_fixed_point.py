import decimal
from decimal import *

from pyteal import *

from tests.helpers import assert_output, logged_bytes

from .fixed_point import *


def float_as_string(a: float, b: float, p: int, op):
    getcontext().prec = p
    a = Decimal(a)
    b = Decimal(b)
    return "{}".format(op(a, b))


def test_fixed_point_add():
    a, b = 2.3, 3.3
    fp = FixedPoint(64, 8)

    FixedPoint(64, 16)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_add(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [
        logged_bytes(float_as_string(a, b, fp.precision, decimal.getcontext().add))
    ]

    assert_output(expr, output)


def test_fixed_point_sub():
    b, a = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_sub(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [
        logged_bytes(float_as_string(a, b, fp.precision, decimal.getcontext().subtract))
    ]

    assert_output(expr, output)


def test_fixed_point_div():
    b, a = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_div(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [
        logged_bytes(float_as_string(a, b, fp.precision, decimal.getcontext().divide))
    ]

    assert_output(expr, output)


def test_fixed_point_mul():
    a, b = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_mul(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [
        logged_bytes(float_as_string(a, b, fp.precision, decimal.getcontext().multiply))
    ]

    assert_output(expr, output)
