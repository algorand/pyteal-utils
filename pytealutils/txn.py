from pyteal import Global, TealType, Subroutine, Assert, Gtxn


@Subroutine(TealType.none)
def no_rekey(idx: TealType.uint64):
    """Checks that the rekey_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].rekey_to() == Global.zero_address)


@Subroutine(TealType.none)
def no_close_to(idx: TealType.uint64):
    """Checks that the close_remainder_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].close_remaineder_to() == Global.zero_address)


@Subroutine(TealType.none)
def no_asset_close_to(idx: TealType.uint64):
    """Checks that the asset_close_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].asset_close_to() == Global.zero_address)
