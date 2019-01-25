// Returns the cell number (hash value) associated with the given positions on the unit sphere 
// in the HEALPix NESTED scheme.
// Inputs:
// - depth: HEALPix depth, must be in [0, 24?]
// - num_coords: number of positions submited (= size of the `coords` array divided by 2 = size of `result`)
// - lon: longitudes in radians of size `num_coords`
// - lat: latitudes in radians of size `num_coords`
// - ipixels: array storing the result of size `num_coords`
// Output: void
// We use the `ipixels` array so that the memory is managed by the Python's garbage collector and it does not have to be free
// by an explicit call to a specific free function.
void hpx_hash_lonlat(uint8_t depth, uint32_t num_coords, const double* lon, const double* lat, uint64_t* ipixels);

void hpx_center_lonlat(uint8_t depth, uint32_t num_ipixels, const uint64_t* ipixels, double* center_coords);

void hpx_vertices_lonlat(uint8_t depth, uint32_t num_ipixels, const uint64_t* ipixels, double* vertices_coords);
    
void hpx_neighbours(uint8_t depth, uint32_t num_ipixels, const uint64_t* ipixels, int64_t* res);
    
// Structure storing a BMOC cell informations, i.e.
// the cell depth, the cell number and a flag telling if the cell is fully (1) or partially (0) covered
typedef struct {
    uint8_t depth;
    uint64_t hash;
    uint8_t flag;
} bmoc_cell;

// BMOC: simple ordered array of BMOC cells
typedef struct {
    uint32_t ncells;
    const bmoc_cell* cells;
} bmoc;
// Free the BMOC memory owned by Rust
void bmoc_free(const bmoc* bmoc);

const bmoc* hpx_query_cone_approx(uint8_t depth,
                                  double lon, double lat,
                                  double radius);
const bmoc* hpx_query_cone_approx_custom(uint8_t depth, uint8_t delta_depth,
                                         double lon, double lat,
                                         double radius);
const bmoc* hpx_query_polygon_approx(uint8_t depth,
                                     uint32_t n_vertices,
                                     const double* lon,
                                     const double* lat);
