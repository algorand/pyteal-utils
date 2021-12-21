from pyteal import Int, Expr, Subroutine, ScratchVar, For, TealType

# TODO: pass the scratch var to use?

# TODO: union type?
def iterate(sub: Expr, n: Int, i: ScratchVar = None):

    if i is None:
        i = ScratchVar()

    @Subroutine(TealType.none)
    def _impl():
        init = i.store(Int(0))
        cond = i.load() < n
        iter = i.store(i.load() + Int(1))
        return For(init, cond, iter).Do(sub)

    return _impl()
