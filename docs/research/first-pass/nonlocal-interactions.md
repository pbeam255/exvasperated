# Nonlocal exchange and dispersion: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The
`nonlocal_interactions` partition contains 17 files and 73,489 lines, identified
by the [inventory](../vasp-source-inventory.csv). This report is original prose
from source inspection. No calculation, derivative check or hardware test ran.

## Reading scope

Procedure and dependency searches established entry points. Body reading was
bounded as follows; an entry in this table does not mean a complete analysis.

| Files | Body scope and remaining limits |
| --- | --- |
| `fock_glb.F` | Persistent settings and state, 20–163. Full initialization and all consumers remain open. |
| `fock.F` | Setup 1164–1260; reciprocal kernel 1620–1778; beginning of singular contribution 2070–2170. Most setup, operator and correction bodies remain unread. |
| `fock_ace.F` | Construction 65–274 and application 275–402. Refresh scheduling and later helpers remain partial. |
| `fock_dbl.F` | Setup fragment 755–793; operator work 1117–1355. Buffer ownership, full driver and all spin branches remain partial. |
| `fock_frc.F` | Entry, eligibility and allocation 36–166. Derivative accumulation remains largely unread. |
| `fock_multipole.F` | Selected moment correction 1274–1337. Generation and physical boundary derivation remain unread. |
| `pawfock.F` | Radial cache 34–114 and selected four-index integral 437–527. Complete angular and core-valence treatment remains open. |
| `pawlhf.F` | Local one-center entry 792–846. Most reconstruction and derivatives remain unread. |
| `pwlhf.F` | Local potential reconstruction 1521–1610. Full exchange-energy construction and later PAW correction remain unread. |
| `wpbe.F` | Screened-exchange table construction and reuse 63–153. Analytic expression and boundary derivatives remain unread. |
| `vdw_nl.F` | Entry/setup 88–175, 231–293, 519–593; selected scalar convolution 1066–1104, 1155–1338, 1375–1461; alternative kernel calculation 2564–2605, 2645–2718, 2800–2908. Spin path and full kernel derivations remain partial. |
| `vdwforcefield.F` | Initialization 119–275; dispatch 2421–2535; pair-model entry 4661–4737; many-body preparation and accumulation 5253–5411; iterative atomic partition declarations 10909–10988 and update fragment 11230–11365. Most of this 12,345-line file remains unread. |
| `vdwforcefield_glb.F` | Reference-parameter selection 62–103 and charge/volume adjustment 626–711. Numerical tables were not independently assessed. |
| `subdftd3.F` | Entry 59–170; setup 459–534; coefficient interpolation 2533–2582; included-table unpacking 4070–4103. Pair/triple derivatives and periodic convergence remain unread. |
| `parsD3.inc` | Metadata and consuming loader only. Its 35,628 lines of numerical material were not reviewed record by record, adopted or certified. |
| `subdftd4.F` | Build boundary, structure adaptation and external evaluation 1–176. Remaining damping/input choices are partial. |
| `libmbd.F` | Structure/input setup 35–113; evaluation and conversion 279–354. Full library behavior lies outside this file and this pass. |

## Several different scientific contracts share this partition

The inspected code separates an orbital-dependent exchange operator, an
approximation built from its action on selected states, local exchange-potential
reconstruction, density-dependent nonlocal correlation, and atom-based dispersion
corrections. They differ in inputs, self-consistency, derivatives and state.
Treating them as one optional energy correction would lose those distinctions.

The exchange setup can also be needed by response and density-matrix work
(`fock.F` 1164–1260). Its presence does not by itself imply a ground-state
hybrid calculation. Global state includes screening, reciprocal sampling,
cutoffs and atomic angular limits (`fock_glb.F` 20–163). The electronic and
PAW studies therefore supply only part of this area's contract.

## Exchange depends on representation, sampling and the singular limit

The exchange grid initially aliases the ordinary grid; selected precision modes
allocate a distinct grid using a wave cutoff and cell-dependent dimensions.
The setup also rejects one overlap-enabled, non-PAW dataset combination
(`fock.F` 1164–1260). Grid choice and atomic representation are scientific
inputs to the implemented approximation, as well as memory concerns.

The sampled operator traverses the full reciprocal-point set, skipping zero
weights and excluded sampling points. It maps each full point to a stored
representative, handles spin reversal and reconstructs symmetry-related waves
with phases when needed (`fock_dbl.F` 1189–1234). Occupation thresholds also
remove partner states. This connects exchange convergence to the geometry
study's symmetry and sampling contracts.

