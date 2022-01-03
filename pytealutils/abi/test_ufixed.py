import algosdk.abi as sdkabi
from algosdk.abi.ufixed_type import UfixedType
from pyteal import *

from tests.helpers import assert_close_enough

from .ufixed import *

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
    return A, B, UFixed(N, M)


def sdk_encode(t: UfixedType, v: float):
    return Bytes(t.encode(int(v * (10 ** t.precision))))


def test_ufixed_add():
    exprs, outputs, precisions = [], [], []
    for _ in range(1):
        a, b, fp = generate_valid_operands()
        t = sdkabi.UfixedType(fp.bits, fp.precision)

        exprs.append(Log(fp.encode(fp(a) + fp(b))))
        outputs.append(a + b)
        precisions.append(t)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_ufixed_sub():
    exprs, outputs, precisions = [], [], []
    for _ in range(1):
        a, b, fp = generate_valid_operands()
        t = sdkabi.UfixedType(fp.bits, fp.precision)

        exprs.append(Log(fp.encode(fp(a) - fp(b))))
        outputs.append((a - b))
        precisions.append(t)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_ufixed_div():
    exprs, outputs, precisions = [], [], []
    for _ in range(1):
        a, b, fp = generate_valid_operands()
        t = sdkabi.UfixedType(fp.bits, fp.precision)

        exprs.append(Log(fp.encode(fp(a) / fp(b))))
        outputs.append(a / b)
        precisions.append(t)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_ufixed_mul():
    exprs, outputs, precisions = [], [], []
    for _ in range(1):
        a, b, fp = generate_valid_operands()
        t = sdkabi.UfixedType(fp.bits, fp.precision)

        exprs.append(Log(fp.encode(fp(a) * fp(b))))
        outputs.append(a * b)
        precisions.append(t)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)


def test_ufixed_rescale():
    exprs, outputs, precisions = [], [], []

    fp = UFixed(64, 2)
    t = sdkabi.UfixedType(fp.bits, fp.precision)
    val = 123123.12

    exprs.append(Log(fp.encode(fp(val))))
    outputs.append(val)
    precisions.append(t)

    assert_close_enough(Seq(*exprs), outputs, precisions, pad_budget=15)
