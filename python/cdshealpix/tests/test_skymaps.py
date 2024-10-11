from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np

from ..skymap import Skymap

path_to_test_skymap = Path(__file__).parent.resolve() / "resources" / "skymap.fits"


def test_read():
    values = Skymap.from_fits(path_to_test_skymap).values
    assert values.dtype == np.int32
    assert len(values) == 49152


def test_read_write_read_conservation():
    skymap = Skymap.from_fits(path_to_test_skymap)
    with NamedTemporaryFile() as fp:
        skymap.to_fits(fp.name)
        skymap2 = Skymap.from_fits(fp.name)
        assert all(skymap.values == skymap2.values)
