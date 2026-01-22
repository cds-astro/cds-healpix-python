"""Manipulation of skymaps.

SkyMaps are described in <Data formats for gamma-ray astronomy
 https://gamma-astro-data-formats.readthedocs.io/en/latest/skymaps/healpix/index.html>_
This sub-module supports skymaps in the nested scheme, and in the implicit and explicit
formats.
The coordinates system should be 'CEL'.
"""
from .. import cdshealpix

from enum import Enum
from pathlib import Path
from typing import Union

from astropy.io.fits import open as open_fits

try:
    import matplotlib.pyplot as plt

    _matplotlib_missing = False
except ImportError:
    _matplotlib_missing = True
import numpy as np

valid_dtypes = (
    np.float64,
    np.float32,
    np.int64,
    np.int32,
    np.int16,
    np.uint8,
    float,
    int,
)


class SkymapImplicit:
    """An implicit Skymap, containing values to associate to healpix cells."""

    def __init__(self, values, null_value=None):
        """Instantiate an implicit skymap.

        Parameters
        ----------
        values : `np.array`
            Is a one dimensional array-like. It should have
        null_value : `~numpy.number`, optional
            Is the value to use in case of missing data. It defaults to 0.

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapImplicit
        >>> import numpy as np
        >>> map = SkymapImplicit(np.array([1.1] * 11 + [np.nan]))
        >>> map.order
        0
        """
        self._order = None
        self.values = values
        self.null_value = null_value

    @property
    def values(self):
        """Are the values associates to the HEALPix cells of the implicit skymap.

        Parameters
        ----------
        values : `numpy.array`
            An array-like object. It should be one-dimensional, and its length should be
            the number of cells in a HEALPix order.
            It should be in the nested ordering (not tested).

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapImplicit
        >>> import numpy as np
        >>> skymap =SkymapImplicit(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=np.uint8))
        """
        return self._values

    @values.setter
    def values(self, values):
        # only makes a copy if it was not C-contiguous in the first place
        values = np.ascontiguousarray(values)
        if values.ndim != 1:
            raise ValueError(
                "Implicit Skymap values should be one-dimensional. Got an array of "
                f"shape {values.shape}."
            )
        n = int(len(values) / 12)
        # test if it is a power of two (1000 & 0111 = 0000)
        if n & (n - 1) != 0 or n == 0:
            raise ValueError(
                "The length of values should be a valid number of cells in "
                "a given HEALPix order, i.e something like 12, 48, 192... "
                f"Got '{len(values)}'."
            )

        if values.dtype not in valid_dtypes:
            raise ValueError(
                f"The accepted types are f64, f32, i64, i32, u8. Got '{values.dtype}'."
            )
        self._values = values

    @property
    def order(self):
        """The depth/order of the implicit skymap.

        Avoids the costly log calculation.

        Returns
        -------
        `int`
            The order of the skymap.

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapImplicit
        >>> map = SkymapImplicit([0]*12)
        >>> map.order
        0
        """
        if self._order is None:
            self._order = cdshealpix.depth_skymap_implicit(self.values)
        return self._order

    @property
    def null_value(self):
        """The value in the empty cells.

        Defaults to 0.
        """
        return self._null_value

    @null_value.setter
    def null_value(self, null_value):
        if null_value is None:
            if np.issubdtype(self.values.dtype, np.floating):
                self._null_value = self.values.dtype.type(0)
            else:  # can only be float or integer
                self._null_value = self.values.dtype.type(0)
        self._null_value = null_value

    @classmethod
    def from_fits(cls, path: Union[str, Path]):
        """Read a skymap in the nested schema from a FITS file.

        This reader supports files which are:

        - all sky maps
        - in the nested scheme
        - and the implicit format

        Parameters
        ----------
        path : str, `pathlib.Path`
            The file's path.

        Returns
        -------
        `SkymapImplicit`
            A skymap. Its values are in a numpy array which data type in inferred from
            the FITS header.
        """
        with open(path, "rb") as f:
            order, values = cdshealpix.read_skymap_implicit(f.read())
            return cls(values, order)

    def to_fits(self, path):
        """Write an implicit Skymap in a fits file.

        Parameters
        ----------
        path : `str`, `pathlib.Path`
            The file's path.
        """
        cdshealpix.write_skymap_implicit(self.values, str(path))

    def to_explicit(self):
        """Convert this implicit skymap into an explicit one.

        Returns
        -------
        `SkymapExplicit`

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapImplicit
        >>> implicit_map = SkymapImplicit([-1]*8 + [1, 2, 3, 4], null_value=-1)
        >>> explicit_map = implicit_map.to_explicit()
        >>> print(explicit_map.keys, explicit_map.values)
        [ 8  9 10 11] [1 2 3 4]
        """
        order, keys, values = cdshealpix.to_explicit(
            self.order, self.null_value, self.values
        )
        return SkymapExplicit(keys, values, order)

    def quick_plot(self, *, size=256, convert_to_gal=True, path=None):
        """Preview a skymap in the Mollweide projection.

        Parameters
        ----------
        size : `int`, optional
            The size of the plot in the y-axis in pixels.
            It fixes the resolution of the image. By default 256
        convert_to_gal : `bool`, optional
            Should the image be converted into a galactic frame? by default True
        path : `str` or `pathlib.Path`, optional
            If different from none, the image will not only be displayed, but also saved
            at the given location. By default None
        """
        if _matplotlib_missing:
            raise ModuleNotFoundError(
                "matplotlib is mandatory to use 'quick_plot'. "
                "See https://matplotlib.org/ for installation "
                "instructions."
            )
        img = cdshealpix.pixels_skymap_implicit(self.values, size, convert_to_gal)
        fig = plt.imshow(img)
        plt.axis("off")
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        if path:
            plt.savefig(path, bbox_inches="tight", pad_inches=0, transparent=True)
        plt.show()


