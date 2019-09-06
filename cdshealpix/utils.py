import numpy as np

from . import cdshealpix # noqa

# Raise a ValueError exception if the input 
# HEALPix cells array contains invalid values
def _check_ipixels(data, depth):
    npix = 12 * 4 ** (depth)
    if (data >= npix).any() or (data < 0).any():
        raise ValueError("The input HEALPix cells contains value out of [0, {0}]".format(npix - 1))


def to_ring(ipix, depth):
    """Convert HEALPix cells from the NESTED to the RING scheme

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes in the NESTED scheme.
    depth : int
        The depth of the HEALPix cells.

    Returns
    -------
    ipix_ring : `numpy.ndarray`
        The corresponding HEALPix cells in the RING scheme.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import to_ring
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> ipix_ring = to_ring(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the cells under the RING scheme
    ipix_ring = np.zeros(ipix.shape, dtype=np.uint64)
    cdshealpix.to_ring(depth, ipix, ipix_ring)

    return ipix_ring

def from_ring(ipix, depth):
    """Convert HEALPix cells from the RING to the NESTED scheme

    Parameters
    ----------
    ipix : `numpy.ndarray`
        The HEALPix cell indexes in the RING scheme.
    depth : int
        The depth of the HEALPix cells.

    Returns
    -------
    ipix_nested : `numpy.ndarray`
        The corresponding HEALPix cells in the NESTED scheme.

    Raises
    ------
    ValueError
        When the HEALPix cell indexes given have values out of :math:`[0, 4^{29 - depth}[`.

    Examples
    --------
    >>> from cdshealpix import from_ring
    >>> import numpy as np
    >>> ipix = np.array([42, 6, 10])
    >>> depth = 12
    >>> ipix = from_ring(ipix, depth)
    """
    if depth < 0 or depth > 29:
        raise ValueError("Depth must be in the [0, 29] closed range")

    ipix = np.atleast_1d(ipix)
    _check_ipixels(data=ipix, depth=depth)
    ipix = ipix.astype(np.uint64)
    
    # Allocation of the array containing the cells under the NESTED scheme
    ipix_nested = np.zeros(ipix.shape, dtype=np.uint64)
    cdshealpix.from_ring(depth, ipix, ipix_nested)

    return ipix_nested