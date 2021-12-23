# Contribution Guide

If you are interested in contributing to the project, we welcome and thank you.
We want to make PyTEAL the best and easiest way to build on Algorand Virtual Machine.

We appreciate your willingness to help us.

## Pull Requests guidelines for new PyTEAL utils

Pull Requests (PR) are the best way to propose your PyTEAL utils.

We actively welcome and support community proposals to grow PyTEAL utils,
let's do it in a clean, organized, tested and well documented way:

1. Fork this repo and create your branch from `main`, please name it `util/...`
2. Each PyTEAL utils `subpackage` must have its own folder inside `pytealutils`.
3. New PyTEAL utils must be tested. Please follow `pytest` best practices.
4. Unit Tests: add specific unit-tests as `*_test.py` in the same `subpackage` folder!
5. E2E Tests: add end-to-end tests as `*_test.py` in the [tests](https://github.com/algorand/pyteal-utils/tree/main/tests) folder.
6. Verify coding style consistency with `pre-commit run --all-files` before submitting your PR!
7. Ensure all your specifc unit-tests or end-to-end pass!
8. Make sure your code lints.
9. New PyTEAL utils must be documented. Examples are useful too. [Get inspired](https://github.com/algorand/pyteal/blob/master/pyteal/ast/cond.py#L18)!
10. Issue your PR!

### Running tests

The Sandbox repository has to either be available at `../sandbox` or set via `ALGORAND_SANBOX_DIR`.

```shell
(.venv) pytest
```

## Testing utils

How many times you already found your self copying&pasting the same helper
functions and classes from different projects? We want to avoid this!

To ensure homogeneous and repeatable tests please use common helpers from
[utils.py](https://github.com/algorand/pyteal-utils/blob/main/tests/utils.py).
Growing and maintaining common helpers avoid code repetition and fragmentation
for those general utilities like: instantiate an Algod client, create and fund
an Accout in Sandbox, etc.

Unless your test *really* needs ad-hoc helpers, the best practice is using
common helpers.

Do you think a really useful helper for everybody is missing? Please consider [filing an issue](https://help.github.com/en/articles/creating-an-issue) providing:

1. Helper function/class name
2. Helper function/class short description
3. Optional: implementation draft/proposal

## Request new PyTEAL utils

Want to suggest a new PyTEAL utils to the community? Please consider [filing an issue](https://help.github.com/en/articles/creating-an-issue) providing:

1. PyTEAL utils name
2. PyTEAL utils short description
3. Optional: implementation draft/proposal

## Use a Consistent Coding Style

We recommand the contributing code following [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

We rely on pre-commit and hooks running recommended validators. Refer to `pre-commit-config.yaml`, make sure to have the hook activated when commiting to this repository.


## License

By contributing, you agree that your contributions will be licensed under its MIT License.
