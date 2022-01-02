ABI Types
--------

Each PyTEAL ABIType, it must implement encode/decode to convert to and from over the wire formats and stack types

 Decode:
- Uint8-64 => ExtractUintN => TealType.uint64
- Uint64-512 => N/64 ExtractUint64 => TealType.uint64
- Address => TealType.bytes
- String/Bytes[] => Remove uint16 encoded byte length => TealType.bytes
- T[] => Remove uint16 encoded element length, Remove positions? => TealType.bytes
- T[N]/Tuple(T...) => Remove the positions encodings? => TealType.bytes

# Details

## Boolean
    A boolean value that is restricted to either 0 or 1.  When encoded, up to 8 consecutive bool values will be packed into a single byte.

    Stack type      - bytes of length 1 (could use uint64?)
    Access Methods  - getbit(b: any, idx: uint64)uint64 | setbit(b: any, idx: uint64, val: uint64)any  //TODO: If we use bytes it sets leftmost bit, if uint64 it sets right most. Which should we use? @jj @jp?
    Example Encoded - [1,0,0,0,0,0,0]  represents a single Boolean `True` encoded as the left most bit in a byte set to 1 (implies we have it encoded as a single byte string)

## Byte
    A Single Byte of 8 bits, alias for Uint8.

    Stack type  - bytes of length 1 (could use uint64?)
    Access Methods - getbyte(b: bytes, pos: uint64)uint64 | setbyte(b:bytes, pos:uint64, val:uint64)bytes
    Example Encoded - [1,0,0,0,0,0,0,1] represents the uint8 `65`, hex 0x41, ascii character `A`

## UintN
    An N-bit unsigned integer, where 8 <= N <= 512 and N % 8 = 0.

    Stack type      - uint64 [, uint64... for numbers with > 64 bits]
    Access Methods  - For numbers with <= 64 bits, all normal integer operations are supported. For numbers larger, the values are stored as byte arrays
    Example Encoded - [0x00,0x00,0x00,0x01] represents the number 1 as a 4 byte, 32 bit integer

## String/Byte[]
    A variable-length byte array (byte[]) assumed to contain UTF-8 encoded content.

    Stack type      - bytes
    Access Methods  - All normal string operations are supported
    Example Encoded - [0x00,0x04,0xDE,0xAD,0xBE,0xEF] represents the encoded version of the byte string, prefixed with uint16 encoded length

## Address
    Used to represent a 32-byte Algorand address. This is equivalent to byte[32].

    Stack type      - bytes
    Access Methods  - All normal string operations are supported
    Example Encoded - [0x00, {..30 0x00s}, 0x00] represents the encoded version of the zero address

## UfixedNxM
    An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which denotes a value v as v / (10^M).

    Stack type      - bytes?
    Access Methods  - ??
    Example Encoded - ??

## T[N]
    A fixed-length array of length N, where N >= 0. type can be any other type.

    Stack type      - bytes
    Access Methods  - extract(b: bytes, start: uint64, len: uint64)bytes | extract_uint{16|32|64}(b: bytes, start: uint64)uint64
    Example Encoded - [0x02,0x05,0x00,0x01,0x41,0x00,0x01,0x42] represents the string[2] of ["A","B"]

## T[]
    A variable-length array. type can be any other type.

    Stack type      - bytes
    Access Methods  - extract(b: bytes, start: uint64, len: uint64)bytes | extract_uint{16|32|64}(b: bytes, start: uint64)uint64
    Example Encoded - [0x00,0x02,0x02,0x05,0x00,0x01,0x41,0x00,0x01,0x42] represents the string[] of ["A","B"] with element length and start positions of elements (relative to the start of the start positions)

## Tuple(T1, T2, ..., TN)
    A tuple of the types T1, T2, …, TN, N >= 0.

    Stack type      - bytes
    Access Methods  - extract(b: bytes, start: uint64, len: uint64)bytes | extract_uint{16|32|64}(b: bytes, start: uint64)uint64
    Example Encoded - [0x02,0x05,0x00,0x01,0x41,0x00,0x04] represents the Tuple(string, uint16) of ["A",4]
