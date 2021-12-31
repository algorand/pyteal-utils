import random

from pyteal import *

from tests.helpers import assert_close_enough

from .fixed_point import *

tests_per_contract = 15


def generate_valid_operands():
    """generate_valid_operands generates operands and"""
    # random.seed()
    # TODO
    return 3.3, 2.3, FixedPoint(random.randrange(8, 64, 8), random.randrange(1, 2, 1))


def generate_invalid_operands():
    """generate_invalid_operands generates operands and"""
    return 2.3, 3.3, FixedPoint(64, 8)


def test_fixedpoint_add():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b, fp = generate_valid_operands()

        exprs.append(Log(fp.to_ascii(fp_add(fp.wrap(a), fp.wrap(b)))))

        outputs.append(a + b)
        precisions.append(fp.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_sub():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b, fp = generate_valid_operands()

        exprs.append(Log(fp.to_ascii(fp_sub(fp.wrap(a), fp.wrap(b)))))

        outputs.append(a - b)
        precisions.append(fp.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_div():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b, fp = generate_valid_operands()

        exprs.append(Log(fp.to_ascii(fp_div(fp.wrap(a), fp.wrap(b)))))

        outputs.append(a / b)
        precisions.append(fp.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_fixedpoint_mul():
    exprs, outputs, precisions = [], [], []
    for _ in range(tests_per_contract):
        a, b, fp = generate_valid_operands()

        exprs.append(Log(fp.to_ascii(fp_mul(fp.wrap(a), fp.wrap(b)))))

        outputs.append(a * b)
        precisions.append(fp.precision)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)
