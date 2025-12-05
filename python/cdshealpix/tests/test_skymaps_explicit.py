from pathlib import Path
import os
from tempfile import NamedTemporaryFile

import numpy as np
import pytest

from ..skymap import SkymapExplicit

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
