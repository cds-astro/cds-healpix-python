"""Read and plots a quick preview of a skymap in a FITS file."""

from cdshealpix.skymap import SkymapImplicit

my_skymap = SkymapImplicit.from_fits("skymap.fits")
print(my_skymap.order)
my_skymap.quick_plot()
