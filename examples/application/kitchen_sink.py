import json
from typing import Tuple

from pyteal import (
    ABIDynamicArray,
    Bytes,
    Concat,
    Expr,
    Extract,
    If,
    Int,
    Len,
    Mode,
    String,
    Subroutine,
    TealType,
    Uint32,
    compileTeal,
)

from pytealutils.application import ABIMethod, DefaultApprove


class StringArray(ABIDynamicArray[Tuple[String, String, String]]):
    pass


class KitchenSink(DefaultApprove):
    @staticmethod
    @ABIMethod
    def reverse(a: String) -> String:
        @Subroutine(TealType.bytes)
        def reverse(a: TealType.bytes) -> Expr:
            return (
                If(Len(a) == Int(0))
                .Then(Bytes(""))
                .Else(
                    Concat(
                        Extract(a, Len(a) - Int(1), Int(1)),
                        reverse(Extract(a, Int(0), Len(a) - Int(1))),
                    )
                )
            )

        return reverse(a)

    @staticmethod
    @ABIMethod
    def echo_first(a: StringArray) -> String:
        return a[0]

    @staticmethod
    @ABIMethod
    def add(a: Uint32, b: Uint32) -> Uint32:
        return a + b

    @staticmethod
    @ABIMethod
    def sub(a: Uint32, b: Uint32) -> Uint32:
        return a - b

    @staticmethod
    @ABIMethod
    def div(a: Uint32, b: Uint32) -> Uint32:
        return a / b

    @staticmethod
    @ABIMethod
    def mul(a: Uint32, b: Uint32) -> Uint32:
        return a * b


if __name__ == "__main__":
    app = KitchenSink()

    with open("interface.json", "w") as f:
        f.write(json.dumps(app.get_interface().dictify()))

    with open("approval.teal", "w") as f:
        f.write(
            compileTeal(
                app.handler(), mode=Mode.Application, version=5, assembleConstants=True
            )
        )
