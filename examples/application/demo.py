from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
)
from algosdk.v2client.algod import AlgodClient
from kitchen_sink import KitchenSink

from pytealutils.application.client import ContractClient
from tests.helpers import get_kmd_accounts


def demo():
    accts = get_kmd_accounts()
    signer = AccountTransactionSigner(accts[0].private_key)

    # Connect to sandbox
    client = AlgodClient("a" * 64, "http://localhost:4001")

    # Instantiate App Object that is also our pyteal
    app = KitchenSink()

    # Create client to make calls with, default is the default network we're connected to in the client
    cc = ContractClient(client, app, "default", signer)

    # Create app on chain
    cc.create_app()
    print("Created {}".format(cc.app_id))

    try:
        print_results(cc.reverse(["desrever yllufsseccus"], budget=2))
        print_results(cc.add([1, 1]))
        print_results(cc.sub([3, 1]))
        print_results(cc.div([4, 2]))
        print_results(cc.mul([3, 2]))
        print_results(cc.echo_first([["a", "b"]]))

        # Compose from set of app calls
        comp = AtomicTransactionComposer()
        cc.compose(cc.methods["add"], [1, 1], comp)
        cc.compose(cc.methods["sub"], [3, 1], comp)
        cc.compose(cc.methods["div"], [4, 2], comp)
        cc.compose(cc.methods["mul"], [3, 2], comp)
        print_results(comp.execute(cc.client, 2))
    except Exception as e:
        print("Fail: {}".format(e))
    finally:
        cc.delete_app()
        print("Deleted {}".format(cc.app_id))


def print_results(results):
    for result in results.abi_results:
        if result.return_value is None:
            continue
        print("Parsed Result: {}".format(result.return_value))


if __name__ == "__main__":
    demo()
