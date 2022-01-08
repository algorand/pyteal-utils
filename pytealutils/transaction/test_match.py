from pyteal import Approve, Cond
from pytest import *

from tests.helpers import *

from .match import *


def test_match():
    # Swap of algos for asset
    payMe = {**Common, **ToMe, **PaymentAmount(100)}
    giveThing = {**Common, **FromMe, **AssetIdAndAmount(10, 100)}

    # In cond, check if the txns match and route to the right method, in this case just approve
    expr = Cond([Match(payMe, giveThing), Approve()])

    # No actual testing being done here yet
    print(compile_app(expr))
