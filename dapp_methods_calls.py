from pyteal import *


def methods_calls(methods: list, methods_branches: list):

    assert len(methods) == len(methods_branches)

    args = []
    for i in range(len(methods)):
        args += [[Txn.application_args[0] == methods[i], methods_branches[i]]]

    precondition = And(
        Txn.type_enum() == TxnType.ApplicationCall,
        Txn.rekey_to() == Global.zero_address(),
        Txn.application_args.length() >= Int(1),
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


    methods = [
        Bytes("methodA"),
        Bytes("methodB"),
        Bytes("methodC"),
    ]

    methods_branches = [
        method_a(),
        method_b(),
        method_c(),
    ]

    teal = compile_stateful(methods_calls(methods, methods_branches))
