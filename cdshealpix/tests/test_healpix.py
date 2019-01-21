import pytest
import astropy.units as u

from ..healpix import healpix_from_lonlat

def test_healpix_from_lonlat():
    lon = [0, 0] * u.deg
    lat = [0, 54] * u.deg
    
    ipixels = healpix_from_lonlat(lon=lon, lat=lat, depth=0)