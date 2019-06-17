import pytest
import numpy as np

from astropy.coordinates import Angle, SkyCoord
import astropy.units as u

from ..healpix import lonlat_to_healpix, \
 healpix_to_lonlat, \
 healpix_to_xy, \
 lonlat_to_xy, \
 xy_to_lonlat, \
 healpix_to_skycoord, \
 vertices, \
 neighbours, \
 cone_search, \
 polygon_search, \
 elliptical_cone_search, \
 external_neighbours

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

@pytest.mark.parametrize("depth,ipix,expected_border_cells,expected_corner_cells", [
    (0, 0, np.array([90, 91, 94, 95, 26, 27, 30, 31, 53, 55, 61, 63, 69, 71, 77, 79]), np.array([143, -1, 47, -1])),
    (27, 0, np.array(
        [1633305464859699882, 1633305464859699883, 1633305464859699886, 1633305464859699887, 16, 18,
         24, 26, 32, 33, 36, 37, 1248998296657417557, 1248998296657417559, 1248998296657417565, 1248998296657417567]),
        np.array([2594073385365405695, 1633305464859699898, 48, 1248998296657417589]))
])
def test_external_neighbours(depth, ipix, expected_border_cells, expected_corner_cells):
    delta_depth = 2
    ipix_border_cells, ipix_corner_cells = external_neighbours(ipix, depth, delta_depth)
    assert((expected_border_cells == ipix_border_cells).all())
    assert((expected_corner_cells == ipix_corner_cells).all())

@pytest.mark.parametrize("ipix, depth, expected_x, expected_y", [
    (np.arange(12), 0,
     np.array([1., 3., 5., 7., 0., 2., 4., 6., 1., 3., 5., 7.], dtype=np.float64),
     np.array([1., 1., 1., 1., 0., 0., 0., 0., -1., -1., -1., -1.], dtype=np.float64)),
    ([], 0,
     np.array([], dtype=np.float64),
     np.array([], dtype=np.float64)),
    (0, 0,
     np.array([1.], dtype=np.float64),
     np.array([1.], dtype=np.float64))
])
def test_healpix_to_xy(ipix, depth, expected_x, expected_y):
    healpix_to_xy(ipix, depth)
    x, y = healpix_to_xy(ipix, depth)

    assert (x == expected_x).all()
    assert (y == expected_y).all()

def test_healpix_to_xy_expection():
    with pytest.raises(ValueError):
        healpix_to_xy(np.array([]), -5)
    
    with pytest.raises(ValueError):
        healpix_to_xy(np.array([-5]), 12)


def assert_equal_array(first, second, tol=1e-8):
    assert ((first - second) < tol).all()

@pytest.mark.parametrize("lon, lat, expected_x, expected_y", [
    (np.array([0., 0.78539816, 1.57079633]) * u.rad,
     np.array([-0.72972766, 0., 0.72972766]) * u.rad,
     np.array([0., 1., 2.]),
     np.array([-1., 0., 1.]))
])
def test_lonlat_to_xy(lon, lat, expected_x, expected_y):
    x, y = lonlat_to_xy(lon, lat)
    assert_equal_array(x, expected_x)
    assert_equal_array(y, expected_y)

@pytest.mark.parametrize("x, y, expected_lon, expected_lat", [
    (np.array([0., 1., 2.]),
     np.array([-1., 0., 1.]),
     np.array([0., 0.78539816, 1.57079633]) * u.rad,
     np.array([-0.72972766, 0., 0.72972766]) * u.rad)
])
def test_xy_to_lonlat(x, y, expected_lon, expected_lat):
    lon, lat = xy_to_lonlat(x, y)
    assert_equal_array(lon.to_value(u.rad), expected_lon.to_value(u.rad))
    assert_equal_array(lat.to_value(u.rad), expected_lat.to_value(u.rad))