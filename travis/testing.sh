#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

### Run the tests ###
# Download the dependencies for compiling cdshealpix
$PIP install -r requirements-dev.txt
# Install Rust compiler
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
export PATH="$HOME/.cargo/bin:$PATH"
# Generate the dynamic library from the cdshealpix Rust crate.
# This will download the crate from crates.io and build it first.
$PYTHON setup.py build_rust
# Move the dynamic lib to the python package folder
find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \;
$PYTHON -m pytest -v -s cdshealpix/tests/test_nested_healpix.py
$PYTHON -m pytest -v -s cdshealpix/tests/test_ring_healpix.py

