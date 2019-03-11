API
===

This is the API for the cdshealpix python package. This package is a wrapper around the Rust `cdshealpix <https://crates.io/crates/cdshealpix>`__  crate.
This functions currently available by `cdshealpix` are the following:

* :meth:`~cdshealpix.lonlat_to_healpix` and :meth:`~cdshealpix.skycoord_to_healpix` returns the
  HEALPix cell(s) containing some user-defined sky coordinates.
* :meth:`~cdshealpix.healpix_to_lonlat` and :meth:`~cdshealpix.healpix_to_skycoord` returns the center(s)
  of user-defined HEALPix cell(s).
* :meth:`~cdshealpix.healpix_neighbours` returns the neighbours of user-defined HEALPix cell(s).
* :meth:`~cdshealpix.healpix_vertices_lonlat` and :meth:`~cdshealpix.healpix_vertices_skycoord` returns the vertices of user-defined HEALPix cell(s).
* :meth:`~cdshealpix.cone_search_lonlat`, :meth:`~cdshealpix.polygon_search_lonlat` and :meth:`~cdshealpix.elliptical_cone_search_lonlat` return the HEALPix cells
  being located in user-defined cone (resp. polygon and elliptical cone).

.. automodule:: cdshealpix
   :members:
