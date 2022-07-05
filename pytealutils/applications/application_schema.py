from algosdk.future.transaction import StateSchema
from pyteal import (
    App,
    Assert,
    Bytes,
    CompileOptions,
    Expr,
    If,
    Int,
    Not,
    ScratchVar,
    Seq,
    SubroutineFnWrapper,
    TealInputError,
    TealType,
    TealTypeError,
)


class ApplicationState:
    def __init__(self):
        attrs = {
            attr: getattr(self, attr)
            for attr in set(dir(self.__class__)) - set(dir(super()))
            if not attr.startswith("__")
        }

        self.declared_vals: dict[str, GlobalStateValue] = {
            k: GlobalStateValue(
                stack_type=v.stack_type,
                key=v.key if v.key is not None else Bytes(k),
                default=v.default,
            )
            for k, v in attrs.items()
            if isinstance(v, GlobalStateValue)
        }
        self.__dict__.update(self.declared_vals)

        self.dynamic_vals: dict[str, DynamicGlobalStateValue] = {
            k: v for k, v in attrs.items() if isinstance(v, DynamicGlobalStateValue)
        }
        self.__dict__.update(self.dynamic_vals)

        self.num_uints = len(
            [l for l in self.declared_vals.values() if l.stack_type == TealType.uint64]
        ) + len(
            [l for l in self.dynamic_vals.values() if l.stack_type == TealType.uint64]
        )

        self.num_byte_slices = len(
            [l for l in self.declared_vals.values() if l.stack_type == TealType.bytes]
        ) + len(
            [l for l in self.dynamic_vals.values() if l.stack_type == TealType.bytes]
        )

    def initialize(self):
        return Seq(*[g.set_default() for g in self.declared_vals.values()])

    def schema(self):
        return StateSchema(
            num_uints=self.num_uints, num_byte_slices=self.num_byte_slices
        )


class DynamicGlobalStateValue:
    def __init__(
        self, stack_type: TealType, max_keys: int, key_gen: SubroutineFnWrapper = None
    ):
        self.stack_type = stack_type
        self.max_keys = max_keys

        if key_gen is not None:
            if key_gen.type_of() != TealType.bytes:
                raise Exception("key generator must evaluate to bytes")
            self.key_generator = key_gen

    def __call__(self, key_seed: Expr):
        key = key_seed
        if self.key_generator is not None:
            key = self.key_generator(key)
        return GlobalStateValue(stack_type=self.stack_type, key=key)


class GlobalStateValue(Expr):
    def __init__(
        self,
        stack_type: TealType,
        key: Expr = None,
        default: Expr = None,
        static: bool = False,
        descr: str = None,
    ):

        if key is not None:
            if key.type_of() != TealType.bytes:
                raise Exception("key must evaluate to bytes")
            self.key = key
        else:
            self.key = None

        self.stack_type = stack_type
        self.static = static
        self.default = default
        self.descr = descr

    def has_return(self) -> bool:
        return super().has_return()

    def type_of(self) -> TealType:
        return self.stack_type

    def __teal__(self, options: "CompileOptions"):
        return self.get().__teal__(options)

    def __str__(self) -> str:
        return f"GlobalState {self.key}"

    def __call__(self, val: Expr) -> Expr:
        return self.set(val)

    def set_default(self) -> Expr:
        if self.default:
            return App.globalPut(self.key, self.default)

        if self.stack_type == TealType.uint64:
            return App.globalPut(self.key, Int(0))
        else:
            return App.globalPut(self.key, Bytes(""))

    def set(self, val: Expr) -> Expr:
        if self.static:
            return Seq(
                v := App.globalGetEx(Int(0), self.key),
                Assert(Not(v.hasValue())),
                App.globalPut(self.key, val),
            )

        return App.globalPut(self.key, val)

    def increment(self, cnt: Expr = Int(1)) -> Expr:
        if self.stack_type != TealType.uint64:
            raise TealInputError("Only uint64 types can be incremented")

        return Seq(
            (sv := ScratchVar()).store(self.get()),
            self.set(sv.load() + cnt),
            sv.load(),
        )

    def decrement(self, cnt: Expr = Int(1)) -> Expr:
        if self.stack_type != TealType.uint64:
            raise TealInputError("Only uint64 types can be decremented")

        return Seq(
            (sv := ScratchVar()).store(self.get()),
            self.set(sv.load() - cnt),
            sv.load(),
        )

    def get(self) -> Expr:
        return App.globalGet(self.key)

    def get_maybe(self) -> Expr:
        return App.globalGetEx(Int(0), self.key)

    def get_else(self, val: Expr) -> Expr:
        return If((v := App.globalGetEx(Int(0), self.key)).hasValue(), v.value(), val)


