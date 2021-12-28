"""Module containing helper functions for testing PyTeal Utils."""

from base64 import b64decode
from typing import List, Optional

from algosdk import account, encoding, kmd, mnemonic
from algosdk.future import transaction
from algosdk.v2client import algod, indexer
from pyteal import Cond, Expr, Int, Mode, Seq, Txn, compileTeal

TEAL_VERSION = 5
CLEAR_PROG = b64decode("BYEB")  # pragma 5; int 1

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


class Account:
    def __init__(
        self,
        address: str,
        private_key: Optional[str],
        lsig: Optional[transaction.LogicSig] = None,
    ):
        self.address = address
        self.private_key = private_key
        self.lsig = lsig

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


def sign(signer: Account, txn: transaction.Transaction):
    """Sign a transaction with an Account."""
    if signer.is_lsig():
        return transaction.LogicSigTransaction(txn, signer.lsig)
    else:
        assert signer.private_key
        return txn.sign(signer.private_key)


def sign_send_wait(
    algod_client: algod.AlgodClient,
    signer: Account,
    txn: transaction.Transaction,
    debug=False,
):
    """Sign a transaction, submit it, and wait for its confirmation."""
    signed_txn = sign(signer, txn)
    tx_id = signed_txn.transaction.get_txid()

    if debug:
        transaction.write_to_file([signed_txn], "/tmp/txn.signed", overwrite=True)

    algod_client.send_transactions([signed_txn])
    transaction.wait_for_confirmation(algod_client, tx_id)
    return algod_client.pending_transaction_info(tx_id)


## Teal Helpers

# Create global client to be used in tests
client = _algod_client()


def logged_bytes(b: str):
    return bytes(b, "ascii").hex()


def logged_int(i: int):
    return i.to_bytes(8, "big").hex()


def assert_stateful_output(expr: Expr, output: List[str]):
    assert expr is not None

    src = compile_stateful_app(expr)
    assert len(src) > 0

    compiled = assemble_bytecode(client, src)
    assert len(compiled["hash"]) == 58

    app_id = create_app(
        client,
        compiled["result"],
        transaction.StateSchema(0, 16),
        transaction.StateSchema(0, 64),
    )

    logs, _ = call_app(client, app_id)
    assert logs == output


def assert_stateful_fail(expr: Expr, output: List[str]):
    assert expr is not None

    emsg = None

    try:
        src = compile_stateful_app(expr)
        assert len(src) > 0

        compiled = assemble_bytecode(client, src)
        assert len(compiled["hash"]) == 58

        app_id = create_app(
            client,
            compiled["result"],
            transaction.StateSchema(0, 16),
            transaction.StateSchema(0, 64),
        )

        call_app(client, app_id)
    except Exception as e:
        emsg = str(e)

    assert emsg is not None
    assert output.pop() in emsg

    destroy_app(client, app_id)


def assert_output(expr: Expr, output: List[str], **kwargs):
    assert expr is not None

    src = compile_app(expr)
    assert len(src) > 0

    compiled = assemble_bytecode(client, src)
    assert len(compiled["hash"]) == 58

    logs, _ = execute_app(client, compiled["result"], **kwargs)
    assert logs == output


def assert_fail(expr: Expr, output: List[str], **kwargs):
    assert expr is not None

    emsg = None

    try:
        src = compile_app(expr)
        assert len(src) > 0

        compiled = assemble_bytecode(client, src)
        assert len(compiled["hash"]) == 58

        execute_app(client, compiled["result"])
    except Exception as e:
        emsg = str(e)

    assert emsg is not None

    assert output.pop() in emsg


def compile_app(method: Expr, version: int = TEAL_VERSION):
    return compileTeal(Seq(method, Int(1)), mode=Mode.Application, version=version)


def compile_stateful_app(method: Expr, version: int = TEAL_VERSION):
    expr = Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.application_args.length() > Int(0), Int(1)],
        [Int(1), Seq(method, Int(1))],
    )
    return compileTeal(expr, mode=Mode.Application, version=version)


def compile_sig(method: Expr, version: int = TEAL_VERSION):
    return compileTeal(Seq(method, Int(1)), mode=Mode.Signature, version=version)


def assemble_bytecode(client: algod.AlgodClient, src: str):
    return client.compile(src)


def execute_app(client: algod.AlgodClient, bytecode: str, **kwargs):
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()

    if "local_schema" not in kwargs:
        kwargs["local_schema"] = transaction.StateSchema(0, 0)

    if "global_schema" not in kwargs:
        kwargs["global_schema"] = transaction.StateSchema(0, 0)

    txns = [
        transaction.ApplicationCallTxn(
            acct.address,
            sp,
            0,
            transaction.OnComplete.DeleteApplicationOC,
            kwargs["local_schema"],
            kwargs["global_schema"],
            b64decode(bytecode),
            CLEAR_PROG,
        )
    ]
    if "pad_budget" in kwargs:
        for i in range(kwargs["pad_budget"]):
            txns.append(
                transaction.ApplicationCallTxn(
                    acct.address,
                    sp,
                    0,
                    transaction.OnComplete.DeleteApplicationOC,
                    transaction.StateSchema(0, 0),
                    transaction.StateSchema(0, 0),
                    CLEAR_PROG,
                    CLEAR_PROG,
                    note=str(i).encode(),
                )
            )

    txns = transaction.assign_group_id(txns)
    txid = client.send_transactions([txn.sign(acct.private_key) for txn in txns])
    result = transaction.wait_for_confirmation(client, txid, 3)
    return [b64decode(l).hex() for l in result["logs"]], result


def create_app(
    client: algod.AlgodClient,
    bytecode: str,
    local_schema: transaction.StateSchema,
    global_schema: transaction.StateSchema,
    **kwargs
):
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()

    txn = transaction.ApplicationCallTxn(
        acct.address,
        sp,
        0,
        transaction.OnComplete.NoOpOC,
        local_schema,
        global_schema,
        b64decode(bytecode),
        CLEAR_PROG,
        **kwargs
    )

    txid = client.send_transaction(txn.sign(acct.private_key))
    result = transaction.wait_for_confirmation(client, txid, 3)

    return result["application-index"]


def call_app(client: algod.AlgodClient, app_id: int, **kwargs):
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()

    txns = transaction.assign_group_id(
        [
            transaction.ApplicationOptInTxn(acct.address, sp, app_id),
            transaction.ApplicationCallTxn(
                acct.address,
                sp,
                app_id,
                transaction.OnComplete.DeleteApplicationOC,
                **kwargs
            ),
            transaction.ApplicationClearStateTxn(acct.address, sp, app_id),
        ]
    )

    client.send_transactions([txn.sign(acct.private_key) for txn in txns])

    result = transaction.wait_for_confirmation(client, txns[1].get_txid(), 3)
    return [b64decode(l).hex() for l in result["logs"]], result


def destroy_app(client: algod.AlgodClient, app_id: int, **kwargs):
    sp = client.suggested_params()

    acct = get_kmd_accounts().pop()

    txns = transaction.assign_group_id(
        [
            transaction.ApplicationCallTxn(
                acct.address,
                sp,
                app_id,
                transaction.OnComplete.DeleteApplicationOC,
                app_args=["cleanup"],
                **kwargs
            )
        ]
    )

    txid = client.send_transactions([txn.sign(acct.private_key) for txn in txns])

    transaction.wait_for_confirmation(client, txid, 3)
