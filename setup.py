from setuptools import setup
from setuptools_rust import Binding, RustExtension

from cdshealpix.version import __version__

def get_package_dependencies():
    dependencies = []
    with open("./requirements.txt", "r") as f_in:
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
    install_requires=get_package_dependencies(),
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
