# Numerical representations and Fourier contracts

First pass, 2026-09-24. Study area: `representation`, 41 files. This pass examines
selected grid, wavefunction, transform and lifetime contracts. No source was
compiled or executed, and no numerical accuracy claim follows from this reading.
Reference file identities are in the [inventory](../vasp-source-inventory.csv).

## Reading scope and file roles

Fortran files received declaration/procedure searches and the bounded body
readings below. The bundled C++ FFT adapter received interface/build inspection
and selected implementation reading. Large files remain partially examined.

| File | Body scope | Role and remaining depth |
| --- | --- | --- |
| `mgrid_struct.F` | 1-124 | Physical dimensions, storage extents, three distributed layouts, transform maps and packing flags. |
| `wave_struct.F` | 1-257 | Multi-point/single-point descriptors and owning/view-like wavefunction containers. |
| `mgrid.F` | 65-104, 703-851, 1121-1172, 1200-1295 | Grid initialization, distribution, reduced-grid weights and spin density/potential transformations. Subgrids and most remapping remain open. |
| `wave.F` | 109-139, 283-369, 627-738, 3434-3575; cutoff/layout searches | Copy semantics, wave allocation, basis selection and kinetic terms. Full layout generation and invalidation remain open. |
| `gridq.F` | 38-103, 231-265, 316-370, 418-495 | Multiple views of shared grid storage, representation flags, delayed operations and conformance checks. Expression evaluation and complete lifetimes remain open. |
| `fft_base.F` | 10-208, 224-312, 404-485, 566-710 | Admissible dimensions, planning setup, packed coefficient placement/extraction and serial transform dispatch. Distributed/batched bodies remain mostly unread. |
| `fft_comm.F` | 295-445 | Forward/backward redistribution, local shortcuts, zeroing and all-to-all communication. Map construction remains open. |
| `fft_wrappers.F` | 1-186 | CPU/device transform dispatch. |
| `fftw.F` | 95-273 | Host complex and real transform plans; optional complex-plan caching. Batched/distributed planning remains open. |
| `ffttest.F` | 1-168 | Historical transform benchmark/comparison driver; active build compatibility unverified. |
| `opergrid.F` | 1-67; remaining procedure scan | Grid sum and dump diagnostics, not a scientific acceptance suite. |
| `dfast.F` | 99-143, 156-237 | Blocking choices and simultaneous orbital/projector linear combinations. Most overlap and distributed matrix operations remain open. |
| `wave_high.F` | 149-340 | Spinor transforms, pointer assignment and data-copy distinction. Most algebra and normalization consumers remain open. |
| `wave_mpi.F` | 56-137, 325-432 | Redistribution request storage and full/reduced coefficient distribution. Communication progress and completion callers remain open. |
| `wave_cacher.F` | 21-135, 215-260, 334-386 | Reference-counted real-space/projector cache coupled to exchange/many-body work. Invalidation and most solver bodies remain open. |
| `wave_window.F` | 113-146, 178-237, 270-320, 542-602 | MPI window publication, rank/displacement metadata, explicit completion and release. Full access-epoch handling remains open. |
| `wave_rotator.F` | 86-126, 191-230 | Cached symmetry state and separate plane-wave/projector rotation calls. Rotation kernels remain mostly unread. |
| `wave_interpolate.F` | 55-123, 281-340, 878-917 | Additional sampling batches, borrowed original state and restoration of method-dependent projectors/layouts. Interpolation equations remain open. |
| `wavpre.F` | 55-175 | File-backed ionic-step prediction setup; MPI rejection and host visibility before the inspected path. |
| `wavpre_noio.F` | 195-275, 314-403; call searches | In-memory prediction histories, charge/augmentation/kinetic-density state and displacement-based coefficients. Gauge alignment and predictor stability remain open. |

The other 21 files are the bundled adapter. Names below are relative to `fftlib/`;
header names are relative to its `include/fftlib/` directory.

