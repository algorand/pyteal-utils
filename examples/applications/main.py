from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from contract import ExampleApp
from sandbox import get_accounts

from pytealutils.applications import ApplicationClient

addr, sk = get_accounts()[0]
signer = AccountTransactionSigner(sk)

client = AlgodClient("a" * 64, "http://localhost:4001")

# Initialize Application from contract.py
app = ExampleApp()

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, app)

# Create the applicatiion on chain, set the app id for the app client
app_id, app_addr, txid = app_client.create(signer)
app_client.app_id = app_id
print(f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid}")

# Call some of the methods we declared
result = app_client.call(
    signer, app.optin.method_spec(), on_complete=transaction.OnComplete.OptInOC
)
print([f"{res.method.name}=>{res.return_value}" for res in result.abi_results])

result = app_client.call(signer, app.set_balance.method_spec(), args=[addr])
print([f"{res.method.name}=>{res.return_value}" for res in result.abi_results])

result = app_client.call(signer, app.get_admin.method_spec())
print([f"{res.method.name}=>{res.return_value}" for res in result.abi_results])

# Call update on the application, assuming we've modified some logic
txid = app_client.update(signer)
print(f"Updated with tx: {txid}")

# Destroy the application
txid = app_client.delete(signer)
print(f"Deleted with tx: {txid}")
