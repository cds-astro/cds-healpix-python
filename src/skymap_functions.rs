extern crate healpix;

use std::fs::File;
use std::i64;

use numpy::{IntoPyArray, PyReadonlyArray1};
use pyo3::{
  exceptions::PyIOError,
  prelude::*,
  types::{PyAny, PyModule},
  Bound, PyErr, PyResult,
};

use healpix::nested::map::{
  fits::write::write_implicit_skymap_fits,
  skymap::{SkyMap, SkyMapEnum},
};

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

// we define an enum for the supported numpy dtypes
#[derive(FromPyObject)]
pub enum SupportedArray<'py> {
  F64(PyReadonlyArray1<'py, f64>),
  I64(PyReadonlyArray1<'py, i64>),
  F32(PyReadonlyArray1<'py, f32>),
  I32(PyReadonlyArray1<'py, i32>),
  I16(PyReadonlyArray1<'py, i16>),
  U8(PyReadonlyArray1<'py, u8>),
}

#[pyfunction]
pub fn write_skymap<'py>(values: SupportedArray<'py>, path: String) -> Result<(), PyErr> {
  let writer = File::create(path).map_err(|err| PyIOError::new_err(err.to_string()))?;
  match values {
    SupportedArray::F64(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
    SupportedArray::I64(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
    SupportedArray::F32(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
    SupportedArray::I32(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
    SupportedArray::I16(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
    SupportedArray::U8(values) => values.as_slice().map_err(|e| e.into()).and_then(|slice| {
      write_implicit_skymap_fits(writer, slice)
        .map_err(|err| PyIOError::new_err(err.to_string()).into())
    }),
  }
}
