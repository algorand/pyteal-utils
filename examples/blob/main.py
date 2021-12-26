from pyteal import (Assert, Bytes, Cond, Int, Len, Log, Mode, OnComplete, Pop,
                    Seq, Txn, compileTeal)

from pytealutils.storage.blob import Blob


def test():
    b = Blob()

    data = Bytes("base16", "deadbeef" * 16)
    test = Seq(
        b.zero(Int(0)),  # Required on initialization
        Pop(
            b.write(Int(0), Int(0), data)
        ),  # write returns the number of bits written, just pop it
        Log(
            b.read(Int(0), Int(0), Int(32))
        ),  # Should return the first 32 bytes of `data`
        Assert(b.read(Int(0), Int(0), Len(data)) == data),  # Should pass assert
        Int(1),
    )
    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Int(1), test],
    )


print(compileTeal(test(), mode=Mode.Application, version=5))
