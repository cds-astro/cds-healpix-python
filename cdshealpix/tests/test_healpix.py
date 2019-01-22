import pytest
import astropy.units as u
import numpy as np
from astropy_healpix.core import lonlat_to_healpix

from ..healpix import healpix_from_lonlat, \
 healpix_center_lonlat, \
 healpix_center_skycoord, \
 healpix_vertices_lonlat, \
 healpix_vertices_skycoord, \
 healpix_neighbours

def test_healpix_from_lonlat():
    size = 1000000
    lon = np.random.rand(size) * 360 * u.deg
    #     lat = [0, 54, 9, 32, 49, 21, 0] * u.deg
    lat = (np.random.rand(size) * 180 - 90) * u.deg
    depth = 12
    healpix_from_lonlat(lon=lon, lat=lat, depth=depth)
    lonlat_to_healpix(lon=lon, lat=lat, nside=(1 << depth), order='nested')
    print('\n')
    from datetime import datetime
    t0 = datetime.now()
    ipixels = healpix_from_lonlat(lon=lon, lat=lat, depth=depth)
    d1 = datetime.now() - t0
    print('cdshealpix: ', d1)
    print(ipixels)

    t1 = datetime.now()
    ipixels2 = lonlat_to_healpix(lon=lon, lat=lat, nside=(1 << depth), order='nested')
    d2 = datetime.now() - t1
    print('astropy_healpix: ', d2)
    print(ipixels2)

    print('speedup factor: ', d2 / d1)

def test_healpix_center_lonlat():
    lon, lat = healpix_center_lonlat(ipixels=[0, 2, 4], depth=0)

def test_healpix_center_skycoord():
    skycoord = healpix_center_skycoord(ipixels=[0, 2, 4], depth=0)

#TODO: see a cleaner method for performing benchmarks
def test_healpix_vertices_lonlat():
    depth = 0
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)
    print(ipixels)

    print('\n')
    from datetime import datetime
    t0 = datetime.now()
    lon, lat = healpix_vertices_lonlat(ipixels=ipixels, depth=depth)
    d1 = datetime.now() - t0
    print('cdshealpix: ', d1)

    from astropy_healpix.core import boundaries_lonlat
    t1 = datetime.now()
    lon2, lat2 = boundaries_lonlat(ipixels, nside=(1 << depth), step=1, order='nested')
    d2 = datetime.now() - t1
    print('astropy_healpix: ', d2)

def test_healpix_neighbours():
    print(healpix_neighbours([0, 6], depth=0))