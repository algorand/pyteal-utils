"""Module containing helper functions for testing PyTeal Utils."""

from dataclasses import dataclass
from typing import Optional

from algosdk import account, encoding, kmd, mnemonic
from algosdk.future import transaction
from algosdk.v2client import algod, indexer
from pyteal import Expr, Int, Mode, Seq, compileTeal


def compile_app(method: Expr):
    return compileTeal(Seq(method, Int(0)), mode=Mode.Application, version=5)


def compile_sig(method: Expr):
    return compileTeal(Seq(method, Int(0)), mode=Mode.Signature, version=5)


def fully_compile(src: str):
    client = _algod_client()
    return client.compile(src)


# CLIENTS
###############################################################################
def _algod_client(algod_address="http://localhost:4001", algod_token="a" * 64):
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(algod_token, algod_address)


def _indexer_client(indexer_address="http://localhost:8980", indexer_token="a" * 64):
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(indexer_token, indexer_address)


def _kmd_client(kmd_address="http://localhost:4002", kmd_token="a" * 64):
    """Instantiate and return a KMD client object."""
    return kmd.KMDClient(kmd_token, kmd_address)


# HELPERS
#############################################################################


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


def compile_app(method: Expr):
    return compileTeal(Seq(method, Int(0)), mode=Mode.Application, version=5)
