#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

if [[ $TRAVIS_TAG ]]; then
    # Build and deploy if the tests pass and
    # the commit is tagged
    ### Install Rust (no nighlty)
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain nightly -y
    ### Build the wheels ###
    $PIP install maturin
    maturin build --release
    # maturin publish --username <username> --password <password> --repository-url <registry>?
    ### Upload the wheels to PyPI ###
    $PIP install twine
    $PYTHON -m twine upload --repository-url https://upload.pypi.org/legacy/ target/wheels/*.whl --skip-existing
fi
