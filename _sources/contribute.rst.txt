Contributing
============

This section describes how you can contribute to the project. It will require you to install:

- `Rustup <https://www.rust-lang.org/learn/get-started>`__: the Rust installer and version management tool
- `setuptools_rust <https://github.com/PyO3/setuptools-rust>`__ PyPI package
- For running the basic tests: `pytest <https://docs.pytest.org/en/latest/>`__
- For running the benchmarks: `pytest_benchmark <https://pytest-benchmark.readthedocs.io/en/latest/>`__ `astropy_healpix <https://github.com/astropy/astropy-healpix>`__

Compiling the cdshealpix Rust dynamic library
---------------------------------------------

Setting up your development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to contribute you first must download Rustup:

.. code-block:: bash

    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh


and follow the installation instructions.

Rustup will allow you to compile the shared library for your local architecture. You will then obtain a .so (Linux/MacOS) or a .pyd (Windows) file that can be loaded and called from python.

Then you can create a new virtual environment (using the virtualenv package) by specifying the version of python you need. Let is call it ``cdshealpix-env``.

.. code-block:: bash

    virtualenv -p /usr/bin/python3 cdshealpix-env


Activate it: 

.. code-block:: bash

    source cdshealpix-env/bin/activate


Install all the python dependencies for contributing:

.. code-block:: bash

    pip install -r <path_to_cloned_repo>/requirements-dev.txt


At this moment you have correctly set up your development environment. When you will be done with your developments, remember to deactivate your environment by typing ```deactivate```.

The next step tells you how to generate the shared library associated with `cdshealpix`.

Dynamic library compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The generation of the shared library is managed by [setuptools_rust](https://github.com/PyO3/setuptools-rust). Just go to the root of your cloned repo:

.. code-block:: bash

    cd <path_to_cloned_repo>


and run this command:

.. code-block:: bash

    python setup.py build


The generated .so will be located in a build/lib folder. Just copy it from build/lib to cdshealpix:

.. code-block:: bash

    cp build/lib/cdshealpix/*.so cdshealpix


You do not have to recompile the dynamic library every time if you just work on the python-side code. It is only necessary if you want to update the Rust code located in src/lib.rs.

Running the tests
-----------------

For running the tests + benchmarks:

.. code-block:: bash

    python -m pytest -v cdshealpix


For running only the benchmarks:

.. code-block:: bash

    python -m pytest -v cdshealpix/tests/test_benchmark_healpix.py

Working on the documentation
----------------------------

To work on the documentation you have to install a few more packages:

- `sphinx <http://www.sphinx-doc.org/en/master/>`__ is responsible for building the documentation in HTML.
- `numpydoc <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__ defines a very convenient way to write API documentation by introducing the numpy docstring format.
- `sphinxcontrib-bibtex <https://sphinxcontrib-bibtex.readthedocs.io/en/latest/>`__ allows to add bibtex references to the documentation.
- `mocpy <https://mocpy.readthedocs.io/en/latest/>`__ is used to generate plots of the HEALPix cells obtained.
- `matplotlib <https://matplotlib.org/>`__ is used by `mocpy` for plotting purposes.

These packages can be installed via pip but are already referred in `requirements-dev.txt`. So if you did a: 

.. code-block:: bash

    pip install -r <path_to_cloned_repo>/requirements-dev.txt

Then they are already installed.

To build the documentation:

.. code-block:: bash

    cd docs
    make html
    cd ..

The HTML files can then be consulted:

.. code-block:: bash

    firefox docs/_build/html/index.html &
