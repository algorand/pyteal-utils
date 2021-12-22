from pyteal import Assert, Expr, Global, Gtxn, Subroutine, TealType


@Subroutine(TealType.none)
def assert_no_rekey(idx: TealType.uint64) -> Expr:
    """Checks that the rekey_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].rekey_to() == Global.zero_address)


@Subroutine(TealType.none)
def assert_no_close_to(idx: TealType.uint64) -> Expr:
    """Checks that the close_remainder_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].close_remaineder_to() == Global.zero_address)


@Subroutine(TealType.none)
def assert_no_asset_close_to(idx: TealType.uint64) -> Expr:
    """Checks that the asset_close_to field is empty, Assert if it is set"""
    return Assert(Gtxn[idx].asset_close_to() == Global.zero_address)
