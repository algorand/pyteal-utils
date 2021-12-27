# pyteal-utils

*EXPERIMENTAL* *WIP*

There is no guarantee to the API of this repository. It is subject to change without a tagged release.

This repository is meant to contain PyTEAL utility methods common in many Smart Contract programs.

## Strings

atoi - ascii representation of number to integer
itoa - integer to ascii representation

head - first byte of string returned as uint64
tail - string minus first byte

## Txn

common transaction filter safety checks

common inner transaction operations

## Nums

Some common math functions

## Storage

App Global and Local storage methods

### Blob

Treat local storage of an account as a Binary Large Object with ~2k storage. (16 * (128 - 1) = 2032 bytes)

API allow read/write by index into `[2032]byte` array

> Note: You must zero the blob on initialization, see `examples/blob/main.py`


## Contributing

As PyTEAL user, your contribution is extremely valuable to grow PyTEAL utilities!
As [PyTEAL](https://github.com/algorand/pyteal) user, your contribution is extremely valuable to grow PyTEAL utilities!

Please follow the [contribution guide](https://github.com/algorand/pyteal-utils/blob/main/CONTRIBUTING.md)!

## Prerequisites
- [poetry](https://python-poetry.org/)
- [pre-commit](https://pre-commit.com/)
- [py-algorand-sdk](https://github.com/algorand/py-algorand-sdk)
- [pyteal](https://github.com/algorand/pyteal)
- [pytest](https://docs.pytest.org/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Algorand Sandbox](https://github.com/algorand/sandbox)

## Set up your PyTeal environment
1. Set up the [sandbox](https://github.com/algorand/sandbox) and start it (`dev` mode recommended): `./sandbox up dev`
2. Clone this repo: `git clone https://github.com/algorand/pyteal-utils.git`
3. Install Python dependecies: `poetry install`
4. Activate a virual env: `poetry shell`
5. Configure pre-commit hooks: `pre-commit install`
