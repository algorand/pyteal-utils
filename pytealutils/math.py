from pyteal import Subroutine, TealType, Exp, Int, If

# Wide math?

@Subroutine(TealType.uint64)
def exp10(x: TealType.uint64):
    return Exp(Int(10), x)


@Subroutine(TealType.uint64)
def max(a: TealType.uint64, b: TealType.uint64):
    return If(a > b, a, b)


@Subroutine(TealType.uint64)
def min(a: TealType.uint64, b: TealType.uint64):
    return If(a < b, a, b)


# By default division is truncated to floor, this offers the opposite
@Subroutine(TealType.uint64)
def ceil(n, d):
    q = n / d
    return If(n % d != Int(0), q + Int(1), q)
