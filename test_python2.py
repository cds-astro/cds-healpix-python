import numpy as np
import astropy.units as u

lon = 45 * u.deg
lat = 5 * u.deg
depth = np.uint8(8)

lon = np.atleast_1d(lon.to_value(u.rad))
lat = np.atleast_1d(lat.to_value(u.rad))

if depth < 0 or depth > 29:
    raise ValueError("Depth must be between 0 and 29 included")

if lon.shape != lat.shape:
    raise ValueError("The number of longitudes does not match with the number of latitudes given")

num_ipixels = lon.shape[0]
# Allocation of the array containing the resulting ipixels
ipixels = np.zeros(num_ipixels, dtype=np.uint64)
print("args:")
print(depth)
print(lon)
print(lat)
print(ipixels)

print(ipixels.dtype)
print(type(depth))
print(lon.dtype)
print(lat.dtype)

from cdshealpix.cdshealpix import lonlat_to_healpix # noqa
lonlat_to_healpix(depth, lon, lat, ipixels)
