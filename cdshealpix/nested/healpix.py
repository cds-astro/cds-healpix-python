from .. import cdshealpix # noqa

import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
import numpy as np

# Raise a ValueError exception if the input 
# HEALPix cells array contains invalid values
def _check_ipixels(data, depth):
    npix = 12 * 4 ** (depth)
    if (data >= npix).any() or (data < 0).any():
        raise ValueError("The input HEALPix cells contains value out of [0, {0}]".format(npix - 1))

def lonlat_to_healpix(lon, lat, depth, return_offsets=False):
    r"""Get the HEALPix indexes that contains specific sky coordinates

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
    return_offsets : bool, optional
        If set to `True`, returns a tuple made of 3 elements, the HEALPix cell
        indexes and the dx, dy arrays telling where the (``lon``, ``lat``) coordinates
        passed are located on the cells. ``dx`` and ``dy`` are :math:`\in [0, 1]`

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
    dx = np.empty(num_ipix, dtype=np.float64)
    dy = np.empty(num_ipix, dtype=np.float64)

    cdshealpix.lonlat_to_healpix(depth, lon, lat, ipix, dx, dy)

    if return_offsets:
        return ipix, dx, dy
    else:
        return ipix

def skycoord_to_healpix(skycoord, depth, return_offsets=False):
    r"""Get the HEALPix indexes that contains specific sky coordinates

    The depth of the returned HEALPix cell indexes must be specified.
    This method is wrapped around the
    `hash <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.hash>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    skycoord : `astropy.coordinates.SkyCoord`
        The sky coordinates.
    depth : int
        The depth of the returned HEALPix cell indexes.
    return_offsets : bool, optional
        If set to `True`, returns a tuple made of 3 elements, the HEALPix cell
        indexes and the dx, dy arrays telling where the (``lon``, ``lat``) coordinates
        passed are located in the cells. ``dx`` and ``dy`` are :math:`\in [0, 1]`

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
    >>> from cdshealpix import skycoord_to_healpix
    >>> import astropy.units as u
    >>> from astropy.coordinates import SkyCoord
    >>> import numpy as np
    >>> skycoord = SkyCoord([0, 50, 25] * u.deg, [6, -12, 45] * u.deg, frame="icrs")
    >>> depth = 12
    >>> ipix = skycoord_to_healpix(skycoord, depth)
    """
    return lonlat_to_healpix(skycoord.icrs.ra, skycoord.icrs.dec, depth, return_offsets)

def healpix_to_lonlat(ipix, depth, dx=0.5, dy=0.5):
    r"""Get the longitudes and latitudes of the center of some HEALPix cells at a given depth.

    This method does the opposite transformation of `lonlat_to_healpix`.
    It's wrapped around the `center <https://docs.rs/cdshealpix/0.1.5/cdshealpix/nested/struct.Layer.html#method.center>`__
    method from the `cdshealpix Rust crate <https://crates.io/crates/cdshealpix>`__.

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cell indexes given as a `np.uint64` numpy array.
    depth : int
        The depth of the HEALPix cells.
    dx : float, optional
        The offset position :math:`\in [0, 1]` along the X axis. By default, `dx=0.5`
    dy : float, optional
        The offset position :math:`\in [0, 1]` along the Y axis. By default, `dy=0.5`

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

    if dx < 0 or dx > 1:
        raise ValueError("dx must be between [0, 1]")

    if dy < 0 or dy > 1:
        raise ValueError("dy must be between [0, 1]")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)

    size_skycoords = ipix.shape
    # Allocation of the array containing the resulting coordinates
    lon = np.zeros(size_skycoords)
    lat = np.zeros(size_skycoords)

    cdshealpix.healpix_to_lonlat(depth, ipix, dx, dy, lon, lat)

    return lon * u.rad, lat * u.rad

