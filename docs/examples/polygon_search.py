from cdshealpix import polygon_search_lonlat
import astropy.units as u
import numpy as np

lon = [20, -20, -20, 20] * u.deg
lat = [20, 20, -20, -20] * u.deg

depth = 7
poly = polygon_search_lonlat(lon, lat, depth)

from mocpy import MOC, WCS
from astropy.coordinates import SkyCoord, Angle

moc = MOC.from_cells(poly)
# Plot the MOC using matplotlib
import matplotlib.pyplot as plt
fig = plt.figure(111, figsize=(10, 10))
# Define a astropy WCS easily
with WCS(fig,
        fov=100 * u.deg,
        center=SkyCoord(0, 0, unit='deg', frame='icrs'),
        coordsys="icrs",
        rotation=Angle(0, u.degree),
        projection="AIT") as wcs:
    ax = fig.add_subplot(1, 1, 1, projection=wcs)
    # Call fill with a matplotlib axe and the `~astropy.wcs.WCS` wcs object.
    moc.fill(ax=ax, wcs=wcs, alpha=0.5, fill=True, color="green")
    moc.border(ax=ax, wcs=wcs, alpha=0.5, color="black")
plt.xlabel('ra')
plt.ylabel('dec')
plt.title('Polygon search')
plt.grid(color="black", linestyle="dotted")
plt.show()
