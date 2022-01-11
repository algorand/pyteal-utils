from pyteal import Approve, Expr, Reject, Subroutine, TealType

from .application import Application


class DefaultApprove(Application):
    @staticmethod
    @Subroutine(TealType.uint64)
    def create() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def update() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def delete() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def optIn() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def closeOut() -> Expr:
        return Approve()

    @staticmethod
    @Subroutine(TealType.uint64)
    def clearState() -> Expr:
        return Approve()


class DefaultReject(Application):
    @staticmethod
    @Subroutine(TealType.uint64)
    def create() -> Expr:
        return Reject()

    @staticmethod
    @Subroutine(TealType.uint64)
    def update() -> Expr:
        return Reject()

    @staticmethod
    @Subroutine(TealType.uint64)
    def delete() -> Expr:
        return Reject()

    @staticmethod
    @Subroutine(TealType.uint64)
    def optIn() -> Expr:
        return Reject()

    @staticmethod
    @Subroutine(TealType.uint64)
    def closeOut() -> Expr:
        return Reject()

    @staticmethod
    @Subroutine(TealType.uint64)
    def clearState() -> Expr:
        return Reject()
