from typing import Dict, Tuple, Union

from pyteal import (
    And,
    CompileOptions,
    Expr,
    Global,
    GtxnExpr,
    Int,
    TealBlock,
    TealSimpleBlock,
    TealType,
    TxnField,
    TxnType,
)

# Common field checks

NoRekey = {TxnField.rekey_to: Global.zero_address()}
NoCloseTo = {TxnField.close_remainder_to: Global.zero_address()}
NoCloseAsset = {TxnField.asset_close_to: Global.zero_address()}
Common = {**NoRekey, **NoCloseTo, **NoCloseAsset}

Payment = {TxnField.type_enum: TxnType.Payment}
AssetTransfer = {TxnField.type_enum: TxnType.AssetTransfer}
AssetConfig = {TxnField.type_enum: TxnType.AssetConfig}

ToMe = {TxnField.receiver: Global.current_application_address()}
FromMe = {TxnField.sender: Global.current_application_address()}


def PaymentAmount(amount: Union[int, Int]) -> Dict[TxnField, Expr]:
    if type(amount) == int:
        amount = Int(amount)
    return {**Payment, TxnField.amount: amount}


def AssetIdAndAmount(
    id: Union[int, Int], amount: Union[int, Int]
) -> Dict[TxnField, Expr]:
    if type(id) == int:
        id = Int(id)

    if type(amount) == int:
        amount = Int(amount)

    return {**AssetTransfer, TxnField.xfer_asset: id, TxnField.asset_amount: amount}


class Match(Expr):
    """Match checks a transaction group against a set of transaction field to expression mapping.

    """

    def __init__(self, *txns: Dict[TxnField, Expr]):
        filters = []
        for idx, txn in enumerate(txns):
            filters.append(And(*[GtxnExpr(idx, k) == v for k, v in txn.items()]))

        self.value = And(*filters)

    def type_of(self) -> TealType:
        return self.value.type_of()

    def has_return(self) -> bool:
        return self.value.has_return()

    def __teal__(self, options: "CompileOptions") -> Tuple[TealBlock, TealSimpleBlock]:
        return self.value.__teal__(options)

    def __str__(self):
        return "Matcher TODO..."
