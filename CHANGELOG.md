# `cdshealpix-python` Change Log

## 0.6.1

Released 2021-11-08

### Chnages

* Based on cds-healpix-rust v0.5.5


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


