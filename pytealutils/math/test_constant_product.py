from dataclasses import dataclass
from typing import List

from pyteal import Int, Itob, Log

from tests.conftest import assert_output, logged_int

from .constant_product import ConstantProduct

cp = ConstantProduct()


@dataclass
class ConstantProductState:
    a_supply: int
    b_supply: int

    issued: int
    supply: int

    scale: int
    fee: int

    def mint(self, a, b) -> int:
        if a / self.a_supply < b / self.b_supply:
            return (a / self.a_supply) * self.issued
        return int((b / self.b_supply) * self.issued)

    def burn_a(self, amount) -> int:
        return int((self.a_supply * amount) / self.issued)

    def burn_b(self, amount) -> int:
        return int((self.b_supply * amount) / self.issued)

    def swap_a(self, amount) -> int:
        factor = self.scale - self.fee
        return int(
            (amount * factor * self.b_supply)
            / ((self.a_supply * self.scale) + (amount * factor))
        )

    def swap_b(self, amount):
        factor = self.scale - self.fee
        return int(
            (amount * factor * self.a_supply)
            / ((self.b_supply * self.scale) + (amount * factor))
        )

    def ratio(self):
        return min(self.a_supply, self.b_supply) / max(self.a_supply, self.b_supply)


def create_state() -> ConstantProductState:
    # TODO: randomize with constraints
    return ConstantProductState(500, 100, 1000, int(1e9), 1000, 3)


def gen_states() -> List[ConstantProductState]:
    # TODO: more
    return [create_state() for _ in range(1)]


def test_constant_product_mint():
    states = gen_states()
    for state in states:
        # TODO: randomize with constraints
        a_amount = int(100)
        b_amount = int(a_amount * state.ratio())

        print("a amt {} b amt {}".format(a_amount, b_amount))

        expr = Log(
            Itob(
                cp.mint(
                    Int(state.issued),
                    Int(state.a_supply),
                    Int(state.b_supply),
                    Int(a_amount),
                    Int(b_amount),
                    Int(state.scale),
                )
            )
        )

        expected = [logged_int(int(state.mint(a_amount, b_amount)))]

        assert_output(expr, expected)


def test_constant_product_burn():
    states = gen_states()
    for state in states:
        # TODO: randomize with constraints
        amount = 10
        expr = Log(Itob(cp.burn(Int(state.issued), Int(state.a_supply), Int(amount))))

        expected = [logged_int(int(state.burn_a(amount)))]

        assert_output(expr, expected)

        expr = Log(Itob(cp.burn(Int(state.issued), Int(state.b_supply), Int(amount))))

        expected = [logged_int(int(state.burn_b(amount)))]

        assert_output(expr, expected)


def test_constant_product_swap():
    states = gen_states()
    for state in states:
        # TODO: randomize with constraints
        amount = 10
        expr = Log(
            Itob(
                cp.swap(
                    Int(amount),
                    Int(state.a_supply),
                    Int(state.b_supply),
                    Int(state.scale),
                    Int(state.fee),
                )
            )
        )
        expected = [logged_int(int(state.swap_a(amount)))]
        assert_output(expr, expected)

        amount = 10
        expr = Log(
            Itob(
                cp.swap(
                    Int(amount),
                    Int(state.b_supply),
                    Int(state.a_supply),
                    Int(state.scale),
                    Int(state.fee),
                )
            )
        )
        expected = [logged_int(int(state.swap_b(amount)))]
        assert_output(expr, expected)
