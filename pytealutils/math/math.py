from pyteal import Subroutine, TealType, Exp, Int, If

# TODO: Wide math?


@Subroutine(TealType.uint64)
def exp10(x: TealType.uint64):
    """Returns 10^x, useful for things like total supply of an asset"""
    return Exp(Int(10), x)


@Subroutine(TealType.uint64)
def max(a: TealType.uint64, b: TealType.uint64):
    """Returns the max of 2 integers"""
    return If(a > b, a, b)


@Subroutine(TealType.uint64)
def min(a: TealType.uint64, b: TealType.uint64):
    """Returns the min of 2 integers"""
    return If(a < b, a, b)


@Subroutine(TealType.uint64)
def ceil(a: TealType.uint64, b: TealType.uint64):
    """Returns the result of division rounded up to the next integer"""
    q = a / b
    return If(a % b > Int(0), q + Int(1), q)
