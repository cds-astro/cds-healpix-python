extern crate healpix;

extern crate ndarray;
extern crate ndarray_parallel;

extern crate numpy;
extern crate pyo3;

use ndarray::{Array1, Zip};
use ndarray_parallel::prelude::*;

use numpy::{IntoPyArray, PyArrayDyn, PyArray1};
use pyo3::prelude::{pymodule, Py, PyModule, PyResult, Python};

use healpix::compass_point::{MainWind, Cardinal, Ordinal};


/// This uses rust-numpy for numpy interoperability between
/// Python and Rust.
/// PyArrayDyn rust-numpy array types are converted to ndarray
/// compatible array types.
/// ndarray then exposes several numpy-like methods for operating 
/// like in python.
/// ndarray also offers a way to zip arrays (immutably and mutably) and
/// operate on them element-wisely. This is done in parallel using the
/// ndarray-parallel crate that offers the par_apply method on zipped arrays.

#[pymodule]
fn cdshealpix(_py: Python, m: &PyModule) -> PyResult<()> {
    /// wrapper of `lonlat_to_healpix`
    #[pyfn(m, "lonlat_to_healpix")]
    fn lonlat_to_healpix(_py: Python,
        depth: u8,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>,
        ipix: &PyArrayDyn<u64>,
        dx: &PyArrayDyn<f64>,
        dy: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let lon = lon.as_array();
        let lat = lat.as_array();
        let mut ipix = ipix.as_array_mut();
        let mut dx = dx.as_array_mut();
        let mut dy = dy.as_array_mut();
        
        let layer = healpix::nested::get_or_create(depth);
        Zip::from(&mut ipix)
            .and(&mut dx)
            .and(&mut dy)
            .and(&lon)
            .and(&lat)
            .par_apply(|p, x, y, &lon, &lat| {
                let r = layer.hash_with_dxdy(lon, lat);
                *p = r.0;
                *x = r.1;
                *y = r.2;
            });

        Ok(())
    }

    /// wrapper of `healpix_to_lonlat`
    #[pyfn(m, "healpix_to_lonlat")]
    fn healpix_to_lonlat(_py: Python,
        depth: u8,
        ipix: &PyArrayDyn<u64>,
        dx: f64,
        dy: f64,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let mut lon = lon.as_array_mut();
        let mut lat = lat.as_array_mut();
        let ipix = ipix.as_array();

        let layer = healpix::nested::get_or_create(depth);
        Zip::from(&ipix)
            .and(&mut lon)
            .and(&mut lat)
            .par_apply(|&p, lon, lat| {
                let (l, b) = layer.sph_coo(p, dx, dy);
                *lon = l;
                *lat = b;
            });

        Ok(())
    }

    /// wrapper of `healpix_to_xy`
    #[pyfn(m, "healpix_to_xy")]
    fn healpix_to_xy(_py: Python,
        ipix: &PyArrayDyn<u64>,
        depth: u8,
        x: &PyArrayDyn<f64>,
        y: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let mut x = x.as_array_mut();
        let mut y = y.as_array_mut();
        let ipix = ipix.as_array();

        let layer = healpix::nested::get_or_create(depth);
        Zip::from(&ipix)
            .and(&mut x)
            .and(&mut y)
            .par_apply(|&p, hpx, hpy| {
                let (x, y) = layer.center_of_projected_cell(p);
                *hpx = x;
                *hpy = y;
            });

        Ok(())
    }

    /// wrapper of `lonlat_to_xy`
    #[pyfn(m, "lonlat_to_xy")]
    fn lonlat_to_xy(_py: Python,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>,
        x: &PyArrayDyn<f64>,
        y: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let mut x = x.as_array_mut();
        let mut y = y.as_array_mut();
        let lon = lon.as_array();
        let lat = lat.as_array();

        Zip::from(&lon)
            .and(&lat)
            .and(&mut x)
            .and(&mut y)
            .par_apply(|&l, &b, hpx, hpy| {
                let (x, y) = healpix::proj(l, b);
                *hpx = x;
                *hpy = y;
            });

        Ok(())
    }

        /// wrapper of `xy_to_lonlat`
    #[pyfn(m, "xy_to_lonlat")]
    fn xy_to_lonlat(_py: Python,
        x: &PyArrayDyn<f64>,
        y: &PyArrayDyn<f64>,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let x = x.as_array();
        let y = y.as_array();
        let mut lon = lon.as_array_mut();
        let mut lat = lat.as_array_mut();

        Zip::from(&x)
            .and(&y)
            .and(&mut lon)
            .and(&mut lat)
            .par_apply(|&hpx, &hpy, l, b| {
                let r = healpix::unproj(hpx, hpy);
                *l = r.0;
                *b = r.1;
            });

        Ok(())
    }

    /// wrapper of `vertices`
    #[pyfn(m, "vertices")]
    fn vertices(_py: Python,
        depth: u8,
        ipix: &PyArrayDyn<u64>,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>)
    -> PyResult<()> {
        let ipix = ipix.as_array();
        let mut lon = lon.as_array_mut();
        let mut lat = lat.as_array_mut();

        Zip::from(lon.genrows_mut())
            .and(lat.genrows_mut())
            .and(&ipix)
            .par_apply(|mut lon, mut lat, &p| {
                let [(s_lon, s_lat), (e_lon, e_lat), (n_lon, n_lat), (w_lon, w_lat)] = healpix::nested::vertices(depth, p);
                lon[0] = s_lon;
                lat[0] = s_lat;
                
                lon[1] = e_lon;
                lat[1] = e_lat;
                
                lon[2] = n_lon;
                lat[2] = n_lat;
                
                lon[3] = w_lon;
                lat[3] = w_lat;
            });

        Ok(())
    }

    /// Wrapper of `neighbours`
    /// The given array must be of size 9
    /// `[S, SE, E, SW, C, NE, W, NW, N]`
    #[pyfn(m, "neighbours")]
    fn neighbours(_py: Python,
        depth: u8,
        ipix: &PyArrayDyn<u64>,
        neighbours: &PyArrayDyn<i64>)
    -> PyResult<()> {
        let ipix = ipix.as_array();
        let mut neighbours = neighbours.as_array_mut();

        Zip::from(neighbours.genrows_mut())
            .and(&ipix)
            .par_apply(|mut n, &p| {
                let map = healpix::nested::neighbours(depth, p, true);

                n[0] = to_ref_i64(map.get(MainWind::S));
                n[1] = to_ref_i64(map.get(MainWind::SE));
                n[2] = to_ref_i64(map.get(MainWind::E));
                n[3] = to_ref_i64(map.get(MainWind::SW));
                n[4] = p as i64;
                n[5] = to_ref_i64(map.get(MainWind::NE));
                n[6] = to_ref_i64(map.get(MainWind::W));
                n[7] = to_ref_i64(map.get(MainWind::NW));
                n[8] = to_ref_i64(map.get(MainWind::N));
            });

        Ok(())
    }

    /// Cone search
    #[pyfn(m, "cone_search")]
    fn cone_search(py: Python,
        depth: u8,
        delta_depth: u8,
        lon: f64,
        lat: f64,
        radius: f64,
        flat: bool)
    -> (Py<PyArray1<u64>>, Py<PyArray1<u8>>, Py<PyArray1<bool>>) {
        let bmoc = healpix::nested::cone_coverage_approx_custom(
            depth,
            delta_depth,
            lon,
            lat,
            radius,
        );

        let (ipix, depth, fully_covered) = if flat {
            get_flat_cells(bmoc)
        } else {
            get_cells(bmoc)
        };

        (ipix.into_pyarray(py).to_owned(),
        depth.into_pyarray(py).to_owned(),
        fully_covered.into_pyarray(py).to_owned())
    }

    /// Elliptical cone search
    #[pyfn(m, "elliptical_cone_search")]
    fn elliptical_cone_search(py: Python,
        depth: u8,
        delta_depth: u8,
        lon: f64,
        lat: f64,
        a: f64,
        b: f64,
        pa: f64,
        flat: bool)
    -> (Py<PyArray1<u64>>, Py<PyArray1<u8>>, Py<PyArray1<bool>>) {
        let bmoc = healpix::nested::elliptical_cone_coverage_custom(
            depth,
            delta_depth,
            lon,
            lat,
            a,
            b,
            pa,
        );

        let (ipix, depth, fully_covered) = if flat {
            get_flat_cells(bmoc)
        } else {
            get_cells(bmoc)
        };

        (ipix.into_pyarray(py).to_owned(),
        depth.into_pyarray(py).to_owned(),
        fully_covered.into_pyarray(py).to_owned())
    }

    /// Polygon search
    #[pyfn(m, "polygon_search")]
    fn polygon_search(py: Python,
        depth: u8,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>,
        flat: bool)
    -> (Py<PyArray1<u64>>, Py<PyArray1<u8>>, Py<PyArray1<bool>>) {
        let lon = lon.as_array();
        let lat = lat.as_array();

        // Stack the longitude and latitudes and store them in a
        // Vec<(f64, f64)>
        let vertices = lon
            .iter()
            .zip(lat.iter())
            .map(|(&lon, &lat)| (lon, lat))
            .collect::<Vec<(f64, f64)>>();

        let bmoc = healpix::nested::polygon_coverage(
            depth,
            &vertices.into_boxed_slice(),
            true
        );

        let (ipix, depth, fully_covered) = if flat {
            get_flat_cells(bmoc)
        } else {
            get_cells(bmoc)
        };

        (ipix.into_pyarray(py).to_owned(),
        depth.into_pyarray(py).to_owned(),
        fully_covered.into_pyarray(py).to_owned())
    }

    #[pyfn(m, "external_neighbours")]
    fn external_neighbours(_py: Python,
        depth: u8,
        delta_depth: u8,
        ipix: &PyArrayDyn<u64>,
        corners: &PyArrayDyn<i64>,
        edges: &PyArrayDyn<u64>)
    -> PyResult<()> {
        let ipix = ipix.as_array();

        let mut corners = corners.as_array_mut();
        let mut edges = edges.as_array_mut();

        let layer = healpix::nested::get_or_create(depth);
        Zip::from(corners.genrows_mut())
            .and(edges.genrows_mut())
            .and(&ipix)
            .par_apply(|mut c, mut e, &p| {
                let external_edges = layer.external_edge_struct(p, delta_depth);

                c[0] = to_i64(external_edges.get_corner(&Cardinal::S));
                c[1] = to_i64(external_edges.get_corner(&Cardinal::E));
                c[2] = to_i64(external_edges.get_corner(&Cardinal::N));
                c[3] = to_i64(external_edges.get_corner(&Cardinal::W));

                // TODO: investigate why it does not abort when adding this line...
                println!("");

                let num_cells_per_edge = 2_i32.pow(delta_depth as u32) as usize;
                let mut offset = 0;
                // SE
                let se_edge = external_edges.get_edge(&Ordinal::SE);
                for i in 0..num_cells_per_edge {
                    e[offset + i] = se_edge[i];
                }
                offset += num_cells_per_edge;
                // NE
                let ne_edge = external_edges.get_edge(&Ordinal::NE);
                for i in 0..num_cells_per_edge {
                    e[offset + i] = ne_edge[i];
                }
                offset += num_cells_per_edge;
                // NW
                let nw_edge = external_edges.get_edge(&Ordinal::NW);
                for i in 0..num_cells_per_edge {
                    e[offset + i] = nw_edge[i];
                }
                offset += num_cells_per_edge;
                // SW
                let sw_edge = external_edges.get_edge(&Ordinal::SW);
                for i in 0..num_cells_per_edge {
                    e[offset + i] = sw_edge[i];
                }
            });

        Ok(())
    }

    Ok(())
}

