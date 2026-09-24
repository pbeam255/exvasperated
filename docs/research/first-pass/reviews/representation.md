# Independent review: numerical representations first pass

Reviewed 2026-09-24 against quarantined VASP 6.5.1. One review round at
depth one, with no delegated review, compilation or execution. Findings
are written independently without proprietary implementation excerpts.

## Findings

No substantive correction is required by this bounded review. The report
separates observed source behavior from possible runtime consequences and
leaves consumer normalization, cache invalidation and device visibility
explicitly unresolved. Its scope table accounts for all 41 inventory files
without presenting that accounting as completed analysis.

## Assessed claims

The grid structures distinguish physical dimensions, local occupied points
and allocation size. The distributed layouts have different fast axes;
the serial real-space branch uses a different ordering from the distributed
real-space branch (`mgrid.F` 703-901). The two transform/storage flags do
select the four combinations described in `fft_base.F` 566-710. The
shared views, allocation ownership flag and limited conformance checks in
`gridq.F` support the report's distinction between matching local shapes
and establishing physical compatibility.

The basis-index routine uses the supplied initial reciprocal basis for
cutoff selection and the current basis for kinetic energies. Its cutoff
comparison is strict, and the two spinor kinetic components receive
opposite shifts (`wave.F` 3434-3575). The report appropriately avoids
extending this finding into a universal policy for moving-cell workflows.
The sampled descriptor operations have different allocation and aliasing
semantics; neither supports a claim of an unrestricted deep clone.

Placement, extraction and reduced-grid weighting support the separate
normalization concerns. The host transform routines do not themselves
apply a global normalization, and the historical comparison driver
explicitly rescales the round-trip result. The report does not mistake
that comparison for complete physical normalization. The collinear charge
and potential conversions place their half factors in opposite directions
(`mgrid.F` 1208-1295); the density-potential pairing interpretation is
correctly marked for later consumer verification.

Device dispatch has the reported difference between the OpenACC presence
check and the OpenMP activation check. The communication routines expose
the stated local shortcuts and variable-count exchanges. The conditional
complex FFT plan cache really does compare the total grid size rather
than the three separate dimensions (`fftw.F` 118-177). The report does
not claim that the relevant build option is enabled or that a wrong
calculation has been observed.

The bundled adapter's configuration equality checks more properties,
including dimensions, layout, alignment, in-place status and thread
configuration. Under its MKL build branch, the thread configuration field
uses a fixed sentinel rather than the current thread count; the report's
general description does not assert a universal thread-count cache key.
Optional synchronization and richer comparison do not establish complete
concurrency safety, which remains outside the report's claim.

The MPI window publishes the supplied wave buffer and retains separate
location metadata; explicit flush, wait and release routines exist.
The report accurately leaves access epochs and device visibility open.
The older wave cache stores orbital/projector data and increments reference
counts when a key is reused. Its local key logic cannot establish the
caller-controlled invalidation policy by itself.

The prediction paths retain the described histories, and the inspected
file-backed entry rejects MPI builds before its OpenACC host update and
offload suspension. The in-memory path contains special cases for
displacement histories; the report makes no claim that these prove
predictor stability. The interpolation cleanup can regenerate the exchange
layout and rebuild reciprocal projectors, supporting the state-restoration
finding.

No proprietary implementation text was identified in the report. The
open normalization, lifetime and consumer questions are appropriate return
conditions for subsequent studies.

## Review scope

Read current project guidance, the full report and the representation
inventory entries. Independently inspected these source regions:

- `mgrid_struct.F` 1-124; `mgrid.F` 690-917 and 1090-1305;
  `gridq.F` 30-110, 225-375 and 390-470.
- `wave.F` 100-145, 278-375, 620-745 and 3410-3585;
  `wave_high.F` 255-345.
- `fft_base.F` 105-315, 400-490 and 560-715;
  `fft_wrappers.F` in full; `fft_comm.F` 270-455;
  `fftw.F` 90-185 and 200-272; `ffttest.F` 100-125.
- `wave_window.F` 112-237, 265-321 and 540-608;
  `wave_cacher.F` 75-138, 212-265 and 332-390.
- `wavpre.F` 100-182; `wavpre_noio.F` 187-408;
  `wave_interpolate.F` 40-122, 277-340 and 865-925.
- The full bundled adapter configuration implementation and plan
  implementation headers, plus its main implementation at 140-320 and
  365-425.

This review did not independently audit every file listed in the report
or verify the author's historical reading activity. It did not establish
all build combinations, trace every normalization consumer, prove MPI or
cache lifetimes, or measure numerical behavior on any hardware. No second
review round is requested.
