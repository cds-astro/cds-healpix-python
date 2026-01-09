from pathlib import Path
import os
from tempfile import NamedTemporaryFile

import numpy as np
import pytest

from ..skymap import SkymapExplicit, SkymapImplicit, Skymap
from .. import cdshealpix

###################
# Explicit
###################

path_to_skymap_explicit = (
    Path(__file__).parent.resolve() / "resources" / "skymap-explicit.fits"
)


def test_read_explicit():
    map_exp = SkymapExplicit.from_fits(path_to_skymap_explicit)
    assert map_exp.values.dtype == np.int32
    assert len(map_exp.values) == 48
    assert map_exp.keys.dtype == np.uint64


def test_read_write_read_conservation_explicit():
    skymap = SkymapExplicit.from_fits(path_to_skymap_explicit)
    with NamedTemporaryFile(delete=False) as fp:
        skymap.to_fits(fp.name)
        skymap2 = SkymapExplicit.from_fits(fp.name)
        assert all(skymap.values == skymap2.values)
        # this is needed for windows
        fp.close()
        os.unlink(fp.name)


def test_to_implicit():
    explicit = SkymapExplicit(keys=[12, 13, 14], values=[0.1, 0.2, 0.3], order=1)
    implicit = explicit.to_implicit()
    assert implicit.order == 1
    assert len(implicit.values) == 12 * 4


def test_instantiation_skymap_explicit():
    with pytest.raises(
        ValueError, match="`keys` and `values` must have the same length, got 3 and 2."
    ):
        SkymapExplicit(keys=np.zeros(3), values=np.zeros(2), order=5)
    with pytest.raises(ValueError, match="The accepted types are*"):
        SkymapExplicit(keys=[1, 2, 3], values=["a", "b", "c"], order=5)
    with pytest.raises(ValueError, match="Skymap values should be one-dimensional*"):
        SkymapExplicit(
            keys=[[1, 2, 3], [1, 2, 3]], values=[[1, 2, 3], [1, 2, 3]], order=5
        )


###################
# Implicit
###################

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


###################
# Generic Skymap
###################


def test_io():
    implicit_map_from_file = Skymap.from_fits(path_to_skymap_implicit)
    assert isinstance(implicit_map_from_file.skymap, SkymapImplicit)

    with NamedTemporaryFile(delete=False) as fp:
        implicit_map_from_file.to_fits(fp.name)
        implicit_map_from_file_read_again = Skymap.from_fits(fp.name)
        assert all(
            implicit_map_from_file.skymap.values
            == implicit_map_from_file_read_again.skymap.values
        )
        # this is needed for windows
        fp.close()
        os.unlink(fp.name)

    explicit_map_from_file = Skymap.from_fits(path_to_skymap_explicit)
    assert isinstance(explicit_map_from_file.skymap, SkymapExplicit)

    with NamedTemporaryFile(delete=False) as fp:
        explicit_map_from_file.to_fits(fp.name)
        explicit_map_from_file_read_again = Skymap.from_fits(fp.name)
        assert all(
            explicit_map_from_file.skymap.values
            == explicit_map_from_file_read_again.skymap.values
        )
        # this is needed for windows
        fp.close()
        os.unlink(fp.name)
