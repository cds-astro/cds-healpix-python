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
    apt install -y build-essential libfreetype6-dev libpng12-dev pkg-config libcurl4-openssl-dev libssl-dev \
	libexpat-dev gettext python3 python3-pip >/dev/null &&
    ln -s /usr/bin/python3 /usr/bin/python
' &&

# Run the tests
linux32 --32bit i386 sh -c '
    # Download the dependencies for compiling cdshealpix
    pip3 install -r requirements.txt &&
    pip3 install pytest setuptools-rust astropy_healpix && 
    # Install Rust compiler
    curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y &&
    export PATH="$HOME/.cargo/bin:$PATH" &&
    # Generate the dynamic library from the cdshealpix Rust crate.
    # This will download the crate from crates.io and build it first.
    python3 setup.py build_rust &&
    # Move the dynamic lib to the python package folder
    find build/ -name "*.so" -type f -exec cp {} ./cdshealpix \; &&
    python3 -m pytest -v cdshealpix/tests/test_healpix.py
' &&

# Build and test the docs
linux32 --32bit i386 sh -c '
    # Compile the docs
    pip3 install sphinx numpydoc sphinxcontrib-bibtex matplotlib spherical-geometry &&
    # Use of the healpix branch mocpy version (def of from_healpix_cells)
    # to run the test examples
    pip3 install git+https://github.com/cds-astro/mocpy@healpix &&
    cd ./docs &&
    # Generate the HTML files
    make html &&
    # Run the API examples
    make doctest &&
    cd ..
'