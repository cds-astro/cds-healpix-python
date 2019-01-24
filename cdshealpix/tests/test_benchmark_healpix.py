import pytest
import astropy.units as u
import numpy as np
import astropy_healpix

from ..healpix import lonlat_to_healpix_nest, \
 healpix_to_lonlat_nest, \
 healpix_to_skycoord_nest, \
 healpix_vertices_lonlat_nest, \
 healpix_neighbours_nest, \
 cone_search_lonlat_nest

@pytest.mark.benchmark(group="lonlat_to_healpix")
def test_lonlat_to_healpix(benchmark):
    size = 10000
    depth = 12
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipixels = benchmark(lonlat_to_healpix_nest, lon=lon, lat=lat, depth=depth)

@pytest.mark.benchmark(group="lonlat_to_healpix")
def test_lonlat_to_healpix_astropy(benchmark):
    size = 10000
    depth = 12
    nside = 1 << depth
    lon = np.random.rand(size) * 360 * u.deg
    lat = (np.random.rand(size) * 178 - 89) * u.deg

    ipixels = benchmark(astropy_healpix.core.lonlat_to_healpix, lon=lon, lat=lat, nside=nside, order='nested')

@pytest.mark.benchmark(group="healpix_to_lonlat")
def test_healpix_to_lonlat(benchmark):
    size = 10000
    depth = 12
    ipixels = np.random.randint(12 * 4 ** (depth), size=size)

    lon, lat = benchmark(healpix_to_lonlat_nest, ipixels=ipixels, depth=depth)

@pytest.mark.benchmark(group="healpix_to_lonlat")
def test_healpix_to_lonlat_astropy(benchmark):
    size = 10000
    depth = 12
    nside = 1 << depth
    ipixels = np.random.randint(12 * 4 ** (depth), size=size)

    lon, lat = benchmark(astropy_healpix.core.healpix_to_lonlat, healpix_index=ipixels, nside=nside, order='nested')

def test_healpix_to_skycoord():
    skycoord = healpix_to_skycoord_nest(ipixels=[0, 2, 4], depth=0)

@pytest.mark.benchmark(group="healpix_vertices_lonlat")
def test_healpix_vertices_lonlat(benchmark):
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    lon, lat = benchmark(healpix_vertices_lonlat_nest, ipixels=ipixels, depth=depth)

@pytest.mark.benchmark(group="healpix_vertices_lonlat")
def test_healpix_vertices_lonlat_astropy(benchmark):
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    lon2, lat2 = benchmark(astropy_healpix.core.boundaries_lonlat, healpix_index=ipixels, nside=(1 << depth), step=1, order='nested')

@pytest.mark.benchmark(group="healpix_neighbours")
def test_healpix_neighbours(benchmark):
    depth = 12
    size = 100000
    ipixels = np.random.randint(12 * 4**(depth), size=size)

    neighbours = benchmark(healpix_neighbours_nest, ipixels=ipixels, depth=depth)


lon_c = np.random.rand(1)[0] * 360 * u.deg
lat_c = (np.random.rand(1)[0] * 178 - 89) * u.deg
radius_c = np.random.rand(1)[0] * 45 * u.deg
depth_c = 5

@pytest.mark.benchmark(group="cone_search")
def test_cone_search(benchmark):
    ipix, depth = benchmark(cone_search_lonlat_nest, lon=lon_c, lat=lat_c, radius=radius_c, depth=depth_c)

@pytest.mark.benchmark(group="cone_search")
def test_cone_search_astropy(benchmark):
    nside = 1 << depth_c

    res = benchmark(astropy_healpix.core.healpix_cone_search, lon=lon_c, lat=lat_c, radius=radius_c, nside=nside, order="nested")