from pyteal import Int, Expr, Subroutine, ScratchVar, For, TealType

# TODO: pass the scratch var to use?

# TODO: union type?
def range(n: Int, sub: Expr):
    @Subroutine(TealType.none)
    def _impl():
        i = ScratchVar()
        init = i.store(Int(0))
        cond = i.load() < n
        iter = i.store(i.load() + Int(1))
        return For(init, cond, iter).Do(sub)

    return _impl()
