#!/bin/sh
#
# Build and test cdshealpix in a 32-bit environment with python2
#
# Usage:
#   testing_py3_ubuntu32.sh
#

# Update packages to the latest available versions
linux32 --32bit i386 sh -c '
    apt update > /dev/null &&
    apt install -y build-essential libcurl4-openssl-dev libssl-dev \
	libexpat-dev gettext python3 python3-pip >/dev/null &&
    ln -s /usr/bin/python3 /usr/bin/python
' &&

# Run the tests
linux32 --32bit i386 sh -c '
    # Download the dependencies for compiling cdshealpix
    pip3 install -r requirements.txt &&
    pip3 install maturin pytest_benchmark
    # Install Rust compiler
    curl --proto \'=https\' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain nightly -y &&
    export PATH="$HOME/.cargo/bin:$PATH" &&
    # Generate the dynamic library from the cdshealpix Rust crate.
    maturin develop --release &&
    python3 -m pytest -v cdshealpix/tests/test_nested_healpix.py &&
    python3 -m pytest -v cdshealpix/tests/test_ring_healpix.py
'
