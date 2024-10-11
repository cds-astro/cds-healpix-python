"""Manipulation of skymaps.

SkyMaps are described in <Data formats for gamma-ray astronomy https://gamma-astro-data-formats.readthedocs.io/en/latest/skymaps/healpix/index.html>_
This sub-module supports skymaps in the nested scheme, and in the implicit format where the first pixels.
The coordsystem should be 'CEL'.
"""
from .. import cdshealpix

from pathlib import Path
from typing import Union


class Skymap:
    """A Skymap, containing values to associate to healpix cells."""

    def __init__(self, values):
        self.values = values

    @classmethod
    def from_fits(cls, path: Union[str, Path]):
        """Read a skymap in the nested schema from a FITS file.

        This reader supports files which are:

        - all sky maps
        - in the nested scheme
        - and the implicit format

        Parameters
        ----------
        path : Union[str | Path]
            The file's path.

        Returns
        -------
        `numpy.array`
            The map in a numpy array. Its dtype is inferred from the fits header.
        """
        return cls(cdshealpix.read_skymap(str(path)))
