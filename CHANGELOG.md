# `cdshealpix-python` Change Log

## 0.6.2

Released 2022-10-17

### Changes

* Tests for Longitude and Latitude in  `bilinear_interpolation`
* Remove support for Python 3.6 (https://endoflife.date/python)
* Update dependencies
    + update cds-healpix-rust to v0.6
    + ...

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


