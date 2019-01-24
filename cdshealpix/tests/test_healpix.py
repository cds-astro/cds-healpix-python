import pytest
import numpy as np

import astropy.units as u

from ..healpix import lonlat_to_healpix_nest, \
 healpix_to_lonlat_nest, \
 healpix_to_skycoord_nest, \
 healpix_vertices_lonlat_nest, \
 healpix_neighbours_nest, \
 cone_search_lonlat_nest, \
 polygon_search_lonlat_nest

def test_lonlat_to_healpix():
    size = 10000
    depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipixels = lonlat_to_healpix_nest(lon=lon, lat=lat, depth=depth)

    npix = 12 * 4**(depth)
    assert(((ipixels >= 0) & (ipixels < npix)).all())

def test_healpix_to_lonlat():
    size = 10000
    depth = 12
    ipixels = np.random.randint(12 * 4 ** (depth), size=size)

    lon, lat = healpix_to_lonlat_nest(ipixels=ipixels, depth=depth)
    assert(lon.shape == lat.shape)

def test_healpix_to_skycoord():
    skycoord = healpix_to_skycoord_nest(ipixels=[0, 2, 4], depth=0)
    assert(skycoord.icrs.ra.shape == skycoord.icrs.dec.shape)

def test_healpix_vertices_lonlat():
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    lon, lat = healpix_vertices_lonlat_nest(ipixels=ipixels, depth=depth)
    assert(lon.shape == lat.shape)
    assert(lon.shape == (size, 4))

def test_healpix_neighbours():
    depth = 0
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    neighbours = healpix_neighbours_nest(ipixels=ipixels, depth=depth)
    assert(neighbours.shape == (size, 9))

    npix = 12 * 4**(depth)
    assert(((neighbours >= -1) & (neighbours < npix)).all())

def test_cone_search_lonlat():
    lon = np.random.rand(1)[0] * 360 * u.deg
    lat = (np.random.rand(1)[0] * 178 - 89) * u.deg
    radius = (np.random.rand(1)[0] * 45) * u.deg
    depth = 12
    
    res = cone_search_lonlat_nest(lon=lon, lat=lat, radius=radius, depth=depth)

    npix = 12 * 4 ** (depth)
    assert(((res["depth"] >= 0) & (res["depth"] <= depth)).all())
    assert(((res["ipix"] >= 0) & (res["ipix"] < npix)).all())

def test_polygon_search_lonlat():
    size = 10
    depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    res = polygon_search_lonlat_nest(lon=lon, lat=lat, depth=depth)

    npix = 12 * 4 ** (depth)
    assert(((res["depth"] >= 0) & (res["depth"] <= depth)).all())
    assert(((res["ipix"] >= 0) & (res["ipix"] < npix)).all())