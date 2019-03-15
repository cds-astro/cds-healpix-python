.. cdshealpix documentation master file, created by
   sphinx-quickstart on Wed Mar  6 10:20:39 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to cdshealpix's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   examples/examples
   api
   contribute

`cdshealpix` is a Python wrapper around the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

`cdshealpix` is deployed to the PyPI server as the `cdshealpix <https://pypi.org/project/cdshealpix/>`__ named pip package and
is available for Python 2.7, 3.4, 3.5 (not for windows archs), 3.6 and 3.7 through the following architectures:

* Linux i686/x86_64
* Windows 32/64 bits
* MacOS

What is HEALPix ?
-----------------

HEALPix describes a partionning of the sky into several equal area cells.
This partionning is hierarchical meaning that each cell has a depth associated to it.
Possible depths are in :math:`[0, 29]`. A cell of depth :math:`N` can be subdivided into
its four children of depth :math:`N+1`:

- At the depth :math:`0`, the sky is fractionned into :math:`12` cells of equal areas.
- At the depth :math:`1`, the sky is fractionned into :math:`12 \times 4` cells.
- ...
- At the depth :math:`N`, the sky is fractionned into :math:`12 \times 4^{N}` cells.
- ...
- At the depth :math:`29`, the sky is fractionned into :math:`12 \times 4^{29}` cells.

The HEALPix nested scheme relies on the following papers that you can check it out if you want to know
more about HEALPix:

- :cite:`Gorski:2004by`
- :cite:`Calabretta:2004vi`
- :cite:`2007MNRAS.381..865C`
- :cite:`2015A&A...580A.132R`

References
----------

.. bibliography:: references.bib
    :all:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


