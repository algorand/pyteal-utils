from algosdk.atomic_transaction_composer import AccountTransactionSigner
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

    # Create client to make calls with
    cc = ContractClient(client, app, "default", signer)

    # Create app on chain
    cc.create_app()
    print("Created {}".format(cc.app_id))

    try:
        print_results(cc.reverse(["desrever yllufsseccus"], budget=2))

        # print_results(cc.concat([["this", "string", "is", "joined"]]))
        ### Single call, increase budget with dummy calls
        # print_results(cc.split(["this string is split"], budget=2))

        print_results(cc.add([1, 1]))
        print_results(cc.sub([3, 1]))
        print_results(cc.div([4, 2]))
        print_results(cc.mul([3, 2]))

        # Compose from set of app calls
        # comp = AtomicTransactionComposer()
        # cc.compose(cc.add, [1, 1], comp)
        # cc.compose(cc.sub, [3, 1], comp)
        # cc.compose(cc.div, [4, 2], comp)
        # cc.compose(cc.mul, [3, 2], comp)
        # print_results(comp.execute(cc.client, 2))
    except Exception as e:
        print("Fail: {}".format(e))
    finally:
        cc.delete_app()
        print("Deleted {}".format(cc.app_id))


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format(result.return_value))


if __name__ == "__main__":
    demo()
