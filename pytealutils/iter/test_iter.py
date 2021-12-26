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

from tests.conftest import compile_app, execute_app, fully_compile


def test_iterate():
    expr = iterate(Log(Bytes("a")), Int(10))
    assert type(expr) is SubroutineCall
    assert expr is not None

    src = compile_app(expr)
    assert len(src) > 0

    compiled = fully_compile(src)
    assert len(compiled["hash"]) == 58

    result = execute_app(compiled["result"])
    assert result == ["a"] * 10


def test_iterate_with_closure():
    i = ScratchVar()

    @Subroutine(TealType.none)
    def logthing():
        return Log(Itob(i.load()))

    expr = iterate(logthing(), Int(10), i)
    assert expr is not None
    assert type(expr) is SubroutineCall

    src = compile_app(expr)
    assert len(src) > 0

    compiled = fully_compile(src)
    assert len(compiled["hash"]) == 58

    result = execute_app(compiled["result"])
    assert result == [x.to_bytes(8, "big").decode("ascii") for x in range(10)]
