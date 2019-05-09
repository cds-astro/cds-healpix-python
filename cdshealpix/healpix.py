from . import cdshealpix # noqa

import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
import numpy as np

# Raise a ValueError exception if the input 
# HEALPix cells array contains invalid values
def _check_ipixels(data, depth):
    npix = 12 * 4 ** (depth)
    if (data >= npix).any() or (data < 0).any():
        raise ValueError("The input HEALPix cells contains value out of [0, {0}]".format(npix - 1))

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
    ipix : `numpy.array`
        A numpy array containing all the HEALPix cell indexes stored as `np.uint64`.

    Raises
    ------
    ValueError
        When the number of longitudes and latitudes given do not match.

    Examples
    --------
    >>> from cdshealpix import lonlat_to_healpix
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = [0, 50, 25] * u.deg
    >>> lat = [6, -12, 45] * u.deg
    >>> depth = 12
    >>> ipix = lonlat_to_healpix(lon, lat, depth)
    """
    # Handle the case of an uniq lon, lat tuple given by creating a
    # 1d numpy array from the 0d astropy quantities.
    lon = np.atleast_1d(lon.to_value(u.rad))
    lat = np.atleast_1d(lat.to_value(u.rad))

    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_ipix = lon.shape
    # Allocation of the array containing the resulting ipixels
    ipix = np.empty(num_ipix, dtype=np.uint64)

    cdshealpix.lonlat_to_healpix(depth, lon, lat, ipix)
    return ipix

def healpix_to_lonlat(ipix, depth):
    """Get the longitudes and latitudes of the center of some HEALPix cells at a given depth.

    This method does the opposite transformation of `lonlat_to_healpix`.
    It's wrapped around the `center <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.center>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.

    Returns
    -------
    lon, lat : (`astropy.units.Quantity`, `astropy.units.Quantity`)
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
    >>> depth = 12
    >>> lon, lat = healpix_to_lonlat(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)

    size_skycoords = ipix.shape
    # Allocation of the array containing the resulting coordinates
    lon = np.zeros(size_skycoords)
    lat = np.zeros(size_skycoords)

    cdshealpix.healpix_to_lonlat(depth, ipix, lon, lat)

    return lon * u.rad, lat * u.rad

def healpix_to_skycoord(ipix, depth):
    """Get the sky coordinates of the center of some HEALPix cells at a given depth.

    This method does the opposite transformation of `lonlat_to_healpix`.
    It is the equivalent of `healpix_to_lonlat` except that it returns `astropy.coordinates.SkyCoord` instead
    of `astropy.units.Quantity`.
    It's wrapped around the `center <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.center>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.

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
    lon, lat = healpix_to_lonlat(ipix, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def vertices(ipix, depth):
    """Get the longitudes and latitudes of the vertices of some HEALPix cells at a given depth.

    This method returns the 4 vertices of each cell in `ipix`.
    This method is wrapped around the `vertices <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.vertices>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.

    Returns
    -------
    lon, lat : (`astropy.units.Quantity`, `astropy.units.Quantity`)
        The sky coordinates of the 4 vertices of the HEALPix cells. `lon` and `lat` are each `~astropy.units.Quantity` instances
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

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the resulting coordinates
    lon = np.zeros(ipix.shape + (4,))
    lat = np.zeros(ipix.shape + (4,))
    
    cdshealpix.vertices(depth, ipix, lon, lat)

    return lon * u.rad, lat * u.rad

def vertices_skycoord(ipix, depth):
    """Get the sky coordinates of the vertices of some HEALPix cells at a given depth.

    This method returns the 4 vertices of each cell in `ipix`.
    This method is wrapped around the `vertices <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.vertices>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.

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
    lon, lat = vertices(ipix, depth)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def neighbours(ipix, depth):
    """Get the neighbouring cells of some HEALPix cells at a given depth.

    This method returns a :math:`N` x :math:`9` `np.uint64` numpy array containing the neighbours of each cell of the :math:`N` sized `ipix` array.
    This method is wrapped around the `neighbours <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.neighbours>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.

    Returns
    -------
    neighbours : `numpy.array`
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
    cdshealpix.neighbours(depth, ipix, neighbours)

    return neighbours

def external_edges_cells(ipix, depth, delta_depth):
    """
    Get the neighbours of specific healpix cells

    This method returns two arrays. One containing the healpix cells
    located on the external borders of the cells (at depth: `depth` + `delta_depth`).
    The other containing the healpix cells located on the external corners of the cells
    (at depth: `depth` + `delta_depth`). Please note that some pixels do not have 4 external corners
    e.g. the 12 base pixels have each only 2 external corners.

    Parameters
    ----------
    ipix : `numpy.array`
        The healpix cells from which the external neighbours will be computed
    depth : int
        The depth of the input healpix cells
    delta_depth : int
        The depth of the returned external neighbours will be equal to: `depth` + `delta_depth`

    Returns
    -------
    external_border_cells, external_corner_cells : (`numpy.array`, `numpy.array`)
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

    cdshealpix.external_edges_cells(depth, delta_depth, ipix, corner_cells, edge_cells)

    return edge_cells, corner_cells

