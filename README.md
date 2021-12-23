# pyteal-utils
As [PyTEAL](https://github.com/algorand/pyteal) user, your contribution is extremely valuable to grow PyTEAL utilities!

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

## Pull Requests guidelines for new PyTEAL utilites
Pull Requests (PR) are the best way to propose your PyTEAL utilities.

We actively welcome and support community proposals to grow PyTEAL utilities,
let's do it in a clean, organized, tested and well documented way:

1. Fork this repo and create your branch from `main`, please name it `util/...`
2. Each PyTEAL utils subpackage must have its own folder inside `pytealutils`.
3. New PyTEAL utilities must be tested. Please follow `pytest` best practices.
4. Unit Tests: add specific unit-tests as `*_test.py` in the same subpackage folder!
5. E2E Tests: add end-to-end tests as `*_test.py` in the [tests](https://github.com/algorand/pyteal-utils/tree/main/tests) folder.
6. Verify coding style consistency with `pre-commit run --all-files` before submitting your PR!
7. Ensure all your specifc unit-tests or end-to-end pass!
8. Make sure your code lints.
9. New PyTEAL utilities must be documented. Examples are useful too. [Get inspired](https://github.com/algorand/pyteal/blob/master/pyteal/ast/cond.py#L18)!
10. Issue your PR!

### Running tests
The Sandbox repository has to either be available at `../sandbox` or set via `ALGORAND_SANBOX_DIR`.

```shell
(.venv) pytest
```

### Fortmatting Coding Style
Refer to `pre-commit-config.yaml`, make sure to have the hook activated when commiting to this repository.

## Testing utilites
How many times you already found your self copying&pasting the same helper
functions and classes from different projects? We want to avoid this!

To ensure homogeneous and repeatable tests please use common helpers from
[utils.py](https://github.com/algorand/pyteal-utils/blob/main/tests/utils.py).
Growing and maintaining common helpers avoid code repetition and fragmentation
for those general utilities like: instantiate an Algod client, create and fund
an Accout in Sandbox, etc.

Unless your test *really* needs ad-hoc helpers, the best practice is using
common helpers.

Do you think a really useful helper for everybody is missing? Please open an `Issue` providing:

1. Helper function/class name
2. Helper function/class short description
3. Optional: implementation draft/proposal

## Request new PyTEAL utils
Want to suggest a new PyTEAL utils to the community? Please open an `Issue` providing:

1. PyTEAL utils name
2. PyTEAL utils short description
3. Optional: implementation draft/proposal
