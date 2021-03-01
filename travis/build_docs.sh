#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

### Run the tests ###
# Download the dependencies for compiling cdshealpix
# and building its documentation
$PIP install -r requirements-dev.txt
# Install Rust compiler
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"
### Install virtualenv, maturin and twine
$PIP install virtualenv
### Create and activate a virtual env
virtualenv cdshealpixenv
source cdshealpixenv/bin/activate
### Install maturin and twine
pip install maturin twine
# Generate the dynamic library from the cdshealpix Rust crate.
maturin develop --release
# Compile the docs
# to run the test examples
cd ./docs
# Generate the HTML files
make html
# Run the API test examples
make doctest
cd ..
deactivate