| Files | Scope and role |
| --- | --- |
| `LICENSE`, `README.md`, `howto.txt`, `makefile` | Entire small files inspected: a separate license notice, an empty README, build/link instructions and compilation rule. No material adopted. |
| `fftlib.hpp`, `fftlib_configuration.hpp`, `fftlib_configuration_implementation.hpp` | Entire declarations and configuration body inspected: transform API, cached plans and equality/hash inputs. |
| `fftlib_constants.hpp`, `fftlib_types.hpp`, `fftlib_macros.hpp` | Entire small headers: alignment/cache settings, scalar/backend types and diagnostics/profiling controls. |
| `fftlib_dynamic_lib.hpp` | Interface inspection: dynamic symbol resolution and thread configuration. |
| `fftlib_dynamic_lib_implementation.hpp` | Selected searches and 62-105: symbol lookup and conditional locking; full loader cleanup remains open. |
| `fftlib_dynamic_lib_implementation_fftw.hpp` | 6-80 and selected declaration search: runtime loading and thread state; most numerical-library forwarding remains unread. |
| `fftlib_ext_plan.hpp`, `fftlib_ext_plan_implementation.hpp` | Small bodies inspected: external handle metadata and original buffer pointers. |
| `fftlib_plan.hpp`, `fftlib_plan_implementation.hpp` | Entire small headers: underlying plan construction, null-result warning and destruction. |
| `fftlib_reader_writer_lock.hpp`, `fftlib_reader_writer_lock_implementation.hpp` | Entire small headers inspected; no concurrency proof or runtime stress test. |
| `fftlib_implementation.hpp` | 155-305, 365-424 and selected searches: thread-local lookup slots, shared map, conditional locking and execution dispatch; cleanup and all build options remain open. |
| `src/fftlib.cpp` | Export/forwarding scan, especially dimension reversal at the Fortran boundary; not every wrapper body audited. |

## One array shape does not identify one physical representation

Grid state distinguishes global dimensions, local occupied elements and allocated
workspace. Reciprocal, intermediate and real-space layouts have different fast
axes and distributions. The serial and distributed real-space layouts do not
have the same ordering (`mgrid_struct.F`; `mgrid.F` 703-851). Padding is storage,
not another set of physical grid points.

Two independent choices determine whether the transform uses a reduced reciprocal
grid and whether real-space storage is real-valued. `fft_base.F` 566-710 handles
multiple combinations, including changes of stride for in-place transforms.
Consequently, treating every real-space buffer as an ordinary dense complex
array would be incorrect. A saved pointer can remain addressable while its
interpretation has changed.

The higher-level grid quantity contains complex, real and build-dependent views
of the same allocation, together with flags for real/reciprocal space and spin
representation. It distinguishes allocated storage from borrowed storage
(`gridq.F` 231-370). Its strict conformance check compares representation flags,
local point counts and component count; it does not establish equality of lattice,
global dimensions, distribution maps or physical units (418-451). Such checks
are useful local guards, while stronger compatibility remains a caller obligation.

## Basis selection and kinetic energy can use different cells

The sampled indexing routine computes current kinetic energies from the current
reciprocal basis but tests cutoff membership using the supplied initial basis
(`wave.F` 3434-3575). It uses a strict energy inequality and additional conditions
to select stored members of conjugate pairs. Spin spirals introduce opposite
shifts for the two kinetic components. Thus the basis is not fully specified by
the current cell and a scalar cutoff alone during all workflows.

This connects moving-cell calculations, stress, restart and geometry changes.
Which callers keep or replace the initial basis is an explicit return question.
It would be premature to infer either a universal fixed-basis policy or an error
from this one routine.

Wave descriptors separately carry local/global band counts, local/global
coefficient counts, spinor multiplicity, projector dimensions, sampling weights
and communicator relationships. Multi-spin wave allocation creates local
occupation/eigenvalue views into global arrays and optional spin-specific aliases
(`wave.F` 627-738). These are ownership relationships, not independent copies.

There is also no universal meaning of copying a descriptor. One helper releases
old storage and assigns the new record; another allocates copies of many arrays,
clears selected inversion-related pointers and allocates communicator records
(`wave.F` 109-135, 283-364). The latter records can themselves contain handles or
pointers. Neither routine should be described as an unrestricted deep clone.
Single-wave assignment likewise aliases buffers, while another operation copies
their contents (`wave_high.F` 266-340).

## Fourier normalization and reduced storage require separate accounting

Placement on the transform grid zeroes unused entries and inserts the retained
coefficients. Extraction can replace or add to existing coefficients. Reduced
storage uses coefficient scaling and, in one build branch, explicit conjugate
partners (`fft_base.F` 108-208, 224-312, 404-485). The grid's integration weights
and the wavefunction's placement/extraction factors serve related but distinct
purposes; substituting one for the other would change normalization.

