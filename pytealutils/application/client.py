import base64
from os import urandom
from typing import List

from algosdk.abi import Contract, Method, NetworkInfo
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionSigner,
    TransactionWithSigner,
)
from algosdk.future.transaction import (
    ApplicationCreateTxn,
    ApplicationDeleteTxn,
    ApplicationUpdateTxn,
    OnComplete,
    wait_for_confirmation,
)
from algosdk.v2client.algod import AlgodClient

from pytealutils.application import Application


class ContractClient:
    def __init__(
        self,
        client: AlgodClient,
        app: Application,
        network: str,
        signer: TransactionSigner,
        app_id: int = 0,
    ):
        self.app = app
        self.client = client
        self.network = network
        self.signer = signer

        self.app_id = app_id
        self.contract = self.get_contract()

        self.addr = address_from_private_key(self.signer.private_key)

        methods = {}
        for m in self.contract.methods:
            caller = self._get_caller(m)
            setattr(self, m.name, caller)
            methods[m.name] = m

        setattr(self, "methods", methods)

    def _get_caller(self, m):
        def call(args, budget=1):
            return self.call(m, args, budget)

        return call

    def compose(self, method: Method, args: List[any], ctx: AtomicTransactionComposer):
        # TODO: Cache suggested params?
        sp = self.client.suggested_params()

        ctx.add_method_call(
            self.app_id, method, self.addr, sp, self.signer, method_args=args
        )

    def call(self, method: Method, args: List[any], budget=1):
        ctx = AtomicTransactionComposer()

        sp = self.client.suggested_params()

        ctx.add_method_call(
            self.app_id, method, self.addr, sp, self.signer, method_args=args
        )

        for _ in range(budget - 1):
            ctx.add_method_call(
                self.app_id,
                self.contract.methods[-1],  # pad
                self.addr,
                sp,
                self.signer,
                note=urandom(5),
            )

        return ctx.execute(self.client, 2)

    def get_contract(self) -> Contract:
        interface = self.app.get_interface()
        return Contract(
            interface.name,
            interface.methods,
            "",
            {self.network: NetworkInfo(self.app_id)},
        )

    def create_app(self):
        sp = self.client.suggested_params()

        approval_result = self.client.compile(self.app.approval_source())
        approval_program = base64.b64decode(approval_result["result"])

        clear_result = self.client.compile(self.app.clear_source())
        clear_program = base64.b64decode(clear_result["result"])

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationCreateTxn(
                    address_from_private_key(self.signer.private_key),
                    sp,
                    OnComplete.NoOpOC,
                    approval_program,
                    clear_program,
                    self.app.global_schema(),
                    self.app.local_schema(),
                ),
                self.signer,
            )
        )
        result = wait_for_confirmation(self.client, ctx.submit(self.client)[0])
        self.app_id = result["application-index"]
        self.contract = self.get_contract()

    def update_app(self):
        sp = self.client.suggested_params()

        approval_result = self.client.compile(self.app.approval_source())
        approval_program = base64.b64decode(approval_result["result"])

        clear_result = self.client.compile(self.app.clear_source())
        clear_program = base64.b64decode(clear_result["result"])

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationUpdateTxn(
                    address_from_private_key(self.signer.private_key),
                    sp,
                    self.app_id,
                    approval_program,
                    clear_program,
                ),
                self.signer,
            )
        )
        ctx.execute(self.client, 2)
        return self.get_contract(self.app_id)

    def delete_app(self):
        sp = self.client.suggested_params()

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationDeleteTxn(
                    address_from_private_key(self.signer.private_key), sp, self.app_id
                ),
                self.signer,
            )
        )
        return ctx.execute(self.client, 2)
