import json

from pyteal import (
    Bytes,
    Concat,
    Expr,
    Extract,
    If,
    Int,
    Len,
    Mode,
    Subroutine,
    TealType,
    compileTeal,
)
from pyteal.ast.abi_bytes import String
from pyteal.ast.abi_uint import Uint32

from pytealutils.application import ABIMethod, DefaultApprove


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

    # @staticmethod
    # @ABIMethod
    # def echo_array(a: ABIDynamicArray(String)) -> ABIDynamicArray(String):
    #    return a

    # @staticmethod
    # @ABIMethod
    # def split(a: String) -> ABIDynamicArray:
    #   l = ABIDynamicArray(Bytes(""))

    #   @Subroutine(TealType.none)
    #   def rsplit(
    #       data: TealType.bytes, idx: TealType.uint64, lastIdx: TealType.uint64
    #   ) -> Expr:
    #       return If(
    #           Len(data) == idx,  # we're finished, append the last one
    #           l.append(Substring(data, lastIdx, idx)),
    #           If(
    #               GetByte(data, idx) == Int(32),
    #               Seq(
    #                   l.append(Substring(data, lastIdx, idx)),
    #                   rsplit(data, idx + Int(1), idx),
    #               ),
    #               rsplit(data, idx + Int(1), lastIdx),
    #           ),
    #       )
    #   return Seq(l.init(), rsplit(a, Int(0), Int(0)), l.serialize())

    # @staticmethod
    # @ABIMethod
    # def concat(a: ABIDynamicArray[String]) -> String:
    #    idx = ScratchVar()
    #    buff = ScratchVar()
    #    return Seq(
    #        buff.store(Bytes("")),
    #        For(
    #            idx.store(Int(0)),
    #            idx.load() < a.size.load(),
    #            idx.store(idx.load() + Int(1)),
    #        ).Do(buff.store(Concat(buff.load(), Bytes(" "), a[idx.load()]))),
    #        buff.load(),
    #    )

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
