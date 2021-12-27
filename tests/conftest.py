"""Module containing helper functions for testing PyTeal Utils."""

from base64 import b64decode
from dataclasses import dataclass
from typing import List, Optional

from algosdk import account, encoding, kmd, mnemonic
from algosdk.future import transaction
from algosdk.v2client import algod, indexer
from pyteal import Cond, Expr, Int, Mode, Seq, Txn, compileTeal

## Clients


def _algod_client(algod_address="http://localhost:4001", algod_token="a" * 64):
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(algod_token, algod_address)


def _indexer_client(indexer_address="http://localhost:8980", indexer_token="a" * 64):
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(indexer_token, indexer_address)


def _kmd_client(kmd_address="http://localhost:4002", kmd_token="a" * 64):
    """Instantiate and return a KMD client object."""
    return kmd.KMDClient(kmd_token, kmd_address)


# Env helpers


@dataclass
class Account:
    address: str
    private_key: Optional[str]  # Must be explicitly set to None when setting `lsig`.
    lsig: Optional[transaction.LogicSig] = None

    def __post_init__(self):
        assert self.private_key or self.lsig

    def mnemonic(self) -> str:
        return mnemonic.from_private_key(self.private_key)

    def is_lsig(self) -> bool:
        return bool(not self.private_key and self.lsig)

    @classmethod
    def create(cls) -> "Account":
        private_key, address = account.generate_account()
        return cls(private_key=private_key, address=str(address))

    @property
    def decoded_address(self):
        return encoding.decode_address(self.address)


def get_kmd_accounts(
    kmd_wallet_name="unencrypted-default-wallet", kmd_wallet_password=""
):
    kmd_client = _kmd_client()
    wallets = kmd_client.list_wallets()

    walletID = None
    for wallet in wallets:
        if wallet["name"] == kmd_wallet_name:
            walletID = wallet["id"]
            break

    if walletID is None:
        raise Exception("Wallet not found: {}".format(kmd_wallet_name))

    walletHandle = kmd_client.init_wallet_handle(walletID, kmd_wallet_password)

    try:
        addresses = kmd_client.list_keys(walletHandle)

        privateKeys = [
            kmd_client.export_key(walletHandle, kmd_wallet_password, addr)
            for addr in addresses
        ]

        kmdAccounts = [
            Account(address=addresses[i], private_key=privateKeys[i])
            for i in range(len(privateKeys))
        ]
    finally:
        kmd_client.release_wallet_handle(walletHandle)

    return kmdAccounts


## Teal Helpers


def logged_bytes(b: str):
    return bytes(b, "ascii").hex()


def logged_int(i: int):
    return i.to_bytes(8, "big").hex()


def assert_stateful_output(expr: Expr, output: List[str]):
    assert expr is not None

    src = compile_stateful_app(expr)
    assert len(src) > 0

    compiled = fully_compile(src)
    assert len(compiled["hash"]) == 58

    app_id = create_app(
        compiled["result"],
        transaction.StateSchema(0, 16),
        transaction.StateSchema(0, 64),
    )

    result = call_app(app_id)

    assert result == output


def assert_output(expr: Expr, output: List[str]):
    assert expr is not None

    src = compile_app(expr)
    assert len(src) > 0

    compiled = fully_compile(src)
    assert len(compiled["hash"]) == 58

    result = execute_app(compiled["result"])
    assert result == output


def compile_app(method: Expr):
    return compileTeal(Seq(method, Int(1)), mode=Mode.Application, version=5)


def compile_stateful_app(method: Expr):
    expr = Cond([Txn.application_id() == Int(0), Int(1)], [Int(1), Seq(method, Int(1))])
    return compileTeal(expr, mode=Mode.Application, version=5)


def compile_sig(method: Expr):
    return compileTeal(Seq(method, Int(1)), mode=Mode.Signature, version=5)


def fully_compile(src: str):
    client = _algod_client()
    return client.compile(src)


def execute_app(bc: str, **kwargs):
    client = _algod_client()
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()
    schema = transaction.StateSchema(0, 0)
    clearprog = b64decode("BYEB")  # pragma 5; int 1

    txn = transaction.ApplicationCallTxn(
        acct.address,
        sp,
        0,
        transaction.OnComplete.DeleteApplicationOC,
        schema,
        schema,
        b64decode(bc),
        clearprog,
        **kwargs
    )

    txid = client.send_transaction(txn.sign(acct.private_key))
    result = transaction.wait_for_confirmation(client, txid, 3)
    return [b64decode(l).hex() for l in result["logs"]]


def create_app(
    bc: str,
    local_schema: transaction.StateSchema,
    global_schema: transaction.StateSchema,
    **kwargs
):
    client = _algod_client()
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()
    clearprog = b64decode("BYEB")  # pragma 5; int 1

    txn = transaction.ApplicationCallTxn(
        acct.address,
        sp,
        0,
        transaction.OnComplete.NoOpOC,
        local_schema,
        global_schema,
        b64decode(bc),
        clearprog,
        **kwargs
    )

    txid = client.send_transaction(txn.sign(acct.private_key))
    result = transaction.wait_for_confirmation(client, txid, 3)

    return result["application-index"]


def call_app(app_id: int, **kwargs):
    client = _algod_client()
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()

    txns = transaction.assign_group_id(
        [
            transaction.ApplicationOptInTxn(acct.address, sp, app_id),
            transaction.ApplicationCallTxn(
                acct.address, sp, app_id, transaction.OnComplete.DeleteApplicationOC, **kwargs
            ),
        ]
    )

    client.send_transactions([txn.sign(acct.private_key) for txn in txns])

    result = transaction.wait_for_confirmation(client, txns[-1].get_txid(), 3)
    return [b64decode(l).hex() for l in result["logs"]]
