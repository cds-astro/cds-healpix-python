from . import ffi, lib
import numpy as np

class BMOC(object):
    def __init__(self, obj):
        self.__obj = obj
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

class BMOCConeApprox(BMOC):
    def __init__(self, depth, lon, lat, radius):
        BMOC.__init__(self, lib.hpx_query_cone_approx(
            depth,
            lon,
            lat,
            radius
        ))

class BMOCPolygonApprox(BMOC):
    def __init__(self, depth, num_vertices, lon, lat):
        BMOC.__init__(self, lib.hpx_query_polygon_approx(
            depth,
            num_vertices,
            ffi.cast("const double*", lon.ctypes.data),
            ffi.cast("const double*", lat.ctypes.data)
        ))