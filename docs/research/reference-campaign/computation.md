# Numerical machinery, CPU/NVIDIA execution and compatibility

2026-09-25. Broad expedition for bucket 1 and the six core responsibilities in
[the working outline](../core-program-outline.md). CPU and NVIDIA are alpha
requirements; AMD is a second-wave objective. No backend is selected.

**This acquisition supports overall design. Each subsystem needs a focused deep
expedition and scientific re-grounding before detailed design and implementation.**

## Acquired and inspected

[Catalog](catalogs/computation.json): **23 records, all acquired**: four papers,
13 implementation archives and six documentation snapshots. Source archives are
pinned to full commits or an upstream release. PDFs live in ignored
`papers/exvasperated/computation/`; source and documentation in ignored
`quarantine/references/computation/`. Hashes identify the actual local bytes.

Reading covered selected paper sections, root licenses/manifests/READMEs, and a
few interface bodies identified in the catalog. No downloaded program was built
or run. These are candidates and reading material, not measured performance,
validated dependencies, a complete Rust ecosystem audit or a deployment recipe.

## What the numerical references bring into view

### Data movement belongs in the algorithm study

[FFTW3](https://fftw.org/fftw-paper-ieee.pdf) motivates adapting algorithm and
layout choices to actual hardware. [heFFTe](https://www.netlib.org/utk/people/JackDongarra/PAPERS/heffte.pdf)
separates local transforms from distributed reshaping, packing and communication.
Those are useful foundations for studying plane-wave FFTs with actual grid shapes,
batches and decompositions. A fast isolated one-dimensional transform is
insufficient evidence for the distributed application. Published speedups have
not been reproduced here.

[ELPA2](https://arxiv.org/abs/2002.10991v4), Section 2.1, starts with a metric
factorization for a generalized eigenproblem, then follows two-stage reduction
and eigenvector back-transformation. This exposes distinct computation and
communication costs. The [LAPACK guide](https://www.netlib.org/lapack/lug/node34.html)
also distinguishes problem forms and driver choices. The future focused study
must follow conditioning, metric positivity, residuals, orthogonality, clustered
spectra and requested eigenvectors through the selected driver. A backend's
availability does not resolve those numerical questions.

### Reproducibility has several scopes

[Demmel, Ahrens and Nguyen](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-121.html)
distinguish complete from selective reproducibility and discuss exceptional
values as well as reduction order. Their construction is a reference for
examining where controlled reductions help debugging or stability, with explicit
costs. It does not establish a need for global bitwise equality in Exvasperated.
The detailed accumulator proofs remain to read.

Current [cuBLAS documentation](https://docs.nvidia.com/cuda/cublas/index.html#results-reproducibility)
qualifies reproducibility by toolkit, device and execution conditions; concurrent
streams and workspace choices matter. [cuSOLVER](https://docs.nvidia.com/cuda/cusolver/index.html)
separates numerical modes, workspace and solver status. It deprecates cuSolverMG
in favor of cuSOLVERMp and the sparse SP/RF interfaces in favor of cuDSS. Wrapper
availability must therefore be checked against the actual vendor API and version.
FP64 storage alone does not specify the complete numerical execution path.

The [NVIDIA floating-point guide](https://docs.nvidia.com/cuda/floating-point/index.html)
is useful for FMA and evaluation-order discussions, but retains historical CPU
hardware claims inside current documentation. Verify architecture claims against
current hardware documentation instead of inferring freshness from the manual's
version banner.

### Normalization and layout need explicit scientific derivation

RustFFT's acquired `src/lib.rs` documents unnormalized transforms;
[cuFFT](https://docs.nvidia.com/cuda/cufft/index.html) does likewise. The focused
FFT study must derive the physical Fourier convention, grid-volume factors,
reciprocal indexing, real/complex storage and distributed layouts together.
Round-trip agreement alone cannot establish the correct physical normalization.

## Implementation candidates

Exact revisions and license observations are in the catalog. These are root
license observations, not a review of every dependency or bundled file.

| Reference | Purpose of acquiring it | Inspected terms |
| --- | --- | --- |
| [faer](https://github.com/sarah-quinones/faer-rs) | Rust dense/sparse algebra; selected eigensolver API documentation read | MIT |
| [RustFFT](https://github.com/ejmahler/RustFFT) | CPU FFT planning, scratch and conventions | MIT / Apache-2.0 choice |
| [ndarray](https://github.com/rust-ndarray/ndarray) | Array shapes, strides, views and native-library boundaries | MIT / Apache-2.0 choice |
| [ndarray-linalg](https://github.com/rust-ndarray/ndarray-linalg) | Rust LAPACK adapter and backend organization | MIT / Apache-2.0 choice; backend separate |
| [RLST](https://codeberg.org/rlst/rlst) | Rust numerical toolbox and native/distributed integration | MIT / Apache-2.0 choice; README separately flags FFTW GPL terms |
| [LAPACK](https://github.com/Reference-LAPACK/lapack) | Numerical algorithms, driver behavior and test-matrix references | BSD three-clause terms with additional disclaimer |
| [ELPA](https://elpa.mpcdf.mpg.de/software/tarball-archive/ELPA_TARBALL_ARCHIVE.html) | Distributed dense eigensolvers; acquired release 2026.02.002 | LGPLv3 |
| [heFFTe](https://github.com/icl-utk-edu/heffte) | Distributed FFT and CPU/GPU data redistribution | BSD-3-Clause |
| [rsmpi](https://github.com/rsmpi/rsmpi) | MPI buffers, requests and ownership reference | MIT / Apache-2.0 choice |
| [cudarc](https://github.com/coreylowman/cudarc) | Rust CUDA driver and vendor-library interfaces | MIT / Apache-2.0 choice; CUDA separate |
| [cuda-oxide](https://github.com/NVlabs/cuda-oxide) | Rust CUDA kernel compiler/runtime candidate | Apache-2.0; toolchain/dependencies separate |
| [CubeCL](https://github.com/tracel-ai/cubecl) | Alternative kernel compiler/runtime and later portability comparison | MIT / Apache-2.0 choice |
| [py4vasp](https://github.com/vasp-dev/py4vasp) | Public output consumer, versioned quantity/schema behavior | Apache-2.0; not an independent physics oracle |

RLST's GitHub predecessor is archived and points to Codeberg; we acquired the
current Codeberg commit. rsmpi's README identifies RMA and MPI parallel I/O as
unimplemented. That is an interface gap to investigate if a workload needs those
operations, not proof that they are required.

The acquired cudarc manifest lists CUDA versions and library features, but
`src/cusolver/safe.rs` illustrates why coverage needs closer inspection: handle
and stream management do not imply a safe wrapper for every numerical operation.
Its deterministic-mode helpers also have a finite feature-gate list that warrants
checking against the chosen toolkit. No runtime failure has been demonstrated.

## cuda-oxide: concrete starting evidence

Acquired commit `ec4aa4797956534578a1af010f86252a0b6d8626` pins
`nightly-2026-08-28`. Its in-tree supported-features appendix documents f32/f64
libdevice math, f64 shuffle variants, device FFI/LTOIR and small MathDx examples.
The cooperative reduction type matrix is narrower, and a device heap allocator
is not wired up. These are specific investigation points; the release label
provides no verdict. The archived appendix supplies a stable counterpart to the
[live feature table](https://nvlabs.github.io/cuda-oxide/appendix/supported-features.html).

A focused evaluation should establish the actual compiler path for complex FP64
arithmetic, cancellation-sensitive reductions, projector contractions, FFT/vendor
library interoperability, synchronization and error handling. Compare generated
code, numerical error and end-to-end cost on identified NVIDIA hardware. Include
multi-stream lifetimes and distributed communication where the chosen workload
needs them. Establish these results before selecting an execution approach.
Existing task **exv-x34** remains open for that work.

## Core interfaces and continuation

The acquired [public VASP file index](https://vasp.at/wiki/Category%3AFiles)
and py4vasp source provide interface starting points. In py4vasp,
`src/py4vasp/_raw/schema.py` associates quantities with selections, source fields
and version requirements. Public OSS interface research is distinct from copying
proprietary VASP implementation text; no such text has been included here.

A focused compatibility expedition still needs representative downstream tools,
public format definitions, units, array ordering, partial outputs, errors, process
completion and restart behavior. ASE, HDF5 and workflow/scheduler interactions
need dedicated acquisition. A parseable file is only one part of substitutability.

Construction and drivers need the scientific state requirements established by
each subsystem expedition. Generic serialization or an execution framework cannot
decide which histories may be discarded. External interfaces similarly require
scientifically justified units, ownership and callback behavior.

## Required focused follow-up

Before subsystem work, deepen the relevant portion of this survey: derive the
numerical problem, inspect full reference bodies, choose difficult cases and
measure the actual implementation. For numerics, acquisition is strongest for
FFT/eigensolvers; quadrature, interpolation, radial integration, special functions,
root solving, random-number streams and high-precision comparison tools remain
underrepresented. For execution, compile/toolchain, FP64 throughput, memory,
MPI/GPU behavior and packaging remain unmeasured. For compatibility, downstream
workload coverage and continuation semantics remain open.