The inspected host FFT calls do not apply a global normalization factor
(`fftw.F` 95-265). The historical benchmark compares a forward/backward result
after division by the total grid size (`ffttest.F` 107-117). This supports the
need for normalization outside those calls; it does not locate every physical
volume or quadrature factor in production consumers. Those consumers still need
tracing. Even a successful round trip would not detect two compensating sign
errors or establish the density's physical normalization.

Spin transformations offer another example. The collinear charge conversion
forms total and difference components, with the inverse carrying a half factor.
The potential conversion places that factor in the opposite direction
(`mgrid.F` 1208-1295). This is consistent with preserving the density-potential
pairing under a change of components, an interpretation to verify through energy
consumers. Noncollinear conversions also fix the sign convention of the imaginary
off-diagonal component. Component count alone cannot encode these conventions.

## Plans, distributed maps and device residency carry hidden preconditions

FFT dispatch chooses device or host implementations from activation state; the
OpenACC branch additionally checks presence of the array, whereas the OpenMP
branch shown here relies on activation (`fft_wrappers.F`). Redistribution can
take a local-copy shortcut, gather/scatter locally, or exchange variable counts
across ranks (`fft_comm.F` 295-437). The same numerical transform therefore has
different storage and completion obligations depending on build and topology.
CPU/NVIDIA/AMD parity must eventually test these combinations on real hardware.

A concrete source concern is the optional host complex-plan cache: its reuse
condition checks the total grid size, rather than the three dimensions separately
(`fftw.F` 118-177). Distinct shapes can have the same product. Whether an enabled
build encounters that sequence, and whether alignment or changed thread count
introduces additional restrictions, remains untested. This is a conditional
contract concern, not an observed wrong calculation.

The bundled C++ adapter has a much richer configuration comparison: dimensions,
embedding, strides, distances, transform direction, flags, alignment, in-place
status and thread configuration participate. It adds dynamic symbol resolution,
external handles and optional synchronization around cache maps. Its presence
does not repair every other cache or prove safe use under all build options.
The separate license notice is recorded for later dependency assessment; this
study adopts no adapter source or implementation text.

The MPI wave window exposes original wave storage and separately maintains rank
and displacement maps, request completion, flush operations and collective release
(`wave_window.F` 178-237, 270-292, 542-600). Its buffers must outlive the permitted
remote access. Full epoch handling and accelerator visibility were not established.
The older cache stores real-space waves and projectors with reference counts and
exchange handles; its keys alone do not demonstrate invalidation after geometry,
potential or basis changes (`wave_cacher.F` 81-125, 215-252, 334-373).

## Prediction and interpolation expose cross-study dependencies

Prediction retains orbital, charge and on-site state across ionic steps; the
in-memory path can also retain kinetic-density history. It derives coefficients
from displacement history and has special treatment for nearly dependent
directions (`wavpre_noio.F` 195-403). A stable storage path is not evidence of
stable extrapolation or consistent wavefunction gauge. The file-backed path
explicitly rejects MPI in the inspected entry and updates host data before
disabling offload (`wavpre.F` 109-175).

Additional-point processing borrows original wave/grid/sampling state and creates
batch state. Its release path can regenerate the original exchange layout and
rebuild reciprocal projectors (`wave_interpolate.F` 878-917). Cleanup thus has
scientific state-restoration effects. The mathematical interpolation and every
exceptional exit need later consumer study.

## Return conditions

Return with PAW for projector/overlap normalization; electrostatics and XC for
charge, volume and spin-component conventions; electronic solution for inner
products, orthogonalization and orbital gauge; ions for basis/predictor histories;
and many-body/response for caches and additional sampling. Later bounded checks
should challenge basis-boundary membership, Fourier amplitudes and phases,
packing special modes, equal-size/different-shape plan reuse, layout changes and
buffer lifetimes. These are proposed questions, not tests that have run. The
first pass does not select the replacement's data structures or backend libraries.

## Review disposition

The [single independent review](reviews/representation.md) checked the substantive
claims and reported no corrections. Its bounded scope and unresolved runtime
questions are recorded separately. No second review round was requested.
