#!/bin/bash

### Run the tests ###
# Download the dependencies for compiling cdshealpix
$PIP install -r requirements.txt
$PIP install pytest setuptools-rust
# Install Rust compiler
curl https://sh.rustup.rs -sSf | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"
# Generate the dynamic library from the cdshealpix Rust crate.
# This will download the crate from crates.io and build it first.
$PYTHON setup.py build_rust
# Move the dynamic lib to the python package folder
find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \;
$PYTHON -m pytest -v cdshealpix/tests/test_healpix.py