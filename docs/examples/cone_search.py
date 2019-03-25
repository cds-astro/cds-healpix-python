from cdshealpix import cone_search
import astropy.units as u
ipix, depth, fully_covered = cone_search(lon=0 * u.deg, lat=0 * u.deg, radius=10 * u.deg, depth=10)

from mocpy import MOC, WCS
from astropy.coordinates import SkyCoord, Angle

moc = MOC.from_healpix_cells(ipix, depth, fully_covered)
# Plot the MOC using matplotlib
import matplotlib.pyplot as plt
fig = plt.figure(111, figsize=(10, 10))
# Define a astropy WCS from the mocpy.WCS class
with WCS(fig,
        fov=30 * u.deg,
        center=SkyCoord(0, 0, unit='deg', frame='icrs'),
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
plt.title('Cone search')
plt.grid(color="black", linestyle="dotted")
plt.show()
