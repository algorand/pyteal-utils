from pyteal import *
from pyteal.ast.abi_bytes import String

from tests.helpers import _algod_client, get_kmd_accounts

from .application import *
from .client import ContractClient
from .defaults import *


def test_application():
    class testapp(DefaultApprove):
        @staticmethod
        @ABIMethod
        def echo(a: String) -> String:
            return a

    app = testapp()

    client = _algod_client()

    acct = get_kmd_accounts().pop()

    signer = AccountTransactionSigner(acct.private_key)

    # Create app on chain
    contract = app.create_app(client, signer)
    print("Created {}".format(contract.networks["default"].app_id))

    # Create client to make calls with
    cc = ContractClient(client, contract, signer)

    try:
        print_results(cc.call(cc.echo, ["echo me"]))
    except Exception as e:
        print("Fail: {}".format(e))
    finally:
        app.delete_app(client, contract.networks["default"].app_id, signer)
        print("Deleted {}".format(contract.networks["default"].app_id))


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format(result.return_value))
