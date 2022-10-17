from .. import cdshealpix # noqa

import astropy.units as u
from astropy.coordinates import SkyCoord, Angle, Longitude, Latitude
import numpy as np

# Do not fill by hand :)
# > egrep "^ *def" healpix.py | cut -c 5- | egrep -v '^_'| cut -d '(' -f 1 | sed -r "s/^(.*)$/ '\1'/" | tr '\n' ','
__all__ = ['lonlat_to_healpix', 'skycoord_to_healpix', 'healpix_to_lonlat', 'healpix_to_skycoord', 'vertices', 'vertices_skycoord', 'neighbours', 'external_neighbours', 'cone_search', 'polygon_search', 'elliptical_cone_search', 'healpix_to_xy', 'lonlat_to_xy', 'xy_to_lonlat', 'bilinear_interpolation']

# Raise a ValueError exception if the input 
# HEALPix cells array contains invalid values
# data and depth must have the same shape
def _check_ipixels(data, depth):
    if isinstance(depth, int):
        npix = 12 * 4 ** (depth)
        valid_ipix = [0, npix]
    else:
        npix = np.array(12 * 4 ** depth.astype(np.uint64))
        valid_ipix = np.stack((np.zeros(npix.shape), npix)).T

    if (data >= npix).any() or (data < 0).any():
        raise ValueError("The input HEALPix array contains values out of {0}.".format(valid_ipix))

def lonlat_to_healpix(lon, lat, depth, return_offsets=False, num_threads=0):
    r"""Get the HEALPix indexes that contains specific sky coordinates

    The depth of the returned HEALPix cell indexes must be specified. This 
    method is wrapped around the `hash <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.hash>`__ 
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        The longitudes of the sky coordinates.
    lat : `astropy.coordinates.Latitude`
        The latitudes of the sky coordinates.
    depth : `numpy.ndarray`
        The depth of the returned HEALPix cell indexes.
    return_offsets : bool, optional
        If set to `True`, returns a tuple made of 3 elements, the HEALPix cell
        indexes and the dx, dy arrays telling where the (``lon``, ``lat``) coordinates
        passed are located on the cells. ``dx`` and ``dy`` are :math:`\in [0, 1]`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    ipix : `numpy.ndarray`
        A numpy array containing all the HEALPix cell indexes stored as `np.uint64`.

    Raises
    ------
    ValueError
        When the number of longitudes and latitudes given do not match.

    Examples
    --------
    >>> from cdshealpix import lonlat_to_healpix
    >>> from astropy.coordinates import Longitude, Latitude
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = Longitude([0, 50, 25], u.deg)
    >>> lat = Latitude([6, -12, 45], u.deg)
    >>> depth = np.array([5, 6])
    >>> ipix = lonlat_to_healpix(lon[:, np.newaxis], lat[:, np.newaxis], depth[np.newaxis, :])
    """
    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"

    # Handle the case of an uniq lon, lat tuple given by creating a
    # 1d numpy array from the 0d astropy quantities.
    #
    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    lon = np.atleast_1d(lon.rad)
    lat = np.atleast_1d(lat.rad)
    depth = np.atleast_1d(depth)

    if (depth < 0).any() or (depth > 29).any():
        raise ValueError("Depth must be in the [0, 29] closed range")

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    # Broadcasting arrays
    lon, lat, depth = np.broadcast_arrays(lon, lat, depth)

    # Allocation of the arrays storing the results
    num_ipix = lon.shape
    ipix = np.empty(num_ipix, dtype=np.uint64)
    dx = np.empty(num_ipix, dtype=np.float64)
    dy = np.empty(num_ipix, dtype=np.float64)

    # Call the Rust extension
    depth = depth.astype(np.uint8)
    num_threads = np.uint16(num_threads)
    cdshealpix.lonlat_to_healpix(depth, lon, lat, ipix, dx, dy, num_threads)

    if return_offsets:
        return ipix, dx, dy
    else:
        return ipix

