from pyteal import *


@Subroutine(TealType.anytype)
def must_get(key: TealType.bytes) -> Expr:
    """Returns the result of a global storage MaybeValue if it exists, else Assert and fail the program"""
    maybe = App.globalGet(0, key)
    return Seq(maybe, Assert(maybe.hasValue()), maybe.value())


@Subroutine(TealType.anytype)
def get_else(key: TealType.bytes, default: Expr) -> Expr:
    """Returns the result of a global storage MaybeValue if it exists, else return a default value"""
    maybe = App.globalGet(0, key)
    return Seq(maybe, If(maybe.hasValue(), maybe.value(), default))


@Subroutine(TealType.anytype)
def local_must_get(acct: TealType.uint64, key: TealType.bytes) -> Expr:
    """Returns the result of a loccal storage MaybeValue if it exists, else Assert and fail the program"""
    mv = App.localGetEx(acct, Int(0), key)
    return Seq(mv, Assert(mv.hasValue()), mv.value())


@Subroutine(TealType.anytype)
def local_get_else(acct: TealType.uint64, key: TealType.bytes, default: Expr) -> Expr:
    """Returns the result of a local storage MaybeValue if it exists, else return a default value"""
    mv = App.localGetEx(acct, Int(0), key)
    return Seq(mv, If(mv.hasValue()).Then(mv.value()).Else(default))
