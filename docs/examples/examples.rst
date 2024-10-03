********
Examples
********

Getting coordinates in a HEALPix cell
=====================================

In this example, we chose a HEALPix cell, and we plot its center

.. plot:: examples/healpix_to_lonlat.py
    :include-source:


Getting the healpix cells contained in a region of the sky
==========================================================

Cone search
-----------

.. plot:: examples/search_methods/cone_search.py
    :include-source:

Elliptical cone search
----------------------

.. plot:: examples/search_methods/elliptic_search.py
    :include-source:

Polygon search
--------------

.. plot:: examples/search_methods/polygon_search.py
    :include-source:

Box search
----------

.. plot:: examples/search_methods/box_search.py
    :include-source:

Zone search
-----------

In this example, we get the ``ipix`` and ``depth`` in a zone and plot them by combining
:external:ref:`~cdshealpix.nested.vertices`_ with :external:ref:`~matplotlib.path.Polygon`_

.. plot:: examples/search_methods/zone_search.py
    :include-source:

Notebook examples
=================

.. nbgallery::
    ../_collections/notebooks/coordinate_conversion.ipynb
    ../_collections/notebooks/external_neighbours.ipynb
