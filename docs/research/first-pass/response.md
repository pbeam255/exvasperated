# Perturbations, polarization and response observables: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `response`
partition contains 20 files and 38,584 lines; identities are in the
[inventory](../vasp-source-inventory.csv). This original analysis is based on
source reading. No response calculation or numerical validation ran.

## Reading scope

Procedure and dependency searches guided the following bounded reads. Large
unread bodies remain, including complete physical derivations.

| Files | Body scope and limits |
| --- | --- |
| `linear_response.F` | Driver conditions/call map; 210–324, 576–691, 877–973; orbital refinement 1211–1293. Full displacement reconstruction and final restoration remain partial. |
| `ilinear_response.F` | 407–454, 530–576, 600–710, 750–877, 928–1005. Perturbation construction, occupations, mixing and exits sampled; complete force differentiation unread. Debug-only branches in these ranges were distinguished from normal execution. |
| `elinear_response.F` | 364–439, 559–686, 853–938. Field-loop coupling, stopping and tensor accumulation sampled; full field source and commutator derivation remain open. |
| `lr_helper.F` | Two-point potential derivative 663–742; selected higher-order stencil 850–920. Other helpers and full reset behavior remain partial. |
| `hamil_lr.F` | Batched action 204–265, 284–333; nonlocal/metric terms 655–722. Complete differentiated operator unread. |
| `hamil_lrf.F` | Field action/residual fragment 740–816. Commutator and full action remain partial. |
| `rmm-diis_lr.F` | Failure response 535–602; reductions/cleanup 678–734. Full linear solver remains unread. |
| `rmm-diis_mlr.F` | Residual, energy and stop fragment 688–735. Magnetic solver mostly unread. |
| `subrot_lr.F` | Subspace/degeneracy handling 170–229; occupied-space projection 670–735. Complete gauge/metric derivation remains open. |
| `pead.F` | Setup 365–438; polarization 926–1100; overlap adapter 1530–1571; band-bound helpers 1670–1743; phase accumulation/history 3735–3865; determinant helper 3936–3965. Most finite-field optimization and force code remains unread. |
| `elpol.F` | Berry entry 1289–1330; string overlaps, determinant conditioning and phases 1464–1599. Full normalization, ionic part and input remain partial. |
| `linear_optics.F` | Entry 195–282; matrix-element call search; assembly 802–955; transition accumulation 1376–1462. Broadening transforms, tetrahedra and conductivity kernels remain mostly unread. |
| `optics.F` | Older entry restriction 46–92; smooth matrix product 260–295; augmentation 297–362. Full writer and radial integrals unread. |
| `linear_response_NMR.F` | Entry/remapping 147–218; susceptibility 322–357; shifted-point and atomic work 826–914; spectral inverse 3401–3485. Most magnetic-response derivation unread. |
| `nmr.F` | Induced-field entry 2695–2725 and selected reciprocal/grid evaluation 2780–2870. Current construction, gauge and augmentation mostly unread. |
| `dmatrix.F` | Spin-tensor assembly 118–196; reciprocal kernel 658–723. Pair contractions and atomic angular terms mostly unread. |
| `egrad.F` | Fourier tensor 305–411; radial contribution 417–521 and output assembly 141–144; separate extrapolation helper 527–584. PAW caller 1748–1767 also inspected. Full reconstruction/output remains partial. |
| `hyperfine.F` | Fourier part 277–352; radial setup 382–478 and 567–633. Full core/relativistic treatment remains partial. |
| `cl_shift.F` | Core-hole density 214–281; potential-reference shifts 1337–1434. Radial eigenproblem, dataset mutation and full workflow unread. |
| `core_con_mat.F` | Core-state setup 134–169; spectrum 244–325. Radial matrix elements, normalization and input remain partial. |

## Response starts from a prepared state, not just a final density

The principal response driver rejects active exact exchange and meta-GGA in
this route, rebuilds potential and PAW matrices, refines orbitals and constructs
degenerate clusters (`linear_response.F` 210–324). Its refinement attempts at
most three Davidson updates with a tighter target, then restores the original
solver threshold (1238–1271). The cap does not establish that the tighter
criterion was reached. This is a concrete dependency on the electronic study.

Perturbations can lower symmetry. The inspected driver rereads reciprocal
sampling, rebuilds layouts, reallocates waves and optimizes newly introduced
states, then restores the unperturbed sampling after field directions
(576–639). A response tensor depends on these mappings and on consistent PAW
projector and wave phases, beyond having nominally the same point coordinates.

The driver distinguishes independent-particle response and self-consistent
field response, with or without the XC contribution. Its selected output
assembly also removes the mean Born-charge tensor over atoms and symmetrizes
it before storing the result (906–939). Later comparisons must distinguish
raw derivatives from enforced sum rules and symmetry projection. Agreement
after projection alone can hide disagreement in the underlying perturbations.

