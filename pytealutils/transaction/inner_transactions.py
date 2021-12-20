from pyteal import *


@Subroutine(TealType.none)
def axfer(receiver: TealType.uint64, asset_id: TealType.uint64, amt: TealType.uint64):
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: receiver,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_amount: amt,
            }
        ),
        InnerTxnBuilder.Submit(),
    )


@Subroutine(TealType.none)
def pay(receiver: TealType.uint64, amt: TealType.uinit64):
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: receiver,
                TxnField.amount: amt,
            }
        ),
        InnerTxnBuilder.Submit(),
    )