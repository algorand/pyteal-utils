from pyteal import Itob, Log, Seq

from tests.helpers import assert_output, logged_int

from .signed_int import SignedInt


def test_signed_sub():
    num = 100
    expr = Seq(
        Log(Itob(SignedInt(num) - SignedInt(num + 1))),
        Log(Itob(SignedInt(num) + SignedInt(num + 1))),
    )

    output = ["ff" * 8, logged_int(num + num + 1)]
    assert_output(expr, output)
