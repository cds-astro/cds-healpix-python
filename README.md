# cdshealpix Python package

[![Build Status](https://travis-ci.org/cds-astro/cds-healpix-python.svg?branch=master)](https://travis-ci.org/cds-astro/cds-healpix-python) [![Build status](https://ci.appveyor.com/api/projects/status/obx59vfwehpxf13g/branch/master?svg=true)](https://ci.appveyor.com/project/bmatthieu3/cds-healpix-python/branch/master) [![PyPI version](https://badge.fury.io/py/cdshealpix.svg)](https://badge.fury.io/py/cdshealpix)

This repository contains all the wrapping code for interfacing the [cdshealpix Rust crate](https://github.com/cds-astro/cds-healpix-rust) with Python.

It also performs the deployment of the [cdshealpix](https://pypi.org/project/cdshealpix/) PyPI python package for Linux/MacOS/Windows i686 and x86_64 architectures.
This package is available for Python 2.7/3.4/3.5 (not for windows archs)/3.6 and 3.7.

## [Documentation](https://cds-astro.github.io/cds-healpix-python/)

The documentation of `cdshealpix` is hosted on github and can be accessed through this [link](https://cds-astro.github.io/cds-healpix-python/). You will find:

- A general description of what features `cdshealpix` provides as well as a brief description of what HEALPix is.
- Some examples of code using `mocpy` for plotting the HEALPix cells obtained.
- The API documentation.
- The directives to contribute to the project and its documentation.

## Examples

### HEALPix indices to (lon, lat) astropy quantities

```python
from cdshealpix import healpix_to_lonlat
import numpy as np

ipix = np.array([42, 6, 10])

lon, lat = healpix_to_lonlat(ipix, depth=12)
```

### (lon, lat) astropy quantities to HEALPix indices

```python
from cdshealpix import lonlat_to_healpix
import astropy.units as u

ipix = lonlat_to_healpix(lon=[0, 50, 25] * u.deg, lat=[6, -12, 45] * u.deg, depth=12)
```

### Get the vertices (lon, lat) position from HEALPix indices

```python
from cdshealpix import vertices
import numpy as np

ipix = np.array([42, 6, 10])

lon, lat = vertices(ipix, depth=12)
```

### Get the neighbours from HEALPix indices

```python
from cdshealpix import neighbours
import numpy as np

ipix = np.array([42, 6, 10])

neighbours = neighbours(ipix, depth=12)
```

### Cone search

```python
from cdshealpix import cone_search
import astropy.units as u

# Returns a tuple of three equal sized numpy arrays
# - the first contains the HEALPix cell indices
# - the second contains the HEALPix cell depths
# - the third contains for each HEALPix cell whether it is fully covered by the region (cone, elliptical cone or polygon).
ipix, depth, fully_covered = cone_search(lon=0 * u.deg, lat=0 * u.deg, radius=10 * u.deg, depth=10, delta_depth=2)
```

### Elliptical cone search

```python
from cdshealpix import elliptical_cone_search
import astropy.units as u

# Returns a tuple of three equal sized numpy arrays
# - the first contains the HEALPix cell indices
# - the second contains the HEALPix cell depths
# - the third contains for each HEALPix cell whether it is fully covered by the region (cone, elliptical cone or polygon).
ipix, depth, fully_covered = elliptical_cone_search(lon=0 * u.deg, lat=0 * u.deg, radius=10 * u.deg, depth=10, delta_depth=2)
```

### Polygon search

```python
from cdshealpix import polygon_search
import astropy.units as u
import numpy as np

max_depth = 12
# Generate a triangle
lon = np.random.rand(3) * 360 * u.deg
lat = (np.random.rand(3) * 178 - 89) * u.deg

ipix, depth, fully_covered = polygon_search(lon=lon, lat=lat, depth=max_depth)
```

## Contributing

This section describes how you can contribute to the project. It will require you to install:

- [Rustup](https://www.rust-lang.org/learn/get-started): the Rust installer and version management tool
- [setuptools_rust](https://github.com/PyO3/setuptools-rust) PyPI package
- For running the basic tests: [pytest](https://docs.pytest.org/en/latest/)
- For running the benchmarks: [pytest_benchmark](https://pytest-benchmark.readthedocs.io/en/latest/) [astropy_healpix](https://github.com/astropy/astropy-healpix)

### Compiling the cdshealpix Rust dynamic library

#### Setting up your development environment

If you want to contribute you first must download Rustup:
```shell
curl https://sh.rustup.rs -sSf | sh
```
and follow the installation instructions.

Rustup will allow you to compile the dynamic library for your local architecture. You will then obtain a .so (Linux/MacOS) or a .pyd (Windows) file that can be loaded from python by the CFFI package.

Then you can create a new virtual environment (using the virtualenv package) cdshealpix-env specifying the version of python you need:

```shell
virtualenv -p /usr/bin/python3 cdshealpix-env
```

Activate it: 

```shell
source cdshealpix-env/bin/activate
```

Install all the python dependencies for contributing:

```shell
pip install -r <path_to_cloned_repo>/requirements-dev.txt
```

At this moment you have correctly set up your development environment. When you will be done with your developments, remember to deactivate your environment by typing ```deactivate```.

The next step tells you how to generate the dynamic library associated with `cdshealpix`.

#### Dynamic library compilation

The generation of the dynamic library is managed by [setuptools_rust](https://github.com/PyO3/setuptools-rust). Just go to the root of your cloned repo:

```shell
cd <path_to_cloned_repo>
```

and run this command:

```shell
python setup.py build_rust
```

The generated dynamic library will be located in a build/ folder. Just copy it into the root of the python code.

```shell
cp build/lib/cdshealpix/*.so cdshealpix
```

You do not have to recompile the dynamic library every time if you just work on the python-side code. It is only necessary if you want to update the Rust code located in src/lib.rs.

### Running the tests

For running the tests :

```shell
python -m pytest -v cdshealpix/tests/test_healpix.py
```

For running the benchmarks :

```shell
python -m pytest -v cdshealpix/tests/test_benchmark_healpix.py
```
