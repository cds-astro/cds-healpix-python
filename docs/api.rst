API
===

This is the API for the cdshealpix_ Python package.

This package is a wrapper around the Rust `cdshealpix <https://crates.io/crates/cdshealpix>`__  crate.
The functions currently implemented by `cdshealpix <https://github.com/cds-astro/cds-healpix-python>`__ are the following:

cdshealpix
~~~~~~~~~~

.. automodule:: cdshealpix

    .. autosummary::
        :toctree: stubs

        to_ring
        from_ring

cdshealpix.nested
~~~~~~~~~~~~~~~~~

.. automodule:: cdshealpix.nested

    .. autosummary::
        :toctree: stubs

        lonlat_to_healpix
        skycoord_to_healpix

        healpix_to_lonlat
        healpix_to_skycoord
        healpix_to_xy

        lonlat_to_xy
        xy_to_lonlat

        vertices
        vertices_skycoord
        neighbours
        external_neighbours

        cone_search
        polygon_search
        elliptical_cone_search

        bilinear_interpolation

cdshealpix.ring
~~~~~~~~~~~~~~~

.. automodule:: cdshealpix.ring

    .. autosummary::
        :toctree: stubs

        lonlat_to_healpix
        skycoord_to_healpix

        healpix_to_lonlat
        healpix_to_skycoord
        healpix_to_xy

        vertices
        vertices_skycoord

.. _cdshealpix: https://github.com/cds-astro/cds-healpix-python
