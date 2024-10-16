use ndarray::{Array1, Zip};
use numpy::{IntoPyArray, PyArray1, PyArrayDyn, PyArrayMethods, PyReadonlyArrayDyn};
use pyo3::{
  prelude::{pymodule, Bound, PyModule, PyResult, Python},
  types::PyModuleMethods,
  wrap_pyfunction,
};

use healpix::compass_point::{Cardinal, MainWind, Ordinal};

mod skymap_functions;

/// This uses rust-numpy for numpy interoperability between
/// Python and Rust.
/// PyArrayDyn rust-numpy array types are converted to ndarray
/// compatible array types.
/// ndarray then exposes several numpy-like methods for operating
/// like in python.
/// ndarray also offers a way to zip arrays (immutably and mutably) and
/// operate on them element-wisely. This is done in parallel using the
/// ndarray-parallel crate that offers the par_for_each method on zipped arrays.
#[pymodule]
fn cdshealpix(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
  // add skymap pyfunctions here
  m.add_function(wrap_pyfunction!(skymap_functions::read_skymap, m)?)
    .unwrap();
  m.add_function(wrap_pyfunction!(skymap_functions::write_skymap, m)?)
    .unwrap();
  m.add_function(wrap_pyfunction!(skymap_functions::pixels_skymap, m)?)
    .unwrap();
  m.add_function(wrap_pyfunction!(skymap_functions::depth_skymap, m)?)
    .unwrap();

  // wrapper of to_ring and from_ring
  #[pyfn(m)]
  #[pyo3(name = "to_ring")]
  unsafe fn to_ring<'a>(
    _py: Python,
    depth: u8,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    ipix_ring: &Bound<'a, PyArrayDyn<u64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let ipix = ipix.as_array();
    let mut ipix_ring = ipix_ring.as_array_mut();

    let layer = healpix::nested::get(depth);
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix)
          .and(&mut ipix_ring)
          .par_for_each(|&pix, pix_ring| {
            *pix_ring = layer.to_ring(pix);
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix)
        .and(&mut ipix_ring)
        .for_each(|&pix, pix_ring| {
          *pix_ring = layer.to_ring(pix);
        });
    }
    Ok(())
  }

  #[pyfn(m)]
  unsafe fn from_ring<'a>(
    _py: Python,
    depth: u8,
    ipix_ring: &Bound<'a, PyArrayDyn<u64>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let ipix_ring = ipix_ring.as_array();
    let mut ipix = ipix.as_array_mut();

    let layer = healpix::nested::get(depth);
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix_ring)
          .and(&mut ipix)
          .par_for_each(|&pix_ring, pix| {
            *pix = layer.from_ring(pix_ring);
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix_ring)
        .and(&mut ipix)
        .for_each(|&pix_ring, pix| {
          *pix = layer.from_ring(pix_ring);
        });
    }

    Ok(())
  }

  /// wrapper of `lonlat_to_healpix`
  #[pyfn(m)]
  unsafe fn lonlat_to_healpix<'a>(
    _py: Python,
    depth: &Bound<'a, PyArrayDyn<u8>>,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    dx: &Bound<'a, PyArrayDyn<f64>>,
    dy: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let lon = lon.as_array();
    let lat = lat.as_array();
    let depth = depth.as_array();
    let mut ipix = ipix.as_array_mut();
    let mut dx = dx.as_array_mut();
    let mut dy = dy.as_array_mut();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&mut ipix)
          .and(&mut dx)
          .and(&mut dy)
          .and(&lon)
          .and(&lat)
          .and(&depth)
          .par_for_each(|p, x, y, &lon, &lat, &d| {
            let r = healpix::nested::hash_with_dxdy(d, lon, lat);
            *p = r.0;
            *x = r.1;
            *y = r.2;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&mut ipix)
        .and(&mut dx)
        .and(&mut dy)
        .and(&lon)
        .and(&lat)
        .and(&depth)
        .for_each(|p, x, y, &lon, &lat, &d| {
          let r = healpix::nested::hash_with_dxdy(d, lon, lat);
          *p = r.0;
          *x = r.1;
          *y = r.2;
        });
    }

    Ok(())
  }

  #[pyfn(m)]
  unsafe fn lonlat_to_healpix_ring<'a>(
    _py: Python,
    nside: &Bound<'a, PyArrayDyn<u32>>,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    dx: &Bound<'a, PyArrayDyn<f64>>,
    dy: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let lon = lon.as_array();
    let lat = lat.as_array();
    let nside = nside.as_array();
    let mut ipix = ipix.as_array_mut();
    let mut dx = dx.as_array_mut();
    let mut dy = dy.as_array_mut();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&mut ipix)
          .and(&mut dx)
          .and(&mut dy)
          .and(&lon)
          .and(&lat)
          .and(&nside)
          .par_for_each(|p, x, y, &lon, &lat, &n| {
            let r = healpix::ring::hash_with_dxdy(n, lon, lat);
            *p = r.0;
            *x = r.1;
            *y = r.2;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&mut ipix)
        .and(&mut dx)
        .and(&mut dy)
        .and(&lon)
        .and(&lat)
        .and(&nside)
        .for_each(|p, x, y, &lon, &lat, &n| {
          let r = healpix::ring::hash_with_dxdy(n, lon, lat);
          *p = r.0;
          *x = r.1;
          *y = r.2;
        });
    }
    Ok(())
  }

  /// wrapper of `healpix_to_lonlat`
  #[pyfn(m)]
  unsafe fn healpix_to_lonlat<'a>(
    _py: Python,
    depth: &Bound<'a, PyArrayDyn<u8>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    dx: f64,
    dy: f64,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let mut lon = lon.as_array_mut();
    let mut lat = lat.as_array_mut();
    let ipix = ipix.as_array();
    let depth = depth.as_array();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix)
          .and(&depth)
          .and(&mut lon)
          .and(&mut lat)
          .par_for_each(|&p, &d, lon, lat| {
            let (l, b) = healpix::nested::sph_coo(d, p, dx, dy);
            *lon = l;
            *lat = b;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix)
        .and(&depth)
        .and(&mut lon)
        .and(&mut lat)
        .for_each(|&p, &d, lon, lat| {
          let (l, b) = healpix::nested::sph_coo(d, p, dx, dy);
          *lon = l;
          *lat = b;
        });
    }
    Ok(())
  }

  #[pyfn(m)]
  unsafe fn healpix_to_lonlat_ring<'a>(
    _py: Python,
    nside: &Bound<'a, PyArrayDyn<u32>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    dx: f64,
    dy: f64,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let mut lon = lon.as_array_mut();
    let mut lat = lat.as_array_mut();
    let ipix = ipix.as_array();
    let nside = nside.as_array();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix)
          .and(&nside)
          .and(&mut lon)
          .and(&mut lat)
          .par_for_each(|&p, &n, lon, lat| {
            let (l, b) = healpix::ring::sph_coo(n, p, dx, dy);
            *lon = l;
            *lat = b;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix)
        .and(&nside)
        .and(&mut lon)
        .and(&mut lat)
        .for_each(|&p, &n, lon, lat| {
          let (l, b) = healpix::ring::sph_coo(n, p, dx, dy);
          *lon = l;
          *lat = b;
        });
    }
    Ok(())
  }

  /// wrapper of `healpix_to_xy`
  #[pyfn(m)]
  unsafe fn healpix_to_xy<'a>(
    _py: Python,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    depth: &Bound<'a, PyArrayDyn<u8>>,
    x: &Bound<'a, PyArrayDyn<f64>>,
    y: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let mut x = x.as_array_mut();
    let mut y = y.as_array_mut();
    let ipix = ipix.as_array();
    let depth = depth.as_array();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix)
          .and(&depth)
          .and(&mut x)
          .and(&mut y)
          .par_for_each(|&p, &d, hpx, hpy| {
            let layer = healpix::nested::get(d);
            let (x, y) = layer.center_of_projected_cell(p);
            *hpx = x;
            *hpy = y;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix)
        .and(&depth)
        .and(&mut x)
        .and(&mut y)
        .for_each(|&p, &d, hpx, hpy| {
          let layer = healpix::nested::get(d);
          let (x, y) = layer.center_of_projected_cell(p);
          *hpx = x;
          *hpy = y;
        });
    }
    Ok(())
  }

  #[pyfn(m)]
  unsafe fn healpix_to_xy_ring<'a>(
    _py: Python,
    nside: &Bound<'a, PyArrayDyn<u32>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    x: &Bound<'a, PyArrayDyn<f64>>,
    y: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let mut x = x.as_array_mut();
    let mut y = y.as_array_mut();
    let ipix = ipix.as_array();
    let nside = nside.as_array();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&ipix)
          .and(&nside)
          .and(&mut x)
          .and(&mut y)
          .par_for_each(|&p, &n, hpx, hpy| {
            let (x, y) = healpix::ring::center_of_projected_cell(n, p);
            *hpx = x;
            *hpy = y;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&ipix)
        .and(&nside)
        .and(&mut x)
        .and(&mut y)
        .for_each(|&p, &n, hpx, hpy| {
          let (x, y) = healpix::ring::center_of_projected_cell(n, p);
          *hpx = x;
          *hpy = y;
        });
    }
    Ok(())
  }

  /// wrapper of `lonlat_to_xy`
  #[pyfn(m)]
  unsafe fn lonlat_to_xy<'a>(
    _py: Python,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    x: &Bound<'a, PyArrayDyn<f64>>,
    y: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let mut x = x.as_array_mut();
    let mut y = y.as_array_mut();
    let lon = lon.as_array();
    let lat = lat.as_array();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&lon)
          .and(&lat)
          .and(&mut x)
          .and(&mut y)
          .par_for_each(|&l, &b, hpx, hpy| {
            let (x, y) = healpix::proj(l, b);
            *hpx = x;
            *hpy = y;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&lon)
        .and(&lat)
        .and(&mut x)
        .and(&mut y)
        .for_each(|&l, &b, hpx, hpy| {
          let (x, y) = healpix::proj(l, b);
          *hpx = x;
          *hpy = y;
        });
    }
    Ok(())
  }

  /// wrapper of `xy_to_lonlat`
  #[pyfn(m)]
  unsafe fn xy_to_lonlat<'a>(
    _py: Python,
    x: &Bound<'a, PyArrayDyn<f64>>,
    y: &Bound<'a, PyArrayDyn<f64>>,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let x = x.as_array();
    let y = y.as_array();
    let mut lon = lon.as_array_mut();
    let mut lat = lat.as_array_mut();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(&x)
          .and(&y)
          .and(&mut lon)
          .and(&mut lat)
          .par_for_each(|&hpx, &hpy, l, b| {
            let r = healpix::unproj(hpx, hpy);
            *l = r.0;
            *b = r.1;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(&x)
        .and(&y)
        .and(&mut lon)
        .and(&mut lat)
        .for_each(|&hpx, &hpy, l, b| {
          let r = healpix::unproj(hpx, hpy);
          *l = r.0;
          *b = r.1;
        });
    }
    Ok(())
  }

  /// wrapper of `vertices`
  #[pyfn(m)]
  unsafe fn vertices<'a>(
    _py: Python,
    depth: &Bound<'a, PyArrayDyn<u8>>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    step: usize,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let depth = depth.as_array();
    let ipix = ipix.as_array();
    let mut lon = lon.as_array_mut();
    let mut lat = lat.as_array_mut();

    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        if step == 1 {
          Zip::from(lon.rows_mut())
            .and(lat.rows_mut())
            .and(&ipix)
            .and(&depth)
            .par_for_each(|mut lon, mut lat, &p, &d| {
              let [(s_lon, s_lat), (e_lon, e_lat), (n_lon, n_lat), (w_lon, w_lat)] =
                healpix::nested::vertices(d, p);
              lon[0] = s_lon;
              lat[0] = s_lat;

              lon[1] = e_lon;
              lat[1] = e_lat;

              lon[2] = n_lon;
              lat[2] = n_lat;

              lon[3] = w_lon;
              lat[3] = w_lat;
            });
        } else {
          Zip::from(lon.rows_mut())
            .and(lat.rows_mut())
            .and(&ipix)
            .and(&depth)
            .par_for_each(|mut lon, mut lat, &p, &d| {
              let r = healpix::nested::path_along_cell_edge(d, p, &Cardinal::S, false, step as u32);

              for i in 0..(4 * step) {
                let (l, b) = r[i];
                lon[i] = l;
                lat[i] = b;
              }
            });
        }
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      if step == 1 {
        Zip::from(lon.rows_mut())
          .and(lat.rows_mut())
          .and(&ipix)
          .and(&depth)
          .for_each(|mut lon, mut lat, &p, &d| {
            let [(s_lon, s_lat), (e_lon, e_lat), (n_lon, n_lat), (w_lon, w_lat)] =
              healpix::nested::vertices(d, p);
            lon[0] = s_lon;
            lat[0] = s_lat;

            lon[1] = e_lon;
            lat[1] = e_lat;

            lon[2] = n_lon;
            lat[2] = n_lat;

            lon[3] = w_lon;
            lat[3] = w_lat;
          });
      } else {
        Zip::from(lon.rows_mut())
          .and(lat.rows_mut())
          .and(&ipix)
          .and(&depth)
          .for_each(|mut lon, mut lat, &p, &d| {
            let r = healpix::nested::path_along_cell_edge(d, p, &Cardinal::S, false, step as u32);

            for i in 0..(4 * step) {
              let (l, b) = r[i];
              lon[i] = l;
              lat[i] = b;
            }
          });
      }
    }

    Ok(())
  }

  #[pyfn(m)]
  unsafe fn vertices_ring<'a>(
    _py: Python,
    nside: u32,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    _step: usize,
    lon: &Bound<'a, PyArrayDyn<f64>>,
    lat: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let ipix = ipix.as_array();
    let mut lon = lon.as_array_mut();
    let mut lat = lat.as_array_mut();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(lon.rows_mut())
          .and(lat.rows_mut())
          .and(&ipix)
          .par_for_each(|mut lon, mut lat, &p| {
            let [(s_lon, s_lat), (e_lon, e_lat), (n_lon, n_lat), (w_lon, w_lat)] =
              healpix::ring::vertices(nside, p);
            lon[0] = s_lon;
            lat[0] = s_lat;

            lon[1] = e_lon;
            lat[1] = e_lat;

            lon[2] = n_lon;
            lat[2] = n_lat;

            lon[3] = w_lon;
            lat[3] = w_lat;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(lon.rows_mut())
        .and(lat.rows_mut())
        .and(&ipix)
        .for_each(|mut lon, mut lat, &p| {
          let [(s_lon, s_lat), (e_lon, e_lat), (n_lon, n_lat), (w_lon, w_lat)] =
            healpix::ring::vertices(nside, p);
          lon[0] = s_lon;
          lat[0] = s_lat;

          lon[1] = e_lon;
          lat[1] = e_lat;

          lon[2] = n_lon;
          lat[2] = n_lat;

          lon[3] = w_lon;
          lat[3] = w_lat;
        });
    }
    Ok(())
  }

  /// Wrapper of `neighbours`
  /// The given array must be of size 9
  /// `[S, SE, E, SW, C, NE, W, NW, N]`
  #[pyfn(m)]
  unsafe fn neighbours<'a>(
    _py: Python,
    depth: u8,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    neighbours: &Bound<'a, PyArrayDyn<i64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let ipix = ipix.as_array();
    let mut neighbours = neighbours.as_array_mut();
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(neighbours.rows_mut())
          .and(&ipix)
          .par_for_each(|mut n, &p| {
            let map = healpix::nested::neighbours(depth, p, true);

            n[0] = map
              .get(MainWind::S)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[1] = map
              .get(MainWind::SE)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[2] = map
              .get(MainWind::E)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[3] = map
              .get(MainWind::SW)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[4] = p as i64;
            n[5] = map
              .get(MainWind::NE)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[6] = map
              .get(MainWind::W)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[7] = map
              .get(MainWind::NW)
              .map_or_else(|| -1_i64, |&val| val as i64);
            n[8] = map
              .get(MainWind::N)
              .map_or_else(|| -1_i64, |&val| val as i64);
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(neighbours.rows_mut())
        .and(&ipix)
        .for_each(|mut n, &p| {
          let map = healpix::nested::neighbours(depth, p, true);

          n[0] = map
            .get(MainWind::S)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[1] = map
            .get(MainWind::SE)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[2] = map
            .get(MainWind::E)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[3] = map
            .get(MainWind::SW)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[4] = p as i64;
          n[5] = map
            .get(MainWind::NE)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[6] = map
            .get(MainWind::W)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[7] = map
            .get(MainWind::NW)
            .map_or_else(|| -1_i64, |&val| val as i64);
          n[8] = map
            .get(MainWind::N)
            .map_or_else(|| -1_i64, |&val| val as i64);
        });
    }
    Ok(())
  }

  /// Cone search
  #[pyfn(m)]
  fn cone_search(
    py: Python<'_>,
    depth: u8,
    delta_depth: u8,
    lon: f64,
    lat: f64,
    radius: f64,
    flat: bool,
  ) -> (
    Bound<'_, PyArray1<u64>>,
    Bound<'_, PyArray1<u8>>,
    Bound<'_, PyArray1<bool>>,
  ) {
    let bmoc = healpix::nested::cone_coverage_approx_custom(depth, delta_depth, lon, lat, radius);

    let (ipix, depth, fully_covered) = if flat {
      get_flat_cells(bmoc)
    } else {
      get_cells(bmoc)
    };

    (
      ipix.into_pyarray_bound(py),
      depth.into_pyarray_bound(py),
      fully_covered.into_pyarray_bound(py),
    )
  }

  /// Elliptical cone search
  #[pyfn(m)]
  fn elliptical_cone_search(
    py: Python<'_>,
    depth: u8,
    delta_depth: u8,
    lon: f64,
    lat: f64,
    a: f64,
    b: f64,
    pa: f64,
    flat: bool,
  ) -> (
    Bound<'_, PyArray1<u64>>,
    Bound<'_, PyArray1<u8>>,
    Bound<'_, PyArray1<bool>>,
  ) {
    let bmoc =
      healpix::nested::elliptical_cone_coverage_custom(depth, delta_depth, lon, lat, a, b, pa);

    let (ipix, depth, fully_covered) = if flat {
      get_flat_cells(bmoc)
    } else {
      get_cells(bmoc)
    };

    (
      ipix.into_pyarray_bound(py),
      depth.into_pyarray_bound(py),
      fully_covered.into_pyarray_bound(py),
    )
  }

  /// Polygon search
  #[pyfn(m)]
  unsafe fn polygon_search<'a>(
    py: Python<'a>,
    depth: u8,
    lon: PyReadonlyArrayDyn<'a, f64>,
    lat: PyReadonlyArrayDyn<'a, f64>,
    flat: bool,
  ) -> (
    Bound<'a, PyArray1<u64>>,
    Bound<'a, PyArray1<u8>>,
    Bound<'a, PyArray1<bool>>,
  ) {
    let lon = lon.as_array();
    let lat = lat.as_array();

    // Stack the longitude and latitudes and store them in a
    // Vec<(f64, f64)>
    let vertices = lon
      .iter()
      .zip(lat.iter())
      .map(|(&lon, &lat)| (lon, lat))
      .collect::<Vec<(f64, f64)>>();

    let bmoc = healpix::nested::polygon_coverage(depth, &vertices.into_boxed_slice(), true);

    let (ipix, depth, fully_covered) = if flat {
      get_flat_cells(bmoc)
    } else {
      get_cells(bmoc)
    };

    (
      ipix.into_pyarray_bound(py),
      depth.into_pyarray_bound(py),
      fully_covered.into_pyarray_bound(py),
    )
  }

  /// A box is defined by a center, two angles on the sides
  /// and one rotation angle. Its sides follow great circles.
  ///
  /// # Arguments
  ///
  /// * ``depth``
  /// * ``lon`` - center longitude, in degrees
  /// * ``lat`` - center latitude in degrees
  /// * ``a`` - size in degrees
  /// * ``b`` - size in degrees
  /// * ``pa`` -rotation angle in degrees
  #[pyfn(m)]
  fn box_search(
    py: Python<'_>,
    depth: u8,
    lon: f64,
    lat: f64,
    a: f64,
    b: f64,
    pa: f64,
    flat: bool,
  ) -> (
    Bound<'_, PyArray1<u64>>,
    Bound<'_, PyArray1<u8>>,
    Bound<'_, PyArray1<bool>>,
  ) {
    let bmoc = healpix::nested::box_coverage(depth, lon, lat, a, b, pa);

    let (ipix, depth, fully_covered) = if flat {
      get_flat_cells(bmoc)
    } else {
      get_cells(bmoc)
    };

    (
      ipix.into_pyarray_bound(py),
      depth.into_pyarray_bound(py),
      fully_covered.into_pyarray_bound(py),
    )
  }

  /// A zone is defined by its corners. Its sides follow great circles along the
  /// north/south axis and small circles along the east/west axis.
  ///
  /// # Arguments
  ///
  /// * ``depth``
  /// * ``lon_min`` - west south corner longitude
  /// * ``lat_min`` - west south corner latitude
  /// * ``lon_max`` - east north corner longitude
  /// * ``lat_max`` - east north corner latitude
  #[pyfn(m)]
  fn zone_search(
    py: Python<'_>,
    depth: u8,
    lon_min: f64,
    lat_min: f64,
    lon_max: f64,
    lat_max: f64,
    flat: bool,
  ) -> (
    Bound<'_, PyArray1<u64>>,
    Bound<'_, PyArray1<u8>>,
    Bound<'_, PyArray1<bool>>,
  ) {
    let bmoc = healpix::nested::zone_coverage(depth, lon_min, lat_min, lon_max, lat_max);

    let (ipix, depth, fully_covered) = if flat {
      get_flat_cells(bmoc)
    } else {
      get_cells(bmoc)
    };

    (
      ipix.into_pyarray_bound(py),
      depth.into_pyarray_bound(py),
      fully_covered.into_pyarray_bound(py),
    )
  }

  #[pyfn(m)]
  unsafe fn external_neighbours<'a>(
    _py: Python,
    depth: u8,
    delta_depth: u8,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    corners: &Bound<'a, PyArrayDyn<i64>>,
    edges: &Bound<'a, PyArrayDyn<u64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let ipix = ipix.as_array();

    let mut corners = corners.as_array_mut();
    let mut edges = edges.as_array_mut();

    let layer = healpix::nested::get(depth);
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(corners.rows_mut())
          .and(edges.rows_mut())
          .and(&ipix)
          .par_for_each(|mut c, mut e, &p| {
            let external_edges = layer.external_edge_struct(p, delta_depth);

            c[0] = external_edges
              .get_corner(&Cardinal::S)
              .map_or_else(|| -1_i64, |val| val as i64);
            c[1] = external_edges
              .get_corner(&Cardinal::E)
              .map_or_else(|| -1_i64, |val| val as i64);
            c[2] = external_edges
              .get_corner(&Cardinal::N)
              .map_or_else(|| -1_i64, |val| val as i64);
            c[3] = external_edges
              .get_corner(&Cardinal::W)
              .map_or_else(|| -1_i64, |val| val as i64);

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
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(corners.rows_mut())
        .and(edges.rows_mut())
        .and(&ipix)
        .for_each(|mut c, mut e, &p| {
          let external_edges = layer.external_edge_struct(p, delta_depth);

          c[0] = external_edges
            .get_corner(&Cardinal::S)
            .map_or_else(|| -1_i64, |val| val as i64);
          c[1] = external_edges
            .get_corner(&Cardinal::E)
            .map_or_else(|| -1_i64, |val| val as i64);
          c[2] = external_edges
            .get_corner(&Cardinal::N)
            .map_or_else(|| -1_i64, |val| val as i64);
          c[3] = external_edges
            .get_corner(&Cardinal::W)
            .map_or_else(|| -1_i64, |val| val as i64);

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
        })
    }
    Ok(())
  }

  ////////////////////////////
  // Bilinear interpolation //
  ////////////////////////////
  #[pyfn(m)]
  fn bilinear_interpolation<'a>(
    depth: u8,
    lon: PyReadonlyArrayDyn<'a, f64>,
    lat: PyReadonlyArrayDyn<'a, f64>,
    ipix: &Bound<'a, PyArrayDyn<u64>>,
    weights: &Bound<'a, PyArrayDyn<f64>>,
    nthreads: u16,
  ) -> PyResult<()> {
    let lon = lon.as_array();
    let lat = lat.as_array();

    let mut ipix = unsafe { ipix.as_array_mut() };
    let mut weights = unsafe { weights.as_array_mut() };

    let layer = healpix::nested::get(depth);
    #[cfg(not(target_arch = "wasm32"))]
    {
      let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(nthreads as usize)
        .build()
        .unwrap();
      pool.install(|| {
        Zip::from(ipix.rows_mut())
          .and(weights.rows_mut())
          .and(&lon)
          .and(&lat)
          .par_for_each(|mut pix, mut w, &l, &b| {
            let [(p1, w1), (p2, w2), (p3, w3), (p4, w4)] = layer.bilinear_interpolation(l, b);

            pix[0] = p1;
            pix[1] = p2;
            pix[2] = p3;
            pix[3] = p4;

            w[0] = w1;
            w[1] = w2;
            w[2] = w3;
            w[3] = w4;
          })
      });
    }
    #[cfg(target_arch = "wasm32")]
    {
      Zip::from(ipix.rows_mut())
        .and(weights.rows_mut())
        .and(&lon)
        .and(&lat)
        .for_each(|mut pix, mut w, &l, &b| {
          let [(p1, w1), (p2, w2), (p3, w3), (p4, w4)] = layer.bilinear_interpolation(l, b);

          pix[0] = p1;
          pix[1] = p2;
          pix[2] = p3;
          pix[3] = p4;

          w[0] = w1;
          w[1] = w2;
          w[2] = w3;
          w[3] = w4;
        });
    }
    Ok(())
  }

  Ok(())
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
