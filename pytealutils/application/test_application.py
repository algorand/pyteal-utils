from algosdk.atomic_transaction_composer import AccountTransactionSigner
from pyteal import *
from pyteal import String

from tests.helpers import _algod_client, get_kmd_accounts

from .application import *
from .client import ContractClient
from .defaults import *


def test_application():
    client = _algod_client()

    acct = get_kmd_accounts().pop()
    signer = AccountTransactionSigner(acct.private_key)

    class testapp(DefaultApprove):
        @staticmethod
        @ABIMethod
        def echo(a: String) -> String:
            return a

    app = testapp()

    # Create client to make calls with
    cc = ContractClient(client, app, "default", signer)
    cc.create_app()
    print("Created {}".format(cc.app_id))

    try:
        # print(cc.echo.name)
        print_results(cc.echo(["echo me"]))

    except Exception as e:
        print("Fail: {}".format(e))
    finally:
        cc.delete_app()
        print("Deleted {}".format(cc.app_id))


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format(result.return_value))
