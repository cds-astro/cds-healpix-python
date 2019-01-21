from . import C, ffi

import astropy.units as u
import numpy as np

def healpix_from_lonlat(lon, lat, depth):
    # Handle the case of an uniq lon, lat tuple given by creating a
    # 1d numpy array from the 0d astropy quantities.
    lon = np.atleast_1d(lon.to_value(u.rad)).ravel()
    lat = np.atleast_1d(lat.to_value(u.rad)).ravel()

    print("dtype", lon.dtype)

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
        ffi.cast("double*", lon.ctypes.data),
        ffi.cast("double*", lat.ctypes.data),
        # result
        ffi.cast("uint64_t*", ipixels.ctypes.data)
    )

    return ipixels