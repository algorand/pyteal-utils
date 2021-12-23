from iter import iterate
from pyteal import (
    Bytes,
    Int,
    Itob,
    Log,
    ScratchVar,
    Subroutine,
    SubroutineCall,
    TealType,
)

from tests.conftest import compile_app, fully_compile


def test_iterate():
    res = iterate(Log(Bytes("a")), Int(10))
    assert type(res) is SubroutineCall
    assert res is not None

    src = compile_app(res)
    assert len(src) > 0

    res = fully_compile(src)
    assert len(res['hash']) == 58


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

    res = fully_compile(src)
    assert len(res['hash']) == 58