class SkymapExplicit:
    """An explicit Skymap, containing values to associate to healpix cells.

    ``values`` is a 2D numpy array.
    """

    def __init__(self, keys, values, order):
        """Instantiate an explicit skymap.

        Parameters
        ----------
        keys : `np.array`
            Is a one-dimensional array-like. Contains the HEALPix number.
        values : `np.array`
            Is a one dimensional array-like.

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapExplicit
        >>> import numpy as np
        >>> map = SkymapExplicit(np.array([0, 1, 2]), np.array([2, 3, 4]), 0)
        >>> map.order
        0
        """
        if len(values) != len(keys):
            raise ValueError(
                "`keys` and `values` must have the same length, got "
                f"{len(keys)} and {len(values)}."
            )
        self.values = values
        self.keys = keys
        self.order = order

    @property
    def values(self):
        """Are the values associated to the HEALPix cells in the explicit skymap.

        Parameters
        ----------
        values : `numpy.array`
            An array-like object. It should be one-dimensional.
        """
        return self._values

    @values.setter
    def values(self, values):
        # only makes a copy if it was not C-contiguous in the first place
        values = np.ascontiguousarray(values)
        if values.ndim != 1:
            raise ValueError(
                "Skymap values should be one-dimensional. Got an array of "
                f"shape {values.shape}."
            )

        if values.dtype not in valid_dtypes:
            raise ValueError(
                f"The accepted types are f64, f32, i64, i32, u8. Got '{values.dtype}'."
            )
        self._values = values

    @property
    def keys(self):
        """Are the HEALPix cells associated to the values of the explicit skymap.

        Parameters
        ----------
        keys : `numpy.array`
            An array-like object. It should be one-dimensional.
        """
        return self._keys

    @keys.setter
    def keys(self, keys):
        # only makes a copy if it was not C-contiguous in the first place
        keys = np.ascontiguousarray(keys, dtype="uint64")
        if keys.ndim != 1:
            raise ValueError(
                "Skymap keys should be one-dimensional. Got an array of "
                f"shape {keys.shape}."
            )
        self._keys = keys

    @classmethod
    def from_fits(cls, path: Union[str, Path]):
        """Read an explicit skymap in the nested schema from a FITS file.

        This reader supports files which are:

        - in the nested scheme
        - and the explicit format

        Parameters
        ----------
        path : str, `pathlib.Path`
            The file's path.

        Returns
        -------
        `SkymapExplicit`
            An explicit skymap. Its values are in a 2D numpy array which data type in
            inferred from the FITS header.
        """
        with open(path, "rb") as f:
            order, keys, values = cdshealpix.read_skymap_explicit(f.read())
            return cls(keys, values, order)

    def to_fits(self, path):
        """Write an explicit Skymap in a fits file.

        Parameters
        ----------
        path : `str`, `pathlib.Path`
            The file's path.
        """
        cdshealpix.write_skymap_explicit(self.order, self.keys, self.values, str(path))

    def to_implicit(self, null_value=None):
        """Convert this `SkymapExplicit` into a `SkymapImplicit`.

        Parameters
        ----------
        null_value: `int` or `float`
            Is the value to be used as a null to fill the implicit skymap where the
            explicit one has gaps. Its type should be compatible with the type of
            values. It defaults to 0.

        Examples
        --------
        >>> from cdshealpix.skymap import SkymapExplicit
        >>> import numpy as np
        >>> map = SkymapExplicit(np.array([0, 1, 2]), np.array([2.1, 3.2, 4.4]), 0)
        >>> map.to_implicit(null_value=np.nan).values
        array([2.1, 3.2, 4.4, nan, nan, nan, nan, nan, nan, nan, nan, nan])
        """
        if null_value is None:
            null_value = 0.0 if np.issubdtype(self.values.dtype, np.floating) else 0
        return SkymapImplicit(
            cdshealpix.to_implicit(
                self.order, null_value, self.keys.astype("uint64"), self.values
            ),
            null_value=null_value,
        )