## Linear response still contains numerical differentiation

The ionic-response loop constructs a density derivative and calls a potential
derivative helper selected at preprocessing time (`ilinear_response.F`
421–452). The two-point helper evaluates the potential and PAW matrices at
positive and negative perturbations of density, on-site occupations and
displacement, then differences the results (`lr_helper.F` 683–739). A separate
body combines a higher-order stencil (850–920). Calling this route linear
response does not remove its finite step, cancellation or stencil dependence.

The ionic loop also perturbs eigenvalues in both directions, reruns occupation
integration and differences occupations, entropy and Fermi energy
(`ilinear_response.F` 663–680). Metallic occupation response therefore depends
on the smearing/integration contract examined in the electronic study. It
cannot be replaced by holding occupations fixed without changing the method.

The differentiated operator includes PAW projector derivatives, changes in
atomic matrices and overlap terms (`hamil_lr.F` 655–714). The subspace stage
forms reduced matrix elements, resolves selected degenerate clusters or removes
their terms, and divides by energy differences with a complex shift when
present (`subrot_lr.F` 170–229). At zero shift, differences below a threshold
are assigned zero in this stage. A selected occupied-space projection removes
rotations within filled states (706–715). These are gauge and degeneracy choices
to derive together with the full response equation.

The field Hamiltonian path separately checks the component along the reference
state and reports an internal failure above its bound (`hamil_lrf.F` 751–816).
The ionic operator uses a different diagnostic threshold and response
(`hamil_lr.F` 299–313). Shared naming does not imply identical failure behavior.

## Termination can mean stagnation

Both sampled self-consistent response loops compare energy-related measures,
but can also stop when residual histories change little. They have separate
small-density-residual tests and minimum iteration constraints
(`ilinear_response.F` 857–877; `elinear_response.F` 579–600). The ionic tests
include perturbation scaling. Neither a stagnation exit nor an exhausted loop
proves an absolute error bound on a dielectric constant or force constant.

The linear DIIS solver treats first-iteration factorization failure as an
internal error; later failure can increment an optional error count or emit a
warning and discontinue the current band (`rmm-diis_lr.F` 549–565). The sampled
drivers call it without that optional count. Full propagation into observable
validity remains untraced. The magnetic variant also has its own variational
measure and residual stopping (`rmm-diis_mlr.F` 688–733).

Mixing a response density uses the same broad infrastructure as ground-state
mixing but with different inputs: the ionic loop explicitly zeros the average
density change before mixing (`ilinear_response.F` 805–823). Charge neutrality,
PAW occupation derivatives and the Fermi response must remain consistent through
that operation. A complete proof or numerical check is still missing.

## Polarization carries a phase branch and history

The sampled finite-field/polarization setup requires a regular full sampling
grid, constructs point translations and atomic position-overlap corrections,
and rejects metallic occupations in polarization evaluation (`pead.F`
365–438, 962–975). Some field paths temporarily restrict active bands to the
occupied count, with a separate helper to restore the full bound (1679–1722).
Those state changes need a full lifecycle trace.

Both polarization implementations form occupied-state overlap matrices along
reciprocal-space strings. The older body checks square dimensions and estimated
conditioning, multiplies determinants and combines their phases around a mean
(`elpol.F` 1469–1599). The newer body normalizes individual determinants,
accumulates string products and phases, and warns when phases spread too far
around the mean (`pead.F` 3751–3802). Thus polarization is a branch-dependent
quantity; a pointwise comparison without branch correspondence is insufficient.

The newer routine stores an initial phase state and combines wrapped phase
differences with atomic expectation-value changes (3807–3864). A specific
source concern appears here: inside the spin loop, the phase-history difference
at 3831–3832 explicitly selects the first spin channel for both current and
initial arrays. Whether this affects a reachable spin-polarized finite-field
workflow requires tracing the calling conditions and an independent perturbation
comparison. This report does not claim an observed error.

Matrix conditioning, phase clustering and continuity of a physical path are
different questions. The determinant helper treats nonpositive estimated
conditioning as failure (3936–3965), but that alone does not bound errors near
a closing gap or guarantee a well-defined branch along a large perturbation.

## Optical spectra add empty states, frequency grids and conventions

The optical driver sets a frequency range from available unoccupied states,
allows an override and imposes a minimum grid size. It returns early for
certain metallic/tetrahedron and fixed-occupation combinations
(`linear_optics.F` 242–275). Those are restrictions of this route, not a
universal statement about every response method in the program.

