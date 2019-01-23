import pytest
import numpy as np

import astropy.units as u

from ..healpix import lonlat_to_healpix, \
 healpix_to_lonlat, \
 healpix_to_skycoord, \
 healpix_vertices_lonlat, \
 healpix_neighbours

def test_lonlat_to_healpix():
    size = 10000
    depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipixels = lonlat_to_healpix(lon=lon, lat=lat, depth=depth)

    npix = 12 * 4**(depth)
    assert(((ipixels >= 0) & (ipixels < npix)).all())

def test_healpix_to_lonlat():
    size = 10000
    depth = 12
    ipixels = np.random.randint(12 * 4 ** (depth), size=size)

    lon, lat = healpix_to_lonlat(ipixels=ipixels, depth=depth)
    assert(lon.shape == lat.shape)

def test_healpix_to_skycoord():
    skycoord = healpix_to_skycoord(ipixels=[0, 2, 4], depth=0)
    assert(skycoord.icrs.ra.shape == skycoord.icrs.dec.shape)

def test_healpix_vertices_lonlat():
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    lon, lat = healpix_vertices_lonlat(ipixels=ipixels, depth=depth)
    assert(lon.shape == lat.shape)
    assert(lon.shape == (size, 4))

def test_healpix_neighbours():
    depth = 0
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    neighbours = healpix_neighbours(ipixels=ipixels, depth=depth)
    assert(neighbours.shape == (size, 9))

    npix = 12 * 4**(depth)
    assert(((neighbours >= -1) & (neighbours < npix)).all())