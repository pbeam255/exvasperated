# Electrostatics, charge assembly and Hamiltonian fields: first pass

Studied 2026-09-24 against the quarantined VASP 6.5.1 snapshot. The
`electrostatics` partition contains 16 files and 15,224 lines. This report
connects selected charge, potential, boundary and operator paths. No program
was compiled or run, and no numerical result or hardware capability was verified.
Source references use the [inventory](../vasp-source-inventory.csv).

## Reading scope

Declarations and procedure maps were inspected across all 16 files. Body reading
was bounded as follows; substantial unlisted routines remain unread.

| Files | Body scope and remaining limits |
| --- | --- |
| `pot_struct.F`, `hamil_struct.F` | Entire short records: 1–31 and 1–14. |
| `charge.F` | 46–187, 1399–1423: smooth density and zero-mode extraction. Core-density and structure-factor machinery remains partial. |
| `pot_electrostat.F` | 22–219, 420–564: Hartree dispatch, kernel contraction, energy and padded/coarse correction. Detailed local ionic terms remain open. |
| `coulomb_cutoff.F` | 23–94, 151–259, 556–682: kernels, validation and setup. Full padding/index maps remain open. |
| `coulomb_cutoff_gradients.F` | 29–100: derivative setup and padded state; final force contraction remains unread. |
| `pot.F` | 180–320, 360–480, 490–630, 719–758 and call searches: assembly, transforms and soft-grid potential. Other specialized entry points remain open. |
| `hamil.F` | 921–977, 1115–1225: selected single-wave and batched application; later kinetic-density operator algebra remains open. |
| `hamil_rot.F` | 153–263: selected subspace subtraction and projector contraction. |
| `tau_mu.F` | 6–45, 194–252, 708–864: field storage and kinetic-density formation. Functional derivatives and all spin combinations remain open. |
| `dipol.F` | 51–90, 560–650, 674–735, 870–925: stored state, center choice and selected correction/force handling. Full applicability checks remain open. |
| `ebs.F` | 1143–1210, 1500–1751 and stress-call searches: Ewald dispatch and assembly. Real-space summation details remain largely unread. |
| `scpc.F` | 1–170, 199–261, 1210–1285: activation, grid setup and external solver call. Reference-density loading and detailed correction equations remain partial. |
| `bext.F` | 1–136: magnetic-field input shape and zero-mode addition. |
| `extpot.F`, `solvation.F` | Entire files, 1–73 and 1–121: extension placeholders in this snapshot. |

A cross-partition read of `electron.F` 634–650 checked the consumer of the
electrostatic energy correction. This does not constitute the electronic-solution
study.

## Charge is a family of coupled representations

Smooth electronic density is accumulated from transformed orbitals with
occupations, reciprocal-sampling weights and spin multiplicity. Zero-weight
states can be skipped. The sampled driver handles band redistribution, reduces
across sampling and band communicators, and performs another transform and
unbalanced-mode cleanup with offload disabled (`charge.F` 46–187). The PAW study
established the accompanying augmentation and on-site state. The array supplied
to electrostatics cannot be interpreted by its shape alone.

The origin-extraction helper locates the reciprocal zero mode and reduces its
contribution (`charge.F` 1399–1423). Checking total charge therefore needs the
Fourier normalization and ownership convention from the representation study.
An integral over the raw array without those conventions can be wrong even
when all its values are plausible.

Kinetic-density-dependent calculations introduce further fields and history.
The sampled path forms orbital gradients using the physical reciprocal vector,
including the sampling-point displacement, transforms them, and accumulates
weighted gradient products. Weights include cell volume and grid normalization;
spinor cross terms can occur (`tau_mu.F` 708–864). Its real-space and reciprocal
representations are then mapped between grids. The Hamiltonian record carries
both fine-grid and soft-grid derivatives of the energy with respect to this
quantity (`hamil_struct.F` 1–14). A scalar potential array alone is insufficient
to describe these operator states.

## The energy sign depends on its consumer

For the periodic Hartree path, the inspected kernel is proportional to
\(4\pi e^2/|G|^2\) away from the origin, while the origin is assigned zero.
Physical reciprocal vectors include the factor \(2\pi\). The potential
contraction divides by cell volume (`coulomb_cutoff.F` 23–94;
`pot_electrostat.F` 129–185).

The following energy helper contracts the potential with the conjugate density,
uses the reduced-storage weighting macros, performs a communicator reduction,
and returns **minus one half** of that contraction (`pot_electrostat.F`
187–218). This is stored as a correction in the total-energy assembly alongside
the band-energy sum (`pot.F` 490–569; `electron.F` 639–643). It should not be
mistaken for a claim that the physical Hartree self-energy is negative. The
band sum already contains interactions that require double-counting corrections.

Local ionic potential terms, atomic reference contributions, PAW terms, Ewald
terms, entropy and optional corrections enter through distinct paths. This
first pass has not derived their complete cancellation. A later independent
energy derivation must connect each stored contribution to its consumer before
comparing individual printed components or differentiating the total.

## Boundary conditions change kernels and the calculation around them

The truncated kernels explicitly treat the reciprocal origin. The sampled
spherical and slab formulas give different finite values there, including a
different sign. Reusing the periodic zero-mode rule would change the model.
The kernel helper's optional origin indicator defaults to false; the inspected
grid loop supplies it explicitly (`coulomb_cutoff.F` 151–259;
`pot_electrostat.F` 157–169). Other callers require their own check.

