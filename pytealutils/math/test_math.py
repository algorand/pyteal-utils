from pyteal import Int, Itob, Log

from tests.helpers import assert_output, logged_int

from .math import div_ceil, exp10, max, min


def test_exp10():
    expr = Log(Itob(exp10(Int(3))))
    output = [logged_int(int(1e3))]
    assert_output(expr, output)


def test_min():
    expr = Log(Itob(min(Int(100), Int(10))))
    output = [logged_int(int(10))]
    assert_output(expr, output)


def test_max():
    expr = Log(Itob(max(Int(100), Int(10))))
    output = [logged_int(int(100))]
    assert_output(expr, output)


def test_div_ceil():
    expr = Log(Itob(div_ceil(Int(100), Int(3))))
    output = [logged_int(int(34))]
    assert_output(expr, output)
