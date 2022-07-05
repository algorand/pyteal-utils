import json
from typing import Final

from pyteal import *

from pytealutils.applications import *


class ExampleAppState(ApplicationState):
    # Global KVs known at compile time.
    # If no key is specified, the name of the attribute is used
    # The `static` argument will allow setting only once and error if there is an attempt to overwrite
    # The default value may be provided for easier initialization
    admin = GlobalStateValue(
        stack_type=TealType.bytes, default=Global.creator_address(), static=True
    )
    asset_a = GlobalStateValue(
        stack_type=TealType.uint64, default=Int(123), static=True
    )
    asset_b = GlobalStateValue(
        stack_type=TealType.uint64, default=Int(456), static=True
    )
    decimals = GlobalStateValue(stack_type=TealType.uint64, default=Int(4), static=True)
    ratio = GlobalStateValue(stack_type=TealType.uint64, default=Int(0))
    membership_token = GlobalStateValue(stack_type=TealType.uint64)


class ExampleAcctState(AccountState):
    # Local KVs known at compile time, if no key is specified the name of the attribute is used
    # A default value may be provided and all local state can be initialized if they have a default value
    balance_a = LocalStateValue(
        stack_type=TealType.uint64, key=Bytes("a"), default=Int(0)
    )
    balance_b = LocalStateValue(
        stack_type=TealType.uint64, key=Bytes("b"), default=Int(0)
    )

    # Unknown at compile time, key_gen may be provided to build a key from some expression input
    tags = DynamicLocalStateValue(
        stack_type=TealType.bytes,
        max_keys=10,
        key_gen=Subroutine(TealType.bytes, name="make_key")(
            lambda v: Concat(Bytes("tag:"), Itob(v))
        ),
    )


class ExampleApp(Application):
    # We're calling global state `app_state`
    app_state: Final[ExampleAppState] = ExampleAppState()
    # We're calling local state `acct_state`
    acct_state: Final[ExampleAcctState] = ExampleAcctState()

    # Decorate the create method with `handler` which accepts arguments and applies wrapping functions
    # to augment the behavior before adding to the router in the parent class
    @handler(method_config=MethodConfig(no_op=CallConfig.CREATE))
    def create():
        return ExampleApp.app_state.initialize()

    # Silly test for auth below
    @internal(TealType.uint64)
    def is_whale(sender: Expr):
        return Seq(
            bal := AccountParam.balance(sender),
            Assert(bal.hasValue()),
            bal.value() > Int(int(1e10)),
        )

    # The authorize method param takes a subroutine that accepts a single argument, the app call transaction sender.
    # There are several pre-defined Authorize.xxx methods to for common functions
    @handler(authorize=is_whale, method_config=MethodConfig(opt_in=CallConfig.ALL))
    def optin():
        return ExampleApp.acct_state.initialize(Txn.sender())

    # Token gate access to something priveliged action
    @handler(authorize=Authorize.holds_token(app_state.membership_token))
    def do_special_thing(access_token: abi.Asset):
        return Assert(Int(1))

    # Use the dynamic state var to create a key and set the value
    @handler(authorize=Authorize.opted_in(Application.id))
    def set_tag(tag_key: abi.Uint64, tag_val: abi.String):
        return ExampleApp.acct_state.tags(tag_key.get()).set(
            Txn.sender(), tag_val.get()
        )

    # Use the dynamic state var to create a key and set the value
    @handler(authorize=Authorize.opted_in(Application.id))
    def get_tag(tag_id: abi.Uint64, *, output: abi.String):
        return output.set(ExampleApp.acct_state.tags(tag_id.get()).get(Txn.sender()))

    # We can access a stored value here to compare with Txn.sender
    @handler(authorize=Authorize.only(app_state.admin))
    def set_balance(a: abi.Account):
        """Sets the balance on an account to the constant 100"""
        return ExampleApp.acct_state.balance_a.set(a.address(), Int(100))

    # Doesn't do anything yet but may follow arc22
    @handler(read_only=True)
    def get_admin(*, output: abi.Address):
        return output.set(ExampleApp.app_state.admin)

    # no args necessary if none are needed
    @handler
    def stuff():
        return Assert(Int(1))


if __name__ == "__main__":
    import json

    app = ExampleApp()

    with open("abi.json", "w") as f:
        f.write(json.dumps(app.contract.dictify()))
    with open("approval.teal", "w") as f:
        f.write(app.approval_program)
    with open("clear.teal", "w") as f:
        f.write(app.clear_program)