def skycoord_to_healpix(skycoord, depth, return_offsets=False, num_threads=0):
    r"""Get the HEALPix indexes that contains specific sky coordinates

    The depth of the returned HEALPix cell indexes must be specified.
    This method is wrapped around the
    `hash <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.hash>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    skycoord : `astropy.coordinates.SkyCoord`
        The sky coordinates.
    depth : `numpy.ndarray`
        The depth of the returned HEALPix cell indexes.
    return_offsets : bool, optional
        If set to `True`, returns a tuple made of 3 elements, the HEALPix cell
        indexes and the dx, dy arrays telling where the (``lon``, ``lat``) coordinates
        passed are located in the cells. ``dx`` and ``dy`` are :math:`\in [0, 1]`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    ipix : `numpy.ndarray`
        A numpy array containing all the HEALPix cell indexes stored as `np.uint64`.

    Raises
    ------
    ValueError
        When the number of longitudes and latitudes given do not match.

    Examples
    --------
    >>> from cdshealpix import skycoord_to_healpix
    >>> import astropy.units as u
    >>> from astropy.coordinates import SkyCoord
    >>> import numpy as np
    >>> skycoord = SkyCoord([0, 50, 25] * u.deg, [6, -12, 45] * u.deg, frame="icrs")
    >>> depth = 12
    >>> ipix = skycoord_to_healpix(skycoord, depth)
    """
    return lonlat_to_healpix(Longitude(skycoord.icrs.ra), Latitude(skycoord.icrs.dec), depth, return_offsets, num_threads)

def healpix_to_lonlat(ipix, depth, dx=0.5, dy=0.5, num_threads=0):
    r"""Get the longitudes and latitudes of the center of some HEALPix cells at a given depth.

    This method does the opposite transformation of `lonlat_to_healpix`.
    It's wrapped around the `center <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.center>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : `numpy.ndarray`
        The HEALPix cell depth given as a `np.uint8` numpy array.
    dx : float, optional
        The offset position :math:`\in [0, 1]` along the X axis. By default, `dx=0.5`
    dy : float, optional
        The offset position :math:`\in [0, 1]` along the Y axis. By default, `dy=0.5`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    lon, lat : (`astropy.coordinates.Longitude`, `astropy.coordinates.Latitude`)
        The sky coordinates of the center of the HEALPix cells given as a longitude, latitude tuple.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import healpix_to_lonlat
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = np.array([12, 20])
    >>> lon, lat = healpix_to_lonlat(ipix[:, np.newaxis], depth[np.newaxis, :])
    """
    # Check arrays
    ipix = np.atleast_1d(ipix)
    depth = np.atleast_1d(depth)

    if (depth < 0).any() or (depth > 29).any():
        raise ValueError("Depth must be in the [0, 29] closed range")

    if dx < 0 or dx > 1:
        raise ValueError("dx must be between [0, 1]")

    if dy < 0 or dy > 1:
        raise ValueError("dy must be between [0, 1]")

    _check_ipixels(ipix, depth)

    # Broadcasting
    ipix, depth = np.broadcast_arrays(ipix, depth)

    # Allocation of the array containing the resulting coordinates
    lon = np.empty(ipix.shape)
    lat = np.empty(ipix.shape)

    # Call the Rust extension
    ipix = ipix.astype(np.uint64)
    depth = depth.astype(np.uint8)
    num_threads = np.uint16(num_threads)

    cdshealpix.healpix_to_lonlat(depth, ipix, dx, dy, lon, lat, num_threads)

    return Longitude(lon, u.rad), Latitude(lat, u.rad)

