"""Demonstration of the cone_search function."""

# Astropy tools
import astropy.units as u

# For plots
import matplotlib.pyplot as plt
from astropy.coordinates import Angle, Latitude, Longitude, SkyCoord

# Moc and HEALPix tools
from cdshealpix.nested import box_search
from mocpy import MOC, WCS as mocpy_WCS  # noqa: N811

max_depth = 10

ipix, depth, fully_covered = box_search(
    lon=Longitude(0, u.deg),
    lat=Latitude(0, u.deg),
    a=2 * u.deg,
    b=1 * u.deg,
    angle=0 * u.deg,
    depth=max_depth,
)


moc_fully_covered = MOC.from_healpix_cells(
    ipix[fully_covered], depth[fully_covered], max_depth
)
moc_partially_covered = MOC.from_healpix_cells(
    ipix[~fully_covered], depth[~fully_covered], max_depth
)

# plot
fig = plt.figure(111, figsize=(10, 10))
# Define a astropy WCS from the mocpy.WCS class
with mocpy_WCS(
    fig,
    fov=5 * u.deg,
    center=SkyCoord(0, 0, unit="deg", frame="icrs"),
    coordsys="icrs",
    rotation=Angle(0, u.degree),
    projection="AIT",
) as wcs:
    ax = fig.add_subplot(1, 1, 1, projection=wcs)
    # Call fill with a matplotlib axe and the `~astropy.wcs.WCS` wcs object.
    moc_fully_covered.fill(
        ax=ax, wcs=wcs, alpha=0.5, fill=True, color="green", label="fully inside"
    )
    moc_partially_covered.fill(
        ax=ax, wcs=wcs, alpha=0.5, fill=True, color="red", label="crosses the border"
    )

plt.xlabel("ra")
plt.ylabel("dec")
plt.legend()
plt.title(
    "Box search, accessing the cells that are partially covered by the sky region"
)
plt.grid(color="black", linestyle="dotted")
plt.show()
