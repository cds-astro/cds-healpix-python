#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

### Run the tests ###
# Download the dependencies for compiling cdshealpix
$PIP install -r requirements-dev.txt
# Install Rust compiler
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain nightly -y
export PATH="$HOME/.cargo/bin:$PATH"
# Generate the dynamic library from the cdshealpix Rust crate.
maturin develop --release
$PYTHON -m pytest -v -s cdshealpix/tests/test_nested_healpix.py
$PYTHON -m pytest -v -s cdshealpix/tests/test_ring_healpix.py