fn to_i64(val: Option<u64>) -> i64 {
    match val {
        Some(val) => val as i64,
        None => -1_i64,
    }
}

fn to_ref_i64(val: Option<&u64>) -> i64 {
    match val {
        Some(&val) => val as i64,
        None => -1_i64,
    }
}

fn get_cells(bmoc: healpix::nested::bmoc::BMOC) -> (Array1<u64>, Array1<u8>, Array1<bool>) {
    let len = bmoc.entries.len();
    let mut ipix = Vec::<u64>::with_capacity(len);
    let mut depth = Vec::<u8>::with_capacity(len);
    let mut fully_covered = Vec::<bool>::with_capacity(len);

    for c in bmoc.into_iter() {
        ipix.push(c.hash);
        depth.push(c.depth);
        fully_covered.push(c.is_full);
    }

    depth.shrink_to_fit();
    ipix.shrink_to_fit();
    fully_covered.shrink_to_fit();

    (ipix.into(), depth.into(), fully_covered.into())
}

fn get_flat_cells(bmoc: healpix::nested::bmoc::BMOC) -> (Array1<u64>, Array1<u8>, Array1<bool>) {
    let len = bmoc.deep_size();
    let mut ipix = Vec::<u64>::with_capacity(len);
    let mut depth = Vec::<u8>::with_capacity(len);
    let mut fully_covered = Vec::<bool>::with_capacity(len);

    for c in bmoc.flat_iter_cell() {
        ipix.push(c.hash);
        depth.push(c.depth);
        fully_covered.push(c.is_full);
    }

    depth.shrink_to_fit();
    ipix.shrink_to_fit();
    fully_covered.shrink_to_fit();

    (ipix.into(), depth.into(), fully_covered.into())
}