For each retained orbital pair, the body constructs pair charge with PAW
augmentation, transforms it, applies the interaction, transforms back and
accumulates the action on a target orbital. Occupations, reciprocal weights and
transform normalization enter explicitly (`fock_dbl.F` 1240–1355). The exact
energy expression and its partial-occupation term need a later derivation;
the present reading establishes the dependencies, not that derivation.

The reciprocal interaction is not universally an unmodified inverse square.
The inspected kernel branches on finite-radius truncation, screening and model
interactions; it includes sampling weights and volume factors and can suppress
components using cutoffs (`fock.F` 1620–1778). Near the singular point it uses
a separately supplied correction. The beginning of its construction distinguishes
finite-radius formulas, an unscreened regular-mesh route through an enlarged-cell
electrostatic calculation, and a further reciprocal summation (2070–2170).
That remaining sum and its limiting behavior are unread.

A selected multipole path adds a projected correction through ten moments
(`fock_multipole.F` 1274–1337). Its existence requires returning to boundary
conditions; it does not establish accuracy for isolated systems or any particular
cell shape. Screening, mesh refinement, truncation and moment corrections must
eventually be varied independently when investigating the physical limit.

## Compressed exchange has a construction space and a lifetime

The compressed construction forms a projected matrix from exchange-applied
states, changes its sign, uses Cholesky and triangular inversion, and transforms
the action vectors. It checks the factorization/inversion statuses and has local
and distributed routes (`fock_ace.F` 65–274). If no state is considered occupied
at the current reciprocal point and spin, it clears the corresponding
representation; this is not a test for zero allocated construction-space size.

Application consists of overlaps with the compressed vectors, a reduction and
a second matrix product, followed by the negative sign of the exchange action
and a weighted energy contribution (275–402). This makes both the state used
to construct the operator and the time of reconstruction material. The electronic
study already found solver-dependent availability and scheduling. No inference
of unrestricted equivalence to the full operator follows from inspecting this
factorization: the construction subspace, PAW metric, occupancy changes and
refresh criteria still need joint analysis.

The exchange-force entry finds the highest band index whose occupation magnitude
exceeds its cutoff across points and spins, bounds its batch size with that index,
and prepares three or nine derivative directions. It returns early for several conditions,
including a model-interaction branch (`fock_frc.F` 36–166). This is one
contribution's entry; it cannot establish that a whole method lacks forces or
stress. The complete derivative sum belongs with the ionic and PAW consumers.

## Atomic exchange and local reconstruction need their own domains

The radial screened-interaction cache uses atomic identity, angular channel,
screening and range selection in its key (`pawfock.F` 34–114). Radial-grid
identity is not explicit in the sampled comparison. Whether identity already
fixes the grid and all dependent data is a caller invariant to trace, not a
demonstrated stale-cache defect.

The selected four-index radial integral combines products of partial waves,
angular triangle/parity restrictions, radial quadrature and screened interaction
data, accumulating into a supplied result (437–527). Its normalization must be
derived with the PAW angular representation. The local one-center reconstruction
in `pawlhf.F` was only entered, not followed through.

The local exchange potential has a separate density domain. The collinear
reconstruction divides an energy-like field by charge plus core density, with
a small-density branch. The noncollinear body projects onto the magnetization
direction, divides by its magnitude, and reconstructs spin components
(`pwlhf.F` 1521–1610). Two source-level concerns deserve a return: the sampled
body lacks a local zero-magnetization guard, and one spin-channel value is
assigned only when its density exceeds the threshold, without a corresponding
assignment in the other branch. Caller restrictions and reachable inputs remain
untraced; neither concern is a reproduced failure.

The screened semilocal exchange table is another coupling to XC. Its construction
requires a selected functional/screening combination and reuses data according
to screening and functional identity (`wpbe.F` 63–153). Table domains and
derivative continuity remain part of the XC follow-up.

## Density-based correlation has interpolation and vacuum contracts

The nonlocal-density path builds auxiliary interpolation functions and Fourier
interaction tables, then convolves auxiliary density fields. The sampled table
generation includes a real-space window, a transform, reciprocal truncation,
spline data and finite-difference derivatives (`vdw_nl.F` 231–293, 519–593).
These approximations need convergence analysis independently of the physical
functional.

The scalar calculation forms a local density/gradient variable, saturates it,
selects interpolation intervals and transforms one auxiliary field per channel.
It combines Fourier channels using interpolated kernels, accounts for reduced
reciprocal storage in contractions, and constructs density and gradient
derivatives (1155–1338, 1375–1461). A stress contribution differentiates the
kernel with respect to reciprocal magnitude. Full cell derivatives and the
spin variant were not traced.

