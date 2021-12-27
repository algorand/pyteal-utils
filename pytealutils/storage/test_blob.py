from pyteal import *

from tests.conftest import *

from .blob import Blob

b = Blob()


def test_blob_zero():
    expr = Seq(b.zero(Int(0)), Log(b.read(Int(0), Int(0), Int(64))))
    expected = [logged_int(0) * 8]
    assert_stateful_output(expr, expected)


def test_blob_write_read_bytes():
    expr = Seq(
        b.zero(Int(0)),
        Pop(b.write(Int(0), Int(0), Bytes("deadbeef" * 8))),
        Log(b.read(Int(0), Int(32), Int(40))),
    )
    expected = [logged_bytes("deadbeef")]
    assert_stateful_output(expr, expected)


def test_blob_write_read_byte():
    expr = Seq(
        b.zero(Int(0)),
        b.set_byte(Int(0), Int(32), Int(123)),
        Log(Itob(b.get_byte(Int(0), Int(32)))),
    )
    expected = [logged_int(123)]
    assert_stateful_output(expr, expected)
