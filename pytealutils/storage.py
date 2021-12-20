from pyteal import *


@Subroutine(TealType.anytype)
def must_get(key: TealType.bytes) -> Expr:
    maybe = App.globalGet(0, key)
    return Seq(maybe, Assert(maybe.hasValue()), maybe.value())


@Subroutine(TealType.anytype)
def get_else(key: TealType.bytes, default: Expr) -> Expr:
    maybe = App.globalGet(0, key)
    return Seq(maybe, If(maybe.hasValue(), maybe.value(), default))


@Subroutine(TealType.anytype)
def local_must_get(acct: TealType.uint64, key: TealType.bytes) -> Expr:
    mv = App.localGetEx(acct, Int(0), key)
    return Seq(mv, Assert(mv.hasValue()), mv.value())


@Subroutine(TealType.anytype)
def local_get_else(acct: TealType.uint64, key: TealType.bytes, default: Expr) -> Expr:
    mv = App.localGetEx(acct, Int(0), key)
    return Seq(mv, If(mv.hasValue()).Then(mv.value()).Else(default))
