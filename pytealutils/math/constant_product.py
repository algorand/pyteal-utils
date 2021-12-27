from pyteal import Expr, Subroutine, TealType, WideRatio

from .math import min


class ConstantProduct:
    """ConstantProduct implements the basic functions for a Constant Product AMM"""

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
        """mint returns the number of tokens that should be minted given the current state and input amounts

        Args
            issued: The number of tokens issued, usually (total supply - current balance)
            a_supply: The number of tokens of asset A held by the pool
            b_supply: The number of tokens of asset B held by the pool
            a_amount: The nubmer of tokens of asset A passed by the caller
            b_amount: The nubmer of tokens of asset B passed by the caller
            scale: How accurate to be, (fine default is 1000)

        Returns the number of tokens to send to caller
        """
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
        """burn returns the number of tokens for one of the assets to send given the number of burned tokens

        Args
            issued: The number of pool tokens issued, usually (total supply - current balance)
            supply: The number of tokens held of this asset
            amount: The number of pool tokens sent to be burned

        Returns the number of tokens of the asset to be sent back in exchange for the pool tokens
        """
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
        """swap returns the number of tokens of asset 2 to get in exchange for some number of asset 1

        Args
            in_amount: The number of tokens of asset 1 sent in
            in_supply: The number of tokens of asset 1 held by the pool
            out_supply: The number of tokens of asset 2 held by the pool
            scale: How accurate to be (default to 1000)
            fee: Base fee to apply for the swap (default to 3)

        Returns the number of tokens of asset 2 to send back
        """
        factor = scale - fee
        return WideRatio(
            [in_amount, factor, out_supply],
            [(in_supply * scale) + (in_amount * factor)],
        )
