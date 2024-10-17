"""Plot a cell and its center."""

from cdshealpix.nested import healpix_to_lonlat, vertices

import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

# choose a cell
ipix = 5
depth = 0

fig = plt.figure()
ax = fig.add_subplot(projection="aitoff")
ax.grid(visible=True)
# plot the center of the cell
lon, lat = healpix_to_lonlat(ipix, depth)
ax.scatter(lon, lat, color="purple")
# plot the cell
border_lon, border_lat = vertices(ipix, depth, step=5)
border_lon = border_lon.wrap_at(180 * u.deg).radian[0]
border_lat = border_lat.radian[0]
polygon = Polygon(
    np.column_stack((border_lon, border_lat)), fill=False, edgecolor="green", hatch="\\"
)
ax.add_patch(polygon)
plt.show()
