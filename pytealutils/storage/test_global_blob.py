from algosdk.future.transaction import StateSchema
from pyteal import Int, Itob, Log, Seq

from tests.helpers import assert_output, logged_int

from .global_blob import GlobalBlob

# Can re-use the same blob
b = GlobalBlob()


def test_global_blob_zero():
    expr = Seq(b.zero(), Log(b.read(Int(0), Int(64))))
    expected = [logged_int(0) * 8]
    assert_output(expr, expected, global_schema=StateSchema(0, 64))


# TODO: Too expensive to do in a single call
# def test_global_blob_write_read_bytes():
#    expr = Seq(
#        b.zero(),
#        Pop(b.write(Int(0), Bytes("deadbeef" * 2))),
#        Log(b.read(Int(0), Int(8))),
#    )
#    expected = [logged_bytes("deadbeef")]
#    assert_output(expr, expected, global_schema=StateSchema(0, 64))


def test_global_blob_write_read_byte():
    expr = Seq(b.zero(), b.set_byte(Int(32), Int(123)), Log(Itob(b.get_byte(Int(32)))))
    expected = [logged_int(123)]
    assert_output(expr, expected, global_schema=StateSchema(0, 64))
