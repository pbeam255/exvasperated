# Independent review: parallel first pass

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 snapshot. One review
round, depth one; no delegated review, build or execution. Findings refer to
the report before author fixes. Source discussion is original prose.

## Findings

### P2 — Activation changes do synchronize the OpenACC path

The report's activation paragraph (lines 90-94) says that restoring activation
does not itself synchronize work. Both stack operations issue an OpenACC wait
before changing state (`offload.F` 123 and 139). This is a material distinction
for the caller's completion obligations and for later ownership analysis.

Suggested fix: state that the examined push and pop operations contain OpenACC
synchronization, while they do not explicitly copy scientific arrays between
host and device. There is no corresponding OpenMP synchronization directive in
these bodies. Preserve the unresolved thread context and backend/runtime scope
of completion; the presence of these waits is not a proof that all device work
from every host thread is complete. Balanced nesting and correct residency
remain separate requirements.

### P3 — Cite the actual OpenMP wavefunction copy-in counterpart

The OpenMP copy-in citation at report lines 100-101 points to `openmp.F`
247-321, which contains another object's mapping helpers. The wavefunction
copy-in body is at 716-748; the cited copyout body at 1914-1946 is correct.
The wavefunction body also has the additional pointer-mapping branch discussed
in the report, so the substantive comparison is supported once the citation
and reading-scope table are updated after inspecting this range.

### P3 — Qualify the NVIDIA MPI-support query by build selection

Report lines 125-126 describe the runtime query without its compile-time
exception. `nvcuda.F` 161-178 omits that query for the Cray MPI branch and
initially assumes device support; subsequent environment handling can still
change the result. The AMD helper's empty body is correctly identified.

Suggested fix: describe the queried path and the Cray exception explicitly.
The report's caution that these checks do not establish a working build or
scientific method should remain.

## Other assessed claims

The AMD identity bridge concern is supported directly: its pointer assignment
does not populate the destination used by the Fortran device-identity consumers.
The allocation/free side effects inside FFT assertions and the conditional
impact of disabling assertions are also accurately described. External build
flags and actual execution remain unverified, as the report states. The sampled
BLAS wrappers discard library status, and the identified inactive eigensolver
wrapper has no matching reference in `crayhip.F`; method-level reachability
remains unresolved.

The sampled MPI send and sum wrappers have different completion behavior, as
reported. The MPI initializer requests single-thread support, and the report
appropriately leaves the application/runtime interaction unresolved. Shared
memory allocation and release impose collective lifetime constraints; direct
process exits in the System V C helpers support the stated distributed-failure
question. The source contains backend asymmetries without establishing complete
CPU/NVIDIA/AMD coverage.

The report is a useful bounded first pass after the above corrections. Its
return conditions, absence of hardware claims and distinction between source
findings and observed failures are appropriate. No copied proprietary
implementation text was found in the report.

## Review scope

Read project guidance and the complete report. Independently inspected:

- `offload.F` 1-181, `offload_struct.F`, `openacc_struct.F` and
  `openmp_struct.F` in full.
- `openacc.F` 1-330, 737-758 and 1574-1595; `openmp.F` 1-175,
  716-748 and 1914-1946; selected mapping portions of 247-321 and a
  declaration search to locate the matching copy-in body.
- `mpi.F` 88-381, 882-916, 1199-1253 and 1650-1780;
  `mpi_shmem.F` 206-273, 661-727 and 741-790; `lib/getshmem.c` 1-233.
- `crayhip.F` 1-245 and a targeted search for the inactive eigensolver
  bridge; `HIP/runtime_interface.cpp`, `HIP/rocfft_interface.cpp` and
  `HIP/makefile` in full; `HIP/rocblas_interface.cpp` 1-140 and 280-344.
- `nvcuda.F` 127-207 and 286-361; `intelmkl.F` 198-280.
- The full simple and historical scaled clock providers, the corresponding
  historical resource provider, and the unavailable-status Fortran timing
  provider cited by the report's timing comparison.

This review did not independently audit every scope-table file or verify the
author's historical reading activity. It checked the substantive backend,
synchronization, topology and ownership claims at source level. Compiler,
library, MPI and accelerator behavior were not tested.