class Scheme(Enum):  # noqa: D101
    IMPLICIT = 0
    EXPLICIT = 1


class Skymap:
    """A Skymap can be either explicit or implicit."""

    def __init__(self, skymap: Union[SkymapExplicit, SkymapImplicit]):
        """Instantiate a Skymap.

        Parameters
        ----------
        skymap : Union[SkymapExplicit, SkymapImplicit]
            The content of the skymap.
        """
        self._skymap = skymap
        self._scheme = None

    @property
    def scheme(self):
        """The scheme of the skymap.

        Returns
        -------
        Scheme
            Can be either `Scheme.EXPLICIT` or `Scheme.IMPLICIT`
        """
        if self._scheme:
            return self._scheme
        if isinstance(self.skymap, SkymapExplicit):
            self._scheme = Scheme.EXPLICIT
            return self._scheme
        self._scheme = Scheme.IMPLICIT
        return self._scheme

    @property
    def skymap(self):
        """The Skymap object.

        Returns
        -------
        Union[SkymapImplicit, SkymapExplicit]
        """
        return self._skymap

    @skymap.setter
    def skymap(self, skymap):
        if isinstance(skymap, SkymapExplicit):
            self._scheme = Scheme.EXPLICIT
        if isinstance(skymap, SkymapImplicit):
            self._scheme = Scheme.IMPLICIT
        self._skymap = skymap

    @classmethod
    def from_fits(cls, path: Union[str, Path]):
        """Read a Skymap from a fits file.

        This reader supports files which are:

        - in the nested scheme
        - and the explicit or implicit format

        Parameters
        ----------
        path : str, `pathlib.Path`
            The file's path.

        Returns
        -------
        `Skymap`
            A skymap object. It contains either a `SkymapImplicit` or a `SkymapExplicit`
        """
        with open(path, "rb") as f:
            scheme = open_fits(f)[1].header["INDXSCHM"]
        if scheme == "EXPLICIT":
            return cls(SkymapExplicit.from_fits(path))
        if scheme == "IMPLICIT":
            return cls(SkymapImplicit.from_fits(path))
        raise ValueError("Unsupported INDXSCHM.")

    def to_fits(self, path):
        """Write a `Skymap` in a FITS file.

        It conserves the current scheme of the `Skymap`.

        Parameters
        ----------
        path : `str`, `pathlib.Path`
            The file's path.
        """
        self.skymap.to_fits(path)

    def quick_plot(self, *, size=256, convert_to_gal=True, path=None):
        """Preview a skymap in the Mollweide projection.

        Parameters
        ----------
        size : `int`, optional
            The size of the plot in the y-axis in pixels.
            It fixes the resolution of the image. By default 256
        convert_to_gal : `bool`, optional
            Should the image be converted into a galactic frame? by default True
        path : `str` or `pathlib.Path`, optional
            If different from none, the image will not only be displayed, but also saved
            at the given location. By default None
        """
        if self.scheme == Scheme.EXPLICIT:
            self.skymap.to_implicit().quick_plot(
                size=size, convert_to_gal=convert_to_gal, path=path
            )
        else:
            self.skymap.quick_plot(size=size, convert_to_gal=convert_to_gal, path=path)
