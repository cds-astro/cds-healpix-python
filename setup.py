import os
import sys

from setuptools import setup
from setuptools_rust import RustExtension

PYTHON_MAJOR_VERSION = sys.version_info[0]

# Retrieve the cdshealpix current version number
version_file_path = os.path.join(os.path.dirname(__file__), "cdshealpix/version.py")
exec(open(version_file_path).read())

# Get the dependencies of cdshealpix by looking into the requirements.txt file
def get_package_dependencies():
    dependencies = []
    requirement_file_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(requirement_file_path, "r") as f_in:
        dependencies = f_in.read().splitlines()
    return dependencies

setup(
    name="cdshealpix",
    version=__version__,
    # setuptools_rust new parameter
    rust_extensions=[RustExtension(
        # Package name
        "cdshealpix.cdshealpix",
        # The path to the cargo.toml file defining the rust-side wrapper.
        # This file usually contains the name of the project, its version, the author
        # and the dependencies of the crate (in our case the rust wrapper depends on the cdshealpix
        # crate). 
        'Cargo.toml',
        # Specify python version to setuptools_rust
        rustc_flags=['--cfg=Py_{}'.format(PYTHON_MAJOR_VERSION)],
        features=['numpy/python{}'.format(PYTHON_MAJOR_VERSION)],
        # Add the --release option when building the rust code
        debug=False)],
    packages=["cdshealpix"],
    package_dir={'cdshealpix': 'cdshealpix'},
    # include the file containing the prototypes
    # package_data={'cdshealpix': ['bindings.h']},
    install_requires=get_package_dependencies(),
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