def cone_search(lon, lat, radius, depth, depth_delta=2, flat=False):
    """Get the HEALPix cells contained in a cone at a given depth.

    This method is wrapped around the `cone <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.cone_coverage_approx_custom>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.units.Quantity`
        Longitude of the center of the cone.
    lat : `astropy.units.Quantity`
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
    ipix, depth, fully_covered : (`numpy.array`, `numpy.array`, `numpy.array`)
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
    >>> import astropy.units as u
    >>> ipix, depth, fully_covered = cone_search(lon=0 * u.deg, lat=0 * u.deg, radius=10 * u.deg, depth=10)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if not lon.isscalar or not lat.isscalar or not radius.isscalar:
        raise ValueError('The longitude, latitude and radius must be '
                         'scalar Quantity objects')

    lon = lon.to_value(u.rad)
    lat = lat.to_value(u.rad)
    radius = radius.to_value(u.rad)

    ipix, depth, full = cdshealpix.cone_search(depth, depth_delta, lon, lat, radius, flat)
    return ipix, depth, full

def polygon_search(lon, lat, depth, flat=False):
    """Get the HEALPix cells contained in a polygon at a given depth.

    This method is wrapped around the `polygon_coverage <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.polygon_coverage>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    lon : `astropy.units.Quantity`
        The longitudes of the vertices defining the polygon.
    lat : `astropy.units.Quantity`
        The latitudes of the vertices defining the polygon.
    depth : int
        Maximum depth of the HEALPix cells that will be returned.
    flat : boolean, optional
        False by default (i.e. returns a consistent MOC). If True, the HEALPix cells returned will all be at depth indicated by `depth`.

    Returns
    -------
    ipix, depth, fully_covered : (`numpy.array`, `numpy.array`, `numpy.array`)
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
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = np.random.rand(3) * 360 * u.deg
    >>> lat = (np.random.rand(3) * 178 - 89) * u.deg
    >>> max_depth = 12
    >>> ipix, depth, fully_covered = polygon_search(lon, lat, max_depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    lon = np.atleast_1d(lon.to_value(u.rad)).ravel()
    lat = np.atleast_1d(lat.to_value(u.rad)).ravel()

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
    lon : `astropy.coordinates.Quantity`
        Longitude of the center of the elliptical cone.
    lat : `astropy.coordinates.Quantity`
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
    ipix, depth, fully_covered : (`numpy.array`, `numpy.array`, `numpy.array`)
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
    >>> import astropy.units as u
    >>> from astropy.coordinates import Angle, SkyCoord
    >>> import numpy as np
    >>> lon = 0 * u.deg
    >>> lat = 0 * u.deg
    >>> a = Angle(50, unit="deg")
    >>> b = Angle(10, unit="deg")
    >>> pa = Angle(45, unit="deg")
    >>> max_depth = 12
    >>> ipix, depth, fully_covered = elliptical_cone_search(lon, lat, a, b, pa, max_depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if not lon.isscalar or not lat.isscalar or not a.isscalar \
        or not b.isscalar or not pa.isscalar:
        raise ValueError('The longitude, latitude, semi-minor axe, semi-major axe and angle must be '
                         'scalar Quantity objects')

    if a >= Angle(np.pi/2.0, unit="rad"):
        raise ValueError('The semi-major axis exceeds 90deg.')

    if b > a:
        raise ValueError('The semi-minor axis is greater than the semi-major axis.')

    lon = lon.to_value(u.rad)
    lat = lat.to_value(u.rad)
    a = a.to_value(u.rad)
    b = b.to_value(u.rad)
    pa = pa.to_value(u.rad)

    ipix, depth, full = cdshealpix.elliptical_cone_search(depth=depth,
        delta_depth=delta_depth,
        lon=lon,
        lat=lat,
        a=a,
        b=b,
        pa=pa,
        flat=flat)

    return ipix, depth, full
