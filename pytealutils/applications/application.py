from inspect import getattr_static, signature
from typing import Any, Callable, Final

from pyteal import (
    MAX_TEAL_VERSION,
    ABIReturnSubroutine,
    And,
    App,
    Approve,
    Assert,
    AssetHolding,
    BitLen,
    CallConfig,
    Concat,
    Expr,
    Global,
    Int,
    MethodConfig,
    Router,
    Seq,
    Subroutine,
    SubroutineFnWrapper,
    TealInputError,
    TealType,
    Txn,
    TxnField,
)

from .application_schema import AccountState, ApplicationState

HandlerFunc = Callable[..., Expr]
_handler_config_attr: Final[str] = "__handler_config__"


def get_handler_config(fn: HandlerFunc | ABIReturnSubroutine) -> dict[str, Any]:
    handler_config = {}
    if hasattr(fn, _handler_config_attr):
        handler_config = getattr(fn, _handler_config_attr)

    return handler_config


def add_handler_config(fn: HandlerFunc | ABIReturnSubroutine, key: str, val: Any):
    handler_config = get_handler_config(fn)
    handler_config[key] = val
    setattr(fn, _handler_config_attr, handler_config)


class PrependExpr:
    def __init__(self, fn, expr):
        self.fn = fn
        self.expr = expr

    def __get__(self):
        def _impl(*args, **kwargs):
            return Seq(self.expr, self.fn(*args, **kwargs))

        _impl.__name__ = self.fn.__name__
        _impl.__annotations__ = self.fn.__annotations__
        _impl.__signature__ = signature(self.fn)
        _impl.__doc__ = self.fn.__doc__

        return _impl


class AppendExpr:
    def __init__(self, fn, expr):
        self.fn = fn
        self.expr = expr

    def __get__(self):
        def _impl(*args, **kwargs):
            return Seq(self.fn(*args, **kwargs), self.expr)

        _impl.__name__ = self.fn.__name__
        _impl.__annotations__ = self.fn.__annotations__
        _impl.__signature__ = signature(self.fn)
        _impl.__doc__ = self.fn.__doc__

        return _impl


class Authorize:
    @staticmethod
    def only(addr: Expr):
        @Subroutine(TealType.uint64, name="auth_only")
        def _impl(sender: Expr):
            return sender == addr

        return _impl

    @staticmethod
    def holds_token(asset_id: Expr):
        @Subroutine(TealType.uint64, name="auth_holds_token")
        def _impl(sender: Expr):
            return Seq(
                bal := AssetHolding.balance(sender, asset_id),
                And(bal.hasValue(), bal.value() > Int(0)),
            )

        return _impl

    @staticmethod
    def opted_in(app_id: Expr):
        @Subroutine(TealType.uint64, name="auth_opted_in")
        def _impl(sender: Expr):
            return App.optedIn(sender, app_id)

        return _impl


def _authorize(allowed: SubroutineFnWrapper):
    def _decorate(fn: HandlerFunc):
        if allowed.type_of() != TealType.uint64:
            raise TealInputError(
                f"Expected authorize method to return TealType.uint64, got {allowed.type_of()}"
            )

        return PrependExpr(fn, Assert(allowed(Txn.sender()))).__get__()

    return _decorate


def _assert_zero(txn_fields: list[TxnField]):
    def _impl(fn: HandlerFunc):
        concats = Concat(*[Txn.makeTxnExpr(f) for f in txn_fields])
        if len(txn_fields) == 1:
            concats = Txn.makeTxnExpr(txn_fields[0])
        return PrependExpr(fn, Assert(BitLen(concats) == Int(0))).__get__()

    return _impl


def _readonly(fn: HandlerFunc):
    # add_handler_config(fn, "read_only", True)
    return fn


def _on_complete(mc: MethodConfig):
    def _impl(fn: HandlerFunc):
        add_handler_config(fn, "method_config", mc)
        return fn

    return _impl


def internal(return_type: TealType):
    def _impl(fn: HandlerFunc):
        return Subroutine(return_type)(fn)

    return _impl


def handler(
    fn: HandlerFunc = None,
    /,
    *,
    authorize: Expr = None,
    method_config: MethodConfig = None,
    read_only: bool = False,
    assert_zero: list[TxnField] = None,
):
    def _impl(fn: HandlerFunc):
        if authorize is not None:
            fn = _authorize(authorize)(fn)
        if method_config is not None:
            fn = _on_complete(method_config)(fn)
        if read_only:
            fn = _readonly(fn)
        if assert_zero is not None and len(assert_zero) > 0:
            fn = _assert_zero(assert_zero)(fn)

        wrapped = ABIReturnSubroutine(fn)
        setattr(wrapped, _handler_config_attr, get_handler_config(fn))
        return wrapped

    if fn is None:
        return _impl

    return _impl(fn)


class EmptyAppState(ApplicationState):
    pass


class EmptyAccountState(AccountState):
    pass


class Application:
    app_state: ApplicationState = EmptyAppState()
    acct_state: AccountState = EmptyAccountState()

    # Convenience constant fields
    address: Final[Expr] = Global.current_application_address()
    id: Final[Expr] = Global.current_application_id()

    def __init__(self):
        attrs = [
            getattr_static(self, m)
            for m in list(set(dir(self.__class__)) - set(dir(super())))
            if not m.startswith("_")
        ]

        self.router = Router(type(self).__name__)

        self.methods = [c for c in attrs if isinstance(c, ABIReturnSubroutine)]
        for method in self.methods:
            self.router.add_method_handler(method, **get_handler_config(method))

        (
            self.approval_program,
            self.clear_program,
            self.contract,
        ) = self.router.compile_program(version=MAX_TEAL_VERSION)

    @handler(method_config=MethodConfig(no_op=CallConfig.CREATE))
    def create():
        return Approve()

    @handler(method_config=MethodConfig(update_application=CallConfig.ALL))
    def update():
        return Approve()

    @handler(method_config=MethodConfig(delete_application=CallConfig.ALL))
    def delete():
        return Approve()
