# pyteal-utils

*EXPERIMENTAL* *WIP*

There is no guarantee to the API of this repository. It is subject to change without a tagged release. 

This repository is meant to contain PyTeal utility methods common in many Smart Contract programs.

## Strings

atoi - ascii representation of number to integer
itoa - integer to ascii representation 

head - first byte of string returned as uint64
tail - string minus first byte 

## Txn

common transaction filter safety checks

common inner transaction operations

## Math

This is barely a math package

## Storage

App Global and Local storage methods

### Blob

Treat local storage of an account as a Binary Large Object with ~2k storage. (16 * (128 - 1) = 2032 bytes)

Api allow read/write by index into `[2032]byte` array

>Node: You must zero the blob on initialization, see `examples/blob/main.py`
