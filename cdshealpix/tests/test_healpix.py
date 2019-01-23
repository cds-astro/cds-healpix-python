import pytest
import numpy as np

import astropy.units as u

from ..healpix import lonlat_to_healpix, \
 healpix_to_lonlat, \
 healpix_to_skycoord, \
 healpix_vertices_lonlat, \
 healpix_neighbours, \
 cone_search_lonlat, \
 polygon_search_lonlat

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

def test_cone_search_lonlat():
    lon = np.random.rand(1)[0] * 360 * u.deg
    lat = (np.random.rand(1)[0] * 178 - 89) * u.deg
    radius = (np.random.rand(1)[0] * 45) * u.deg
    depth = 12
    
    cone_ipix, cone_depth = cone_search_lonlat(lon=lon, lat=lat, radius=radius, depth=depth)

    npix = 12 * 4 ** (depth)
    assert(((cone_depth >= 0) & (cone_depth <= depth)).all())
    assert(((cone_ipix >= 0) & (cone_ipix < npix)).all())

def test_polygon_search_lonlat():
    size = 10
    depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    poly_ipix, poly_depth = polygon_search_lonlat(lon=lon, lat=lat, depth=depth)

    npix = 12 * 4 ** (depth)
    assert(((poly_depth >= 0) & (poly_depth <= depth)).all())
    assert(((poly_ipix >= 0) & (poly_ipix < npix)).all())