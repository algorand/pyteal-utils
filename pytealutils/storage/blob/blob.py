from typing import Tuple
from pyteal import (
    Extract,
    GetByte,
    SetByte,
    Concat,
    Substring,
    Len,
    Or,
    Itob,
    BytesZero,
    Subroutine,
    Int,
    TealType,
    ScratchVar,
    For,
    App,
    Expr,
    Seq,
    Bytes,
    If,
)

max_keys = 16
page_size = 128 - 1  # need 1 byte for key
max_bytes = max_keys * page_size
max_bits = max_bytes * 8

maxKeys = Int(max_keys)
pageSize = Int(page_size)
maxBytes = Int(max_bytes)


def _key_and_offset(idx: Int) -> Tuple[Int, Int]:
    return idx / pageSize, idx % pageSize


@Subroutine(TealType.bytes)
def intkey(i: TealType.uint64) -> Expr:
    return Extract(Itob(i), Int(7), Int(1))


class Blob:
    """
    Blob is a class holding static methods to work with the local storage of an account as a binary large object

    The `zero` method must be called on an account on opt in and the schema of the local storage should be 16 bytes
    """

    def __init__(self):
        # Add Keyspace range?
        # Allow global storage option
        pass

    @staticmethod
    @Subroutine(TealType.none)
    def zero(acct: TealType.uint64) -> Expr:
        """
        initializes local state of an account to all zero bytes

        This allows us to be lazy later and _assume_ all the strings are the same size

        """
        i = ScratchVar()
        init = i.store(Int(0))
        cond = i.load() < maxKeys
        iter = i.store(i.load() + Int(1))
        return For(init, cond, iter).Do(
            App.localPut(acct, intkey(i.load()), BytesZero(pageSize))
        )

    @staticmethod
    @Subroutine(TealType.uint64)
    def get_byte(acct: TealType.uint64, idx: TealType.uint64):
        """
        Get a single byte from local storage of an account by index
        """
        key, offset = _key_and_offset(idx)
        return GetByte(App.localGet(acct, intkey(key)), offset)

    @staticmethod
    @Subroutine(TealType.none)
    def set_byte(acct: TealType.uint64, idx: TealType.uint64, byte: TealType.uint64):
        """
        Set a single byte from local storage of an account by index
        """
        key, offset = _key_and_offset(idx)
        return App.localPut(
            acct, intkey(key), SetByte(App.localGet(acct, intkey(key)), offset, byte)
        )

    @staticmethod
    @Subroutine(TealType.bytes)
    def read(
        acct: TealType.uint64, bstart: TealType.uint64, bend: TealType.uint64
    ) -> Expr:
        """
        read bytes between bstart and bstop from local storage of an account by index
        """

        startKey, startOffset = _key_and_offset(bstart)
        stopKey, stopOffset = _key_and_offset(bend)

        stopKey += startKey
        stopOffset += startOffset

        key = ScratchVar()
        buff = ScratchVar()

        start = ScratchVar()
        stop = ScratchVar()

        init = key.store(startKey)
        cond = key.load() < stopKey
        incr = key.store(key.load() + Int(1))

        return Seq(
            buff.store(Bytes("")),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    buff.store(
                        Concat(
                            buff.load(),
                            Substring(
                                App.localGet(acct, intkey(key.load())),
                                start.load(),
                                stop.load(),
                            ),
                        )
                    ),
                )
            ),
            buff.load(),
        )

    @staticmethod
    @Subroutine(TealType.uint64)
    def write(
        acct: TealType.uint64, bstart: TealType.uint64, buff: TealType.bytes
    ) -> Expr:
        """
        write bytes between bstart and len(buff) to local storage of an account
        """

        length = Len(buff)

        startKey, startOffset = _key_and_offset(bstart)
        stopKey, stopOffset = _key_and_offset(length)

        stopKey += startKey
        stopOffset += startOffset

        key = ScratchVar()
        start = ScratchVar()
        stop = ScratchVar()
        written = ScratchVar()

        init = key.store(startKey)
        cond = key.load() < stopKey
        incr = key.store(key.load() + Int(1))

        delta = ScratchVar()

        return Seq(
            written.store(Int(0)),
            For(init, cond, incr).Do(
                Seq(
                    start.store(If(key.load() == startKey, startOffset, Int(0))),
                    stop.store(If(key.load() == stopKey, stopOffset, pageSize)),
                    App.localPut(
                        acct,
                        intkey(key.load()),
                        If(
                            Or(stop.load() != pageSize, start.load() != Int(0))
                        )  # Its a partial write
                        .Then(
                            Seq(
                                delta.store(stop.load() - start.load()),
                                Concat(
                                    Substring(
                                        App.localGet(acct, intkey(key.load())),
                                        Int(0),
                                        start.load(),
                                    ),
                                    Extract(
                                        buff,
                                        written.load(),
                                        delta.load(),
                                    ),
                                    Substring(
                                        App.localGet(acct, intkey(key.load())),
                                        stop.load(),
                                        pageSize,
                                    ),
                                ),
                            )
                        )
                        .Else(
                            Seq(
                                delta.store(pageSize),
                                Substring(buff, written.load(), pageSize),
                            )
                        ),
                    ),
                    written.store(written.load() + delta.load()),
                )
            ),
            written.load(),
        )
