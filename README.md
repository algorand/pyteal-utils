# pyteal-utils
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
1. Install Docker Compose
2. Clone Algorand Sandbox repo: `git clone https://github.com/algorand/sandbox.git`
3. Clone this repo: `git clone https://github.com/algorand/pyteal-utils.git`
4. Install Python dependecies: `poetry install`
5. Activate a virual env: `poetry shell`
6. Configure pre-commit hooks: `pre-commit install`
7. Bootstrap Algorand Sandbox (`dev` mode recommended): `./sandbox up dev`
=======

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
