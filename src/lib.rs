extern crate healpix;

extern crate ndarray;
extern crate ndarray_parallel;

extern crate numpy;
extern crate pyo3;

use ndarray::{Array1, Zip};
use ndarray_parallel::prelude::*;

use numpy::{IntoPyArray, PyArrayDyn, PyArray1};
use pyo3::prelude::{pymodinit, Py, PyModule, PyResult, Python};

use healpix::compass_point::MainWind;

/// This uses rust-numpy for numpy interoperability between
/// Python and Rust.
/// PyArrayDyn rust-numpy array types are converted to ndarray
/// compatible array types.
/// ndarray then exposes several numpy-like methods for operating 
/// like in python.
/// ndarray also offers a way to zip arrays (immutably and mutably) and
/// operate on them element-wisely. This is done in parallel using the
/// ndarray-parallel crate that offers the par_apply method on zipped arrays.

#[pymodinit]
fn cdshealpix(_py: Python, m: &PyModule) -> PyResult<()> {
    /// wrapper of `lonlat_to_healpix`
    #[pyfn(m, "lonlat_to_healpix")]
    fn lonlat_to_healpix(_py: Python,
        depth: u8,
        lon: &PyArrayDyn<f64>,
        lat: &PyArrayDyn<f64>,
        ipix: &PyArrayDyn<u64>)
    -> PyResult<()> {
        let lon = lon.as_array();
        let lat = lat.as_array();
        let mut ipix = ipix.as_array_mut();
        
        let layer = healpix::nested::get_or_create(depth);
        Zip::from(&mut ipix)
            .and(&lon)
            .and(&lat)
            .par_apply(|p, &lon, &lat| {
                *p = layer.hash(lon, lat);
            });

        Ok(())
    }

    /// wrapper of `healpix_to_lonlat`
    #[pyfn(m, "healpix_to_lonlat")]
    fn healpix_to_lonlat(_py: Python,
        depth: u8,
        ipix: &PyArrayDyn<u64>,
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
                let (l, b) = layer.center(p);
                *lon = l;
                *lat = b;
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

                n[0] = to_i64(map.get(MainWind::S));
                n[1] = to_i64(map.get(MainWind::SE));
                n[2] = to_i64(map.get(MainWind::E));
                n[3] = to_i64(map.get(MainWind::SW));
                n[4] = p as i64;
                n[5] = to_i64(map.get(MainWind::NE));
                n[6] = to_i64(map.get(MainWind::W));
                n[7] = to_i64(map.get(MainWind::NW));
                n[8] = to_i64(map.get(MainWind::N));
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

        if flat {
            let (ipix, depth, fully_covered) = get_flat_cells(bmoc);
            
            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        } else {
            let (ipix, depth, fully_covered) = get_cells(bmoc);

            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        }
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

        if flat {
            let (ipix, depth, fully_covered) = get_flat_cells(bmoc);
            
            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        } else {
            let (ipix, depth, fully_covered) = get_cells(bmoc);

            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        }
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

        if flat {
            let (ipix, depth, fully_covered) = get_flat_cells(bmoc);
            
            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        } else {
            let (ipix, depth, fully_covered) = get_cells(bmoc);

            (ipix.into_pyarray(py).to_owned(),
            depth.into_pyarray(py).to_owned(),
            fully_covered.into_pyarray(py).to_owned())
        }
    }

    Ok(())
}

fn to_i64(val: Option<&u64>) -> i64 {
    match val {
        Some(&val) => val as i64,
        None => -1_i64,
    }
}

fn get_cells(bmoc: healpix::nested::bmoc::BMOC) -> (Array1<u64>, Array1<u8>, Array1<bool>) {
    let ipix: Array1<u64> = bmoc.iter()
        .map(|c| {
            let cell = bmoc.from_raw_value(*c);
            cell.hash
        })
        .collect::<Vec<u64>>()
        .into();
    let depth: Array1<u8> = bmoc.iter()
        .map(|c| {
            let cell = bmoc.from_raw_value(*c);
            cell.depth
        })
        .collect::<Vec<u8>>()
        .into();
    let fully_covered: Array1<bool> = bmoc.iter()
        .map(|c| {
            let cell = bmoc.from_raw_value(*c);
            cell.is_full
        })
        .collect::<Vec<bool>>()
        .into();
    
    (ipix, depth, fully_covered)
}

fn get_flat_cells(bmoc: healpix::nested::bmoc::BMOC) -> (Array1<u64>, Array1<u8>, Array1<bool>) {
    let ipix: Array1<u64> = bmoc.flat_iter_cell()
        .map(|c| c.hash)
        .collect::<Vec<u64>>()
        .into();
    let depth: Array1<u8> = bmoc.flat_iter_cell()
        .map(|c| c.depth)
        .collect::<Vec<u8>>()
        .into();
    let fully_covered: Array1<bool> = bmoc.flat_iter_cell()
        .map(|c| c.is_full)
        .collect::<Vec<bool>>()
        .into();
    
    (ipix, depth, fully_covered)
}