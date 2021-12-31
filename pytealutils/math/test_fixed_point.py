from pyteal import *

from tests.helpers import assert_close_enough

from .fixed_point import *

tests_per_contract = 15


def generate_valid_operands():
    """generate_valid_operands generates operands and"""
    # random.seed()
    # N = random.randrange(8, 64, 8)
    # M = random.randrange(1, 2, 1)
    N = 64
    M = 3
    # TODO
    A = 3.3
    B = 2.3
    return FixedPoint(N, M, A), FixedPoint(N, M, B)


# def generate_invalid_operands():
#    """generate_invalid_operands generates operands and"""
#    return 2.3, 3.3, FixedPoint(64, 8)


def test_fixedpoint_add():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b = generate_valid_operands()

        exprs.append(Log(fp_to_ascii(a + b)))
        outputs.append(a.raw + b.raw)
        precisions.append(a.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_sub():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b = generate_valid_operands()

        exprs.append(Log(fp_to_ascii(a - b)))
        outputs.append(a.raw - b.raw)
        precisions.append(a.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_div():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b = generate_valid_operands()

        exprs.append(Log(fp_to_ascii(a / b)))
        outputs.append(a.raw / b.raw)
        precisions.append(a.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_mul():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b = generate_valid_operands()

        exprs.append(Log(fp_to_ascii(a * b)))
        outputs.append(a.raw * b.raw)
        precisions.append(a.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_rescale():
    exprs, outputs, precisions = [], [], []

    a = FixedPoint(64, 2, 15234.32)

    exprs.append(Log(fp_to_ascii(a.rescaled(3))))
    outputs.append(a.raw)
    precisions.append(a.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)
