from pyteal import Bytes, Int, Itob, Log

from tests.conftest import assert_output, logged_bytes, logged_int

from .string import atoi, encode_uvarint, head, itoa, tail


def test_atoi():
    expr = Log(Itob(atoi(Bytes("123"))))
    output = [logged_int(int(123))]
    assert_output(expr, output)


def test_itoa():
    expr = Log(itoa(Int(123)))
    output = [logged_bytes("123")]
    assert_output(expr, output)


def test_head():
    expr = Log(head(Bytes("deadbeef")))
    output = [logged_bytes("d")]
    assert_output(expr, output)


def test_tail():
    expr = Log(tail(Bytes("deadbeef")))
    output = [logged_bytes("eadbeef")]
    assert_output(expr, output)


def test_encode_uvarint():
    expr = Log(encode_uvarint(Int(500), Bytes("")))
    output = ["f403"]
    assert_output(expr, output)
