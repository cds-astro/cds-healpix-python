import pytest
import astropy.units as u

from ..healpix import healpix_from_lonlat, \
 healpix_center_lonlat, \
 healpix_center_skycoord

def test_healpix_from_lonlat():
    lon = [0, 0] * u.deg
    lat = [0, 54] * u.deg
    
    ipixels = healpix_from_lonlat(lon=lon, lat=lat, depth=0)

def test_healpix_center_lonlat():
    lon, lat = healpix_center_lonlat(ipixels=[0, 2, 4], depth=0)

def test_healpix_center_skycoord():
    skycoord = healpix_center_skycoord(ipixels=[0, 2, 4], depth=0)