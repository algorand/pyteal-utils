from pyteal import Bytes, Concat, Global, InnerTxn, Log, If, Int

from ..strings import itoa


def log_stats():
    return Log(
        Concat(
            Bytes("\nCurrent App Id: "),
            itoa(Global.current_application_id()),
            Bytes("\nBudget: "),
            itoa(Global.opcode_budget()),
            Bytes("\nGroup size: "),
            itoa(Global.group_size()),
            If(Global.caller_app_id()>Int(0), Concat(Bytes("\nCaller App Id: "), itoa(Global.caller_app_id())), Bytes("")),
        )
    )
