extern crate healpix;
extern crate mapproj;

use std::fs::File;
use std::i64;

use numpy::{IntoPyArray, Ix3, PyArray1, PyArray3, PyArrayMethods, PyReadonlyArray1};
use pyo3::{
  exceptions::{PyIOError, PyValueError},
  prelude::*,
  types::{PyAny, PyModule},
  Bound, PyErr, PyResult,
};

use healpix::{
  depth_from_n_hash_unsafe,
  nested::map::{
    fits::write::write_implicit_skymap_fits,
    img::{to_skymap_img_default, Val},
    skymap::{ImplicitSkyMapArrayRef, SkyMap, SkyMapEnum},
    HHash,
  },
};
use mapproj::pseudocyl::mol::Mol;

use crate::cdshealpix;

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

#[pyfunction]
#[pyo3(pass_module)]
pub fn pixels_skymap<'py>(
  module: &Bound<'py, PyModule>,
  values: SupportedArray<'py>,
  image_size: u16,
) -> PyResult<Bound<'py, PyArray3<u8>>> {
  let n_hash: u64 = match &values {
    SupportedArray::F64(values) => values.as_array().shape()[0] as u64,
    SupportedArray::I64(values) => values.as_array().shape()[0] as u64,
    SupportedArray::F32(values) => values.as_array().shape()[0] as u64,
    SupportedArray::I32(values) => values.as_array().shape()[0] as u64,
    SupportedArray::I16(values) => values.as_array().shape()[0] as u64,
    SupportedArray::U8(values) => values.as_array().shape()[0] as u64,
  };
  let depth: u8 = depth_from_n_hash_unsafe(n_hash);
  // we have to use https://github.com/cds-astro/cds-healpix-rust/blob/847ae35945708efb6b949c3d15b3726ab7adeb2f/src/nested/map/img.rs#L391
  match values {
    SupportedArray::F64(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_,u64,f64>::new(depth, v),
        image_size,
        module.py(),
      )
    }),
    /*SupportedArray::I64(values) => ImplicitSkyMapArrayRef::new(depth, values.as_array()),
    SupportedArray::F32(values) => ImplicitSkyMapArrayRef::new(depth, values.as_slice()),
    SupportedArray::I32(values) => ImplicitSkyMapArrayRef::new(depth, values.as_slice()),
    SupportedArray::I16(values) => ImplicitSkyMapArrayRef::new(depth, values.as_slice()),
    SupportedArray::U8(values) => ImplicitSkyMapArrayRef::new(depth, values.as_slice()),*/
    _ => todo!(),
  }
}

fn skymap_ref_to_img<'py, 'a, S>(
  skymap: &'a S,
  image_size: u16,
  py: Python<'py>,
) -> PyResult<Bound<'py, PyArray3<u8>>>
where
  S: SkyMap<'a> + 'a,
  S::ValueType: Val,
{
  let vec = to_skymap_img_default(
    skymap,
    (image_size << 1, image_size),
    None,
    None,
    None,
    None,
    None,
  )
  .map_err(|e| PyValueError::new_err(e.to_string()))?;
  PyArray1::from_slice_bound(py, vec.as_slice()).reshape(Ix3(
    image_size as usize,
    (image_size << 1) as usize,
    4_usize,
  ))
}
