from cdshealpix import elliptical_cone_search_lonlat
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
import numpy as np

elliptical_cone = elliptical_cone_search_lonlat(
    center=SkyCoord(0, 0, unit="deg", frame="icrs"),
    major_axe=Angle(50, unit="deg"),
    minor_axe=Angle(10, unit="deg"),
    pa=Angle(20, unit="deg"),
    depth=10,
    depth_delta=0
)

#raise Exception("{}".format(elliptical_cone))

from mocpy import MOC, WCS

moc = MOC.from_cells(elliptical_cone)
# Plot the MOC using matplotlib
import matplotlib.pyplot as plt
fig = plt.figure(111, figsize=(10, 10))
# Define a astropy WCS easily
with WCS(fig,
        fov=120 * u.deg,
        center=SkyCoord(0, 0, unit="deg", frame="icrs"),
        coordsys="icrs",
        rotation=Angle(0, u.degree),
        projection="AIT") as wcs:
    ax = fig.add_subplot(1, 1, 1, projection=wcs)
    # Call fill with a matplotlib axe and the `~astropy.wcs.WCS` wcs object.
    moc.fill(ax=ax, wcs=wcs, alpha=0.5, fill=True, color="green")
    # Draw the perimeter of the MOC in black
    moc.border(ax=ax, wcs=wcs, alpha=0.5, color="black")
plt.xlabel('ra')
plt.ylabel('dec')
plt.title('Elliptical cone search')
plt.grid(color="black", linestyle="dotted")
plt.show()
