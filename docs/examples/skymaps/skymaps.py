"""Read and plots a quick preview of a skymap in a FITS file."""

from cdshealpix.skymap import SkymapImplicit

skymap = SkymapImplicit.from_fits("skymap.fits")
print(skymap.depth)
skymap.quick_plot()
