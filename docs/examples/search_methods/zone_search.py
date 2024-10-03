"""Get the HEALPix cells in a zone, and plot all of them as matplotlib polygons."""

from cdshealpix.nested import zone_search, vertices

from astropy.coordinates import Longitude, Latitude

import astropy.units as u
import numpy as np
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt

lon_min = Longitude(-10 * u.deg)
lat_min = Latitude(10 * u.deg)
lon_max = Longitude(60 * u.deg)
lat_max = Latitude(60 * u.deg)

ipix, depth, _ = zone_search(lon_min, lat_min, lon_max, lat_max, depth=4)

n_cells = len(ipix)

lons, lats = vertices(ipix, depth, step=4)

lons = lons.wrap_at(180 * u.deg).radian
lats = lats.radian

path_polygons = np.array([np.column_stack((lon, lat)) for lon, lat in zip(lons, lats)])

polygons = PolyCollection(path_polygons)

fig = plt.figure()
ax = fig.add_subplot(projection="aitoff")
ax.grid(visible=True)
ax.add_collection(polygons)

plt.show()
