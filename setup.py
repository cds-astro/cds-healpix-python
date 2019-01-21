from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="cdshealpix",
    version="0.1.1",
    rust_extensions=[RustExtension("cdshealpix.cdshealpix", 'Cargo.toml', binding=Binding.NoBinding)],
    packages=["cdshealpix"],
    install_requires=[
        # CFFI is used for loading the dynamic lib compiled with cargo
        'cffi',
    ],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
