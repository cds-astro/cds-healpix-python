#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

if [[ $TRAVIS_TAG ]]; then
    # Build and deploy if the tests pass and
    # the commit is tagged
    ### Install Rust (no nighlty)
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain nightly -y
    ### Install virtualenv, maturin and twine
    $PIP install virtualenv maturin twine
    ### Create and activate a virtual env
    virtualenv cdshealpixenv
    source cdshealpixenv/bin/activate
    ### Build the wheels ###
    maturin build --release
    # maturin publish --username <username> --password <password> --repository-url <registry>?
    ### Upload the wheels to PyPI ###
    $PYTHON -m twine upload --repository-url https://upload.pypi.org/legacy/ target/wheels/*.whl --skip-existing
    ### Go back to the native python env
    deactivate
fi
