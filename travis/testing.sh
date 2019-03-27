#!/bin/bash
# Abort if any simple command returns a non-zero value.
# See https://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

### Run the tests ###
# Download the dependencies for compiling cdshealpix
$PIP install -r requirements.txt
$PIP install pytest setuptools-rust astropy_healpix
# Install Rust compiler
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
export PATH="$HOME/.cargo/bin:$PATH"
# Generate the dynamic library from the cdshealpix Rust crate.
# This will download the crate from crates.io and build it first.
$PYTHON setup.py build_rust
# Move the dynamic lib to the python package folder
find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \;
$PYTHON -m pytest -v cdshealpix/tests/test_healpix.py

# Compile the docs
$PIP install sphinx numpydoc sphinxcontrib-bibtex matplotlib spherical-geometry
# Use of the healpix branch mocpy version (def of from_healpix_cells)
# to run the test examples
$PIP install git+https://github.com/cds-astro/mocpy@healpix
cd ./docs
# Generate the HTML files
make html
# Run the API examples
make doctest
cd ..