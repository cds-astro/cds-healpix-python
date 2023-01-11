"""Illustration of the elliptical cone search functionnality."""

# Astropy tools
import astropy.units as u

# For plots
import matplotlib.pyplot as plt
from astropy.coordinates import Angle, Latitude, Longitude, SkyCoord

# Moc and HEALPix tools
from cdshealpix import elliptical_cone_search
from mocpy import MOC, World2ScreenMPL

ipix, depth, fully_covered = elliptical_cone_search(
    lon=Longitude(0, u.deg),
    lat=Latitude(0, u.deg),
    a=Angle(50, unit="deg"),
    b=Angle(5, unit="deg"),
    pa=Angle(30, unit="deg"),
    depth=10,
)

moc = MOC.from_healpix_cells(ipix, depth, fully_covered)
# Plot the MOC using matplotlib


fig = plt.figure(111, figsize=(10, 10))
# Define a astropy WCS easily
with World2ScreenMPL(
    fig,
    fov=100 * u.deg,
    center=SkyCoord(0, 0, unit="deg", frame="icrs"),
    coordsys="icrs",
    rotation=Angle(0, u.degree),
    projection="AIT",
) as wcs:
    ax = fig.add_subplot(1, 1, 1, projection=wcs)
    # Call fill with a matplotlib axe and the `~astropy.wcs.WCS` wcs object.
    moc.fill(ax=ax, wcs=wcs, alpha=0.5, fill=True, color="green")
    # Draw the perimeter of the MOC in black
    moc.border(ax=ax, wcs=wcs, alpha=0.5, color="black")
plt.xlabel("ra")
plt.ylabel("dec")
plt.title("Elliptical cone search")
plt.grid(color="black", linestyle="dotted")
plt.show()
