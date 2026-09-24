# PAW data, projectors and on-site reconstruction

First pass, 2026-09-24. Study area: `paw`, 20 files. This pass establishes the
main data and calculation relationships, with selected radial, projector and
on-site bodies examined. It does not validate a dataset, prove PAW accuracy,
execute VASP or complete every file. The [inventory](../vasp-source-inventory.csv)
identifies the reference snapshot. No source or dataset content is adopted.

## Reading scope and file roles

All 20 files received declaration/procedure scans. Body ranges below describe
bounded reading; large scientific routines remain substantially open.

| File | Body scope | Role and remaining depth |
| --- | --- | --- |
| `pseudo_struct.F` | 1-136 | Atomic dataset state: partial waves, radial/core quantities, projectors, moments, reference energies and derived tables. |
| `radial_struct.F` | 1-34 | Radial mesh and quadrature state plus magnetic treatment settings. |
| `nl_struct.F` | 1-108 | Reciprocal and real-space projector storage, borrowed coordinates, phases and optional shared memory. |
| `pseudo.F` | 33-160, 544-673, 1209-1370; allocation/read searches | Dataset ingress, optional radial blocks, defaults and real-space projector preparation. Full parser/format coverage remains open. |
| `paw.F` | 29-237, 1412-1525, 1660-1740, 1905-1910, 1990-2075, 2090-2135; energy call searches | Augmentation setup and on-site potential/energy assembly. Atomic reference setup, full branches and derivatives remain open. |
| `paw_base.F` | 259-331 | Occupation matrix to angular augmentation coefficients. Complex/current and reverse transforms remain open. |
| `radial.F` | 79-167, 535-660, 823-905, 1651-1680 | Recomputed moments, radial charge/potential contraction, spherical Hartree/XC entry and quadrature weighting. Most XC/current/derivative routines remain unread. |
| `asa.F` | 174-227, 470-534 | Angular-product tables, lookup bounds and harmonic normalization setup. Full coefficients and derivatives need independent checking. |
| `nonl.F` | 254-336, 635-718, 878-960 | Reciprocal projector setup, phase cache, projection and residual contribution. Complete interpolation and derivative kernels remain open. |
| `nonlr.F` | 116-194, 1347-1440 | Real-space projector borrowing, localization parameters and phase setup. Main projection, force and stress bodies remain open. |
| `nonl_high.F` | 29-184 | Real/reciprocal and CPU/device projection dispatch. |
| `optreal.F` | 434-555 | Reciprocal-band/real-radius optimization setup and finite basis. Full objective, stopping behavior and error estimates remain open. |
| `us.F` | 324-429, 1154-1295 | Occupation accumulation and smooth/augmented charge orchestration. Grid augmentation, forces and stress need deeper reading. |
| `aedens.F` | 303-391, 550-631 | Reconstructed density assembly and compensation subtraction. Full radial interpolation/core selection remains open. |
| `pawsym.F` | 177-260 | Noncollinear on-site symmetry setup, orbital rotation and atom maps. Complete magnetic action remains open. |
| `fast_aug.F` | 93-198 | Exchange/many-body augmentation setup and explicit combination restriction. Restoration kernels remain mostly unread. |
| `relativistic.F` | 13-149 | Radial spin-orbit strength and angular assembly. Other matrix/output routines remain open. |
| `core_rel.F` | 63-145, 325-383, 458-515 | Per-ion dataset selection and core-relaxation initialization. Most self-consistent core work remains unread. |
| `rhfatm.F` | 30-115, 298-365 | Atomic solver state and dataset recalculation orchestration. Atomic Dirac/Hartree-Fock solvers remain unread. |
| `setlocalpp.F` | 30-161 | Filtering a local potential into a radial charge representation with a self-energy quantity and finite support choice. Remaining transforms/interpolation remain open. |

The overlap/residual contraction in `wave_high.F` 4812-4900 was also examined.

## Scientific meaning of the representations

