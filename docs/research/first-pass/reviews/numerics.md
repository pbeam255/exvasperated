# Numerical methods and bundled libraries: first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../numerics.md). This is the requested single independent
review at depth one. No child review, build, library execution, numerical test,
benchmark or scientific calculation was performed.

## Disposition

No correction is required for the substantive claims sampled below. The report
distinguishes local source behavior from caller guarantees and measured failures,
and leaves the large unread library bodies explicitly open. Its inverse and
solver-status concerns are supported as bounded observations, without establishing
that a production calculation reaches an invalid state.

## Material claims checked

- **Scope accounting.** The inventory assigns 31 files and 161,031 lines to this
  partition. The bundled LAPACK/LINPACK entries account for 134,137 lines.
  Every assigned path appears in the reading-scope table, including grouped
  entries. This verifies accounting rather than analysis completion.
- **Dispatch and distributed failures.** `blas_wrappers.F` 9–58 and
  `lapack_wrappers.F` 20–78 support the host/offload selection and forwarding
  claims. `scalapack_wrappers.F` 167–198 forwards the distributed eigensolver's
  workspace, count and status arguments. In `scala.F`, lines 34–124 contain
  the inactive-build interfaces; 688–714 support descriptor initialization and
  the ELPA fallback when a rank has no local rows or columns. Lines 1208–1246
  check returned counts, individual failure entries and status bits, including
  a tolerated positive-status branch. Lines 1182–1199 repeatedly assign ELPA
  setup/solve status without local checks before reconstruction at 1249–1253.
  The earlier API initialization itself is checked at 1174–1175; the report's
  narrower concern about subsequent setup and eigensolve results is accurate.
- **Lifecycle and overlap.** `mathtools.F` 170–225 supports workspace-query
  cleanup and caller-visible SVD status. Its inverse at 363–418 separately
  checks shape, factorization, workspace size and final inversion status.
  `choleski2.F` 285–354 supports triangular factorization/inversion followed
  by wave/projector rotation. Lines 806–905 support optional augmentation-only
  overlap, redistribution, summation and the adjustment of an existing matrix
  before rank summation. These are different local contracts, as reported.
- **Inverse transformations and response limits.** `scala.F` 6056–6128
  checks workspace-query status, treats a negative solve status as an error,
  reports positive status and proceeds to threshold/reciprocate eigenvalues.
  `mymath.F` 291–386 confirms the different SVD reconstruction orders: the
  first retains the original factor order after singular-value rescaling,
  while the second reverses and conjugates the factors. The report properly
  avoids equating both to a general pseudoinverse. Its deferred workspace
  question is substantive: lines 297–317 and 345–365 use scalar integer
  workspace arguments and complex declarations for the auxiliary workspace.
  The exact selected library interface, caller reachability and execution
  consequences remain to be established. The occupation-difference cutoff
  and near-degenerate derivative average are supported by `scala.F` 4073–4126.
- **Root and line-search semantics.** `root_find.F` 41–103 confirms strict
  sign-change tests and sequential endpoint expansion. Lines 106–138 confirm
  the signed half-width bisection condition and absent initial bracket check.
  Lines 144–221 support Brent's sign check, stopping terms and exhaustion
  handling. `brent.F` 36–144 separately confirms persistent state, reset
  behavior and the initial bounded trial-step calculation. These sources do
  not establish physical root selection or reentrancy.
- **Fitting.** `ratpol.F` 173–234 supports the reciprocal-linear rational
  representation, paired optional derivative arrays and imaginary-axis
  evaluator. Lines 245–279 accumulate weighted squared complex differences
  without sample-count normalization. Lines 295–361 support damped updates,
  repeated small-change termination and restarting from the original
  parameters after repeated increases. The outer restart has no explicit
  counter bound. The distinction between stagnation and fit accuracy is
  warranted.
- **Quadrature and legacy convergence.** `gauss_quad.F` 90–338 supports
  uncapped local Legendre iteration, bounded Laguerre iteration with a host
  diagnostic, and Hermite/Jacobi continuation after printed exhaustion.
  `Lebedev-Laikov.F` 70–98 and 645–648 support six axial points with equal
  weights normalized to one, to the precision of the stored coefficient.
  `jacobi.F` 19–28, 432–444, 496–504 and 837–855 support the restricted build,
  absolute rotation criterion, small sweep cap and collective convergence
  decision. The report does not misidentify these as residual or observable
  error bounds.
- **Other domains and bundled behavior.** `m_unirnk.F` 225–263 and 760–789
  support strict numerical uniqueness and predecessor construction.
  `mymath.F` 1163–1199 supports thermal width, time/length conversion, lattice
  transformation and constrained-component removal. The selected unblocked
  LU body at `lib/lapack_double_1.1.f` 82–135 records a zero pivot while
  continuing its factorization loop; `lib/lapack_double.f` 1–46 stops in the
  sampled error handler. `lib/linpack_double.f` 210–272 and 285–312 supports
  rescaling and zero reciprocal condition estimate for zero matrix norm.
- **Adapters and harnesses.** `lib/serrf.c` 9–17 confirms single-precision
  returns from double-argument error-function calls. `lib/errf.F` 5–22 uses
  an approximation for the complementary function and subtraction for the
  ordinary function. `dgemmtest.F` 1–136 and 228–273, together with
  `zgemmtest.F` 243–286, support the matrix-product comparison and squared
  discrepancy descriptions. The sampled real main program reports timings
  and differences without an acceptance threshold, with fixed buffers and
  input-dependent work sizes.

## Review limits

This review checked representative source bodies and the inventory, not the
full numerical base. It did not establish complete call domains, external
library ABI agreement, selected build reachability, mathematical correctness
of the unread algorithms, quadrature coefficient provenance, cross-device
equivalence or scientific accuracy. CPU, NVIDIA and AMD execution remain
unverified. These limits agree with the report and preserve useful return
questions for later studies. No proprietary source, comments, diagnostic prose
or coefficient tables were included in this artifact.
