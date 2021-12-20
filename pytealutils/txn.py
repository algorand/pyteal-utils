from pyteal import Global, TealType, Subroutine, Assert, Gtxn


@Subroutine(TealType.none)
def no_rekey(idx: TealType.uint64):
    return Assert(Gtxn[idx].rekey_to() == Global.zero_address)


@Subroutine(TealType.none)
def no_close_to(idx: TealType.uint64):
    return Assert(Gtxn[idx].close_remaineder_to() == Global.zero_address)


@Subroutine(TealType.none)
def no_asset_close_to(idx: TealType.uint64):
    return Assert(Gtxn[idx].asset_close_to() == Global.zero_address)