In PAW, smooth orbitals are the variational objects. A transformation supplements
them with atom-centered differences between all-electron and smooth partial waves,
weighted by projector amplitudes. Density likewise has a smooth term and on-site
addition/subtraction terms. Compensation density matches the relevant multipoles
for grid electrostatics; it is not the fully reconstructed density. These are
public mathematical relationships, summarized by the
[PAW formalism documentation](https://vasp.at/wiki/Projector-augmented-wave_formalism)
(consulted 2026-09-24).

The inspected source exposes several distinct objects implementing these ideas:
smooth wave coefficients, projector amplitudes, on-site occupation matrices,
angular moments, radial densities, compensation functions and effective on-site
potential matrices. Equating any pair merely because they share an array shape
would lose physical meaning. In particular, a converged smooth charge is not by
itself a complete PAW state for restart or energy evaluation.

## Atomic datasets participate in the calculation

The dataset record includes valence/core information, atomic reference energies,
cutoff recommendations, local and nonlocal tables, all-electron/smooth partial
waves, core and kinetic densities, angular moments and original/updated copies
of selected potentials (`pseudo_struct.F`). It is richer than an element label
and a scalar potential.

The public `POTCAR` contract includes ordered species blocks and documents that
some methods require information absent from older datasets. Its reference
functional metadata remains relevant even when a calculation selects another
functional. See the [public format description](https://vasp.at/wiki/index.php/POTCAR)
(consulted 2026-09-24). That page is not a complete binary/text parser specification.

The source reader recognizes optional radial blocks and initializes missing
kinetic-density arrays to zero in the examined path. It preserves original and
updated potential records, and derives mesh spacing information from radial
endpoints (`pseudo.F` 544-673). Downstream method-specific admissibility checks
remain to be traced: a parser fallback is not evidence that missing data are
scientifically sufficient.

Postprocessing checks species count and reference-functional consistency, derives
default cutoffs when unspecified and can optimize real-space projectors using
the selected cutoff and precision settings (1209-1370). Consequently, the dataset
identity and the transformations applied to it both matter in an oracle comparison.
OSS distribution also needs independently sourced or generated scientific data;
supporting an input interface does not supply such data. The acquisition and
assessment choices belong to the later reference campaign.

## Augmentation setup both checks and changes data

The radial moment routine recomputes all-electron overlap quantities over a
selected radius, temporarily rebuilds quadrature weights, restores the original
radial extent, and integrates all-electron minus smooth partial-wave products
with radial powers. It checks the monopole against the supplied value and writes
the computed moments (`radial.F` 79-152). This is an active preprocessing step,
not a read-only consistency report.

Augmentation setup aligns a sphere boundary with the radial grid, builds
compensation functions from a finite spherical-Bessel combination and tabulates
splines (`paw.F` 29-164). Angular channels, reference channels and allocated
leading dimensions are distinct. The optimized-projector helper groups consecutive
channels of equal angular momentum and imposes a fixed small channel bound
(176-219). The supported dataset domain, ordering assumptions and behavior near
those bounds deserve explicit later examination.

Angular products use stored coupling tables and a particular real-harmonic
convention (`asa.F` 174-227, 470-534). The sampled occupation-to-moment transform
visits one triangle of channel pairs and doubles off-diagonal contributions
(`paw_base.F` 259-322). Complex, current and magnetic variants cannot be inferred
from that real case; conjugation and the appropriate independent matrix elements
need separate tracing.

## Projection, overlap and the electronic residual are coupled

Projection can operate in reciprocal space or on localized real-space grids.
The high-level driver selects the path and sets phases before projection
(`nonl_high.F` 29-88). The real-space setup borrows positions and dataset tables
while owning additional indexing/storage state (`nonlr.F` 116-172). Projector
optimization changes the finite real-space representation; equality with the
reciprocal calculation is therefore a convergence question, not a bytewise
equivalence promised by using the same dataset.

The reciprocal phase helper caches a sampling-point index and can return early
for a repeated index. The projection kernel checks that this index agrees with
the wave descriptor (`nonl.F` 635-683, 878-954). Moving ions while reusing a point
requires appropriate cache reset elsewhere. The guard checks point identity;
it does not by itself prove that the positions or basis used to build the phase
are current.

The nonlocal residual path contracts projector amplitudes with an on-site
potential matrix minus eigenvalue times an overlap correction, then applies the
projector contribution back to wave space (`nonl.F` 696-716;
`wave_high.F` 4812-4900). This explains why ordinary Euclidean orbital
orthogonality is not a sufficient description of the generalized electronic
problem. Complete normalization still requires the solver and overlap consumers.

## Charge assembly has multiple representations and symmetry stages

On-site occupations accumulate weighted projector outer products across bands,
sampling points and spin components. The weight includes occupation, reciprocal
weight and spin multiplicity; communicator reductions combine contributions
(`us.F` 324-414). The accelerator path explicitly returns the matrix to the host
and waits before the sampled host reductions.

The charge driver first forms smooth density, converts spin components, applies
selected symmetry treatment, forms on-site occupations and assembles augmentation
and mixed on-site state. Other symmetry settings act after assembly instead
(`us.F` 1154-1279). Matching a final grid alone would miss whether the accompanying
on-site and mixed state is consistent.

The reconstructed-density path adds partial-wave contributions, subtracts
compensation when requested, moves between augmentation/fine grids and adds the
smooth density (`aedens.F` 550-629). Resolution errors near nuclei and the choice
of core/pseudo reconstruction remain open. Output labeled as a density needs
its precise representation and normalization established before comparison.

## On-site energies connect many scientific methods

The sampled on-site driver reconstructs all-electron and smooth radial densities
from mixed angular state and can recover imaginary occupation information for
selected methods (`paw.F` 1660-1740). It then combines radial potential matrix
elements, augmentation contributions, kinetic-density terms, on-site exchange,
Hubbard corrections and spin-orbit contributions in conditional branches
(1990-2075). Energy corrections are accumulated separately and reduced before
being written to the shared energy record (1905-1910, 2090-2135).

Radial quadrature is sometimes incorporated into the potential array before a
later contraction (`radial.F` 593-647, 1651-1672). Reading a contraction in
isolation could mistakenly conclude that quadrature weights are missing—or add
them twice in a reconstruction. The all-electron/smooth cancellation and energy
derivatives need analysis through the entire chain.

The spin-orbit sample forms a radial potential derivative, integrates it against
partial waves and combines it with angular-spin matrices. Its local angular
coverage ends at a fixed bound (`relativistic.F` 13-149). Other capabilities must
be checked at their own callers. The fast augmentation setup rejects spin spirals
on the examined active path (`fast_aug.F` 143-152); that is a combination limit,
not a statement that all PAW calculations reject them.

Core treatment is also not exhausted by the usual frozen-core picture.
`core_rel.F` can select per-ion records after initialization, while `rhfatm.F`
orchestrates atomic calculations and replaces derived dataset information.
Their detailed equations, convergence and supported modes remain largely unread.
These files make a blanket claim that every dataset remains immutable during a
calculation untenable.

## Execution targets and return conditions

The inspected projection and occupation paths have accelerator implementations,
while the sampled on-site assembly explicitly disables offload. Real-space
projectors may also use shared-memory storage. These are data-motion and workload
partitioning facts, not evidence of functioning CPU/NVIDIA/AMD parity. Actual
method combinations and host/device consistency remain untested.

Return with electronic solution for the generalized metric and stationarity;
electrostatics/XC for compensation, double counting and core terms; ions/response
for projector derivatives and phase invalidation; and exchange/many-body methods
for shape restoration and atomic corrections. Later scientific checks should
separately challenge projector duality, radial moments, charge/overlap consistency,
real/reciprocal convergence, angular covariance and energy-force agreement.
Atomic transferability and dataset completeness need independent scientific
evidence beyond matching VASP. These are preserved questions for later work,
not a design selection or a claim of tests already performed.

## Review disposition

The [single independent review](reviews/paw.md) found no substantive corrections.
Its source checks support the bounded claims above; the unexamined equations,
method combinations and execution behavior remain open. No second review was
requested.
