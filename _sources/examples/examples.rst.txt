Examples
========

Cone search
-----------

.. plot:: examples/cone_search.py
    :include-source:

Elliptical cone search
----------------------

.. plot:: examples/elliptic_search.py
    :include-source:

Polygon search
--------------

.. plot:: examples/polygon_search.py
    :include-source:

Coordinate conversion
---------------------


In this example, we will load an archival all-sky Galactic reddening map, E(B-V),
based on the derived reddening maps of Schlegel, Finkbeiner and Davis (1998) :cite:`Schlegel_1998`.
It has been translated into an HEALPix map in galactic coordinates by the Legacy Archive
for Microwave Background Data Analysis `LAMBDA <http://lambda.gsfc.nasa.gov/>`_.
We'll rotate it into equatorial coordinates for demonstration purpose.

Algorithm
^^^^^^^^^

It follows the following reasonning:

- get the coordinates of the centers of the HEALPix map in galactic coordinates,
- converts those to equatorial coordinates with the astropy library,
- find the bilinear interpolation for the neighbors of each of these new coordinates using cdshealpix methods,
- apply it to form a HEALPix map in the new coordinate system.

Disclaimer
^^^^^^^^^^

This example was designed to illustrate the use of this library.
This transformation is not the most precise you could get and should be used
for visualizations or to have a quick view at maps in different coordinate systems.
For scientific use, please have a look at the method rotate_alm in
`healpy <https://github.com/healpy/healpy>`_ or at the sht module of the
`ducc <https://gitlab.mpcdf.mpg.de/mtr/ducc>`_ library that both implement the rotation in the spherical harmonics space.


.. jupyter-execute::

  import cdshealpix

  from mocpy import MOC, World2ScreenMPL
  import astropy.units as u

  from astropy.io import fits
  from astropy.coordinates import SkyCoord, Angle

  import matplotlib.pyplot as plt
  import numpy as np

Fetching the HEALPix map from NASA archives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. jupyter-execute::

  ext_map = fits.open(
    "https://lambda.gsfc.nasa.gov/data/foregrounds/SFD/" + "lambda_sfd_ebv.fits"
    ) # dowloading the map from the nasa archive
  hdr = ext_map[0].header # extracts the header
  data_header = ext_map[1].header
  data = ext_map[1].data # extracts the data
  ext_map.close()
 
  hdr

Let's also have a look at the data header

.. jupyter-execute::

  data_header

After learning that the magnitudes are stored in `'TEMPERATURE'`, we can extract all useful information.

.. jupyter-execute::

  extinction_values = data["TEMPERATURE"]
  nside = hdr["NSIDE"]
  norder = hdr["RESOLUTN"]

Coordinate conversion
^^^^^^^^^^^^^^^^^^^^^
We first create an HEALPix grid at order 9 (like the original) in nested ordering

.. jupyter-execute::

    healpix_index = np.arange(12 * 4**norder, dtype=np.uint64)
    print(
    f"We can check that the NPIX value corresponds to the one in the header here: {len(healpix_index)}"
    )

Then, we get the coordinates of the centers of these healpix cells

.. jupyter-execute::

    center_coordinates_in_equatorial = cdshealpix.healpix_to_skycoord(
        healpix_index, depth=norder
    ) # this function works for nested maps, see cdshealpix documentation
    center_coordinates_in_equatorial

Conversion into galactic coordinates with astropy method 

.. jupyter-execute::

    center_coordinates_in_galactic = center_coordinates_in_equatorial.galactic
    center_coordinates_in_galactic

Calculate the bilinear interpolation that must be applied to each
HEALPix cell to obtain the magnitude values in the other coordinate system.

.. jupyter-execute::

    healpix, weights = cdshealpix.bilinear_interpolation(
    center_coordinates_in_galactic.l, center_coordinates_in_galactic.b, depth=norder
    )
    # then apply the interpolation
    ext_map_equatorial_nested = (extinction_values[healpix.data] * weights.data).sum(axis=1)

Convert the two HEALPix into MOCs for visualisation 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We produce MOCs by excluding the high extinction regions. This allows to have a clear view of the position 
of the galactic disc. 

.. jupyter-execute::

    # For the HEALPix in equatorial coordinate system
    low_extinction_index_equatorial = np.where((ext_map_equatorial_nested < 0.5))[0]
    moc_low_extinction_equatorial = MOC.from_healpix_cells(
        low_extinction_index_equatorial,
        np.full((len(low_extinction_index_equatorial)),norder)
        )

    # For the HEALPix in galactic coordinate system
    low_extinction_index_galactic = np.where((extinction_values < 0.5))[0]
    moc_low_extinction_galactic = MOC.from_healpix_cells(
        low_extinction_index_galactic,
        np.full((len(low_extinction_index_galactic)),norder)
        )

    # Plot the MOCs using matplotlib
    fig = plt.figure(figsize=(20, 10))
    # Define a astropy WCS from the mocpy.WCS class
    with World2ScreenMPL(fig,
        fov=120 * u.deg,
        center=SkyCoord(0, 0, unit='deg', frame='icrs'),
        coordsys="icrs",
        rotation=Angle(0, u.degree),
        projection="SIN") as wcs:
        
        ax1 = fig.add_subplot(121, projection=wcs, aspect='equal', adjustable='datalim')
        ax2 = fig.add_subplot(122, projection=wcs, aspect='equal', adjustable='datalim')
        moc_low_extinction_galactic.fill(ax=ax1, wcs=wcs, alpha=0.5, fill=True, color="green")
        moc_low_extinction_equatorial.fill(ax=ax2, wcs=wcs, alpha=0.5, fill=True, color="green")


    ax1.set(xlabel = 'l', ylabel= 'b', title='galactic')
    ax2.set(xlabel='ra', ylabel='dec', title='ICRS')

    ax1.grid(color="black", linestyle="dotted")
    ax2.grid(color="black", linestyle="dotted")
    plt.show()