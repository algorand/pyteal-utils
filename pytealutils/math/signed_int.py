from pyteal import BinaryExpr, BitwiseXor, Expr, Int, Op, TealType, UnaryExpr

# Credit CiottiGiorgio


class SignedInt(Int):
    def __init__(self, value: int):
        assert (
            -2 ** 63 <= value <= 2 ** 63 - 1
        ), "Value must be between -2^63 and 2^63-1"

        if value < 0:
            value = abs(value)
            value = ((value ^ 0xFFFFFFFFFFFFFFFF) + 1) % 2 ** 64

        super().__init__(value)

    def __sub__(self, other) -> Expr:
        return SignedInt.__add_modulo__(self, SignedInt.two_complement(other))

    @staticmethod
    def __add_modulo__(left, right) -> Expr:
        # We use addition wide because there are instances where the result is greater than 2^64.
        # Of course when adding any two 64bit uint(s) the result can at most be one bit longer.
        # The overflow is not on top of the stack so we have to swap and pop.
        addition_with_overflow = BinaryExpr(
            Op.addw, TealType.uint64, TealType.uint64, left, right
        )
        addition_swapped = UnaryExpr(
            Op.swap, TealType.anytype, TealType.anytype, addition_with_overflow
        )
        addition_without_overflow = UnaryExpr(
            Op.pop, TealType.uint64, TealType.uint64, addition_swapped
        )

        return addition_without_overflow

    @staticmethod
    def two_complement(n) -> Expr:
        n_xor = BitwiseXor(n, Int(0xFFFFFFFFFFFFFFFF))
        return SignedInt.__add_modulo__(n_xor, Int(1))