Vacuum handling differs between stages. Small density is replaced locally by
a floor when computing the auxiliary variable and its derivatives; negative
input density contributes zero to the transformed field. In the alternative
kernel path, the nonnegative-density branch forms a density divided by a
positive power of a scale that itself vanishes at exactly zero density
(2645–2718). That yields an apparent undefined zero-density expression in this
local body. Establishing whether exact zero can reach it, or is excluded by
upstream density construction, remains necessary before claiming a runtime bug.

The alternative path also adds a density-proportional local energy term and
its potential contribution (2800–2908). Comparing only its convolution energy
would omit part of the implemented functional. Uniform-density limits, density
scaling and energy/potential/stress consistency are unresolved scientific checks.

## Atom-based dispersion includes data, charge iteration and external APIs

The force dispatcher selects among pair corrections, density-derived atomic
models, coupled many-body models and optional external libraries
(`vdwforcefield.F` 2421–2524). Energy, force and stress contributions are
accumulated separately. Some paths additionally accept a Hessian; that argument
does not establish Hessian availability for every selection.

The sampled coefficient-table dispersion wrapper converts positions/cell to atomic
units and converts the resulting energy and derivatives back
(`subdftd3.F` 59–170). Its coefficient interpolation weights reference
coordination environments and falls back to the closest valid reference when
the accumulated weight is at or below a positive threshold (2533–2582).
Floating-point underflow is not required. The included numerical asset is unpacked into symmetric
species/environment tables (4070–4103). No values were adopted. Future
independent reconstruction needs appropriately sourced scientific parameters
with their provenance and terms, beyond reproducing a formula.

The density-dependent models use atomic volume and sometimes charge. The
sampled parameter adjustment scales polarizability and pair coefficients with
volume and interpolates charged reference states (`vdwforcefield_glb.F`
626–711). Its index bounds do not alone prove that interpolation weights stay
inside the reference interval. The many-body preparation checks parameter and
volume availability and contains both real-space and reciprocal-space calls.
Its local selector is initialized false and never changed, so the inspected
wrapper takes the reciprocal-space route. Derivatives are added only under a
separate gradient setting (`vdwforcefield.F` 5253–5411). Availability of the
other route through other callers remains untraced.

An iterative atomic-density partition introduces a second convergence problem.
The sampled fragment integrates atom-assigned charge, applies a neutrality
adjustment, tests a charge-change threshold, updates atomic charges, and may
rebuild reference atomic states when charge brackets change (11230–11365).
Electronic convergence therefore does not prove convergence of this partition.
The iteration cap, full density preparation, derivatives through this assignment
and periodic-image convergence remain unread.

The external dispersion interface and the many-body library wrapper
are build-dependent adapters, not complete in-tree implementations of the
external methods (`subdftd4.F` 1–176; `libmbd.F` 279–354). Both adapt geometry
and units; forces negate energy gradients. The sampled lattice derivatives
receive unit/sign or lattice transformations without an immediate division by
cell volume. Their relationship to the caller's stress convention must be
traced before labeling those arrays as intensive pressure. The many-body
wrapper checks an initialization exception and conditionally requests forces;
full external error and version behavior remains outside this inspection.

## Execution targets and return conditions

Exchange uses state reconstruction, batched transforms, matrix operations,
communication and device queues. The compressed and full actions exercise
different kernels. The density-correlation loop has accelerator atomics and
reductions where host code accumulates directly. The dispersion adapters and
atomic partition include substantial host/library work. Source directives
establish none of CPU/NVIDIA/AMD numerical agreement or practical throughput.

Return with ionic derivatives for the complete force/stress sum; with response
and many-body work for exchange reuse and empty-state requirements; with PAW
for atomic normalization; and with numerical libraries for factorizations and
reductions. Later bounded experiments should resolve the specific density-domain
and local-potential concerns, compressed-operator lifetime, singular sampling
limits, parameter interpolation, derivative consistency and external-library
conventions. Those experiments and the broad reference campaign remain future
work. Substantial unread bodies are deliberately carried forward.

## Review disposition

The [single independent review](reviews/nonlocal-interactions.md) identified
four warranted corrections. The report now distinguishes an inactive real-space
branch from a selectable route, occupation-based clearing from an empty
construction space, a weight threshold from numerical underflow, and the highest
retained band index from a count of occupied states. These corrections were
checked against the cited source. No second review or numerical experiment ran.
