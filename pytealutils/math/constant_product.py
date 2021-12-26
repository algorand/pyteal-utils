from pyteal import Expr, Subroutine, TealType, WideRatio

from .math import min


class ConstantProduct:
    @staticmethod
    @Subroutine(TealType.uint64)
    def mint(
        issued: TealType.uint64,
        a_supply: TealType.uint64,
        b_supply: TealType.uint64,
        a_amount: TealType.uint64,
        b_amount: TealType.uint64,
        scale: TealType.uint64,
    ) -> Expr:
        return WideRatio(
            [
                min(
                    WideRatio([a_amount, scale], [a_supply]),
                    WideRatio([b_amount, scale], [b_supply]),
                ),
                issued,
            ],
            [scale],
        )

    @staticmethod
    @Subroutine(TealType.uint64)
    def burn(issued: TealType.uint64, supply: TealType.uint64, amount: TealType.uint64):
        return WideRatio([supply, amount], [issued])

    @staticmethod
    @Subroutine(TealType.uint64)
    def swap(
        in_amount: TealType.uint64,
        in_supply: TealType.uint64,
        out_supply: TealType.uint64,
        scale: TealType.uint64,
        fee: TealType.uint64,
    ) -> Expr:
        factor = scale - fee
        return WideRatio(
            [in_amount, factor, out_supply],
            [(in_supply * scale) + (in_amount * factor)],
        )