Input validation accepts a dimensionality range more broadly than the active
setup implements: the sampled truncated setup selects isolated or slab cases
and rejects the other active choices. A broad integer range is therefore not
evidence of a working wire kernel. Default truncation length and padding depend
on geometry and dimensionality; the simplified slab choice restricts explicit
overrides (`coulomb_cutoff.F` 556–682). Arbitrary cell shapes and orientations
have not been established as admissible.

The padded Hartree path may first coarsen the density. In that branch it forms
a coarse truncated potential minus a coarse periodic potential, maps the
difference back, and adds the fine periodic result (`pot_electrostat.F`
420–564). This is a multiresolution correction, with several transforms and
mode cleanups. Padding extent, coarse-grid error, map correctness and charge
localization all need examination; selecting the kernel alone does not settle
the boundary calculation.

The derivative module constructs padded geometry, density, structure factors
and work arrays independently (`coulomb_cutoff_gradients.F` 29–100). Its remaining
contractions have not been traced. In the Ewald reciprocal dispatcher, the slab
routine has no stress argument, whereas the three-dimensional routine receives
one (`ebs.F` 1143–1197). The final Ewald driver adds reciprocal, real-space,
self and background energy terms and combines force/stress contributions
(1590–1662). These observations make low-dimensional stress a specific return
question; they do not establish either a complete derivative or an observed bug.

## Assembly mutates both physical content and representation

The main potential driver evaluates XC in real space with spin/core handling,
adds selected constraints and dipole/external fields, transforms fields,
adds Hartree and local ionic contributions, and invokes optional corrections
and plugins (`pot.F` selected ranges above). Explicit grid-size scaling appears
in the potential transform, while density uses a separate scaled-transform
helper. The kinetic-density derivative has its own fine-to-soft transfer.

The soft-potential setup removes unbalanced modes, transfers between grids and
broadcasts across band communicators. It also transforms the full fine-grid
potential in place (`pot.F` 719–758). A later user of the same buffer must know
which representation it now contains. Selected constraint and plugin boundaries
explicitly transfer data between host and device and wait; other calls disable
offload. This creates scientific state and execution state dependencies together.

The sampled single-wave Hamiltonian path applies local real-space terms,
nonlocal projector contractions with the eigenvalue-dependent overlap
contribution, and kinetic terms (`hamil.F` 921–977). Batched paths use separate
queues and wait before releasing work arrays (1115–1225). The rotation helper
also subtracts combinations of both wavefunctions and projector coefficients
(`hamil_rot.F` 153–263). Electronic solution must establish which objects
represent the Hamiltonian action, generalized residual or subspace update at
each caller. Their similar-looking buffers do not establish interchangeability.

## Corrections have state and combination constraints

The dipole machinery stores previous moments, a previous center and mixing
state. Its sampled automatic center choice uses a planar-density construction
and combines old and new center information; moments near the periodic boundary
use special weighting (`dipol.F` selected ranges above). Ion forces, external
field energy and vacuum-level analysis also appear. Thus continuation and
iteration history can affect the correction procedure. The full initialization,
allowed geometries and convergence behavior remain open; this is not evidence
of a failure of physical translation invariance.

The self-consistent potential-correction module requires a particular compile
option and MPI, uses external solvers, and keeps a call counter and initialized
reference state. Activation can be delayed until a configured call threshold.
Its sampled setup derives grid spacing from diagonal lattice entries and
coarsens grid sizes (`scpc.F` 1–261). Cell-shape restrictions and reference-data
provenance must be resolved at callers and in the remaining loader. The sampled
multigrid invocation uses a single-process communicator, fixed boundary/finite-
difference choices, tolerances and iteration caps (1210–1285); these controls
are not scientific accuracy evidence. The potential driver supplies this
correction with a periodic Coulomb configuration, raising a concrete combination
question when the surrounding calculation uses a truncated kernel.

`bext.F` distinguishes scalar collinear input from a three-component noncollinear
field and adds the field to appropriate reciprocal zero components. Its field
units and downstream sign conventions remain for a focused interface study.

Two tempting capability shortcuts must be avoided. `extpot.F` contains inactive
extension bodies in this snapshot, but other external-potential paths exist in
`pot.F`. Likewise `solvation.F` supplies zero/no-op implementations here, including
zero force/energy state. This establishes the local extension's behavior only;
it says nothing about other distributions or externally supplied solvation code.

## Execution targets and return conditions

The sampled Hartree, density and operator paths contain accelerator regions;
other corrections use host execution or external solvers. No CPU, NVIDIA or AMD
execution was tested. Device annotations alone cannot establish supported method
combinations, data coherence, numerical agreement or performance.

Return with XC and electronic solution to derive the complete energy and
operator conventions; with ions/response to trace forces, stress and perturbation
derivatives; and with numerical kernels to establish transform and reduction
contracts. Boundary-specific later questions include charge neutrality and
background conventions, low-dimensional stress, padding/coarsening convergence,
reference-state restart behavior and allowed cell shapes. Independent limiting
cases and energy-derivative comparisons will be needed after the equations and
domains are understood. None were executed in this first pass.

## Review disposition

The [single independent review](reviews/electrostatics.md) found no substantive
corrections. Its source checks support the scoped claims; derivative completeness,
allowed combinations and numerical behavior remain open. No second review was
requested.
