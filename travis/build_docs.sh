#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

### Run the tests ###
# Download the dependencies for compiling cdshealpix
# and building its documentation
$PIP install -r requirements-dev.txt
# Install Rust compiler
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
export PATH="$HOME/.cargo/bin:$PATH"
# Generate the dynamic library from the cdshealpix Rust crate.
# This will download the crate from crates.io and build it first.
$PYTHON setup.py build_rust
# Move the dynamic lib to the python package folder
find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \;

# Compile the docs
# to run the test examples
cd ./docs
# Generate the HTML files
make html
# Run the API test examples
make doctest
cd ..
