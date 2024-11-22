# `cdshealpix-python` Change Log

## Unreleased

## 0.7.1

### Added

* support for python 3.13
### Fixed

* fix ``zone_search`` that would fail on lon_max == 180° due to astropy angle wrapping

## 0.7.0

### Added

* new features `box_search` and `zone_search` in `cdshealpix.nested`
* `cdshaelpix.nested.vertices` can now take depth as a `numpy.ndarray` instead of only
  accepting a single depth
* new module `skymap` added.
* read/write, and plot nested all-sky skymaps in the implicit scheme from fits files with
  `Skymap.from_fits`, `Skymap.from_array`, `Skymap.quick_plot`, and `Skymap.to_fits`

### Fixed

* :warning: breaking change. All `fully_covered` returned values have changed from arrays
  of 0 and 255 to boolean arrays. This concerns: `box_search`, `cone_search`,
  `polygon_search`, `elliptical_cone_search`, and `elliptic-search`.
* bilinear_interpolation now accepts longitudes and latitudes with nan values
  (will be a masked value in the output) [#22]
* `nested.healpix_to_lonlat`, failed into rust panic for `dx=1` or `dy=1`. This is
  now indicated in the documentation and is catched in a `ValueError` on the python side.

### Changed

* `matplotlib` is now an optional dependency, to plot previews of skymaps.

## 0.6.5

Released 2023-11-28

### Changed

* supported python versions are now from 3.8 to 3.12. For python 3.8, the astropy dependency is fixed to <5.3.
This will prevent from using new functionalities of astropy until python 3.8 end of life. [#18]
* the documentation now have a section for notebooks in the examples [#19]

## 0.6.4

Released 2023-02-27

This release is mostly documentation and CI improvements

### Changes

* docstring update for ``bilinear_interpolation`` to highlight counter-intuitive use of False and True in ``np.mask``.
* new extended example in documentation for coordinate system rotation using the pixel method
* adopted black codestyle
* BUGFIX : ``from_ring`` doctring example is fixed

### Fix

* Support for Mac M1 processor due to [maturin bug](https://github.com/PyO3/maturin/issues/1207) during last release.


--------------------------------------------------------------------------------

## 0.6.3

Released 2022-10-20

### Changes

* Project layout change ["to avoid the a common ImportError pitfall"](https://github.com/PyO3/maturin#mixed-rustpython-projects)
* Re-introduce support for Python 3.7 ["https://endoflife.date/python"](https://endoflife.date/python)
* Relax astropy contrain (remove numpy since already a dependency of astropy)
* Update ci

--------------------------------------------------------------------------------

## 0.6.2 - Not in conda - Yanked on pypi

Released 2022-10-17

### Changes

* Tests for Longitude and Latitude in  `bilinear_interpolation`
* Remove support for Python <= 3.7 ["https://endoflife.date/python"](https://endoflife.date/python)
* Update dependencies
  * update cds-healpix-rust to v0.6
  * ...

--------------------------------------------------------------------------------

## 0.6.1

Released 2021-11-09

### Changes

* Update cds-healpix-rust to v0.5.5
* Update pyO3 dependencies (replace deprecated methods)

## 0.6.0

Released 2021-03-11

### API changes

* Coordinates inputs/outputs switched from `astropy.units.Quantity` to `astropy.coordinates.Longitude/Latitude`
* Remove automatic transformation of nan by 0 in `bilinear_interpolation`

--------------------------------------------------------------------------------

## 0.5.5

Released 2021-03-09

### Modified

* Remove the need for Rust nightly
* Replace appveyor and travis by github actions
* Replace manylinux1 support by manilinux2014
* Drop support for Windows 32bit
* Drop support for Python <=3.5

--------------------------------------------------------------------------------
