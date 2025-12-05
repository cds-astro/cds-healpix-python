from pathlib import Path
import os
from tempfile import NamedTemporaryFile

import numpy as np
import pytest

from ..skymap import SkymapImplicit
from .. import cdshealpix

path_to_skymap_implicit = (
    Path(__file__).parent.resolve() / "resources" / "skymap-implicit.fits"
)


def test_read_implicit():
    values = SkymapImplicit.from_fits(path_to_skymap_implicit).values
    assert values.dtype == np.int32
    assert len(values) == 49152


def test_read_write_read_conservation_implicit():
    skymap = SkymapImplicit.from_fits(path_to_skymap_implicit)
    with NamedTemporaryFile(delete=False) as fp:
        skymap.to_fits(fp.name)
        skymap2 = SkymapImplicit.from_fits(fp.name)
        assert all(skymap.values == skymap2.values)
        # this is needed for windows
        fp.close()
        os.unlink(fp.name)


def test_plot_implicit():
    skymap = SkymapImplicit([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    img = cdshealpix.pixels_skymap_implicit(skymap.values, 256, True)
    assert img.shape == (256, 512, 4)


def test_depth_implicit():
    n = 12
    skymap = SkymapImplicit(np.zeros(12 * 4**n))
    assert skymap.order == n


def test_instantiation_skymap_implicit():
    with pytest.raises(ValueError, match="The length of values should be*"):
        SkymapImplicit(np.zeros(3))
    with pytest.raises(ValueError, match="The accepted types are*"):
        SkymapImplicit(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"])
    with pytest.raises(ValueError, match="Skymap values should be one-dimensional*"):
        SkymapImplicit([[1, 2, 3], [1, 2, 3]])


def test_to_explicit():
    implicit = SkymapImplicit([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], null_value=0)
    explicit = implicit.to_explicit()
    assert all(explicit.keys == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    assert explicit.order == 0
