from os import urandom
from typing import List

from algosdk.abi import Contract, Method
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionSigner,
)
from algosdk.v2client.algod import AlgodClient

# TODO: Cache suggested params


class ContractClient:
    def __init__(
        self, client: AlgodClient, contract: Contract, signer: TransactionSigner = None
    ):
        self.client = client
        self.networks = contract.networks
        self.contract = contract
        self.signer = signer

        self.addr = address_from_private_key(self.signer.private_key)

        for m in contract.methods:
            caller = self._get_caller(m)
            setattr(self, m.name, caller)

    def _get_caller(self, m):
        def call(args, budget=1):
            return self.call(m, args, budget)
        return call

    def compose(self, method: Method, args: List[any], ctx: AtomicTransactionComposer):
        sp = self.client.suggested_params()
        ctx.add_method_call(
            self.networks["default"].app_id,
            method,
            self.addr,
            sp,
            self.signer,
            method_args=args,
        )

    def call(self, method: Method, args: List[any], budget=1):
        ctx = AtomicTransactionComposer()

        print(method.args, args)

        sp = self.client.suggested_params()
        ctx.add_method_call(
            self.networks["default"].app_id,
            method,
            self.addr,
            sp,
            self.signer,
            method_args=args,
        )

        for _ in range(budget - 1):
            ctx.add_method_call(
                self.networks["default"].app_id,
                self.pad,
                self.addr,
                sp,
                self.signer,
                note=urandom(5),
            )

        return ctx.execute(self.client, 2)