def healpix_to_skycoord(ipix, depth, dx=0.5, dy=0.5, num_threads=0):
    r"""Get the sky coordinates of the center of some HEALPix cells at a given depth.

    This method does the opposite transformation of `lonlat_to_healpix`.
    It is the equivalent of `healpix_to_lonlat` except that it returns `astropy.coordinates.SkyCoord` instead
    of `astropy.coordinates`.
    It's wrapped around the `center <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.center>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : `numpy.ndarray`
        The depth of the HEALPix cells.
    dx : float, optional
        The offset position :math:`\in [0, 1]` along the X axis. By default, `dx=0.5`
    dy : float, optional
        The offset position :math:`\in [0, 1]` along the Y axis. By default, `dy=0.5`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    skycoord : `astropy.coordinates.SkyCoord`
        The sky coordinates of the center of the HEALPix cells given as a `~astropy.coordinates.SkyCoord` object.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import healpix_to_skycoord
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> skycoord = healpix_to_skycoord(ipix, depth)
    """
    lon, lat = healpix_to_lonlat(ipix, depth, dx, dy, num_threads)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def vertices(ipix, depth, step=1, num_threads=0):
    """Get the longitudes and latitudes of the vertices of some HEALPix cells at a given depth.

    This method returns the 4 vertices of each cell in `ipix`.
    This method is wrapped around the `vertices <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.vertices>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.
    step : int, optional
        The number of vertices returned per HEALPix side. By default it is set to 1 meaning that
        it will only return the vertices of the cell. 2 means that it will returns the vertices of
        the cell plus one more vertex per edge (the middle of it). More generally, the number
        of vertices returned is ``4 * step``.
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    lon, lat : (`astropy.coordinates.Longitude`, `astropy.coordinates.Latitude`)
        The sky coordinates of the 4 vertices of the HEALPix cells. 
        `lon` and `lat` are `~astropy.coordinates.Longitude` and `~astropy.coordinates.Latitude` instances respectively, 
        containing a :math:`N` x :math:`4` numpy array where N is the number of HEALPix cell given in `ipix`.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import vertices
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> lon, lat = vertices(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if step < 1:
        raise ValueError("The number of step must be >= 1")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the resulting coordinates
    lon = np.zeros(ipix.shape + (4 * step,))
    lat = np.zeros(ipix.shape + (4 * step,))
    num_threads = np.uint16(num_threads)

    cdshealpix.vertices(depth, ipix, step, lon, lat, num_threads)

    return Longitude(lon, u.rad), Latitude(lat, u.rad)

def vertices_skycoord(ipix, depth, step=1, num_threads=0):
    """Get the sky coordinates of the vertices of some HEALPix cells at a given depth.

    This method returns the 4 vertices of each cell in `ipix`.
    This method is wrapped around the `vertices <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.vertices>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.
    step : int, optional
        The number of vertices returned per HEALPix side. By default it is set to 1 meaning that
        it will only return the vertices of the cell. 2 means that it will returns the vertices of
        the cell plus one more vertex per edge (the middle of it). More generally, the number
        of vertices returned is ``4 * step``.
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    vertices : `astropy.coordinates.SkyCoord`
        The sky coordinates of the 4 vertices of the HEALPix cells. `vertices` is a `~astropy.coordinates.SkyCoord` object
        containing a :math:`N` x :math:`4` numpy array where N is the number of HEALPix cells given in `ipix`.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import vertices
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> vertices = vertices(ipix, depth)
    """
    lon, lat = vertices(ipix, depth, step, num_threads)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def neighbours(ipix, depth, num_threads=0):
    """Get the neighbouring cells of some HEALPix cells at a given depth.

    This method returns a :math:`N` x :math:`9` `np.uint64` numpy array containing the neighbours of each cell of the :math:`N` sized `ipix` array.
    This method is wrapped around the `neighbours <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.neighbours>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    neighbours : `numpy.ndarray`
        A :math:`N` x :math:`9` `np.int64` numpy array containing the neighbours of each cell.
        The :math:`5^{th}` element corresponds to the index of HEALPix cell from which the neighbours are evaluated.
        All its 8 neighbours occup the remaining elements of the line.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import neighbours
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> neighbours = neighbours(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the neighbours
    neighbours = np.zeros(ipix.shape + (9,), dtype=np.int64)
    num_threads = np.uint16(num_threads)
    cdshealpix.neighbours(depth, ipix, neighbours, num_threads)

    return neighbours

def external_neighbours(ipix, depth, delta_depth, num_threads=0):
    """
    Get the neighbours of specific healpix cells

    This method returns two arrays. One containing the healpix cells
    located on the external borders of the cells (at depth: `depth` + `delta_depth`).
    The other containing the healpix cells located on the external corners of the cells
    (at depth: `depth` + `delta_depth`). Please note that some pixels do not have 4 external corners
    e.g. the 12 base pixels have each only 2 external corners.

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The healpix cells from which the external neighbours will be computed
    depth : int
        The depth of the input healpix cells
    delta_depth : int
        The depth of the returned external neighbours will be equal to: `depth` + `delta_depth`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    external_border_cells, external_corner_cells : (`numpy.ndarray`, `numpy.ndarray`)
        external_border_cells will store the pixels located at the external borders of `ipix`.
        It will be of shape: (N, 4 * 2 ** (`delta_depth`)) for N input pixels and because each cells have 4 borders.
        external_corner_cells will store the pixels located at the external corners of `ipix`
        It will be of shape: (N, 4) for N input pixels. -1 values will be put in the array when the pixels have no corners for specific directions.
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)

    # Allocation of the array containing the neighbours
    num_external_cells_on_edges = 4 << delta_depth
    edge_cells = np.zeros(ipix.shape + (num_external_cells_on_edges,), dtype=np.uint64)
    corner_cells = np.zeros(ipix.shape + (4,), dtype=np.int64)

    num_threads = np.uint16(num_threads)
    cdshealpix.external_neighbours(depth, delta_depth, ipix, corner_cells, edge_cells, num_threads)

    return edge_cells, corner_cells

def cone_search(lon, lat, radius, depth, depth_delta=2, flat=False):
    """Get the HEALPix cells contained in a cone at a given depth.

    This method is wrapped around the `cone <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.cone_coverage_approx_custom>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        Longitude of the center of the cone.
    lat : `astropy.coordinates.Latitude`
        Latitude of the center of the cone.
    radius : `astropy.units.Quantity`
        Radius of the cone.
    depth : int
        Maximum depth of the HEALPix cells that will be returned.
    depth_delta : int, optional
        To control the approximation, you can choose to perform the computations at a deeper depth using the `depth_delta` parameter.
        The depth at which the computations will be made will therefore be equal to `depth` + `depth_delta`.
    flat : boolean, optional
        False by default (i.e. returns a consistent MOC). If True, the HEALPix cells returned will all be at depth indicated by `depth`.

    Returns
    -------
    ipix, depth, fully_covered : (`numpy.ndarray`, `numpy.ndarray`, `numpy.ndarray`)
        A tuple containing 3 numpy arrays of identical size:

        * `ipix` stores HEALPix cell indices.
        * `depth` stores HEALPix cell depths.
        * `fully_covered` stores flags on whether the HEALPix cells are fully covered by the cone.

    Raises
    ------
    ValueError
        When one of `lat`, `lon` and `radius` contains more that one value.

    Examples
    --------
    >>> from cdshealpix import cone_search
    >>> from astropy.coordinates import Longitude, Latitude
    >>> import astropy.units as u
    >>> ipix, depth, fully_covered = cone_search(lon=Longitude(0 * u.deg), lat=Latitude(0 * u.deg), radius=10 * u.deg, depth=10)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")
    
    if not lon.isscalar or not lat.isscalar or not radius.isscalar:
        raise ValueError('The longitude, latitude and radius must be scalar objects')

    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"
    assert isinstance(radius, u.Quantity), "`radius` must be of type `astropy.units.Quantity`"

    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    lon = lon.rad
    lat = lat.rad
    radius = radius.to_value(u.rad)

    ipix, depth, full = cdshealpix.cone_search(np.uint8(depth), np.uint8(depth_delta), np.float64(lon), np.float64(lat), np.float64(radius), bool(flat))
    return ipix, depth, full

def polygon_search(lon, lat, depth, flat=False):
    """Get the HEALPix cells contained in a polygon at a given depth.

    This method is wrapped around the `polygon_coverage <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.polygon_coverage>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        The longitudes of the vertices defining the polygon.
    lat : `astropy.coordinates.Latitude`
        The latitudes of the vertices defining the polygon.
    depth : int
        Maximum depth of the HEALPix cells that will be returned.
    flat : boolean, optional
        False by default (i.e. returns a consistent MOC). If True, the HEALPix cells returned will all be at depth indicated by `depth`.

    Returns
    -------
    ipix, depth, fully_covered : (`numpy.ndarray`, `numpy.ndarray`, `numpy.ndarray`)
        A tuple containing 3 numpy arrays of identical size:

        * `ipix` stores HEALPix cell indices.
        * `depth` stores HEALPix cell depths.
        * `fully_covered` stores flags on whether the HEALPix cells are fully covered by the polygon.

    Raises
    ------
    ValueError
        When `lon` and `lat` do not have the same dimensions.
    IndexError
        When the number of distinct vertices given is lesser than 3 (i.e. defining at least a triangle).

    Examples
    --------
    >>> from cdshealpix import polygon_search
    >>> from astropy.coordinates import Longitude, Latitude
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = Longitude(np.random.rand(3) * 360, u.deg)
    >>> lat = Latitude((np.random.rand(3) * 180 - 90), u.deg)
    >>> max_depth = 12
    >>> ipix, depth, fully_covered = polygon_search(lon, lat, max_depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"
   
    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    lon = np.atleast_1d(lon.rad).ravel()
    lat = np.atleast_1d(lat.rad).ravel()

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_vertices = lon.shape[0]

    if num_vertices < 3:
        raise IndexError("There must be at least 3 vertices in order to form a polygon")

    # Check that there is at least 3 distinct vertices.
    vertices = np.vstack((lon, lat)).T
    distinct_vertices = np.unique(vertices, axis=0)
    if distinct_vertices.shape[0] < 3:
        raise IndexError("There must be at least 3 distinct vertices in order to form a polygon")

    ipix, depth, full = cdshealpix.polygon_search(depth, lon, lat, flat)

    return ipix, depth, full

def elliptical_cone_search(lon, lat, a, b, pa, depth, delta_depth=2, flat=False):
    """Get the HEALPix cells contained in an elliptical cone at a given depth.

    This method is wrapped around the `elliptical_cone_coverage_custom <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.elliptical_cone_coverage_custom>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        Longitude of the center of the elliptical cone.
    lat : `astropy.coordinates.Latitude`
        Latitude of the center of the elliptical cone.
    a : `astropy.coordinates.Angle`
        Semi-major axe angle of the elliptical cone.
    b : `astropy.coordinates.Angle`
        Semi-minor axe angle of the elliptical cone.
    pa : `astropy.coordinates.Angle`
        The position angle (i.e. the angle between the north and the semi-major axis, east-of-north).
    depth : int
        Maximum depth of the HEALPix cells that will be returned.
    delta_depth : int, optional
        To control the approximation, you can choose to perform the computations at a deeper depth using the `depth_delta` parameter.
        The depth at which the computations will be made will therefore be equal to `depth` + `depth_delta`.
    flat : boolean, optional
        False by default (i.e. returns a consistent MOC). If True, the HEALPix cells returned will all be at depth indicated by `depth`.

    Returns
    -------
    ipix, depth, fully_covered : (`numpy.ndarray`, `numpy.ndarray`, `numpy.ndarray`)
        A tuple containing 3 numpy arrays of identical size:

        * `ipix` stores HEALPix cell indices.
        * `depth` stores HEALPix cell depths.
        * `fully_covered` stores flags on whether the HEALPix cells are fully covered by the elliptical cone.

    Raises
    ------
    ValueError
        If one of `lon`, `lat`, `major_axe`, `minor_axe` or `pa` contains more that one value.
    ValueError
        If the semi-major axis `a` exceeds 90deg (i.e. area of one hemisphere)
    ValueError
        If the semi-minor axis `b` is greater than the semi-major axis `a`

    Examples
    --------
    >>> from cdshealpix import elliptical_cone_search
    >>> from astropy.coordinates import Angle, SkyCoord, Longitude, Latitude
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = Longitude(0, u.deg)
    >>> lat = Latitude(0, u.deg)
    >>> a = Angle(50, unit="deg")
    >>> b = Angle(10, unit="deg")
    >>> pa = Angle(45, unit="deg")
    >>> max_depth = 12
    >>> ipix, depth, fully_covered = elliptical_cone_search(lon, lat, a, b, pa, max_depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"

    if not lon.isscalar or not lat.isscalar or not a.isscalar \
        or not b.isscalar or not pa.isscalar:
        raise ValueError('The longitude, latitude, semi-minor axe, semi-major axe and angle must be '
                         'scalar objects')

    if a >= Angle(np.pi/2.0, unit="rad"):
        raise ValueError('The semi-major axis exceeds 90deg.')

    if b > a:
        raise ValueError('The semi-minor axis is greater than the semi-major axis.')

    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    ipix, depth, full = cdshealpix.elliptical_cone_search(depth=depth,
        delta_depth=delta_depth,
        lon=lon.rad,
        lat=lat.rad,
        a=a.to_value(u.rad),
        b=b.to_value(u.rad),
        pa=pa.to_value(u.rad),
        flat=flat)

    return ipix, depth, full

def healpix_to_xy(ipix, depth, num_threads=0):
    r"""
    Project the center of a HEALPix cell to the xy-HEALPix plane

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cells which centers will be projected
    depth : `numpy.ndarray`
        The depth of the HEALPix cells
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    x, y: (`numpy.ndarray`, `numpy.ndarray`)
        The position of the HEALPix centers in the xy-HEALPix plane.
        :math:`x \in [0, 8[` and :math:`y \in [-2, 2]`

    Examples
    --------
    >>> from cdshealpix import healpix_to_xy
    >>> import astropy.units as u
    >>> import numpy as np
    >>> depth = np.array([0, 2])
    >>> ipix = np.arange(12)
    >>> x, y = healpix_to_xy(ipix[:, np.newaxis], depth[np.newaxis, :])
    """
    # Check arrays
    ipix = np.atleast_1d(ipix)
    depth = np.atleast_1d(depth)

    if (depth < 0).any() or (depth > 29).any():
        raise ValueError("Depth must be in the [0, 29] closed range")

    _check_ipixels(ipix, depth)

    # Broadcasting
    ipix, depth = np.broadcast_arrays(ipix, depth)

    # Allocation of the array containing the resulting coordinates    
    x = np.zeros(ipix.shape, dtype=np.float64)
    y = np.zeros(ipix.shape, dtype=np.float64)

    # Call the Rust extension
    ipix = ipix.astype(np.uint64)
    depth = depth.astype(np.uint8)
    num_threads = np.uint16(num_threads)

    cdshealpix.healpix_to_xy(ipix, depth, x, y, num_threads)

    return x, y

def lonlat_to_xy(lon, lat, num_threads=0):
    r"""
    Project sky coordinates to the HEALPix space

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        The longitudes of the sky coordinates.
    lat : `astropy.coordinates.Latitude`
        The latitudes of the sky coordinates.
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    x, y: (`numpy.ndarray`, `numpy.ndarray`)
        The position of the (``lon``, ``lat``) coordinates in the HEALPix space.
        :math:`x \in [0, 8[` and :math:`y \in [-2, 2]`

    Examples
    --------
    >>> from cdshealpix import lonlat_to_xy
    >>> from astropy.coordinates import Longitude, Latitude
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = Longitude([10, 25], u.deg)
    >>> lat = Latitude([5, 10], u.deg)
    >>> x, y = lonlat_to_xy(lon, lat)
    """
    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"

    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    lon = np.atleast_1d(lon.rad)
    lat = np.atleast_1d(lat.rad)

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_coords = lon.shape
    # Allocation of the array containing the resulting ipixels
    x = np.empty(num_coords, dtype=np.float64)
    y = np.empty(num_coords, dtype=np.float64)
    num_threads = np.uint16(num_threads)

    cdshealpix.lonlat_to_xy(lon, lat, x, y, num_threads)
    return x, y

def xy_to_lonlat(x, y, num_threads=0):
    r"""
    Project coordinates from the HEALPix space to the sky coordinate space.

    Parameters
    ----------
    x : `numpy.ndarray`
        Position on the X axis of the HEALPix plane, :math:`x \in [0, 8[`
    y : `numpy.ndarray`
        Position on the Y axis of the HEALPix plane, :math:`y \in [-2, 2]`
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    (lon, lat) : (`astropy.coordinates.Longitude`, `astropy.coordinates.Latitude`)
        The coordinates on the sky

    Examples
    --------
    >>> from cdshealpix import xy_to_lonlat
    >>> import astropy.units as u
    >>> import numpy as np
    >>> x = np.array([0.5, 1.5])
    >>> y = np.array([0.5, 0.5])
    >>> lon, lat = xy_to_lonlat(x, y)
    """
    x = np.atleast_1d(x.astype(np.float64))
    y = np.atleast_1d(y.astype(np.float64))

    if x.shape != y.shape:
        raise ValueError("X and Y shapes do not match")

    if ((x < 0) | (x >= 8)).any():
        raise ValueError("X must be in [0, 8[")

    if ((y < -2) | (y > 2)).any():
        raise ValueError("Y must be in [-2, 2]")

    num_coords = x.shape

    # Allocation of the array containing the resulting ipixels
    lon = np.empty(num_coords, dtype=np.float64)
    lat = np.empty(num_coords, dtype=np.float64)
    num_threads = np.uint16(num_threads)

    cdshealpix.xy_to_lonlat(x, y, lon, lat, num_threads)
    return Longitude(lon, u.rad), Latitude(lat, u.rad)


def bilinear_interpolation(lon, lat, depth, num_threads=0):
    r"""
    Compute the HEALPix bilinear interpolation from sky coordinates

    For each (``lon``, ``lat``) sky position given, this function
    returns the 4 HEALPix cells that share the nearest cross of the position.

    +-----+-----+
    |(1)  |(2)  |
    |    x|     |
    +-----+-----+
    |(3)  |(4)  |
    |     |     |
    +-----+-----+

    If ``x`` is the position, then the 4 annotated HEALPix cells will be returned
    along with their weights. These 4 weights sum up to 1.

    Parameters
    ----------
    lon : `astropy.coordinates.Longitude`
        The longitudes of the sky coordinates.
    lat : `astropy.coordinates.Latitude`
        The latitudes of the sky coordinates.
    depth : int
        The depth of the HEALPix cells
    num_threads : int, optional
        Specifies the number of threads to use for the computation. Default to 0 means
        it will choose the number of threads based on the RAYON_NUM_THREADS environment variable (if set),
        or the number of logical CPUs (otherwise)

    Returns
    -------
    pixels, weights: (`numpy.ma.masked_array`, `numpy.ma.masked_array`)
        :math:`N \times 4` arrays where N is the number of ``lon`` (and ``lat``) given.
        For a given sky position, 4 HEALPix cells are returned. Each of them are associated with
        a specific weight. The 4 weights sum up to 1. Invalid positions lead to masked values.

    Warning
    -------
    Panics if a nan value is found in either lon or lat.  
    You can e.g. transform nan by 0 before calling this method using `lon = np.nan_to_num(lon) or `lat = np.nan_to_num(lat)`.
    But it is probably cleaner to pre-filter the pair of coordinates by removing the one containing a nan.


    Examples
    --------
    >>> from cdshealpix import bilinear_interpolation
    >>> from astropy.coordinates import Longitude, Latitude
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = Longitude([10, 25], u.deg)
    >>> lat = Latitude([5, 10], u.deg)
    >>> depth = 5
    >>> ipix, weights = bilinear_interpolation(lon, lat, depth)
    """
    assert isinstance(lon, Longitude), "`lon` must be of type `astropy.coordinates.Longitude`"
    assert isinstance(lat, Latitude), "`lat` must be of type `astropy.coordinates.Latitude`"

    # We could have continued to use `.to_value(u.rad)` instead of `.rad`.
    # Although `to_value` is more generical (method of Quantity),
    # Longitude/Latitude ensure that the values the contain are in the correct ranges.
    lon = np.atleast_1d(lon.rad)
    lat = np.atleast_1d(lat.rad)

    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    # Useless since we test isinstance at the beginning of the function
    #if ((lat < np.pi/2.0) | (lat > np.pi/2.0)).any():
    #    raise ValueError("Lat must be in [-pi/2, 2pi/2]")


    num_coords = lon.shape

    # Retrieve nan and infinite values
    mask_lon_invalid = np.isnan(lon) | ~np.isfinite(lon)
    mask_lat_invalid = np.isnan(lat) | ~np.isfinite(lat)
    mask_invalid = mask_lon_invalid | mask_lat_invalid

    mask_invalid = np.repeat(mask_invalid[:, np.newaxis], 4, axis=mask_invalid.ndim)

    ipix = np.empty(shape=num_coords + (4,), dtype=np.uint64)
    weights = np.empty(shape=num_coords + (4,), dtype=np.float64)

    num_threads = np.uint16(num_threads)

    # Call the rust bilinear interpolation code
    cdshealpix.bilinear_interpolation(
        depth,
        lon, lat,
        ipix, weights,
        num_threads
    )

    ipix_masked_array = np.ma.masked_array(ipix, mask=mask_invalid)
    weights_masked_array = np.ma.masked_array(weights, mask=mask_invalid)

    return ipix_masked_array, weights_masked_array
