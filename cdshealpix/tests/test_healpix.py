import pytest
import numpy as np

from astropy.coordinates import Angle, SkyCoord
import astropy.units as u

from ..healpix import lonlat_to_healpix, \
 healpix_to_lonlat, \
 healpix_to_skycoord, \
 vertices, \
 neighbours, \
 cone_search, \
 polygon_search, \
 elliptical_cone_search

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

    lon, lat = healpix_to_lonlat(ipix=ipixels, depth=depth)
    assert(lon.shape == lat.shape)

def test_healpix_to_skycoord():
    ipix = np.array([0, 2, 4])
    skycoord = healpix_to_skycoord(ipix=ipix, depth=0)
    assert(skycoord.icrs.ra.shape == skycoord.icrs.dec.shape)

def test_healpix_vertices_lonlat():
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    lon, lat = vertices(ipix=ipixels, depth=depth)
    assert(lon.shape == lat.shape)
    assert(lon.shape == (size, 4))

def test_healpix_neighbours():
    depth = 0
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    neigh = neighbours(ipix=ipixels, depth=depth)
    assert(neigh.shape == (size, 9))

    npix = 12 * 4**(depth)
    assert(((neigh >= -1) & (neigh < npix)).all())

def test_cone_search():
    lon = np.random.rand(1)[0] * 360 * u.deg
    lat = (np.random.rand(1)[0] * 178 - 89) * u.deg
    radius = (np.random.rand(1)[0] * 45) * u.deg
    max_depth = 5

    ipix, depth, fully_covered = cone_search(lon=lon, lat=lat, radius=radius, depth=max_depth, flat=True)

    npix = 12 * 4 ** (max_depth)
    assert(((depth >= 0) & (depth <= max_depth)).all())
    assert(((ipix >= 0) & (ipix < npix)).all())

def test_polygon_search():
    size = 3
    max_depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipix, depth, fully_covered = polygon_search(lon=lon, lat=lat, depth=max_depth)

    npix = 12 * 4 ** (max_depth)
    assert(((depth >= 0) & (depth <= max_depth)).all())
    assert(((ipix >= 0) & (ipix < npix)).all())

def test_elliptical_cone_search():
    lon = 0 * u.deg
    lat = 0 * u.deg
    a = Angle(50, unit="deg")
    b = Angle(5, unit="deg")
    pa = Angle(0, unit="deg")
    max_depth = 12

    ipix, depth, fully_covered = elliptical_cone_search(lon, lat, a, b, pa, max_depth)

    npix = 12 * 4 ** (max_depth)
    assert(((depth >= 0) & (depth <= max_depth)).all())
    assert(((ipix >= 0) & (ipix < npix)).all())