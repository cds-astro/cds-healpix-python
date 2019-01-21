import os
import sys
from cffi import FFI

def find_dynamic_lib_file():
    from glob import glob
    import platform

    system = platform.system()

    # For Linux and Darwin platforms, the generated lib file extension is .so
    dyn_lib_name = "cdshealpix*.so"

    if system == 'Windows':
        # On windows, it is a pyd extension file (similar to dll)
        dyn_lib_name = "cdshealpix*.pyd"

    path = os.path.join(os.path.dirname(__file__), dyn_lib_name)
    filename = ""

    try:
        filename = glob(path)[0]
    except IndexError as e:
        print("Cannot find the dynamic lib located in: ", os.path.dirname(__file__))
        # Raising the exception to get the traceback
        raise

    return filename

ffi = FFI()
ffi.cdef("""
   // Returns the cell number (hash value) associated with the given position on the unit sphere
   // in the HEALPix NESTED scheme.
   // Inputs:
   // - depth: HEALPix depth, must be in [0, 24?]
   // - lon: longitude, in radians
   // - lat: latitude, in radians, must be in [-pi/2, pi/2]
   // Output:
   // - the nested cell number if the given position a thte given depth
   unsigned long int hpx_hash(unsigned char depth, double lon, double lat);
   // Returns the cell number (hash value) associated with the given positions on the unit sphere 
   // in the HEALPix NESTED scheme.
   // Inputs
   // - depth: HEALPix depth, must be in [0, 24?]
   // - n_elems: number of positions submited (= size of the `coords` array divided by 2 = size of `result`)
   // - coords: coordinates of the position, in radians, following [lon1, lat1, lon2, lat2, ..., lonN, latN]
   // - result: array storing the result [hash1, hash2, ..., hashN]
   // Output:
   // - no output: the result is stored in the `result` array
   // We use the `result` array so that the memory is managed by Python and do not have to be free
   // by an explicit call to a specific free function.
   void* hpx_hash_multi(unsigned short depth, int n_elems, double* coords, unsigned long int* result);   
   void hpx_hash_lonlat(uint8_t depth, uint32_t num_coords, double* lon, double* lat, uint64_t* ipixels);
     
   void* hpx_center(unsigned char depth, unsigned long int hash, double* lon, double* lat);
     
   void* hpx_center_multi(unsigned char depth, int n_elems, unsigned long int* hash_ptr, double* res_ptr);
   
   void* hpx_vertices(unsigned char depth, unsigned long int hash, double* res_ptr);
     
   void* hpx_neighbours(unsigned char depth, unsigned long int hash, long int* res_ptr);
     
   // Structure storing a BMOC cell informations, i.e.
   // the cell depth, the cell number and a flag telling if the cell is fully (1) or partially (0) covered
   typedef struct {
       unsigned char depth;
       unsigned long int hash;
       unsigned char flag;
   } bmoc_cell;
  
   // BMOC: simple ordrered array of BMOC cells
   typedef struct {
     int ncells;
     bmoc_cell* cells;
   } bmoc;
   // Free the BMOC memory owned by Rust
   void bmoc_free(bmoc* bmoc);
   
   bmoc* hpx_query_cone_approx(unsigned char depth, double lon, double lat, double radius);
   bmoc* hpx_query_cone_approx_custom(unsigned char depth, unsigned chardelta_depth, double lon, double lat, double radius);
   bmoc* hpx_query_polygon_approx(unsigned char depth, int n_vertices, double* vertices_coords);
""")

dyn_lib_path = find_dynamic_lib_file()
C = ffi.dlopen(dyn_lib_path)

from .healpix import healpix_from_lonlat
from .version import __version__

__all__ = [
    'healpix_from_lonlat',
]