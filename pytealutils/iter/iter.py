from pyteal import Expr, For, Int, ScratchVar, Subroutine, TealType


def iterate(sub: Expr, n: Int, i: ScratchVar = None) -> Expr:
    if i is None:
        i = ScratchVar()

    @Subroutine(TealType.none)
    def _impl() -> Expr:
        init = i.store(Int(0))
        cond = i.load() < n
        iter = i.store(i.load() + Int(1))
        return For(init, cond, iter).Do(sub)

    return _impl()