def healpix_to_skycoord(ipix, depth, dx=0.5, dy=0.5):
    r"""Get the sky coordinates of the center of some HEALPix cells at a given depth.

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
    dx : float, optional
        The offset position :math:`\in [0, 1]` along the X axis. By default, `dx=0.5`
    dy : float, optional
        The offset position :math:`\in [0, 1]` along the Y axis. By default, `dy=0.5`

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
    lon, lat = healpix_to_lonlat(ipix, depth, dx, dy)
    return SkyCoord(ra=lon, dec=lat, frame="icrs", unit="rad")

def vertices(ipix, depth, step=1):
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
    step : int, optional
        The number of vertices returned per HEALPix side. By default it is set to 1 meaning that
        it will only return the vertices of the cell. 2 means that it will returns the vertices of
        the cell plus one more vertex per edge (the middle of it). More generally, the number
        of vertices returned is ``4 * step``.

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

    if step < 1:
        raise ValueError("The number of step must be >= 1")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the resulting coordinates
    lon = np.zeros(ipix.shape + (4 * step,))
    lat = np.zeros(ipix.shape + (4 * step,))
    
    cdshealpix.vertices(depth, ipix, step, lon, lat)

    return lon * u.rad, lat * u.rad

def vertices_skycoord(ipix, depth, step=1):
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
    step : int, optional
        The number of vertices returned per HEALPix side. By default it is set to 1 meaning that
        it will only return the vertices of the cell. 2 means that it will returns the vertices of
        the cell plus one more vertex per edge (the middle of it). More generally, the number
        of vertices returned is ``4 * step``.

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
    lon, lat = vertices(ipix, depth, step)
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

def external_neighbours(ipix, depth, delta_depth):
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

    cdshealpix.external_neighbours(depth, delta_depth, ipix, corner_cells, edge_cells)

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

def healpix_to_xy(ipix, depth):
    r"""
    Project the center of a HEALPix cell to the xy-HEALPix plane

    Parameters
    ----------
    ipix : `numpy.array`
        The HEALPix cells which centers will be projected
    depth : int
        The depth of the HEALPix cells

    Returns
    -------
    x, y: (`numpy.array`, `numpy.array`)
        The position of the HEALPix centers in the xy-HEALPix plane.
        :math:`x \in [0, 8[` and :math:`y \in [-2, 2]`

    Examples
    --------
    >>> from cdshealpix import healpix_to_xy
    >>> import astropy.units as u
    >>> import numpy as np
    >>> depth = 0
    >>> ipix = np.arange(12)
    >>> x, y = healpix_to_xy(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)

    x = np.zeros(ipix.shape, dtype=np.float64)
    y = np.zeros(ipix.shape, dtype=np.float64)
    cdshealpix.healpix_to_xy(ipix, depth, x, y)

    return x, y

def lonlat_to_xy(lon, lat):
    r"""
    Project sky coordinates to the HEALPix space

    Parameters
    ----------
    lon : `astropy.units.Quantity`
        The longitudes of the sky coordinates.
    lat : `astropy.units.Quantity`
        The latitudes of the sky coordinates.

    Returns
    -------
    x, y: (`numpy.array`, `numpy.array`)
        The position of the (``lon``, ``lat``) coordinates in the HEALPix space.
        :math:`x \in [0, 8[` and :math:`y \in [-2, 2]`

    Examples
    --------
    >>> from cdshealpix import lonlat_to_xy
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = [10, 25] * u.deg
    >>> lat = [5, 10] * u.deg
    >>> x, y = lonlat_to_xy(lon, lat)
    """
    lon = np.atleast_1d(lon.to_value(u.rad))
    lat = np.atleast_1d(lat.to_value(u.rad))

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_coords = lon.shape
    # Allocation of the array containing the resulting ipixels
    x = np.empty(num_coords, dtype=np.float64)
    y = np.empty(num_coords, dtype=np.float64)

    cdshealpix.lonlat_to_xy(lon, lat, x, y)
    return x, y

def xy_to_lonlat(x, y):
    r"""
    Project coordinates from the HEALPix space to the sky coordinate space.

    Parameters
    ----------
    x : `numpy.array`
        Position on the X axis of the HEALPix plane, :math:`x \in [0, 8[`
    y : `numpy.array`
        Position on the Y axis of the HEALPix plane, :math:`y \in [-2, 2]`

    Returns
    -------
    (lon, lat) : (`astropy.units.Quantity`, `astropy.units.Quantity`)
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

    cdshealpix.xy_to_lonlat(x, y, lon, lat)
    return lon * u.rad, lat * u.rad

def bilinear_interpolation(lon, lat, depth):
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
    lon : `astropy.units.Quantity`
        The longitudes of the sky coordinates.
    lat : `astropy.units.Quantity`
        The latitudes of the sky coordinates.
    depth : int
        The depth of the HEALPix cells

    Returns
    -------
    pixels, weights: (`numpy.array`, `numpy.array`)
        :math:`N x 4` arrays where N is the number of ``lon`` (and ``lat``) given.
        For a given sky position, 4 HEALPix cells are returned. Each of them are associated with
        a specific weight. The 4 weights sum up to 1.

    Examples
    --------
    >>> from cdshealpix import bilinear_interpolation
    >>> import astropy.units as u
    >>> import numpy as np
    >>> lon = [10, 25] * u.deg
    >>> lat = [5, 10] * u.deg
    >>> depth = 5
    >>> ipix, weights = bilinear_interpolation(lon, lat, depth)
    """
    lon = np.atleast_1d(lon.to_value(u.rad))
    lat = np.atleast_1d(lat.to_value(u.rad))

    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    if lon.shape != lat.shape:
        raise ValueError("The number of longitudes does not match with the number of latitudes given")

    num_coords = lon.shape

    ipix = np.empty(num_coords + (4,), dtype=np.uint64)
    weights = np.empty(num_coords + (4,), dtype=np.float64)

    cdshealpix.bilinear_interpolation(depth, lon, lat, ipix, weights)
    return ipix, weights