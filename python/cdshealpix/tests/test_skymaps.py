from pathlib import Path

import numpy as np

from ..skymap import Skymap


def test_read():
    values = Skymap.from_fits(
        Path(__file__).parent.resolve() / "resources" / "skymap.fits"
    ).values
    assert values.dtype == np.int32
    assert len(values) == 49152
