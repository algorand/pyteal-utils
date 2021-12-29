from pyteal import Int, Itob, Log

from tests.helpers import assert_output, logged_int

import math as pymath

from .math import (
    log2,
    pow10,
    max,
    min,
    div_ceil,
    exponential,
    factorial,
    wide_factorial,
)

# def test_bytes_factorial():
#    num = 55
#    expr = Log(bytes_factorial(Itob(Int(num))))
#    #output = [logged_int(int(pymath.factorial(num)))]
#    print(pymath.factorial(num)/1000)
#    assert_output(expr, [], pad_budget=15)

# def test_factorial():
#    num = 21
#    expr = Log(Itob(factorial(Int(num))))
#    output = [logged_int(int(pymath.factorial(num)))]
#    print(pymath.factorial(num))
#    assert_output(expr, output)


def test_wide_exponential():
    num = 10
    expr = Log(exponential(Int(num), Int(30)))
    output = [logged_int(int(pymath.exp(num)))]
    assert_output(expr, output, pad_budget=15)


# def test_log2():
#    num = 123123123
#    expr = Log(Itob(log2(Int(num))))
#    output = [logged_int(int(pymath.log2(num)))]
#    print(pymath.log2(num))
#    assert_output(expr, output)

# def test_log10():
#    num = 123123123
#    expr = Log(Itob(scaled_log10(Int(num))))
#    output = [logged_int(int(pymath.log10(num)))]
#    print(pymath.log10(num))
#    assert_output(expr, output)


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
