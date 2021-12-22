from iter import iterate
from pyteal import (
    Bytes,
    Expr,
    Int,
    Itob,
    Log,
    Mode,
    ScratchVar,
    Seq,
    Subroutine,
    SubroutineCall,
    TealType,
    compileTeal,
)


def test_iterate():
    res = iterate(Log(Bytes("a")), Int(10))
    assert type(res) is SubroutineCall
    assert res is not None

    src = compile_app(res)
    assert len(src) > 0


def test_iterate_with_closure():

    i = ScratchVar()

    @Subroutine(TealType.none)
    def logthing():
        return Log(Itob(i.load()))

    res = iterate(logthing(), Int(10), i)
    assert type(res) is SubroutineCall
    assert res is not None

    src = compile_app(res)
    assert len(src) > 0


def compile_app(method: Expr):
    return compileTeal(Seq(method, Int(1)), mode=Mode.Application, version=5)
