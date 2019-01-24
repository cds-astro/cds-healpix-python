from . import ffi, lib
import numpy as np

class BMOC(object):
    def __init__(self, obj):
        self.__obj = obj
        num_pix = self.__obj.ncells
        self.data = np.zeros(num_pix, dtype={
            'names':('ipix', 'depth', 'fully_covered'),
            'formats':(np.uint64, np.uint32, np.uint8),
        })

        for i in range(num_pix):
            self.data["ipix"][i] = self.__obj.cells[i].hash
            self.data["depth"][i] = self.__obj.cells[i].depth
            self.data["fully_covered"][i] = self.__obj.cells[i].flag

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