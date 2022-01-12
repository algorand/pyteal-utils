import base64
from abc import ABC, abstractmethod
from functools import wraps
from inspect import signature
from typing import List

from algosdk import abi
from algosdk.abi.contract import NetworkInfo
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.future.transaction import (
    ApplicationCreateTxn,
    ApplicationDeleteTxn,
    ApplicationUpdateTxn,
)
from algosdk.future.transaction import OnComplete as oc
from algosdk.future.transaction import StateSchema, wait_for_confirmation
from algosdk.v2client import algod
from Cryptodome.Hash import SHA512
from pyteal import *
from pyteal.ast.abi_collections import *


# Utility function to take the string version of a
# method signature and return the 4 byte selector
def hashy(method: str) -> Bytes:
    chksum = SHA512.new(truncate="256")
    chksum.update(method.encode())
    return Bytes(chksum.digest()[:4])


@Subroutine(TealType.none)
def ABIReturn(b: TealType.bytes) -> Expr:
    return Log(Concat(Bytes("base16", "0x151f7c75"), b))


def ABIMethod(func):
    sig = signature(func)

    args = [v.annotation.__str__() for v in sig.parameters.values()]
    returns = sig.return_annotation

    method = "{}({}){}".format(func.__name__, ",".join(args), returns.__str__())

    setattr(func, "abi_selector", hashy(method))
    setattr(func, "abi_args", [abi.Argument(arg) for arg in args])
    setattr(func, "abi_returns", abi.Returns(returns.__str__()))

    # Get the types specified in the method
    abi_codec = [v.annotation for v in sig.parameters.values()]

    @wraps(func)
    @Subroutine(TealType.uint64)
    def wrapper() -> Expr:
        decoded = [
            abi_codec[idx](Txn.application_args[idx + 1])
            for idx in range(len(abi_codec))
        ]

        return Seq(ABIReturn(returns(func(*decoded)).encode()), Int(1))

    return wrapper


class Application(ABC):
    def global_schema(self) -> StateSchema:
        return StateSchema(0, 0)

    def local_schema(self) -> StateSchema:
        return StateSchema(0, 0)

    @abstractmethod
    def create(self) -> Expr:
        pass

    @abstractmethod
    def update(self) -> Expr:
        pass

    @abstractmethod
    def delete(self) -> Expr:
        pass

    @abstractmethod
    def optIn(self) -> Expr:
        pass

    @abstractmethod
    def closeOut(self) -> Expr:
        pass

    @abstractmethod
    def clearState(self) -> Expr:
        pass

    @classmethod
    def get_methods(cls) -> List[str]:
        return list(set(dir(cls)) - set(dir(cls.__base__)))

    def handler(self) -> Expr:
        methods = self.get_methods()

        routes = [
            [Txn.application_args[0] == f.abi_selector, f()]
            for f in map(lambda m: getattr(self, m), methods)
        ]

        # Hack to add budget padding
        routes.append([Txn.application_args[0] == hashy("pad()void"), Int(1)])

        handlers = [
            [Txn.application_id() == Int(0), self.create()],
            [Txn.on_completion() == OnComplete.UpdateApplication, self.update()],
            [Txn.on_completion() == OnComplete.DeleteApplication, self.delete()],
            *routes,
            [Txn.on_completion() == OnComplete.OptIn, self.optIn()],
            [Txn.on_completion() == OnComplete.CloseOut, self.closeOut()],
            [Txn.on_completion() == OnComplete.ClearState, self.clearState()],
        ]

        return Cond(*handlers)

    def get_interface(self) -> abi.Interface:
        abiMethods = [
            abi.Method(f.__name__, f.abi_args, f.abi_returns)
            for f in map(lambda m: getattr(self, m), self.get_methods())
        ]

        # TODO: hacked this in for now, to provide extended extended budget
        abiMethods.append(abi.Method("pad", [], abi.Returns("void")))

        return abi.Interface(self.__class__.__name__, abiMethods)

    def get_contract(self, app_id: int) -> abi.Contract:
        interface = self.get_interface()
        return abi.Contract(
            interface.name, interface.methods, "", {"default": NetworkInfo(app_id)}
        )

    def create_app(
        self, client: algod.AlgodClient, signer: AccountTransactionSigner
    ) -> abi.Contract:
        sp = client.suggested_params()

        approval_result = client.compile(self.approval_source())
        approval_program = base64.b64decode(approval_result["result"])

        clear_result = client.compile(self.clear_source())
        clear_program = base64.b64decode(clear_result["result"])

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationCreateTxn(
                    address_from_private_key(signer.private_key),
                    sp,
                    oc.NoOpOC,
                    approval_program,
                    clear_program,
                    self.global_schema(),
                    self.local_schema(),
                ),
                signer,
            )
        )
        result = wait_for_confirmation(client, ctx.submit(client)[0])
        return self.get_contract(result["application-index"])

    def update_app(
        self, client: algod.AlgodClient, app_id: int, signer: AccountTransactionSigner
    ):
        sp = client.suggested_params()

        approval_result = client.compile(self.approval_source())
        approval_program = base64.b64decode(approval_result["result"])

        clear_result = client.compile(self.clear_source())
        clear_program = base64.b64decode(clear_result["result"])

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationUpdateTxn(
                    address_from_private_key(signer.private_key),
                    sp,
                    app_id,
                    approval_program,
                    clear_program,
                ),
                signer,
            )
        )
        ctx.execute(client, 2)
        return self.get_contract(app_id)

    def delete_app(
        self, client: algod.AlgodClient, app_id: int, signer: AccountTransactionSigner
    ):
        sp = client.suggested_params()

        ctx = AtomicTransactionComposer()
        ctx.add_transaction(
            TransactionWithSigner(
                ApplicationDeleteTxn(
                    address_from_private_key(signer.private_key), sp, app_id
                ),
                signer,
            )
        )
        return ctx.execute(client, 2)

    def approval_source(self) -> str:
        return compileTeal(
            self.handler(), mode=Mode.Application, version=5, assembleConstants=True
        )

    def clear_source(self) -> str:
        return "#pragma version 5;int 1;return".replace(";", "\n")
