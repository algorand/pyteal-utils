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

This repository is mean to contain PyTeal utility methods common in many Smart Contract programs.

## Strings

## Txn

## Math

## Storage


