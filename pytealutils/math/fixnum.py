from typing import Union

from pyteal import TealType

# From ABI: ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which


class Fixnum:

    # denotes a value v as v / (10^M)
    def __init__(self, bits: int, precision: int, value: Union[int, float]):
        assert 8 <= bits <= 512, "Number of bits must be between 8 and 512"
        assert bits % 8 == 0, "Bits must be a multiple of 8"
        assert 0 < precision <= 160, "Precision must be between 0 and 160"

        self.bits = bits
        self.precision = precision
        self.value = value

    def add(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def subtract(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def divide(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def divide(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def log(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def log2(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def ln(self, x: Union[TealType.uint64, TealType.bytes]):
        pass

    def pow(self, x: Union[TealType.uint64, TealType.bytes]):
        pass
