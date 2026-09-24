# Exchange-correlation, orbital corrections and magnetic constraints: first pass

Studied 2026-09-24 against quarantined VASP 6.5.1. The `xc` partition has
10 files and 25,898 lines. This pass follows functional selection, selected
grid evaluations, derivative conventions and two coupled corrections. It does
not derive or verify every functional. No compilation or numerical execution
was performed. Source identities are in the [inventory](../vasp-source-inventory.csv).

## Reading scope

Procedure/declaration maps were inspected for all ten files. The following body
samples bound the claims; other method bodies remain for later study.

| File | Body reading and limits |
| --- | --- |
| `setex_struct.F` | 16–177: component records, persistent state, library handles and allocation. |
| `setex.F` | 27–110, 788–882, 1029–1143, 1250–1302, 1619–1693: selected mapping, library setup, tables and temporary functional changes. The full selection catalog remains partial. |
| `xc_driver.F` | 19–146, 500–580, 1726–1890, 1920–1984, 2300–2479: scalar GGA and selected meta-GGA/library routes. SIMD and full polarized GGA bodies remain unread. |
| `ldalib.F` | 33–50, 68–170, 211–279, 2716–2755, 2938–3020: tables, spin evaluation, energy and higher derivative helpers. Most elementary functionals remain unread. |
| `ggalib.F` | 372–515: one exchange-family kernel; the other families and SIMD counterparts were mapped, not derived. |
| `mggalib.F` | 3297–3448: one regularized meta-GGA exchange kernel. Most of this large file remains unread. |
| `fexcg.F` | 136–163, 221–267, 443–482, 558–619, 646–738, 1233–1337, plus call/threshold searches throughout: representative gradient, spin, kinetic-density and correction paths. Full stress/divergence algebra remains open. |
| `LDApU.F` | 120–177, 299–403, 911–1025: initialization, projected occupations, method dispatch and one effective-interaction variant. |
| `constrmag.F` | 37–133, 468–665, 714–772: target interpretation, weighted moments, selected potential components and correction energy. Weight construction and its geometry derivatives remain open. |
| `mbj.F` | 35–90, 421–558: grid/radial parameter access and self-consistent updates. Auxiliary-field construction remains partial. |

One focused public-document lookup clarified the meaning of potential-only
methods. The broad literature and implementation comparison campaign remains
later work.

## Selection defines a composite calculation

The functional record is a list of components with family, kind, coefficient,
parameters and table choices. Separate flags request density gradients,
kinetic density, Laplacians and their derivative fields. Exchange/correlation
fractions, screening and nonlocal additions coexist with these components
(`setex_struct.F` 49–106). A short functional label does not describe this
entire state.

The pointwise driver loops over selected components and weights their returned
energy and derivatives (`xc_driver.F` 567–577, 2465–2474). Individual branches
also apply exchange/correlation mixing fractions and sometimes subtract a local
part before adding a gradient correction (500–528). The exact-exchange study
must connect these fractions to the separate nonlocal operator and its energy.
Counting an exchange contribution twice is a concrete risk when reconstructing
the method from isolated routines.

Temporary functional changes also update global exact-exchange/screening state,
reinitialize a screened-exchange helper, and replace device copies. They use a
bounded stack with overflow/underflow checks (`setex.F` 1619–1693). These are
observable calculation-state transitions, not merely local parameter changes.
Restoration, table validity and nesting require caller analysis.

## Tables and analytic kernels coexist

Selected local functionals use generated tables with spline coefficients and
spin interpolation. Setup preserves the functional record used for the table
and updates device state (`setex.F` 1029–1080). The sampled validity check
compares component count and identities, without comparing every coefficient
or parameter (`ldalib.F` 33–50). This is a limited check; it does not prove a
stale table is reachable. The lifecycle of table reconstruction after parameter
changes remains a return question.

The local spin evaluator includes core density, applies a positive density floor,
keeps polarization away from its endpoints, evaluates table entries and forms
spin potentials. It monitors table range and rejects an insufficient range
after a communicator maximum (`ldalib.F` selected ranges). Thus tabulation,
clamping, core treatment and range checks all participate in reference behavior.

The sampled GGA exchange kernel computes a density-scaled enhancement and
explicit derivatives, with distinct expressions for several related functional
variants (`ggalib.F` 372–515). The sampled regularized meta-GGA kernel depends
on density, gradient magnitude and kinetic density, constructs an intermediate
orbital-character variable, and uses different interpolation branches with
derivatives (`mggalib.F` 3297–3448). These samples establish method-dependent
formula and branch complexity. They do not verify coefficients, continuity,
asymptotic limits or equivalence of scalar and vector implementations.

## Units, spin and domain treatment are part of the contract

The grid driver scales density and gradients using cell volume and Fourier
normalization. It forms derivatives through reciprocal multiplication, applies
high-frequency truncation and removes unbalanced modes before transforming
back (`fexcg.F` 221–267). This introduces a discrete derivative operator around
the pointwise functional. Testing only the latter would omit grid errors and
the adjoint relationship needed for energy derivatives.

For noncollinear state, the sampled route constructs two local spin densities
from total density and magnetization magnitude. Gradient and kinetic-density
components are projected using the local magnetization direction, with a floor
in its normalization (`fexcg.F` 558–619, 646–655). Near zero magnetization,
rotation covariance and the chosen limiting procedure deserve direct study.
This path's existence does not establish every functional's support for every
spin or response mode.

