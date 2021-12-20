from pyteal import *

max_keys  = 16
page_size = 128 - 1  # need 1 byte for key
max_bytes = max_keys * page_size
max_bits  = max_bytes * 8

maxKeys  = Int(max_keys)
pageSize = Int(page_size)
maxBytes = int(max_bytes)


@Subroutine(TealType.bytes)
def intkey(i: TealType.uint64) -> Expr:
    return Extract(Itob(i), Int(7), Int(1))

class Blob:
    def __init__(self):
        # Add Keyspace range?
        # Allow global storage option
        pass

    @staticmethod
    @Subroutine(TealType.none)
    def zero(acct: TealType.uint64) -> Expr:
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
        key = intkey(idx / pageSize)
        offset = idx % pageSize
        return GetByte(App.localGet(acct, key), offset)

    @staticmethod
    @Subroutine(TealType.none)
    def set_byte(acct: TealType.uint64, idx: TealType.uint64, byte: TealType.uint64):
        key = intkey(idx / pageSize)
        offset = idx % pageSize
        return App.localPut(acct, key, SetByte(App.localGet(acct, key), offset, byte))

    @staticmethod
    @Subroutine(TealType.bytes)
    def read(
        acct: TealType.uint64, bstart: TealType.uint64, bstop: TealType.uint64
    ) -> Expr:

        startKey = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey = startKey + (bstop / pageSize)
        stopOffset = startOffset + (bstop % pageSize)

        key = ScratchVar()
        buff = ScratchVar()

        start = ScratchVar()
        stop = ScratchVar()

        init = key.store(startKey)
        cond = key.load() <= stopKey
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

        length = Len(buff)

        startKey = bstart / pageSize
        startOffset = bstart % pageSize

        stopKey = startKey + (length / pageSize)
        stopOffset = startOffset + (length % pageSize)

        key = ScratchVar()
        start = ScratchVar()
        stop = ScratchVar()
        written = ScratchVar()

        init = key.store(startKey)
        cond = key.load() <= stopKey
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
