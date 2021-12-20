from pyteal import *
from pytealutils.iter import range


def test():

    test = Seq(range(Int(10), Log(Bytes("Hi"))), Int(1))
    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Int(1), test],
    )


print(compileTeal(test(), mode=Mode.Application, version=5))
