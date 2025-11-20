use std::{
  fs::File,
  io::BufReader,
  io::{BufWriter, Cursor},
};

use numpy::{
  IntoPyArray, Ix3, NotContiguousError, PyArray1, PyArray3, PyArrayMethods, PyReadonlyArray1,
};
use pyo3::{
  exceptions::{PyIOError, PyValueError},
  prelude::*,
  types::{PyAny, PyModule, PyTuple},
  Bound, PyErr, PyResult,
};

use healpix::{
  depth_from_n_hash_unsafe,
  nested::map::{
    fits::write::{write_explicit_skymap_fits_from_parts, write_implicit_skymap_fits},
    img::{to_skymap_img_default, PosConversion, Val},
    skymap::{implicit::ImplicitSkyMapArrayRef, SkyMap, SkyMapEnum, SkyMapValue},
  },
};

#[pyfunction]
#[pyo3(pass_module)]
pub fn read_skymap_implicit<'py>(
  module: &Bound<'py, PyModule>,
  bytes: &[u8],
) -> PyResult<Bound<'py, PyAny>> {
  SkyMapEnum::from_fits(BufReader::new(Cursor::new(bytes)))
    .map_err(|err| PyIOError::new_err(err.to_string()))
    .and_then(|sky_map_enum| match sky_map_enum {
      SkyMapEnum::ImplicitU64U8(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<u8>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      SkyMapEnum::ImplicitU64I16(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<i16>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      SkyMapEnum::ImplicitU64I32(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<i32>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      SkyMapEnum::ImplicitU64I64(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<i64>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      SkyMapEnum::ImplicitU64F32(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<f32>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      SkyMapEnum::ImplicitU64F64(s) => Ok(
        s.values()
          .copied()
          .collect::<Vec<f64>>()
          .into_pyarray(module.py())
          .into_any(),
      ),
      _ => Err(PyIOError::new_err(
        "Implicit skymap not recognized, try explicit?",
      )),
    })
}

#[pyfunction]
#[pyo3(pass_module)]
pub fn read_skymap_explicit<'py>(
  module: &Bound<'py, PyModule>,
  bytes: &[u8],
) -> PyResult<Bound<'py, PyTuple>> {
  SkyMapEnum::from_fits(BufReader::new(Cursor::new(bytes)))
    .map_err(|err| PyIOError::new_err(err.to_string()))
    .and_then(|sky_map_enum| match sky_map_enum {
      // Explicit U32
      SkyMapEnum::ExplicitU32U8(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, u8, Vec<u64>, Vec<u8>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU32I16(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, i16, Vec<u64>, Vec<i16>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU32I32(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, i32, Vec<u64>, Vec<i32>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU32I64(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, i64, Vec<u64>, Vec<i64>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU32F32(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, f32, Vec<u64>, Vec<f32>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU32F64(s) => s
        .owned_entries()
        .map(|(k, v)| (k as u64, v))
        .unzip::<u64, f64, Vec<u64>, Vec<f64>>()
        .into_pyobject(module.py()),
      // Explicit U64
      SkyMapEnum::ExplicitU64U8(s) => s
        .owned_entries()
        .unzip::<u64, u8, Vec<u64>, Vec<u8>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU64I16(s) => s
        .owned_entries()
        .unzip::<u64, i16, Vec<u64>, Vec<i16>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU64I32(s) => s
        .owned_entries()
        .unzip::<u64, i32, Vec<u64>, Vec<i32>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU64I64(s) => s
        .owned_entries()
        .unzip::<u64, i64, Vec<u64>, Vec<i64>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU64F32(s) => s
        .owned_entries()
        .unzip::<u64, f32, Vec<u64>, Vec<f32>>()
        .into_pyobject(module.py()),
      SkyMapEnum::ExplicitU64F64(s) => s
        .owned_entries()
        .unzip::<u64, f64, Vec<u64>, Vec<f64>>()
        .into_pyobject(module.py()),
      _ => Err(PyIOError::new_err(
        "Explicit skymap not recognized, try implicit?",
      )),
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
impl<'py> SupportedArray<'py> {
  fn n_hash(&self) -> u64 {
    let n = match self {
      SupportedArray::F64(values) => values.as_array().shape()[0],
      SupportedArray::I64(values) => values.as_array().shape()[0],
      SupportedArray::F32(values) => values.as_array().shape()[0],
      SupportedArray::I32(values) => values.as_array().shape()[0],
      SupportedArray::I16(values) => values.as_array().shape()[0],
      SupportedArray::U8(values) => values.as_array().shape()[0],
    };
    n as u64
  }
}

#[pyfunction]
pub fn write_skymap_implicit(values: SupportedArray<'_>, path: String) -> Result<(), PyErr> {
  let writer =
    BufWriter::new(File::create(path).map_err(|err| PyIOError::new_err(err.to_string()))?);
  match values {
    SupportedArray::F64(values) => write_skymap_implicit_gen(writer, values.as_slice()),
    SupportedArray::I64(values) => write_skymap_implicit_gen(writer, values.as_slice()),
    SupportedArray::F32(values) => write_skymap_implicit_gen(writer, values.as_slice()),
    SupportedArray::I32(values) => write_skymap_implicit_gen(writer, values.as_slice()),
    SupportedArray::I16(values) => write_skymap_implicit_gen(writer, values.as_slice()),
    SupportedArray::U8(values) => write_skymap_implicit_gen(writer, values.as_slice()),
  }
}
fn write_skymap_implicit_gen<T: SkyMapValue>(
  writer: BufWriter<File>,
  as_slice_res: Result<&[T], NotContiguousError>,
) -> Result<(), PyErr> {
  as_slice_res.map_err(move |e| e.into()).and_then(|slice| {
    write_implicit_skymap_fits(writer, slice).map_err(|err| PyIOError::new_err(err.to_string()))
  })
}

#[pyfunction]
// #[pyo3(pass_module)]
pub fn write_skymap_explicit<'py>(
  // module: &Bound<'py, PyModule>,
  depth: u8,
  keys: PyReadonlyArray1<'py, u64>,
  values: SupportedArray<'_>,
  path: String,
) -> Result<(), PyErr> {
  let writer =
    BufWriter::new(File::create(path).map_err(|err| PyIOError::new_err(err.to_string()))?);
  let keys = keys.as_slice()?;
  match values {
    SupportedArray::F64(values) => {
      write_skymap_explicit_gen(writer, depth, keys, values.as_slice())
    }
    SupportedArray::I64(values) => {
      write_skymap_explicit_gen(writer, depth, keys, values.as_slice())
    }
    SupportedArray::F32(values) => {
      write_skymap_explicit_gen(writer, depth, keys, values.as_slice())
    }
    SupportedArray::I32(values) => {
      write_skymap_explicit_gen(writer, depth, keys, values.as_slice())
    }
    SupportedArray::I16(values) => {
      write_skymap_explicit_gen(writer, depth, keys, values.as_slice())
    }
    SupportedArray::U8(values) => write_skymap_explicit_gen(writer, depth, keys, values.as_slice()),
  }
}
fn write_skymap_explicit_gen<T: SkyMapValue>(
  writer: BufWriter<File>,
  depth: u8,
  keys: &[u64],
  values: Result<&[T], NotContiguousError>,
) -> Result<(), PyErr> {
  values.map_err(move |e| e.into()).and_then(|values| {
    write_explicit_skymap_fits_from_parts(
      writer,
      depth,
      keys.len(),
      keys.iter().cloned(),
      values.iter().cloned(),
    )
    .map_err(|err| PyIOError::new_err(err.to_string()))
  })
}

#[pyfunction]
#[pyo3(pass_module)]
pub fn pixels_skymap_implicit<'py>(
  module: &Bound<'py, PyModule>,
  values: SupportedArray<'py>,
  image_size: u16,
  convert_to_gal: bool,
) -> PyResult<Bound<'py, PyArray3<u8>>> {
  let n_hash = values.n_hash();
  let depth = depth_from_n_hash_unsafe(n_hash);
  // we have to use https://github.com/cds-astro/cds-healpix-rust/blob/847ae35945708efb6b949c3d15b3726ab7adeb2f/src/nested/map/img.rs#L391
  match values {
    SupportedArray::F64(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, f64>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
    SupportedArray::I64(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, i64>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
    SupportedArray::F32(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, f32>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
    SupportedArray::I32(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, i32>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
    SupportedArray::I16(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, i16>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
    SupportedArray::U8(values) => values.as_slice().map_err(|e| e.into()).and_then(|v| {
      skymap_ref_to_img(
        &ImplicitSkyMapArrayRef::<'_, u64, u8>::new(depth, v),
        image_size,
        convert_to_gal,
        module.py(),
      )
    }),
  }
}

fn skymap_ref_to_img<'py, 'a, S>(
  skymap: &'a S,
  image_size: u16,
  convert_to_gal: bool,
  py: Python<'py>,
) -> PyResult<Bound<'py, PyArray3<u8>>>
where
  S: SkyMap<'a> + 'a,
  S::ValueType: Val,
{
  if convert_to_gal {
    let vec = to_skymap_img_default(
      skymap,
      (image_size << 1, image_size),
      None,
      None,
      Some(PosConversion::EqMap2GalImg),
      None,
      None,
    )
    .map_err(|e| PyValueError::new_err(e.to_string()))?;
    PyArray1::from_slice(py, vec.as_slice()).reshape(Ix3(
      image_size as usize,
      (image_size << 1) as usize,
      4_usize,
    ))
  } else {
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
    PyArray1::from_slice(py, vec.as_slice()).reshape(Ix3(
      image_size as usize,
      (image_size << 1) as usize,
      4_usize,
    ))
  }
}

#[pyfunction]
pub fn depth_skymap_implicit(values: SupportedArray) -> u8 {
  depth_from_n_hash_unsafe(values.n_hash())
}
