from pyteal import *


def methods_calls(methods: dict, call_idx: int):
    """
    dApp's methods calls dispatching utility function.

    Args:
        methods: methods calls dictionary {'method_name': method_call()}
        call_idx: method call group index

    Returns:
        dApp's methods calls dispatching TEAL logic
    """

    args = []
    for method_name, method_call in methods.items():
        args += [
            [Gtxn[call_idx].application_args[0] == Bytes(method_name),
             method_call]
        ]

    precondition = And(
        Gtxn[call_idx].type_enum() == TxnType.ApplicationCall,
        Gtxn[call_idx].application_args.length() >= Int(1),
    )

    return Seq([
        Assert(precondition),
        Cond(*args),
        Return(Int(1)),
    ])


if __name__ == "__main__":

    TEAL_VERSION = 3

    def compile_stateful(program):
        return compileTeal(program, Mode.Application, version=TEAL_VERSION)


    def method_a():
        return Return(Int(1))


    def method_b():
        return Return(Int(1))


    def method_c():
        return Return(Int(1))


    methods = {
        'methodA': method_a(),
        'methodB': method_b(),
        'methodC': method_c(),
    }

    call_idx = 0

    teal = compile_stateful(
        Cond(
            [Txn.on_completion() == OnComplete.NoOp,
             methods_calls(methods, call_idx)]
        )
    )
