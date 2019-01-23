from . import C, ffi

import astropy.units as u
from astropy.coordinates import SkyCoord
import numpy as np

def lonlat_to_healpix(lon, lat, depth):
    # Handle the case of an uniq lon, lat tuple given by creating a
    # 1d numpy array from the 0d astropy quantities.
    lon = np.atleast_1d(lon.to_value(u.rad)).ravel()
    lat = np.atleast_1d(lat.to_value(u.rad)).ravel()

    if lon.shape[0] != lat.shape[0]:
        raise IndexError("The number of longitudes does not match with the number of latitudes given")
    
    num_ipixels = lon.shape[0]
    # Allocation of the array containing the resulting ipixels
    ipixels = np.zeros(num_ipixels, dtype=np.uint64)

    C.hpx_hash_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # lon, lat
        ffi.cast("const double*", lon.ctypes.data),
        ffi.cast("const double*", lat.ctypes.data),
        # result
        ffi.cast("uint64_t*", ipixels.ctypes.data)
    )

    return ipixels

def healpix_to_lonlat(ipixels, depth):
    ipixels = np.atleast_1d(ipixels).ravel()
    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the resulting coordinates
    lonlat = np.zeros(num_ipixels << 1, dtype=np.float64)

    C.hpx_center_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("double*", lonlat.ctypes.data)
    )

    lonlat = lonlat.reshape((-1, 2)) * u.rad
    lon, lat = lonlat[:, 0], lonlat[:, 1]

    return lon, lat

def healpix_to_skycoord(ipixels, depth):
    lon, lat = healpix_to_lonlat(ipixels, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def healpix_vertices_lonlat(ipixels, depth):
    ipixels = np.atleast_1d(ipixels).ravel()
    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the resulting coordinates
    lonlat = np.zeros(num_ipixels << 3, dtype=np.float64)

    C.hpx_vertices_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("double*", lonlat.ctypes.data)
    )

    lonlat = lonlat.reshape((-1, 4, 2)) * u.rad
    lon, lat = lonlat[:, :, 0], lonlat[:, :, 1]

    return lon, lat

def healpix_vertices_skycoord(ipixels, depth):
    lon, lat = healpix_vertices_lonlat(ipixels, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def healpix_neighbours(ipixels, depth):
    ipixels = np.atleast_1d(ipixels).ravel()
    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the neighbours
    neighbours = np.zeros(num_ipixels * 9, dtype=np.int64)
    
    C.hpx_neighbours(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("int64_t*", neighbours.ctypes.data)
    )

    neighbours = neighbours.reshape((-1, 9))

    return neighbours
