from abc import abstractmethod

from pyteal import CompileOptions, Expr, TealType


class ABIType(Expr):
    stack_type = TealType.anytype
    byte_len = 0
    dynamic = False

    @abstractmethod
    def encode() -> Expr:
        pass

    def type_of(self) -> TealType:
        return self.stack_type

    def has_return(self) -> bool:
        return True

    def __str__(self) -> str:
        return ""

    def __teal__(self, options: CompileOptions):
        return self.value.__teal__(options)
