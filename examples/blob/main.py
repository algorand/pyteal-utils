from pyteal import *
from pytealutils.storage.blob import Blob


def test():
    b = Blob()

    data = Bytes("deadbeef" * 16)
    test = Seq(
        b.zero(),  # Required on initialization
        Pop(b.write(Int(0), Int(0), data)),
        Assert(b.read(Int(0), Int(7), Int(32)) == Substring(data, Int(7), Int(32))),
        Int(1),
    )
    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Int(1), test],
    )


print(compileTeal(test(), mode=Mode.Application, version=5))
