# Numerical methods, solver dispatch and bundled libraries

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. This final partition
contains 31 files and 161,031 lines, identified by the
[inventory](../vasp-source-inventory.csv). Of those, 134,137 lines belong to
the bundled LAPACK/LINPACK files. This bounded pass samples contracts and
failure behavior; it does not derive or verify the whole numerical base.
No build, numerical test, benchmark or scientific calculation was run.

## Reading scope

| File | Reading in this pass |
| --- | --- |
| `blas_wrappers.F` | Procedure map; representative real copy dispatch, 1–58. |
| `lapack_wrappers.F` | Procedure map; real/complex Cholesky dispatch, 1–78. |
| `scalapack_wrappers.F` | Procedure map; distributed eigensolver dispatch, 167–198. |
| `scala_struct.F` | Descriptor-slot definitions read, 1–28. |
| `scala.F` | Build stubs, maps and selected process-grid, eigensolver, response-divisor and spectral-inverse bodies. Most matrix transformations and distributed kernels unread. |
| `choleski2.F` | Factorization/rotation path, 285–354; PAW overlap helper, 806–905; remaining paths mapped. |
| `mathtools.F` | Selected SVD lifecycle, 104–140, 170–225; checked real inverse, 363–418; other helpers mapped. |
| `mymath.F` | Selected SVD transformations, 291–386; velocity generation, 1163–1199; broader helper map. |
| `jacobi.F` | Build guard and state, 1–71; assembly/output, 160–201; selected sweep/stopping bodies, 290–448, 479–511, 829–903. |
| `root_find.F` | Bracketing, bisection and Brent bodies, 41–221. |
| `brent.F` | Saved-state setup and initial interpolation/bracketing, 36–181; later line search remains unread. |
| `ratpol.F` | Rational evaluation, residual and fitting loop, 173–361; beginning of screened-interaction fitting, 371–411. |
| `gauss_quad.F` | Procedure map and Legendre/Laguerre/Hermite/Jacobi construction, 90–338. Other quadratures and special functions remain unread. |
| `Lebedev-Laikov.F` | Orbit generator's first branch, 70–107; smallest rule, 590–650; remaining rules mapped, coefficient tables unread. |
| `m_unirnk.F` | Maps; final double-precision unique merge, 225–263; predecessor helpers, 760–789. |
| `dgemmtest.F` | Input, random data, timing and comparison loop, 1–136; matrix-vector reference and difference sum, 228–273. |
| `zgemmtest.F` | Procedure map; complex matrix-vector comparison and difference sum, 243–286. |
| `lib/lapack_double.f` | Entry map and error handler, 1–46; numerical bodies otherwise unread. |
| `lib/lapack_double_1.1.f` | Entry map and unblocked pivoted factorization, 82–135; remaining bodies unread. |
| `lib/lapack_atlas.f`, `lib/lapack_single.f`, `lib/lapack_single_1.1.f` | Entry maps only; contents not compared with independent releases. |
| `lib/linpack_double.f` | Entry map and selected condition-estimator scaling, 210–272, 285–312. |
| `lib/linpack_single.f` | Entry map only. |
| `lib/crayerrf.F`, `lib/derrf.c`, `lib/derrf_.c`, `lib/derrf_t3d.c`, `lib/errf.F`, `lib/fujitsu.F`, `lib/serrf.c` | Small platform/error-function adapters read in full; no accuracy comparison or ABI execution. |

## A wrapper is only one part of a numerical contract

Sampled BLAS/LAPACK wrappers select host or offloaded calls through build and
runtime state, then return. Solver status is passed to the caller rather than
interpreted in the wrapper (`blas_wrappers.F` 9–58;
`lapack_wrappers.F` 20–78). The sampled distributed eigensolver wrapper
likewise forwards layout, workspace, eigenpair counts and failure arrays
(`scalapack_wrappers.F` 167–198). Correctness depends on the caller checking
the result and on the selected backend honoring the same memory and numerical
contract. No equivalence across CPU, NVIDIA and AMD follows from dispatch.

The distributed module has empty interfaces in a build without ScaLAPACK
(`scala.F` 34–124). In a supported build, process-grid setup computes local
dimensions, initializes descriptors and checks initialization status. If any
rank has no local rows or columns, the sampled ELPA setup switches the solver
selection back to ScaLAPACK (688–714). Rank count and matrix size can therefore
change the actual numerical route.

