# CDSHealpix

[![Build Status](https://travis-ci.org/cds-astro/cds-healpix-python.svg?branch=master)](https://travis-ci.org/cds-astro/cds-healpix-python)
[![Build status](https://ci.appveyor.com/api/projects/status/obx59vfwehpxf13g/branch/master?svg=true)](https://ci.appveyor.com/project/bmatthieu3/cds-healpix-python/branch/master)
[![PyPI version](https://badge.fury.io/py/cdshealpix.svg)](https://badge.fury.io/py/cdshealpix)
[![Documentation](https://img.shields.io/badge/Documentation-link-green.svg)](https://cds-astro.github.io/cds-healpix-python/)

This is a BSD-licensed HEALPix package which is wrapped around the [cdshealpix Rust crate](https://github.com/cds-astro/cds-healpix-rust).

[cdshealpix](https://pypi.org/project/cdshealpix/) is multi-platform and is currently deployed on PyPI for i686 and x86_64 archs.

It is compatible with Python 3.5 to 3.8.

```bash
pip install cdshealpix
```

# Features

* [Nested and Ring HEALPix notation](https://cds-astro.github.io/cds-healpix-python/api.html#cdshealpix) supported
* [Cone search](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.cone_search.html#cdshealpix.nested.cone_search)
* [Elliptical-Cone search](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.elliptical_cone_search.html#cdshealpix.nested.elliptical_cone_search)
* [Polygon search](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.polygon_search.html#cdshealpix.nested.polygon_search)
* [Bilinear interpolation](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.bilinear_interpolation.html#cdshealpix.nested.bilinear_interpolation)
* [lonlat_to_healpix](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.lonlat_to_healpix.html#cdshealpix.nested.lonlat_to_healpix) and [healpix_to_lonlat](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.healpix_to_lonlat.html#cdshealpix.nested.healpix_to_lonlat) supports numpy broadcasting
* Rust allows easy concurrency. A ``num_threads`` optional parameter can be used to allow parallelism. By default, concurrency is disabled.
* Get the [world vertices corresponding to an HEALPix cell](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.vertices.html#cdshealpix.nested.vertices)
* Get the [neighbours of an HEALPix cell](https://cds-astro.github.io/cds-healpix-python/stubs/cdshealpix.nested.neighbours.html#cdshealpix.nested.neighbours)

# Documentation

Here is the link to the [documentation](https://cds-astro.github.io/cds-healpix-python/) for informations about how to use this package.