The transition loop uses differences in occupations and eigenvalues, products
of directional matrix elements and reciprocal weights. It accumulates distinct
density and current responses, with energy-difference factors in the latter
(1376–1462). The assembler selects smeared or tetrahedron integration, reduces
and symmetrizes tensors, performs a real-part transformation and adds optional
intraband contributions (848–955). The sampled current-response conversion
subtracts its zero-frequency value before dividing by frequency squared, then
copies the second frequency entry to the first. Broadening, frequency range
and the zero-frequency prescription are therefore part of the reported result.

The separate older matrix-element path combines smooth momentum-like matrix
products and PAW augmentation (`optics.F` 260–351). Its entry warns, sets
matrix elements to zero and returns when more than one reciprocal-point
parallel group is used (49–58). This must not be generalized to the newer
optical driver. Tracing consumers of this early return is necessary to know
which workflows can continue with those zeros.

Later scientific checks include spectral-weight and symmetry relations,
gauge consistency and independent convergence of empty states, sampling,
broadening and frequency cutoff. None was performed in this pass.

## Magnetic and near-nucleus observables have additional reconstruction

The magnetic-response driver changes reciprocal sampling and state layout,
uses shifted-point responses and accumulates atomic augmentation separately
(`linear_response_NMR.F` 147–218, 826–914). A selected spectral inverse skips
occupied states and terms with energy denominators below a threshold
(3401–3485); whether that helper is the active route for a chosen calculation
still needs a caller trace. The susceptibility assembly has two related
operator choices and its own macroscopic conversion (322–357).

The sampled current-to-field grid path forms a reciprocal cross product divided
by reciprocal magnitude squared, excludes the origin, applies a small-denominator
floor and includes cell-volume normalization (`nmr.F` 2804–2840). Atomic
augmentation, core contributions and macroscopic boundary terms must be combined
before interpreting shielding or susceptibility. Their full gauge and boundary
derivation remains unread.

Electric-field-gradient reconstruction contracts a traceless reciprocal tensor
after a compensated charge/potential construction, omitting the origin
(`egrad.F` 305–411). The active PAW radial contribution forms all-electron
and pseudo Hartree potentials, extrapolates their angular components divided
by radius squared toward the nucleus, and stores their difference
(417–521; caller `paw.F` 1762). Output adds that contribution to the Fourier
tensor and reverses the sign (`egrad.F` 141–144). A separate sampled
extrapolation helper (527–584) does not establish an alternative assembly.
Hyperfine work
separately accumulates isotropic and anisotropic Fourier terms, with distinct
origin handling, and all-electron/pseudo radial contributions
(`hyperfine.F` 277–352, 414–478, 607–625). The sampled all-electron contact
estimate is subsequently replaced by a relativistic helper's result (613–616).
Reading only the first extrapolation would misidentify the final value.

The spin-spin tensor combines smooth and PAW terms, normalizes by a function
of total spin and diagonalizes the tensor (`dmatrix.F` 126–196). Two local
domain/initialization concerns remain: its entry excludes spin below one half
but the subsequent denominator vanishes at exactly one half (128–143);
the near-origin reciprocal-kernel branch sets only the three diagonal slots
of a six-component output (702–710). Input restrictions and caller initialization
must be checked before concluding that either causes a numerical defect.

Core-level work includes constructing a selected core-hole radial density and
aligning radial energy shifts to potential references (`cl_shift.F` 214–272,
1337–1423). The core-to-band spectrum contracts projector amplitudes with
radial matrix elements, unoccupied fractions and broadened transition energies
(`core_con_mat.F` 244–325). A displayed core transition energy consequently
depends on atomic reconstruction, reference alignment and final-state choices,
not just the ground-state band eigenvalues. Their full scientific interpretation
and solver accuracy remain future work.

## Execution targets and return conditions

Response combines wave redistribution, degenerate subspaces, perturbed density
mixing, matrix products, small tensor solvers and persistent phase state.
Some inspected operators use accelerator queues and reductions; several
postprocessing bodies are host loops. Legacy parallel restrictions coexist
with other distributed routes. No CPU/NVIDIA/AMD capability or agreement was
demonstrated by this inspection.

Return with vibrations for force constants, Born charges and relaxed-ion
response; with many-body methods for frequency and empty-state conventions;
with localized representations for matrix-element interpolation; and with
numerical helpers for conditioning, rank and failure propagation. Explicit
follow-up includes the three local phase/spin-kernel concerns above, stopping
reason versus observable error, branch correspondence, finite-difference limits
and complete restoration of perturbed state. The broad reference campaign and
experiments remain subsequent work, as do the substantial unread bodies.

## Independent review disposition

The [single independent review](reviews/response.md) identified one warranted
correction: distinguish the separate EFG extrapolation helper from the radial
contribution used in the assembled tensor. The author inspected that contribution
and its PAW caller and corrected the scope and explanation above. Other sampled
claims were supported within the stated limits. No second review or numerical
experiment was performed.
