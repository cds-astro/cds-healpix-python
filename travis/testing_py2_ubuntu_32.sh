#!/bin/sh
#
# Build and test cdshealpix in a 32-bit environment with python2
#
# Usage:
#   testing_py2_ubuntu32.sh
#

# Update packages to the latest available versions
linux32 --32bit i386 sh -c '
    apt update > /dev/null &&
    apt install -y build-essential libcurl4-openssl-dev libssl-dev \
	libexpat-dev gettext python python-pip >/dev/null
' &&

# Run the tests
linux32 --32bit i386 sh -c '
    # Upgrade pip
    pip2 install pip --upgrade &&
    # Download the dependencies for compiling cdshealpix
    pip2 install astropy==2.0.12 &&
    pip2 install -r requirements.txt &&
    pip2 install pytest setuptools-rust astropy_healpix &&
    # uninstall more-itertools and re-install version 5.0.0
    pip2 uninstall -y more-itertools &&
    pip2 install more-itertools==5.0.0 &&
    # Install Rust compiler
    curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y &&
    export PATH="$HOME/.cargo/bin:$PATH" &&
    # Generate the dynamic library from the cdshealpix Rust crate.
    # This will download the crate from crates.io and build it first.
    python2 setup.py build_rust &&
    # Move the dynamic lib to the python package folder
    find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \; &&
    python2 -m pytest -v cdshealpix/tests/test_healpix.py
'
