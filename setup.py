import os

from setuptools import setup
from setuptools_rust import Binding, RustExtension

version_file_path = os.path.join(os.path.dirname(__file__), "cdshealpix/version.py")
exec(open(version_file_path).read())

def get_package_dependencies():
    dependencies = []
    requirement_file_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(requirement_file_path, "r") as f_in:
        dependencies = f_in.read().splitlines()
    return dependencies

setup(
    name="cdshealpix",
    version=__version__,
    rust_extensions=[RustExtension(
        "cdshealpix.cdshealpix",
        'Cargo.toml',
        # The binding with the Rust cdshealpix API is done using CFFI
        binding=Binding.NoBinding)],
    packages=["cdshealpix"],
    package_dir={'cdshealpix': 'cdshealpix'},
    # include the file containing the prototypes
    package_data={'cdshealpix': ['bindings.h']},
    install_requires=get_package_dependencies(),
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
