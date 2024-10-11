extern crate healpix;

use std::i64;

use numpy::IntoPyArray;
use pyo3::{
  exceptions::PyIOError,
  prelude::*,
  types::{PyAny, PyModule},
  Bound, PyResult,
};

use healpix::nested::map::skymap::{SkyMap, SkyMapEnum};

#[pyfunction]
#[pyo3(pass_module)]
pub fn read_skymap<'py>(
  module: &Bound<'py, PyModule>,
  path: String,
) -> PyResult<Bound<'py, PyAny>> {
  SkyMapEnum::from_fits_file(path.to_string())
    .map_err(|err| PyIOError::new_err(err.to_string()))
    .map(|sky_map_enum| match sky_map_enum {
      SkyMapEnum::ImplicitU64U8(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<u8>>()
        .into_pyarray_bound(module.py())
        .into_any(),
      SkyMapEnum::ImplicitU64I16(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<i16>>()
        .into_pyarray_bound(module.py())
        .into_any(),
      SkyMapEnum::ImplicitU64I32(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<i32>>()
        .into_pyarray_bound(module.py())
        .into_any(),
      SkyMapEnum::ImplicitU64I64(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<i64>>()
        .into_pyarray_bound(module.py())
        .into_any(),
      SkyMapEnum::ImplicitU64F32(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<f32>>()
        .into_pyarray_bound(module.py())
        .into_any(),
      SkyMapEnum::ImplicitU64F64(s) => s
        .values()
        .map(|v| *v)
        .collect::<Vec<f64>>()
        .into_pyarray_bound(module.py())
        .into_any(),
    })
}
