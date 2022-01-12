from algosdk import mnemonic
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.mnemonic import to_private_key
from algosdk.v2client.algod import AlgodClient
from kitchen_sink import KitchenSink
from tests.helpers import get_kmd_accounts

from pytealutils.application.client import ContractClient


def print_results(results):
    for result in results.abi_results:
        print("Raw Result: {}".format(result.raw_value))
        print("Parsed Result: {}".format(result.return_value))


# Free money

accts = get_kmd_accounts()
signer = AccountTransactionSigner(accts[0].private_key)

# Connect to sandbox
client = AlgodClient("a" * 64, "http://localhost:4001")


# Instantiate App Object that is also our pyteal
app = KitchenSink()

# Create app on chain
contract = app.create_app(client, signer)
print("Created {}".format(contract.networks["default"].app_id))

# Create client to make calls with
cc = ContractClient(client, contract, signer)

try:
    print_results(cc.reverse(["desrever yllufsseccus"], budget=2))
    #print_results(cc.concat([["this", "string", "is", "joined"]]))
    ### Single call, increase budget with dummy calls
    #print_results(cc.split(["this string is split"], budget=2))

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
    app.delete_app(client, contract.networks["default"].app_id, signer)
    print("Deleted {}".format(contract.networks["default"].app_id))
