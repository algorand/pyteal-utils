from pyteal import Bytes, Int, Itob, Log, Pop, Seq

from tests.helpers import assert_stateful_output, logged_bytes, logged_int

from .local_blob import LocalBlob

# Can re-use the same blob
b = LocalBlob()


def test_local_blob_zero():
    expr = Seq(b.zero(Int(0)), Log(b.read(Int(0), Int(0), Int(64))))
    expected = [logged_int(0) * 8]
    assert_stateful_output(expr, expected)


def test_local_blob_write_read_bytes():
    expr = Seq(
        b.zero(Int(0)),
        Pop(b.write(Int(0), Int(0), Bytes("deadbeef" * 8))),
        Log(b.read(Int(0), Int(32), Int(40))),
    )
    expected = [logged_bytes("deadbeef")]
    assert_stateful_output(expr, expected)


def test_local_blob_write_read_byte():
    expr = Seq(
        b.zero(Int(0)),
        b.set_byte(Int(0), Int(32), Int(123)),
        Log(Itob(b.get_byte(Int(0), Int(32)))),
    )
    expected = [logged_int(123)]
    assert_stateful_output(expr, expected)