At the pointwise call boundary, density, gradient, Laplacian and kinetic-density
inputs have distinct unit conversions. Outputs receive different factors before
entering scalar potential, gradient, Laplacian and generalized kinetic operators
(`fexcg.F` 683–738). The same-looking real scalar can consequently denote energy
per particle, an energy-density derivative or an operator coefficient.

Several layers impose lower bounds on densities, gradients and kinetic density;
some branches additionally cap inputs. The external meta-GGA route can enforce
a kinetic-density lower bound related to the density gradient (`xc_driver.F`
2377–2400). It also assigns bounded gradient values back to its arguments.
These are source observations, not endorsed choices for our implementation.
Their effect on the variational derivative and on component order requires
analysis with actual callers and admissible input domains.

## An energy, a potential and a response kernel are different deliverables

The grid code accumulates XC energy separately from its band-sum correction.
The correction subtracts the potential contraction with valence density and,
where required, the kinetic-density operator contraction. Stress includes a
related expression with core density (`fexcg.F` 1233–1337). The local evaluator
likewise retains a separate core contraction (`ldalib.F` 211–279). Comparing
only one named energy field would miss these distinctions.

Not all higher derivatives are analytic. The inspected local derivative helpers
sample nearby densities with a fixed relative step and use differences of
potentials to obtain second and third derivatives (`ldalib.F` 2716–2755,
2938–3020). Their zero-density behavior, polarized endpoints, step sensitivity
and symmetry of mixed derivatives must be checked at response consumers. The
presence of a higher-derivative array does not by itself establish its accuracy.

Potential-only methods are a separate case. The inspected mBJ branch forms a
modified potential but supplies a local-density expression for energy
(`xc_driver.F` 1962–1983). The public documentation explicitly distinguishes
these quantities and excludes ordinary energy-consistent ionic relaxation for
mBJ/local mBJ. This prevents treating an available potential as proof of an
associated total-energy functional or force capability.
[VASP meta-GGA documentation](https://vasp.at/wiki/METAGGA), consulted 2026-09-24.

The mBJ parameter can itself be updated from grid and one-center contributions.
The sampled global update bounds its value, resets accumulators and transfers
state across host/device boundaries. A local variant mixes grid and atomic
auxiliary contributions (`mbj.F` 421–558). Initialization, update cadence and
restart behavior matter alongside the pointwise formula.

## External-library support is version- and capability-dependent

The Libxc setup creates separate unpolarized and polarized handles, inspects
family/kind and energy-availability flags, and requests extra fields from
capability flags. It rejects selected unsupported choices. One version branch
changes library enforcement through an API; an older branch probes behavior
using a selected functional (`setex.F` 788–882). No external library was built
or probed in this study.

At evaluation, absence of an energy capability selects a potential-only call
and zeros the direct library-return energy buffer. Subsequent GGA exchange
mixing can still retain a local-energy term when the local and gradient
fractions differ (503–513). Gradient invariants and their
derivatives are converted to the driver's gradient-magnitude convention
(`xc_driver.F` 500–534, 2377–2420). Correct linking is therefore only one part
of the interface contract. Library version, flags, input conventions and
derivative availability need to be recorded in later comparisons.

## Orbital and magnetic corrections cross partition boundaries

The Hubbard module derives orbital occupations from PAW channel occupations
weighted by all-electron radial overlaps, then dispatches among several
correction variants (`LDApU.F` 299–403). In the sampled effective-interaction
variant, the potential depends on the difference of the two interaction
parameters and on the full occupation matrix. It returns a correction equal
to its orbital energy minus the operator expectation already entering the band
sum (911–1025). Other variants remain unread. The radial subspace and complex
spin conventions are part of this method's identity, not incidental storage.

Magnetic constraints integrate weighted local moments, including spin-spiral
rotations, and reduce them across the grid communicator. Different modes target
direction, vector value or a normalized alignment; near-zero moments receive
special treatment (`constrmag.F` selected ranges). The reported penalty and
the correction to the band sum are stored separately. Force consistency will
also depend on how spatial weights move with ions, which this pass has not
examined.

## Execution targets and return conditions

The grid loops and many pointwise kernels carry accelerator directives, while
library handles, functional stacks, tables and parameter updates require extra
state management. CPU/NVIDIA/AMD support has not been demonstrated by this
reading. Scalar/SIMD/device agreement and external-library availability remain
separate questions.

Return with electronic solution and PAW for the energy/stationarity chain;
with nonlocal interactions for hybrid and dispersion composition; and with
ions/response for derivatives, constraints and unsupported combinations. Later
independent derivations and comparisons should address endpoint limits,
component ordering, table errors, mixed derivatives, spin covariance and
energy-force agreement only for methods with a corresponding energy. A complete
functional catalog and every elementary kernel remain future per-file work.

## Review disposition

The [single independent review](reviews/xc.md) identified an overbroad zero-energy
statement for potential-only library calls. The text now distinguishes the
zeroed library buffer from a possible local-energy term retained by subsequent
mixing. Other sampled claims were supported. The correction was checked against
the cited branch; no numerical test or second review was performed.
