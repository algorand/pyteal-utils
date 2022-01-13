from typing import Tuple

from algosdk.atomic_transaction_composer import AccountTransactionSigner
from pyteal import *

from tests.helpers import _algod_client, get_kmd_accounts

from .application import *
from .client import ContractClient
from .defaults import *


def test_application():
    class MyTuple(ABITuple[Tuple[String, Uint32]]):
        pass

    class MyFixedArray(ABIFixedArray[Tuple[String, String, String]]):
        pass

    class MyDynamicArray(ABIDynamicArray[Tuple[String]]):
        pass

    client = _algod_client()

    acct = get_kmd_accounts().pop()
    signer = AccountTransactionSigner(acct.private_key)

    class testapp(DefaultApprove):
        @staticmethod
        @ABIMethod
        def echo(a: String) -> String:
            return a

        @staticmethod
        @ABIMethod
        def echo_tuple(a: MyTuple) -> MyTuple:
            return a

        @staticmethod
        @ABIMethod
        def echo_fixed(a: MyFixedArray) -> String:
            return a[0]

        @staticmethod
        @ABIMethod
        def echo_dynamic(a: MyDynamicArray) -> String:
            return a[0]

    app = testapp()

    # Create client to make calls with
    cc = ContractClient(client, app, "default", signer)
    cc.create_app()

    try:
        # call abi method with args
        assert cc.echo(["echo me"]).abi_results[0].return_value == "echo me"
        assert cc.echo_tuple([("echo", 123)]).abi_results[0].return_value == [
            "echo",
            123,
        ]
        assert (
            cc.echo_fixed([("echo", "me", "plz")]).abi_results[0].return_value == "echo"
        )
        assert (
            cc.echo_dynamic([("echo", "me", "plz")]).abi_results[0].return_value
            == "echo"
        )
    except Exception as e:
        # whoops
        print("Fail: {}".format(e))
    finally:
        # Clean up
        cc.delete_app()


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format())