class AccountState:
    def __init__(self):
        attrs = {
            attr: getattr(self, attr)
            for attr in set(dir(self.__class__)) - set(dir(super()))
            if not attr.startswith("__")
        }

        self.declared_vals: dict[str, LocalStateValue] = {
            k: LocalStateValue(
                stack_type=v.stack_type,
                key=v.key if v.key is not None else Bytes(k),
                default=v.default,
            )
            for k, v in attrs.items()
            if isinstance(v, LocalStateValue)
        }
        self.__dict__.update(self.declared_vals)

        self.dynamic_vals: dict[str, DynamicLocalStateValue] = {
            k: v for k, v in attrs.items() if isinstance(v, DynamicLocalStateValue)
        }
        self.__dict__.update(self.dynamic_vals)

        self.num_uints = len(
            [l for l in self.declared_vals.values() if l.stack_type == TealType.uint64]
        ) + len(
            [l for l in self.dynamic_vals.values() if l.stack_type == TealType.uint64]
        )

        self.num_byte_slices = len(
            [l for l in self.declared_vals.values() if l.stack_type == TealType.bytes]
        ) + len(
            [l for l in self.dynamic_vals.values() if l.stack_type == TealType.bytes]
        )

    def initialize(self, acct: Expr):
        return Seq(*[l.set_default(acct) for l in self.declared_vals.values()])

    def schema(self):
        return StateSchema(
            num_uints=self.num_uints, num_byte_slices=self.num_byte_slices
        )


class DynamicLocalStateValue:
    def __init__(
        self,
        stack_type: TealType,
        max_keys: int,
        key_gen: SubroutineFnWrapper = None,
        descr: str = None,
    ):
        self.stack_type = stack_type
        self.max_keys = max_keys
        self.descr = descr

        if key_gen is not None:
            if key_gen.type_of() != TealType.bytes:
                raise Exception("key generator must evaluate to bytes")
            self.key_generator = key_gen

    def __call__(self, key_seed: Expr):
        key = key_seed
        if self.key_generator is not None:
            key = self.key_generator(key)
        return LocalStateValue(stack_type=self.stack_type, key=key)


class LocalStateValue:
    def __init__(
        self,
        stack_type: TealType,
        key: Expr = None,
        default: Expr = None,
        descr: str = None,
    ):
        if key is not None:
            if key.type_of() != TealType.bytes:
                raise Exception("key must evaluate to bytes")
            self.key = key
        else:
            self.key = None

        self.default = default
        self.stack_type = stack_type
        self.descr = descr

    def set(self, acct: Expr, val: Expr) -> Expr:
        return App.localPut(acct, self.key, val)

    def set_default(self, acct: Expr) -> Expr:
        if self.default is not None:
            return App.localPut(acct, self.key, self.default)

        if self.stack_type == TealType.uint64:
            return App.localPut(acct, self.key, Int(0))
        else:
            return App.localPut(acct, self.key, Bytes(""))

    def get(self, acct: Expr) -> Expr:
        return App.localGet(acct, self.key)

    def get_maybe(self, acct: Expr) -> Expr:
        return App.localGetEx(Int(0), acct, self.key)

    def get_else(self, acct: Expr, val: Expr) -> Expr:
        if val.type_of() != self.stack_type:
            return TealTypeError(val.type_of(), self.stack_type)

        return Seq(
            (v := App.localGetEx(acct, Int(0), self.key)),
            If(v.hasValue(), v.value(), val),
        )
