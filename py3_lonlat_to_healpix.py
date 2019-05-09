import numpy as np
import astropy.units as u
from cdshealpix import cdshealpix
lon = [0, 5, 75] * u.deg
lat = [-20, 5, 20] * u.deg
depth = 12

# Handle the case of an uniq lon, lat tuple given by creating a
# 1d numpy array from the 0d astropy quantities.
lon = np.atleast_1d(lon.to_value(u.rad))
lat = np.atleast_1d(lat.to_value(u.rad))

if depth < 0 or depth > 29:
    raise ValueError("Depth must be between 0 and 29 included")

if lon.shape != lat.shape:
    raise ValueError("The number of longitudes does not match with the number of latitudes given")

num_ipix = lon.shape[0]
# Allocation of the array containing the resulting ipixels
ipix = np.zeros(num_ipix).astype(np.uint64)
cdshealpix.lonlat_to_healpix(depth, lon, lat, ipix)