from pyteal import *


def methods_calls(methods: dict):

    args = []
    for method_name, method_call in methods.items():
        args += [[Txn.application_args[0] == Bytes(method_name), method_call]]

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


    methods = {
        'methodA': method_a(),
        'methodB': method_b(),
        'methodC': method_c(),
    }

    teal = compile_stateful(methods_calls(methods))
