API
===

This is the API for the cdshealpix_ Python package.

This package is a wrapper around the Rust `cdshealpix <https://crates.io/crates/cdshealpix>`__  crate.
The functions currently implemented by `cdshealpix <https://github.com/cds-astro/cds-healpix-python>`__ are the following:

cdshealpix
~~~~~~~~~~

The HEALPix cells can be represented following two schema.
The nested and the ring one.

Here are two methods in the ``cdshealpix`` base module allowing to
convert HEALPix cells represented in the nested scheme into cells
represented in the ring scheme and vice versa.

.. automodule:: cdshealpix

    .. autosummary::
        :toctree: stubs

        to_ring
        from_ring

cdshealpix.nested
~~~~~~~~~~~~~~~~~

.. automodule:: cdshealpix.nested

    .. figure:: nested.png

        The HEALPix cells at :math:`depth=1` represented in the nested scheme

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

The ring scheme HEALPix methods take a ``nside`` parameter instead
of a ``depth`` one.
``nside`` refers to the number of cells being contained in the side
of a base cell (i.e. the 12 cells at the ``depth`` 0).
While in the nested scheme, ``nside`` is a power of two
(because :math:`N_{side} = 2 ^ {depth}`), in the ring scheme,
``nside`` does not necessary have to be a power of two!

.. automodule:: cdshealpix.ring

    .. figure:: ring.png

        The HEALPix cells at :math:`N_{side}=2` represented in the ring scheme

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
