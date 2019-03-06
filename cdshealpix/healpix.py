"""This module illustrates how to write your docstring in OpenAlea
and other projects related to OpenAlea."""

from . import lib, ffi
from .bmoc import BMOCConeApprox, BMOCPolygonApprox

import astropy.units as u
from astropy.coordinates import SkyCoord
import numpy as np


# Raise a ValueError exception if the input 
# HEALPix cells array contains invalid values
def _check_ipixels(data, depth):
    npix = 12 * 4 ** (depth)
    if (data >= npix).any() or (data < 0).any():
        raise ValueError("The input HEALPix cells contains value out of [0, {0}[".format(npix))


def lonlat_to_healpix(lon, lat, depth):
    """Get the HEALPix indexes that contains specific sky coordinates

    The depth of the returned HEALPix cell indexes must be specified. This 
    method is wrapped around the `hash <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.hash>`__ 
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.units.Quantity`
        The longitudes of the sky coordinates.
    lat : `astropy.units.Quantity`
        The latitudes of the sky coordinates.
    depth : int
        The depth of the returned HEALPix cell indexes.

    Returns
    -------
    result : `numpy.array`
        A numpy array containing all the HEALPix cell indexes stored as `np.uint64`.

    Raises
    ------
    ValueError
        When the number of longitudes and latitudes given do not match.

    References
    ----------
    .. [1] Gorsky2005: "HEALPix: A Framework for High-Resolution Discretization and Fast Analysis of Data Distributed on the Sphere", Górski, K. M. et al., 2005; 2005ApJ...622..759G.
    .. [2] Calabretta2004: "Mapping on the HEALPix grid", Calabretta, M. R., 2004; 2004astro.ph.12607C
    .. [3] Calabretta2007: "Mapping on the HEALPix grid", Calabretta, M. R. et Roukema, B. F., 2007; 2007MNRAS.381..865C
    .. [4] Reinecke2015: "Efficient data structures for masks on 2D grids", Reinecke, M. et Hivon, E., 2015; 2015A&A...580A.132R

    Examples
    --------
    >>> from cdshealpix import lonlat_to_healpix
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = [0, 50, 25] * u.deg
    >>> lat = [6, -12, 45] * u.deg
    >>> depth = 12
    >>> lonlat_to_healpix(lon, lat, depth)
    """
    # Handle the case of an uniq lon, lat tuple given by creating a
    # 1d numpy array from the 0d astropy quantities.
    lon = np.atleast_1d(lon.to_value(u.rad)).ravel()
    lat = np.atleast_1d(lat.to_value(u.rad)).ravel()

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_ipixels = lon.shape[0]
    # Allocation of the array containing the resulting ipixels
    ipixels = np.zeros(num_ipixels, dtype=np.uint64)

    lib.hpx_hash_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # lon, lat
        ffi.cast("const double*", lon.ctypes.data),
        ffi.cast("const double*", lat.ctypes.data),
        # result
        ffi.cast("uint64_t*", ipixels.ctypes.data)
    )

    return ipixels

def healpix_to_lonlat(ipixels, depth):
    """This is the form of a docstring.

    It can be spread over several lines.

    """
    ipixels = np.atleast_1d(ipixels).ravel()
    _check_ipixels(data=ipixels, depth=depth)

    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the resulting coordinates
    lonlat = np.zeros(num_ipixels << 1, dtype=np.float64)

    lib.hpx_center_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("double*", lonlat.ctypes.data)
    )

    lonlat = lonlat.reshape((-1, 2)) * u.rad
    lon, lat = lonlat[:, 0], lonlat[:, 1]

    return lon, lat

def healpix_to_skycoord(ipixels, depth):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    lon, lat = healpix_to_lonlat(ipixels, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def healpix_vertices_lonlat(ipixels, depth):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    ipixels = np.atleast_1d(ipixels).ravel()
    _check_ipixels(data=ipixels, depth=depth)

    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the resulting coordinates
    lonlat = np.zeros(num_ipixels << 3, dtype=np.float64)

    lib.hpx_vertices_lonlat(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("double*", lonlat.ctypes.data)
    )

    lonlat = lonlat.reshape((-1, 4, 2)) * u.rad
    lon, lat = lonlat[:, :, 0], lonlat[:, :, 1]

    return lon, lat

def healpix_vertices_skycoord(ipixels, depth):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    lon, lat = healpix_vertices_lonlat(ipixels, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def healpix_neighbours(ipixels, depth):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    ipixels = np.atleast_1d(ipixels).ravel()
    _check_ipixels(data=ipixels, depth=depth)

    ipixels = ipixels.astype(np.uint64)
    
    num_ipixels = ipixels.shape[0]
    # Allocation of the array containing the neighbours
    neighbours = np.zeros(num_ipixels * 9, dtype=np.int64)
    
    lib.hpx_neighbours(
        # depth
        depth,
        # num of ipixels
        num_ipixels,
        # ipixels data array
        ffi.cast("const uint64_t*", ipixels.ctypes.data),
        # result
        ffi.cast("int64_t*", neighbours.ctypes.data)
    )

    neighbours = neighbours.reshape((-1, 9))

    return neighbours

def cone_search_lonlat(lon, lat, radius, depth, delta_depth=2, flat=False):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    if not lon.isscalar or not lat.isscalar or not radius.isscalar:
        raise ValueError('The longitude, latitude and radius must be '
                         'scalar Quantity objects')

    lon = lon.to_value(u.rad)
    lat = lat.to_value(u.rad)
    radius = radius.to_value(u.rad)

    cone = BMOCConeApprox(depth=depth, depth_delta=delta_depth, lon=lon, lat=lat, radius=radius, flat=flat)

    return cone.data

def polygon_search_lonlat(lon, lat, depth):
    """
    Returns the HEALPix cell indexes containing sky coordinates.
    """
    lon = np.atleast_1d(lon.to_value(u.rad)).ravel()
    lat = np.atleast_1d(lat.to_value(u.rad)).ravel()

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_vertices = lon.shape[0]

    if num_vertices < 3:
        raise IndexError("There must be at least 3 vertices in order to form a polygon")

    polygon = BMOCPolygonApprox(depth=depth, num_vertices=num_vertices, lon=lon, lat=lat)

    return polygon.data