# pyteal-utils
As PyTeal user, your contribution is extremely valuable to grow PyTeal utilities!

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
6. Bootstrap Algorand Sandbox (`dev` mode recommended): `./sandbox up dev`

## Pull Requests guidelines for new PyTeal utilites
Pull requests (PR) are the best way to propose your PyTeal utilities.

We actively welcome and support community proposals to grow PyTeal utilities,
let's do it in a clean and organized way:

1. Fork this repo and create your branch from `main`, please name it `util/...`
2. New PyTeal utilities should be always tested. Please use `pytest` to add tests!
3. Verify coding style consistency with `pre-commit run --all-files` before submitting your PR!
4. Ensure all your specifc unit-tests or end-to-end pass!
5. Make sure your code lints.
6. Issue your PR!

### Running tests
The Sandbox repository has to either be available at `../sandbox` or set via `ALGORAND_SANBOX_DIR`.

```shell
(.venv) pytest
```

### Fortmatting Coding Style
Refer to `pre-commit-config.yaml`, make sure to have the hook activated when commiting to this repository.
