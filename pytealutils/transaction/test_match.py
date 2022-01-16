from pyteal import Approve, Cond, Gtxn, Arg, Return, Bytes
from pytest import *

from tests.helpers import *

from .match import *


def test_match():

    payTxn, giveTxn = Gtxn[0], Gtxn[1]
    # Swap of algos for asset
    payMatcher = {
        **Common,
        **HasMinFee,
        **PaymentAmount(amount=100),
        TxnField.sender: giveTxn.receiver(),
    }
    giveMatcher = {
        **Common,
        **HasMinFee,
        **AssetIdAndAmount(id=10, amount=payTxn.amount()),
        TxnField.sender: payTxn.receiver(),
    }


    # User has a coupon code
    couponAmount = Int(10)
    couponCode = {
        **Common,
        **HasMinFee,
        **AssetIdAndAmount(id=10, amount=couponAmount)
    }


    def check_coupon_arg():
        # prolly use some hash or ed25519 verify thing
        return  Arg(Int(0)) == Bytes("coupon_code")

    # In cond, check if the txns match and route to the right method, in this case just approve
    expr = Cond(
        [Match(payMatcher, giveMatcher), Approve()],
        [Match(couponCode), Return(check_coupon_arg())]
    )

    # No actual testing being done here yet
    print(compile_sig(expr))
