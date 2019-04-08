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

@pytest.mark.parametrize("size", [1, 10, 100, 1000, 10000, 100000, 1000000])
def test_lonlat_to_healpix(size):
    depth = np.random.randint(30)
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipixels = lonlat_to_healpix(lon=lon, lat=lat, depth=depth)
    
    npix = 12 * 4**(depth)
    assert(((ipixels >= 0) & (ipixels < npix)).all())

@pytest.mark.parametrize("size", [1, 10, 100, 1000, 10000, 100000, 1000000])
def test_healpix_to_lonlat(size):
    depth = np.random.randint(30)
    size = 10000
    ipixels = np.random.randint(12 * 4 ** depth, size=size, dtype="uint64")

    lon, lat = healpix_to_lonlat(ipix=ipixels, depth=depth)
    assert(lon.shape == lat.shape)

def test_healpix_to_lonlat_on_brocasted_arrays():
    depth = 12
    x = np.arange(1000000)
    healpix_to_lonlat(ipix=x, depth=depth)
    y = x[::2]
    healpix_to_lonlat(ipix=y, depth=depth)

    z = np.array([1, 2, 3])
    a = np.broadcast_to(z, (10000, 3))
    healpix_to_lonlat(ipix=a, depth=depth)

    b = np.broadcast_to(3, (3, 4, 5))
    healpix_to_lonlat(ipix=b, depth=depth)

def test_invalid_depth_exception():
    size = 10000
    ipix = np.zeros(size)
    with pytest.raises(Exception):
        healpix_to_lonlat(ipix, -2)
    with pytest.raises(Exception):
        healpix_to_lonlat(ipix, 30)
    with pytest.raises(Exception):
        lonlat_to_healpix(0 * u.deg, 0 * u.deg, -2)
    with pytest.raises(Exception):
        vertices(ipix, -2)
    with pytest.raises(Exception):
        neighbours(ipix, -2)
    with pytest.raises(Exception):
        cone_search(0 * u.deg, 0 * u.deg, 15 * u.deg, -2)

def test_lonlat_shape_exception():
    lon = [2, 5] * u.deg
    lat = [5] * u.deg
    
    with pytest.raises(Exception):
        lonlat_to_healpix(lon, lat, 12)

@pytest.mark.parametrize("depth", [0, 12, 24])
def test_invalid_ipix_exception(depth):
    npix = 12 * 4 ** depth
    invalid_ipix1 = np.array([-20, 0, 11])
    invalid_ipix2 = np.array([0, npix + 1, 11])
    with pytest.raises(Exception):
        healpix_to_lonlat(invalid_ipix1, depth)
    with pytest.raises(Exception):
        healpix_to_lonlat(invalid_ipix2, depth)
    with pytest.raises(Exception):
        vertices(invalid_ipix1, depth)
    with pytest.raises(Exception):
        neighbours(invalid_ipix1, depth)

def test_healpix_to_skycoord():
    ipix = np.array([0, 2, 4])
    skycoord = healpix_to_skycoord(ipix=ipix, depth=0)
    assert(skycoord.icrs.ra.shape == skycoord.icrs.dec.shape)

def test_vertices_lonlat():
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4 ** depth, size=size)

    lon, lat = vertices(ipix=ipixels, depth=depth)
    assert(lon.shape == lat.shape)
    assert(lon.shape == (size, 4))

def test_neighbours():
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

    with pytest.raises(Exception):
        cone_search([5, 4] * u.deg, [5, 4] * u.deg, 15 * u.deg, 12)

@pytest.mark.parametrize("size", [0, 1, 2, 3, 5, 6, 9])
def test_polygon_search(size):
    max_depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    if size < 3:
        with pytest.raises(Exception):
            polygon_search(lon=lon, lat=lat, depth=max_depth)
    else:
        ipix, depth, fully_covered = polygon_search(lon=lon, lat=lat, depth=max_depth)

        npix = 12 * 4 ** (max_depth)
        assert(((depth >= 0) & (depth <= max_depth)).all())
        assert(((ipix >= 0) & (ipix < npix)).all())

def test_polygon_search_not_enough_vertices_exception():
    # 4 total vertices but only 2 distincts. This should fail
    with pytest.raises(Exception):
        polygon_search([1, 1, 2, 1] * u.deg, [1, 1, 3, 1] * u.deg, depth=12)
    
    # 4 total vertices and 3 distincts. This should pass
    polygon_search([1, 1, 2, 1] * u.deg, [1, 1, 3, 2] * u.deg, depth=12)

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