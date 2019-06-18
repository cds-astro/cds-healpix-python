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
    pip3 install setuptools_rust pytest_benchmark
    # Install Rust compiler
    curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y &&
    export PATH="$HOME/.cargo/bin:$PATH" &&
    # Generate the dynamic library from the cdshealpix Rust crate.
    # This will download the crate from crates.io and build it first.
    python3 setup.py build_rust &&
    # Move the dynamic lib to the python package folder
    find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \; &&
    python3 -m pytest -v cdshealpix/tests/test_nested_healpix.py
    # python3 -m pytest -v cdshealpix/tests/test_ring_healpix.py
'
