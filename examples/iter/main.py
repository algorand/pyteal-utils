from pyteal import *

from pytealutils.iter import *


def test():

    i = ScratchVar()
    test = Seq(iterate(Log(Itob(i.load())), Int(10), i), Int(1))
    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Int(1), test],
    )


print(compileTeal(test(), mode=Mode.Application, version=5))
