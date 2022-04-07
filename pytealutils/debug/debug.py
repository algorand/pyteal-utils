from inspect import currentframe

from pyteal import Bytes, Concat, Global, Log

from ..strings import itoa


def pimp_my_assert(a: Expr) -> Expr:
    return Assert(And(a, Int(currentframe().f_back.f_lineno)))
    # TODO: come up with a way to switch on prod compile
    # Assert(a)


def log_stats():
    return Log(
        Concat(
            Bytes("Current App Id: "),
            itoa(Global.current_application_id()),
            Bytes("Caller App Id: "),
            itoa(Global.caller_app_id()),
            Bytes("Budget: "),
            itoa(Global.opcode_budget()),
            Bytes("Group size: "),
            itoa(Global.group_size()),
        )
    )