The sampled ScaLAPACK eigensolve checks returned eigenvalue/eigenvector counts,
failure indices and status bits. One positive-status branch is tolerated while
other branches report errors (`scala.F` 1208–1246). In the adjacent ELPA
route, setup and eigensolver status values are assigned repeatedly without
local checks before result reconstruction (1171–1204, 1249–1253). A complete
library/error-policy study is needed before judging consequences. This is
not evidence that a particular calculation failed.

The SVD object helper queries workspace, releases state on query failure and
returns calculation status to its caller (`mathtools.F` 170–225). Its real
matrix inverse separately checks squareness, factorization status, workspace
size and inversion status (363–418). These different local practices explain
why one blanket statement about numerical failure handling would be wrong.

## Overlap metrics and inverse-like transformations

The Cholesky orthonormalization path factors an overlap matrix, inverts its
triangular factor and rotates wave/projector arrays. Local and distributed
branches have different storage and reduction behavior, with checks after
the factorization steps (`choleski2.F` 285–354). The PAW overlap helper
applies augmentation, optionally omits the plane-wave contribution, redistributes
data and sums the result; its add mode compensates an existing matrix for
subsequent rank summation (806–905). Positivity, independence and conditioning
belong to the actual overlap metric, not just the coefficient array shape.

The distributed Hermitian spectral inverse suppresses eigenvalues below an
absolute-magnitude threshold and reciprocates the others. Positive eigensolver
status causes a warning followed by continued construction in the sampled
path (`scala.F` 6056–6128). This is a numerical model choice plus failure
policy; it is not a generic exact inverse or proof of a valid projected
response. Threshold sensitivity and the meaning of retained subspaces belong
with the screening and localized-orbital studies.

Two complex SVD helpers in `mymath.F` use different reconstruction orders
(291–386). One rescales left singular vectors and multiplies in the original
factor order; the other reverses/conjugates the factors. For a general matrix,
these cannot both be identified with the same pseudoinverse merely by their
routine names. Hermitian or other caller restrictions may make some results
coincide. Caller domains, workspace types/shapes and threshold conventions
remain a focused return task; this pass does not claim a reachable failure.

The distributed module also contains physical response conventions. Its
zero-temperature helper drops small occupation differences and small derived
energy/occupation ratios. The finite-temperature counterpart uses averaged
occupation derivatives for nearly equal energies (`scala.F` 4073–4126).
Those branches change a response expression near degeneracy. Their units,
limits and thresholds must be analyzed with occupation and response physics,
not treated as ordinary matrix plumbing.

## Roots and line searches need caller-specific meaning

The root utilities distinguish expanding a bracket from enumerating brackets
on a fixed mesh. Both sampled searches detect strict sign changes; an exact
mesh-point root or a tangential zero is not necessarily recorded
(`root_find.F` 41–103). The expanding search updates its two endpoints
sequentially, so its actual interval growth follows those updates, not a
simple presumed power of the expansion parameter. Finite values, overflow
in sign products and function-domain boundaries remain caller obligations.

Bisection stops on exact zero or half the signed interval width and does not
locally verify an initial sign bracket (`root_find.F` 106–138). It therefore
requires an ordered, valid bracket and meaningful positive tolerance from
the caller. Brent explicitly checks the initial signs, uses absolute plus
position-scaled stopping terms, and reports iteration exhaustion (144–221).
Neither stopping rule establishes that a particular physical root was chosen.

The similarly named routine in `brent.F` is a different, reverse-communication
line-search mechanism: it retains state across calls, accepts sampled energy
and derivative information, and returns trial positions. Its initial fit can
fall back to a bounded step (`brent.F` 36–144). Reset discipline, repeated
or interleaved searches and later acceptance rules need their own study.
The saved state means it cannot simply be assumed reentrant.

## Fitting and quadrature tolerances are not observable errors

The rational evaluator represents a constant plus simple reciprocal-linear
terms and supplies parameter derivatives; a separate evaluator changes the
argument to the imaginary axis (`ratpol.F` 173–234). Poles and derivative
array pairing are therefore explicit domains to establish. The residual helper
sums weighted squared complex differences without dividing by the sample count
(245–279); its name does not make the value a mean or a root-mean-square.

The fitter advances damped parameter updates, stops after repeated small
changes in the square root of that residual sum, and restarts from the initial
parameters with a smaller step after repeated increases (295–361). The
inner iteration cap does not bound the outer restart count. Stagnation can
occur above a useful fit accuracy; analytic continuation additionally needs
pole, asymptotic and physical constraints that this loop does not prove.

