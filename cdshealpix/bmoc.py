from . import ffi, lib
import numpy as np

class BMOC(object):
    def __init__(self, depth, lon, lat, radius):
        self.__obj = lib.hpx_query_cone_approx(
            # depth
            depth,
            # lon
            lon,
            # lat
            lat,
            # radius
            radius
        )

        self.ipixels = np.zeros(self.__obj.ncells, dtype=np.uint64)
        self.depth = np.zeros(self.__obj.ncells, dtype=np.uint32)
        
        for i in range(self.ipixels.shape[0]):
            self.ipixels[i] = self.__obj.cells[i].hash
            self.depth[i] = self.__obj.cells[i].depth

    def __enter__(self):
        return self

    def __del__(self):
        lib.bmoc_free(self.__obj)
        self.__obj = None
