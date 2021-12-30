from pyteal import *

from tests.helpers import assert_close_enough

from .fixed_point import *


def test_fixed_point_add():
    a, b = 2.3, 3.3
    fp = FixedPoint(64, 8)

    FixedPoint(64, 16)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_add(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [a + b]
    precisions = [fp.precision]

    assert_close_enough(expr, output, precisions)


def test_fixed_point_sub():
    b, a = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_sub(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [a - b]
    precisions = [fp.precision]

    assert_close_enough(expr, output, precisions)


def test_fixed_point_div():
    b, a = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_div(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [a / b]
    precisions = [fp.precision]

    assert_close_enough(expr, output, precisions)


def test_fixed_point_mul():
    a, b = 2.3, 3.3

    fp = FixedPoint(64, 8)
    fp1 = fp.wrap(a)
    fp2 = fp.wrap(b)

    s = ScratchVar()
    expr = Seq(s.store(fp_mul(fp1, fp2)), Log(fp.to_ascii(s.load())))
    output = [a * b]
    precisions = [fp.precision]

    assert_close_enough(expr, output, precisions)
