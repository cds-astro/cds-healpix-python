# cdshealpix Python package

[![Build Status](https://travis-ci.org/cds-astro/cds-healpix-python.svg?branch=master)](https://travis-ci.org/cds-astro/cds-healpix-python) [![Build status](https://ci.appveyor.com/api/projects/status/obx59vfwehpxf13g/branch/master?svg=true)](https://ci.appveyor.com/project/bmatthieu3/cds-healpix-python/branch/master) [![PyPI version](https://badge.fury.io/py/cdshealpix.svg)](https://badge.fury.io/py/cdshealpix)

This repository contains all the wrapping code for interfacing the cdshealpix Rust crate with Python.

It also performs the deployment of the [cdshealpix](https://pypi.org/project/cdshealpix/) PyPI python package for Linux/MacOS/Windows i686 and x86_64 architectures.
This package is available for Python 2.7/3.4/3.5/3.6 and 3.7.

## Examples

### HEALPix indices to (lon, lat) astropy quantities

```python
from cdshealpix import healpix_to_lonlat_nest
import numpy as np

ipixels = np.array([42, 6, 10])

lon, lat = healpix_to_lonlat_nest(ipixels=ipixels, depth=12)
```

### (lon, lat) astropy quantities to HEALPix indices

```python
from cdshealpix import lonlat_to_healpix_nest
import astropy.units as u

ipixels = lonlat_to_healpix_nest(lon=[0, 50, 25] * u.deg, lat=[6, -12, 45] * u.deg, depth=12)
```

## Contributing

This section describes how you can contribute to the project. It will require you to install:

- [Rustup](https://www.rust-lang.org/learn/get-started): the Rust installer and version management tool.
- [setuptools_rust](https://github.com/PyO3/setuptools-rust) PyPI package
- For running the basic tests: [pytest](https://docs.pytest.org/en/latest/)
- For running the benchmarks: [pytest_benchmark](https://pytest-benchmark.readthedocs.io/en/latest/) [astropy_healpix](https://github.com/astropy/astropy-healpix), [healpy](https://github.com/healpy/healpy)

### Compiling the cdshealpix Rust dynamic library

#### Setting up your development environment

If you want to contribute you first must download Rustup:
```shell
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
```


Rustup will allow you to compile the dynamic library for your local architecture. You will then obtain a .so (Linux/MacOS) or a .pyd (Windows) file that can be loaded from python by the CFFI package.

Then you can create a new virtual environment cdshealpix-env specifying the version of python you need:

```shell
virtualenv -p /usr/bin/python3 cdshealpix-env
```

Activate it: 

```shell
source cdshealpix/bin/activate
```

Install all the python dependencies for contributing:

```shell
pip install -r <path_to_cloned_repo>/requirements-dev.txt
```

At this moment you have correctly set up your development environment. You can develop and launch tests/benchmarks in it. When you will be done, you can deactivate it by typing ```deactivate```.

The next step tells you how to generate the dynamic library associated with `cdshealpix`.

#### Dynamic library compilation

The generation of the dynamic library is managed by [setuptools_rust](https://github.com/PyO3/setuptools-rust). Just run this command in the root of your cloned repo.

```shell
python setup.py build_rust
```

The generated dynamic library will be located in a build/ folder. Just copy it into the root of the python code.

```shell
cp build/lib/cdshealpix/*.so cdshealpix
```

You do not have to recompile the dynamic library every time if you just work on the python wrapping code. It is only necessary if you want to update the rust wrapping code located in src/lib.rs.

### Running the tests

For running the tests :

```shell
python -m pytest -v cdshealpix/tests/test_healpix.py
```

For running the benchmarks :

```shell
python -m pytest -v cdshealpix/tests/test_benchmark_healpix.py
```
