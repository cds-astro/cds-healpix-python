Contributing
============

This section describes how you can contribute to the project. It will require you to install:

- `Rustup <https://www.rust-lang.org/learn/get-started>`__: the Rust installer and version management tool
- `maturin <https://github.com/PyO3/maturin>`__ PyPI package, see also on [pypi](https://pypi.org/project/maturin/)
- `virtualenv <https://pypi.org/project/virtualenv/>`__ PyPi package
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

    pip install virtualenv
    virtualenv -p /usr/bin/python3 cdshealpix-env


Activate it:

.. code-block:: bash

    source cdshealpix-env/bin/activate


Install all the python dependencies and the pre-commits hooks for contributing:

.. code-block:: bash

    pip install -r <path_to_cloned_repo>/requirements-dev.txt
    pip install -r <path_to_cloned_repo>/requirements-bench.txt
    pre-commit install

At this moment you have correctly set up your development environment. When you will be done with your developments, remember to deactivate your environment by typing ```deactivate```.

The next step tells you how to generate the shared library associated with ``cdshealpix``.

Dynamic library compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The generation of the shared library is managed by [maturin](https://github.com/PyO3/maturin). Just go to the root of your cloned repo:

.. code-block:: bash

    cd <path_to_cloned_repo>


and run this command:

.. code-block:: bash

    pip install maturin
    maturin develop --release

The generated .so will be located in a target/release folder. Just copy it from target/release to cdshealpix:

You do not have to recompile the dynamic library every time if you just work on the python-side code. It is only necessary if you want to update the Rust code located in src/lib.rs.

Remark: if you pull a new version and get errors, you may have to remove ``Cargo.lock`` before executing ``maturin develop --release``.

Running the tests
-----------------

For running the tests + benchmarks:

.. code-block:: bash

    cd python
    python -m pytest -v cdshealpix


For running only the benchmarks:

.. code-block:: bash

    cd python
    python -m pytest -v cdshealpix/tests/test_benchmark_healpix.py
    cd ..

Working on the documentation
----------------------------

To work on the documentation you have to install a few more packages:

- `sphinx <http://www.sphinx-doc.org/en/master/>`__ is responsible for building the documentation in HTML.
- `numpydoc <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__ defines a very convenient way to write API documentation by introducing the numpy docstring format.
- `sphinxcontrib-bibtex <https://sphinxcontrib-bibtex.readthedocs.io/en/latest/>`__ allows to add bibtex references to the documentation.
- `mocpy <https://mocpy.readthedocs.io/en/latest/>`__ is used to generate plots of the HEALPix cells obtained.
- `matplotlib <https://matplotlib.org/>`__ is used by ``mocpy`` for plotting purposes.

These packages can be installed via pip but are already referred in ``requirements-doc.txt``. So if you did a:

.. code-block:: bash

    pip install -r <path_to_cloned_repo>/requirements-doc.txt

Then they are already installed.

To build the documentation:

.. code-block:: bash

    cd docs
    make html
    make doctest
    cd ..

The HTML files can then be consulted:

.. code-block:: bash

    firefox docs/_build/html/index.html &
