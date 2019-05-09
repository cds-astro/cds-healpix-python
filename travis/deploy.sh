#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

if [[ $TRAVIS_TAG ]]; then
    # Build and deploy if the tests pass and
    # the commit is tagged
    ### Build the wheels ###
    $PIP install cibuildwheel setuptools-rust
    export CIBW_BEFORE_BUILD="pip install setuptools-rust && curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y"
    export CIBW_ENVIRONMENT='PATH="$HOME/.cargo/bin:$PATH"'
    cibuildwheel --output-dir dist
    ### Upload the wheels to PyPI ###
    $PIP install twine
    $PYTHON -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*.whl --skip-existing
fi