Gaussian quadrature generators use different convergence behavior. The sampled
Legendre root iteration has a configurable step-change tolerance and no local
iteration cap. Laguerre has a short bounded iteration and routes exhaustion to
a host diagnostic. Hermite and Jacobi print an exhaustion message and continue
to construct nodes/weights (`gauss_quad.F` 90–338). Valid orders, endpoint
parameters, interval scaling, finite derivatives and quadrature exactness need
separate verification. A root displacement threshold is not an integral-error
bound for a research observable.

The smallest spherical rule expands a symmetry orbit into six axial points
with equal weights summing to unity (`Lebedev-Laikov.F` 70–98, 645–648).
That normalization differs from an unnormalized surface-area integral; callers
must supply the intended measure. Larger rules and coefficient provenance
remain unread. No coefficient table has been adopted, and a source filename
is not evidence of an independent, correctly normalized quadrature source.

## Other hidden numerical assumptions

The legacy Jacobi path is restricted by a platform/Gamma-real build guard.
Its sampled rotation criterion uses an absolute off-diagonal threshold,
reduces convergence across ranks, and has a hardcoded small sweep cap before
forming outputs (`jacobi.F` 19–28, 432–444, 496–504, 837–855). This is not
an eigenpair-residual guarantee, and reachability in supported builds remains
to be established. Its communication and precision assumptions need a later
dedicated pass if the path is relevant.

The unique-ranking helper accepts strictly increasing numerical values after
merging, with predecessor helpers based on a neighboring representable real
or integer subtraction (`m_unirnk.F` 225–263, 760–789). This is not approximate
clustering. NaNs, signed zero, infinities and the minimum integer require
explicit domains before using such a helper for physical equivalence classes.

The general math file also generates thermal velocities using a mass- and
temperature-dependent width, applies time/length conversion, transforms to
lattice coordinates and then zeroes constrained components (`mymath.F`
1163–1199). Statistical ensemble, coordinate constraints and random-stream
semantics belong with ionic dynamics. The partition boundary does not isolate
all physical assumptions from these helpers.

## Bundled libraries, adapters and existing harnesses

The bundled unblocked LU sample distinguishes invalid arguments, empty matrices
and zero pivots while continuing factorization after a zero pivot
(`lib/lapack_double_1.1.f` 82–135). The sampled library error handler stops
execution (`lib/lapack_double.f` 1–46). A condition-estimator sample rescales
intermediate vectors and returns zero for a zero matrix norm
(`lib/linpack_double.f` 210–272, 285–312). Full algorithms, release lineage,
local modifications, ABI choices and build selection remain unexamined.
Library-like names do not authorize importing the quarantined copies; any
future dependency must be independently acquired and assessed.

The small error-function adapters select platform/intrinsic functions or a
local approximation. One C adapter returns single precision from a double
argument; the approximation-based complementary function is also used to
form the ordinary error function by subtraction (`lib/serrf.c`; `lib/errf.F`).
Cancellation, tails and selected symbol/return conventions need accuracy and
linkage studies. No approximation coefficients were copied into our system.

The matrix-product harnesses compare products computed through matrix-matrix
and matrix-vector routes and accumulate squared discrepancies
(`dgemmtest.F` 1–136, 228–273; `zgemmtest.F` 243–286). The real harness
prints timing and differences without an explicit scientific acceptance
threshold in the sampled main program. Both routes can share numerical
libraries; agreement does not provide independent scientific validation.
Fixed work buffers and input-dependent loop counts also require a bounded
setup before any execution. None was attempted here.

## Targets and returns

CPU, NVIDIA and AMD alpha acceptance needs actual workloads through every
selected numerical route, including empty local matrix partitions, difficult
conditioning, degeneracy, failed solves, asynchronous ownership and collective
error propagation. Observable tolerances must be derived with the relevant
physics. This pass selects no library, precision policy or replacement method.

Return through the electronic, response, many-body, localized and ionic studies
to establish caller domains for the questions above. Finish the unread
quadrature, special-function, linear-algebra and support bodies in later
bounded studies. Independently sourced library releases, mathematical references
and deliberate numerical experiments belong to the subsequent campaign.
This report closes the first traversal of partitions, not numerical validation
or eventual every-file analysis.

## Review disposition

The [single independent review](reviews/numerics.md) checked representative
numerical, control-flow, build and scope claims and found no warranted
correction. It confirmed that the deferred SVD workspace question deserves
caller/ABI analysis. No second review, numerical test or scientific experiment
was performed; the recorded return questions remain open.
